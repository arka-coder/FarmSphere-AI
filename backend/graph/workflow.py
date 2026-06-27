"""
FarmSphere AI — LangGraph Workflow
Connects all 17 agents with conditional edges, state routing, and parallel execution.
"""
import logging
from langgraph.graph import StateGraph, END

from graph.state import FarmSphereState
from agents.orchestrator import orchestrator_agent, route_after_orchestrator
from agents.disease_agent import disease_agent, route_after_disease
from agents.weather_agent import weather_agent
from agents.knowledge_agent import knowledge_agent
from agents.seasonal_agent import seasonal_agent
from agents.risk_agent import risk_agent
from agents.recommendation_agent import recommendation_agent
from agents.explainability_agent import explainability_agent
from agents.supporting_agents import (
    translation_agent, memory_agent, scheme_agent,
    market_agent, crop_calendar_agent, alert_agent,
)
from agents.advanced_agents import satellite_agent, community_agent, sustainability_agent
from agents.scenario_simulation_agent import scenario_simulation_agent

logger = logging.getLogger(__name__)


def build_workflow() -> StateGraph:
    """
    Build the FarmSphere LangGraph workflow.

    Flow:
    orchestrator → (route by intent) → core agents → recommendation → explainability → translation → memory → END

    Parallel enrichment nodes (weather, seasonal, risk, alert) run after initial routing.
    """
    workflow = StateGraph(FarmSphereState)

    # ── Add all nodes ─────────────────────────────────────────────────────────
    workflow.add_node("orchestrator", orchestrator_agent)
    workflow.add_node("disease_agent", disease_agent)
    workflow.add_node("weather_agent", weather_agent)
    workflow.add_node("knowledge_agent", knowledge_agent)
    workflow.add_node("seasonal_agent", seasonal_agent)
    workflow.add_node("risk_agent", risk_agent)
    workflow.add_node("recommendation_agent", recommendation_agent)
    workflow.add_node("explainability_agent", explainability_agent)
    workflow.add_node("translation_agent", translation_agent)
    workflow.add_node("memory_agent", memory_agent)

    # Layer 2
    workflow.add_node("scheme_agent", scheme_agent)
    workflow.add_node("market_agent", market_agent)
    workflow.add_node("crop_calendar_agent", crop_calendar_agent)
    workflow.add_node("alert_agent", alert_agent)

    # Layer 3
    workflow.add_node("satellite_agent", satellite_agent)
    workflow.add_node("community_agent", community_agent)
    workflow.add_node("sustainability_agent", sustainability_agent)
    workflow.add_node("scenario_simulation_agent", scenario_simulation_agent)

    # ── Entry point ───────────────────────────────────────────────────────────
    workflow.set_entry_point("orchestrator")

    # ── Orchestrator → Route by intent ───────────────────────────────────────
    workflow.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "disease_agent": "disease_agent",
            "knowledge_agent": "knowledge_agent",
            "weather_agent": "weather_agent",
            "market_agent": "market_agent",
            "scheme_agent": "scheme_agent",
            "crop_calendar_agent": "crop_calendar_agent",
            "risk_agent": "risk_agent",
            "satellite_agent": "satellite_agent",
            "scenario_simulation_agent": "scenario_simulation_agent",
            "recommendation_agent": "recommendation_agent",
        },
    )

    # ── Disease agent → Knowledge for treatment context ───────────────────────
    workflow.add_conditional_edges(
        "disease_agent",
        route_after_disease,
        {"knowledge_agent": "knowledge_agent"},
    )

    # ── After primary agents → run enrichment pipeline ───────────────────────
    # knowledge → weather → seasonal → risk → alert → recommendation
    workflow.add_edge("knowledge_agent", "weather_agent")
    workflow.add_edge("weather_agent", "seasonal_agent")
    workflow.add_edge("seasonal_agent", "risk_agent")
    workflow.add_edge("risk_agent", "alert_agent")
    workflow.add_edge("alert_agent", "recommendation_agent")

    # ── Direct intent routes → their enrichment needs ─────────────────────────
    workflow.add_edge("market_agent", "recommendation_agent")
    workflow.add_edge("scheme_agent", "recommendation_agent")
    workflow.add_edge("crop_calendar_agent", "recommendation_agent")
    workflow.add_edge("satellite_agent", "recommendation_agent")
    workflow.add_edge("scenario_simulation_agent", "explainability_agent")

    # ── Final pipeline: recommendation → explainability → translation → memory → END
    workflow.add_edge("recommendation_agent", "explainability_agent")
    workflow.add_edge("explainability_agent", "translation_agent")
    workflow.add_edge("translation_agent", "memory_agent")
    workflow.add_edge("memory_agent", END)

    return workflow


def compile_app():
    """Compile the LangGraph workflow into a runnable app."""
    workflow = build_workflow()
    app = workflow.compile()
    logger.info("FarmSphere LangGraph workflow compiled successfully")
    return app


# Singleton compiled app
_app = None


def get_app():
    global _app
    if _app is None:
        _app = compile_app()
    return _app
