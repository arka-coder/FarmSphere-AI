"""
FarmSphere AI — LangGraph Shared State
Defines the complete state object passed between all agents.
"""
from typing import TypedDict, Annotated, Optional, Any
from operator import add
import operator


def merge_dict(a: dict, b: dict) -> dict:
    """Merge two dicts, b overrides a for existing keys."""
    return {**a, **b}


class AgentTrace(TypedDict):
    agent_name: str
    started_at: float
    ended_at: float
    duration_ms: float
    status: str          # "success" | "error" | "skipped"
    output_summary: str


class SourceDocument(TypedDict):
    title: str
    source: str
    relevance_score: float
    excerpt: str


class FarmSphereState(TypedDict):
    # ── Farmer Context ─────────────────────────────────────────
    farmer_id: Optional[str]
    farmer_name: Optional[str]
    location: Optional[str]
    district: Optional[str]
    state_name: Optional[str]
    crop_type: Optional[str]
    land_size_acres: Optional[float]
    season: Optional[str]
    language: str                          # default: "en"

    # ── Current Request ────────────────────────────────────────
    user_message: str
    intent: Optional[str]                  # classified by orchestrator
    image_base64: Optional[str]            # for disease detection
    image_path: Optional[str]

    # ── Conversation History ───────────────────────────────────
    conversation_history: Annotated[list[dict], add]

    # ── Disease Detection ─────────────────────────────────────
    disease_name: Optional[str]
    disease_confidence: Optional[float]
    disease_symptoms: Optional[list[str]]
    disease_severity: Optional[str]        # mild | moderate | severe
    disease_alternatives: Optional[list[dict]]   # [{name, confidence}]
    hitl_required: bool                    # human-in-the-loop flag

    # ── Treatment ─────────────────────────────────────────────
    treatment_recommendations: Optional[list[dict]]

    # ── Weather ───────────────────────────────────────────────
    weather_data: Optional[dict]
    weather_advice: Optional[str]

    # ── Market ────────────────────────────────────────────────
    market_prices: Optional[dict]
    market_advice: Optional[str]

    # ── Government Schemes ────────────────────────────────────
    applicable_schemes: Optional[list[dict]]

    # ── Knowledge / RAG ───────────────────────────────────────
    retrieved_documents: Optional[list[SourceDocument]]
    knowledge_context: Optional[str]

    # ── Seasonal Intelligence ─────────────────────────────────
    seasonal_advice: Optional[str]
    crop_stage: Optional[str]

    # ── Risk Assessment ───────────────────────────────────────
    risk_scores: Optional[dict]            # {disease: 0.7, pest: 0.3, weather: 0.5}
    risk_summary: Optional[str]
    preventive_actions: Optional[list[str]]

    # ── Crop Calendar ─────────────────────────────────────────
    crop_calendar: Optional[dict]
    upcoming_tasks: Optional[list[dict]]

    # ── Proactive Alerts ──────────────────────────────────────
    active_alerts: Optional[list[dict]]

    # ── Satellite Intelligence ────────────────────────────────
    satellite_data: Optional[dict]         # NDVI, vegetation health, stress

    # ── Sustainability ────────────────────────────────────────
    sustainability_advice: Optional[str]

    # ── Scenario Simulation ───────────────────────────────────
    simulation_scenario: Optional[str]
    simulation_results: Optional[dict]

    # ── Explainability ────────────────────────────────────────
    reasoning_chain: Optional[list[str]]
    source_documents: Annotated[list[SourceDocument], add]
    confidence_breakdown: Optional[dict]
    explanation: Optional[str]

    # ── Translation ───────────────────────────────────────────
    final_response: Optional[str]
    translated_response: Optional[str]

    # ── Observability ─────────────────────────────────────────
    agent_traces: Annotated[list[AgentTrace], add]
    total_latency_ms: Optional[float]
    agents_invoked: Annotated[list[str], add]

    # ── Errors ────────────────────────────────────────────────
    errors: Annotated[list[str], add]
