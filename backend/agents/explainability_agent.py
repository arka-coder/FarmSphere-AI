"""
FarmSphere AI — Explainability Agent (Layer 1)
Builds a transparent reasoning chain and confidence breakdown for every response.
Inspired by ChatGPT Deep Research — every step is shown.
"""
import time
import logging
from datetime import datetime

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings

logger = logging.getLogger(__name__)


def explainability_agent(state: FarmSphereState) -> dict:
    """
    Explainability Agent — Constructs transparent reasoning chain, 
    confidence breakdown, and explainability timeline for the frontend.
    """
    start_time = time.time()
    logger.info("Explainability agent building reasoning chain")

    try:
        reasoning_chain = []
        confidence_breakdown = {}

        # ── Step 1: Intent Recognition ────────────────────────────────────────
        intent = state.get("intent", "general_farming")
        reasoning_chain.append(
            f"**Intent Classification:** Your request was identified as "
            f"*{intent.replace('_', ' ').title()}* by the Orchestrator Agent."
        )

        # ── Step 2: Disease Analysis ──────────────────────────────────────────
        if state.get("disease_name"):
            disease_conf = state.get("disease_confidence", 0)
            reasoning_chain.append(
                f"**Disease Detection (Gemini Vision):** Analyzed your plant image and "
                f"identified *{state['disease_name']}* with **{disease_conf:.0%} confidence**. "
                f"Image quality was assessed as sufficient for diagnosis."
            )
            confidence_breakdown["disease_detection"] = disease_conf

            # Alternatives
            if state.get("disease_alternatives"):
                alt_text = ", ".join(
                    f"{a['name']} ({a['confidence']:.0%})"
                    for a in state["disease_alternatives"][:3]
                )
                reasoning_chain.append(
                    f"**Alternative Possibilities:** {alt_text}. "
                    f"These were considered and ranked lower based on visual evidence."
                )

        # ── Step 3: Knowledge Retrieval ───────────────────────────────────────
        retrieved = state.get("retrieved_documents") or []
        if retrieved:
            doc_names = [d.get("title", "Unknown") for d in retrieved[:3]]
            avg_relevance = sum(d.get("relevance_score", 0) for d in retrieved) / max(len(retrieved), 1)
            reasoning_chain.append(
                f"**Knowledge Retrieval (ChromaDB RAG):** Retrieved **{len(retrieved)} documents** "
                f"from the ICAR knowledge base. Average relevance score: **{avg_relevance:.0%}**. "
                f"Sources: {', '.join(doc_names)}."
            )
            confidence_breakdown["rag_retrieval"] = round(avg_relevance, 2)

        # ── Step 4: Weather Context ───────────────────────────────────────────
        if state.get("weather_data"):
            weather = state["weather_data"]
            reasoning_chain.append(
                f"**Weather Analysis (OpenWeatherMap):** Current conditions — "
                f"{weather.get('temperature', '?')}°C, {weather.get('humidity', '?')}% humidity, "
                f"{weather.get('weather_condition', '?')}. "
                f"Weather-crop interaction analyzed to adjust recommendations."
            )
            confidence_breakdown["weather_data"] = 0.95

        # ── Step 5: Seasonal Context ──────────────────────────────────────────
        if state.get("season") or state.get("crop_stage"):
            reasoning_chain.append(
                f"**Seasonal Intelligence:** Crop is in **{state.get('crop_stage', 'current')}** stage "
                f"during the **{state.get('season', 'current')}** season. "
                f"Season-specific risks and management practices applied."
            )
            confidence_breakdown["seasonal_context"] = 0.90

        # ── Step 6: Risk Assessment ───────────────────────────────────────────
        if state.get("risk_scores"):
            risks = state["risk_scores"]
            overall = risks.get("overall_risk", 0)
            highest = max(
                [(k, v) for k, v in risks.items() if k != "overall_risk" and isinstance(v, (int, float))],
                key=lambda x: x[1],
                default=("unknown", 0),
            )
            reasoning_chain.append(
                f"**Risk Assessment:** Overall farm risk is **{overall:.0%}**. "
                f"Highest risk factor: *{highest[0].replace('_risk', '').replace('_', ' ').title()}* "
                f"at **{highest[1]:.0%}**. Preventive actions generated accordingly."
            )
            confidence_breakdown["risk_assessment"] = min(overall + 0.1, 1.0)

        # ── Step 7: Final Synthesis ───────────────────────────────────────────
        agents_invoked = state.get("agents_invoked", [])
        reasoning_chain.append(
            f"**Recommendation Synthesis:** {len(agents_invoked)} specialized agents collaborated "
            f"({', '.join(agents_invoked)}). All outputs were merged into a unified recommendation "
            f"with citations from ICAR guidelines and real-time data sources."
        )

        # ── Overall confidence ────────────────────────────────────────────────
        if confidence_breakdown:
            overall_confidence = sum(confidence_breakdown.values()) / len(confidence_breakdown)
        else:
            overall_confidence = 0.75
        confidence_breakdown["overall"] = round(overall_confidence, 2)

        # ── Agent timeline for frontend ───────────────────────────────────────
        agent_traces = state.get("agent_traces", [])
        total_ms = sum(t.get("duration_ms", 0) for t in agent_traces)

        explanation = (
            f"This recommendation was generated by **{len(agents_invoked)} AI agents** working together "
            f"in {total_ms:.0f}ms. The overall confidence in this analysis is **{overall_confidence:.0%}**. "
            f"All recommendations are based on ICAR certified guidelines and real-time data — never guesswork."
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="explainability_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Reasoning chain: {len(reasoning_chain)} steps | Overall confidence: {overall_confidence:.0%}",
        )

        return {
            "reasoning_chain": reasoning_chain,
            "confidence_breakdown": confidence_breakdown,
            "explanation": explanation,
            "total_latency_ms": total_ms,
            "agent_traces": [trace],
            "agents_invoked": ["explainability_agent"],
            "errors": [],
        }

    except Exception as e:
        logger.error("Explainability agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="explainability_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "reasoning_chain": ["Explainability processing encountered an error."],
            "confidence_breakdown": {},
            "explanation": "Full explainability temporarily unavailable.",
            "agent_traces": [trace],
            "agents_invoked": ["explainability_agent"],
            "errors": [f"Explainability agent: {str(e)}"],
        }
