"""
FarmSphere AI — Orchestrator Agent (Layer 1)
Classifies intent, activates relevant agents, and manages LangGraph routing.
"""
import time
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace
from config import settings
from agents.llm_helper import invoke_with_fallback

logger = logging.getLogger(__name__)

# Intent taxonomy
INTENTS = Literal[
    "disease_diagnosis",
    "treatment_advice",
    "weather_query",
    "market_query",
    "scheme_query",
    "crop_planning",
    "risk_assessment",
    "satellite_query",
    "scenario_simulation",
    "general_farming",
    "greeting",
]

INTENT_SYSTEM_PROMPT = """You are an agricultural intent classifier for FarmSphere AI.

Classify the farmer's message into ONE of these intents:
- disease_diagnosis: farmer describes plant disease symptoms or uploads a leaf/fruit image
- treatment_advice: farmer asks how to treat a known disease or pest
- weather_query: questions about weather, rain, temperature
- market_query: crop prices, where to sell, market trends
- scheme_query: government schemes, subsidies, PM-KISAN, insurance
- crop_planning: what to plant, when to plant, crop calendar
- risk_assessment: disease risk, pest risk, yield risk
- satellite_query: NDVI, vegetation health, field stress
- scenario_simulation: "what if" questions about rainfall, temperature changes
- general_farming: fertilizer, irrigation, organic farming, general advice
- greeting: hello, who are you, what can you do

Respond with ONLY the intent label. Nothing else."""


def _rule_based_intent(message: str) -> str:
    """Keyword fallback if Gemini is unavailable."""
    msg = message.lower()
    if any(w in msg for w in ["disease", "spot", "blight", "rust", "fungal", "leaf", "yellow", "brown", "symptom"]):
        return "disease_diagnosis"
    if any(w in msg for w in ["rain", "weather", "temperature", "humidity", "forecast", "wind", "sunny"]):
        return "weather_query"
    if any(w in msg for w in ["price", "market", "mandi", "sell", "rate", "quintal"]):
        return "market_query"
    if any(w in msg for w in ["scheme", "pm-kisan", "subsidy", "government", "insurance", "kisan"]):
        return "scheme_query"
    if any(w in msg for w in ["calendar", "when to sow", "planting", "harvest", "schedule"]):
        return "crop_planning"
    if any(w in msg for w in ["risk", "pest", "outbreak"]):
        return "risk_assessment"
    if any(w in msg for w in ["ndvi", "satellite", "vegetation", "field health"]):
        return "satellite_query"
    if any(w in msg for w in ["what if", "simulate", "scenario", "drought", "flood", "what happens"]):
        return "scenario_simulation"
    if any(w in msg for w in ["hello", "hi", "who are you", "what can you"]):
        return "greeting"
    return "general_farming"


def classify_intent(message: str) -> str:
    """Use Gemini with fallback to classify the farmer's intent."""
    try:
        result = invoke_with_fallback(
            [
                SystemMessage(content=INTENT_SYSTEM_PROMPT),
                HumanMessage(content=f"Farmer message: {message}"),
            ],
            temperature=0.1,
        )
        if result:
            intent = result.strip().lower()
            valid_intents = [
                "disease_diagnosis", "treatment_advice", "weather_query",
                "market_query", "scheme_query", "crop_planning", "risk_assessment",
                "satellite_query", "scenario_simulation", "general_farming", "greeting",
            ]
            return intent if intent in valid_intents else "general_farming"
    except Exception as e:
        logger.warning("Intent classification failed: %s", e)
    return _rule_based_intent(message)


def orchestrator_agent(state: FarmSphereState) -> dict:
    """
    Orchestrator Agent — Entry point of the LangGraph workflow.
    Classifies intent and enriches state for downstream agents.
    """
    start_time = time.time()
    logger.info("Orchestrator processing message: %s", state.get("user_message", "")[:100])

    try:
        user_message = state.get("user_message", "")

        # Force disease_diagnosis if image is present
        if state.get("image_base64") or state.get("image_path"):
            intent = "disease_diagnosis"
        else:
            intent = classify_intent(user_message)

        logger.info("Classified intent: %s", intent)

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="orchestrator",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Intent classified as: {intent}",
        )

        return {
            "intent": intent,
            "agent_traces": [trace],
            "agents_invoked": ["orchestrator"],
            "errors": [],
            "source_documents": [],
            "conversation_history": [],
        }

    except Exception as e:
        logger.error("Orchestrator error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="orchestrator",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "intent": "general_farming",
            "agent_traces": [trace],
            "agents_invoked": ["orchestrator"],
            "errors": [f"Orchestrator: {str(e)}"],
            "source_documents": [],
            "conversation_history": [],
        }


def route_after_orchestrator(state: FarmSphereState) -> str:
    """LangGraph conditional edge — decides which agent runs next."""
    intent = state.get("intent", "general_farming")

    routing_map = {
        "disease_diagnosis": "disease_agent",
        "treatment_advice": "knowledge_agent",
        "weather_query": "weather_agent",
        "market_query": "market_agent",
        "scheme_query": "scheme_agent",
        "crop_planning": "crop_calendar_agent",
        "risk_assessment": "risk_agent",
        "satellite_query": "satellite_agent",
        "scenario_simulation": "scenario_simulation_agent",
        "general_farming": "knowledge_agent",
        "greeting": "recommendation_agent",
    }

    return routing_map.get(intent, "knowledge_agent")
