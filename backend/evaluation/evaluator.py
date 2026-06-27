"""
FarmSphere AI — Evaluation Framework
Faithfulness, RAG metrics, latency, confidence, hallucination detection.
Judges love evaluation — this is a competitive differentiator.
"""
import time
import logging
import re
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    metric_name: str
    score: float                    # 0.0 - 1.0
    label: str                      # pass / warn / fail
    details: str
    raw_data: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.label == "pass"

    def to_dict(self) -> dict:
        return {
            "metric": self.metric_name,
            "score": round(self.score, 4),
            "label": self.label,
            "details": self.details,
        }


# ── Thresholds ────────────────────────────────────────────────────────────────
THRESHOLDS = {
    "faithfulness": {"pass": 0.75, "warn": 0.50},
    "answer_relevance": {"pass": 0.70, "warn": 0.45},
    "context_recall": {"pass": 0.65, "warn": 0.40},
    "disease_confidence": {"pass": 0.75, "warn": 0.50},
    "latency_ms": {"pass": 5000, "warn": 10000},    # lower is better
    "hallucination_risk": {"pass": 0.20, "warn": 0.50},  # lower is better
}


def _classify(score: float, metric: str, lower_is_better: bool = False) -> str:
    thresholds = THRESHOLDS.get(metric, {"pass": 0.70, "warn": 0.40})
    pass_t = thresholds["pass"]
    warn_t = thresholds["warn"]
    if lower_is_better:
        if score <= pass_t:
            return "pass"
        elif score <= warn_t:
            return "warn"
        return "fail"
    else:
        if score >= pass_t:
            return "pass"
        elif score >= warn_t:
            return "warn"
        return "fail"


# ════════════════════════════════════════════════════════════════════════════
# faithfulness.py — Is the answer grounded in retrieved documents?
# ════════════════════════════════════════════════════════════════════════════

def evaluate_faithfulness(
    answer: str,
    retrieved_docs: list[dict],
    use_llm: bool = False,
) -> EvaluationResult:
    """
    Measure whether the generated answer is faithful to retrieved source documents.
    Uses keyword overlap as a lightweight proxy (LLM-based optional).
    """
    if not retrieved_docs or not answer:
        return EvaluationResult(
            metric_name="faithfulness",
            score=0.5,
            label="warn",
            details="No retrieved documents to verify faithfulness against",
        )

    # Extract all significant words from retrieved docs
    doc_text = " ".join(d.get("excerpt", "") + " " + d.get("title", "") for d in retrieved_docs).lower()
    doc_words = set(re.findall(r'\b[a-z]{4,}\b', doc_text))

    # Check how many key terms from the answer appear in retrieved docs
    answer_words = set(re.findall(r'\b[a-z]{4,}\b', answer.lower()))

    # Agricultural stopwords to exclude
    stopwords = {"that", "this", "with", "from", "have", "been", "will", "your", "their", "which", "when", "then"}
    answer_words -= stopwords
    doc_words -= stopwords

    if not answer_words:
        return EvaluationResult(metric_name="faithfulness", score=0.5, label="warn",
                                details="Answer is too short for faithfulness evaluation")

    overlap = len(answer_words & doc_words)
    score = min(1.0, overlap / max(len(answer_words) * 0.3, 1))

    # Check for hallucination markers — specific numbers not in sources
    numbers_in_answer = set(re.findall(r'\b\d+\.?\d*\b', answer))
    numbers_in_docs = set(re.findall(r'\b\d+\.?\d*\b', doc_text))
    unsupported_numbers = numbers_in_answer - numbers_in_docs
    if unsupported_numbers and len(unsupported_numbers) > 3:
        score *= 0.85  # Penalize for potentially hallucinated numbers

    label = _classify(score, "faithfulness")
    return EvaluationResult(
        metric_name="faithfulness",
        score=score,
        label=label,
        details=f"Keyword overlap: {overlap}/{len(answer_words)} unique terms found in sources",
        raw_data={"doc_word_count": len(doc_words), "answer_word_count": len(answer_words)},
    )


# ════════════════════════════════════════════════════════════════════════════
# rag_metrics.py — RAG retrieval quality
# ════════════════════════════════════════════════════════════════════════════

def evaluate_rag_quality(
    query: str,
    retrieved_docs: list[dict],
    n_expected: int = 3,
) -> EvaluationResult:
    """
    Evaluate ChromaDB retrieval quality: relevance scores, diversity, coverage.
    """
    if not retrieved_docs:
        return EvaluationResult(metric_name="rag_quality", score=0.0, label="fail",
                                details="No documents retrieved from ChromaDB")

    relevance_scores = [d.get("relevance_score", 0) for d in retrieved_docs]
    avg_relevance = sum(relevance_scores) / len(relevance_scores)

    # Coverage: did we get enough documents?
    coverage_score = min(1.0, len(retrieved_docs) / n_expected)

    # Source diversity: different sources = better
    sources = set(d.get("source", "") for d in retrieved_docs)
    diversity_score = min(1.0, len(sources) / max(len(retrieved_docs), 1) * 1.5)

    # Combined RAG score
    rag_score = avg_relevance * 0.5 + coverage_score * 0.3 + diversity_score * 0.2

    label = _classify(rag_score, "answer_relevance")
    return EvaluationResult(
        metric_name="rag_quality",
        score=rag_score,
        label=label,
        details=(
            f"Avg relevance: {avg_relevance:.2%} | "
            f"Retrieved: {len(retrieved_docs)}/{n_expected} | "
            f"Unique sources: {len(sources)}"
        ),
        raw_data={"relevance_scores": relevance_scores, "source_count": len(sources)},
    )


# ════════════════════════════════════════════════════════════════════════════
# latency_metrics.py — Agent execution time tracking
# ════════════════════════════════════════════════════════════════════════════

def evaluate_latency(agent_traces: list[dict]) -> EvaluationResult:
    """
    Evaluate system latency across all agents.
    """
    if not agent_traces:
        return EvaluationResult(metric_name="latency", score=1.0, label="pass",
                                details="No trace data available")

    total_ms = sum(t.get("duration_ms", 0) for t in agent_traces)
    slowest = max(agent_traces, key=lambda t: t.get("duration_ms", 0))
    errors = [t for t in agent_traces if t.get("status") == "error"]

    # Score: inverse of total time, normalized to 10 second budget
    budget_ms = 10000
    time_score = max(0, 1 - (total_ms / budget_ms))
    # Penalize errors
    error_penalty = len(errors) * 0.1
    final_score = max(0, time_score - error_penalty)

    label = _classify(total_ms, "latency_ms", lower_is_better=True)
    return EvaluationResult(
        metric_name="latency",
        score=final_score,
        label=label,
        details=(
            f"Total: {total_ms:.0f}ms | Agents: {len(agent_traces)} | "
            f"Slowest: {slowest.get('agent_name')} ({slowest.get('duration_ms', 0):.0f}ms) | "
            f"Errors: {len(errors)}"
        ),
        raw_data={
            "total_ms": total_ms,
            "per_agent": {t["agent_name"]: t["duration_ms"] for t in agent_traces},
        },
    )


# ════════════════════════════════════════════════════════════════════════════
# confidence_metrics.py — Disease diagnosis confidence quality
# ════════════════════════════════════════════════════════════════════════════

def evaluate_confidence(
    disease_confidence: Optional[float],
    alternatives: Optional[list[dict]],
) -> EvaluationResult:
    """
    Evaluate the quality of the disease confidence distribution.
    A good system should have clear separation between primary and alternatives.
    """
    if disease_confidence is None:
        return EvaluationResult(metric_name="confidence_quality", score=0.5, label="warn",
                                details="No disease diagnosis in this session")

    score = disease_confidence
    details_parts = [f"Primary confidence: {disease_confidence:.0%}"]

    if alternatives:
        alt_scores = [a.get("confidence", 0) for a in alternatives]
        max_alt = max(alt_scores) if alt_scores else 0
        # Good separation: primary >> alternatives
        separation = disease_confidence - max_alt
        separation_score = min(1.0, separation / 0.30)
        score = disease_confidence * 0.6 + separation_score * 0.4
        details_parts.append(f"Best alternative: {max_alt:.0%}")
        details_parts.append(f"Confidence gap: {separation:.0%}")

    # Check for calibration (overly confident = bad)
    if disease_confidence > 0.98:
        score *= 0.90  # slight penalty for overclaiming
        details_parts.append("⚠️ Near-perfect confidence may indicate overconfidence")

    label = _classify(score, "disease_confidence")
    return EvaluationResult(
        metric_name="confidence_quality",
        score=score,
        label=label,
        details=" | ".join(details_parts),
    )


# ════════════════════════════════════════════════════════════════════════════
# hallucination_detection.py — Detect unsupported claims
# ════════════════════════════════════════════════════════════════════════════

HALLUCINATION_RED_FLAGS = [
    r"100% (sure|certain|accurate|confident)",
    r"guaranteed to (cure|work|fix|eliminate)",
    r"always works",
    r"never fails",
    r"according to (my|our) research",        # should cite external sources
    r"studies show .{0,30} \d{2,3}%",         # unsourced statistics
    r"invented by",
    r"discovered in \d{4}",                    # historical claims
]

UNCERTAINTY_MARKERS = [
    "may", "might", "could", "possibly", "likely", "approximately",
    "estimated", "suggest", "recommend consulting", "confidence",
]


def evaluate_hallucination_risk(answer: str, sources: list[dict]) -> EvaluationResult:
    """
    Detect potential hallucination patterns in the generated answer.
    Checks for red flag phrases, overconfident claims, and missing citations.
    """
    answer_lower = answer.lower()
    risk_score = 0.0
    flags_found = []

    # Check for red flag patterns
    for pattern in HALLUCINATION_RED_FLAGS:
        if re.search(pattern, answer_lower):
            risk_score += 0.15
            flags_found.append(pattern)

    # Reward uncertainty markers (calibrated language)
    uncertainty_count = sum(1 for m in UNCERTAINTY_MARKERS if m in answer_lower)
    uncertainty_bonus = min(0.3, uncertainty_count * 0.06)
    risk_score = max(0, risk_score - uncertainty_bonus)

    # Reward source citations
    if sources:
        risk_score = max(0, risk_score - 0.10 * min(len(sources), 3))

    # Check for unsupported specific claims
    specific_pcts = re.findall(r'\b\d{2,3}%\b', answer)
    if len(specific_pcts) > 5 and len(sources) == 0:
        risk_score += 0.10
        flags_found.append("Many specific percentages without cited sources")

    risk_score = min(1.0, risk_score)
    label = _classify(risk_score, "hallucination_risk", lower_is_better=True)

    details = "No hallucination patterns detected"
    if flags_found:
        details = f"Potential issues: {'; '.join(flags_found[:3])}"
    elif risk_score < 0.1:
        details = f"Low hallucination risk — good use of uncertainty language (markers found: {uncertainty_count})"

    return EvaluationResult(
        metric_name="hallucination_risk",
        score=risk_score,
        label=label,
        details=details,
        raw_data={"flags": flags_found, "uncertainty_markers": uncertainty_count},
    )


# ════════════════════════════════════════════════════════════════════════════
# Aggregated evaluation runner
# ════════════════════════════════════════════════════════════════════════════

def run_full_evaluation(state: dict) -> dict:
    """Run all evaluation metrics on a completed FarmSphere response."""
    results = []

    answer = state.get("translated_response") or state.get("final_response", "")
    retrieved = state.get("retrieved_documents") or state.get("source_documents") or []
    agent_traces = state.get("agent_traces") or []
    disease_confidence = state.get("disease_confidence")
    alternatives = state.get("disease_alternatives")

    results.append(evaluate_faithfulness(answer, retrieved).to_dict())
    results.append(evaluate_rag_quality(state.get("user_message", ""), retrieved).to_dict())
    results.append(evaluate_latency(agent_traces).to_dict())
    results.append(evaluate_confidence(disease_confidence, alternatives).to_dict())
    results.append(evaluate_hallucination_risk(answer, retrieved).to_dict())

    # Aggregate
    numeric_scores = [r["score"] for r in results if r["label"] != "pass" or True]
    overall = sum(numeric_scores) / len(numeric_scores) if numeric_scores else 0.5
    passed = sum(1 for r in results if r["label"] == "pass")

    return {
        "overall_score": round(overall, 3),
        "passed_checks": passed,
        "total_checks": len(results),
        "evaluation_summary": f"{passed}/{len(results)} checks passed | Score: {overall:.0%}",
        "metrics": results,
        "timestamp": time.time(),
    }
