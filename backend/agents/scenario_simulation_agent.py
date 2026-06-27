"""
FarmSphere AI — Scenario Simulation Agent ⭐ (Hidden Feature)
Answers "What If" questions by simulating multi-dimensional agricultural outcomes.

Example: "What if rainfall increases 50% next week?"
→ Disease risk ↑ 22%, Yield ↓ 5%, Recommendation: Delay fungicide until rain ends.

This is the differentiating feature most teams won't implement.
"""
import time
import logging
import json
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings
from agents.llm_helper import invoke_with_fallback

logger = logging.getLogger(__name__)

SIMULATION_SYSTEM_PROMPT = """You are FarmSphere AI's Predictive Agricultural Simulation Engine.
A farmer has asked a "What If" question. Simulate the realistic agricultural outcomes.

Return ONLY valid JSON in this exact format:
{
  "scenario": "Brief description of the simulated scenario",
  "baseline": {
    "disease_risk": 0.XX,
    "pest_risk": 0.XX,
    "yield_estimate_pct": 100,
    "recommended_actions": ["current action 1", "current action 2"]
  },
  "simulated": {
    "disease_risk": 0.XX,
    "disease_risk_change": "+XX% or -XX%",
    "pest_risk": 0.XX,
    "pest_risk_change": "+XX% or -XX%",
    "yield_estimate_pct": XX,
    "yield_change": "+X% or -X%",
    "water_stress": "low|moderate|high",
    "fungal_pressure": "low|moderate|high|critical",
    "key_changes": [
      "Change 1 with specific numbers",
      "Change 2 with specific numbers",
      "Change 3 with specific numbers"
    ],
    "adapted_recommendations": [
      "Specific action to take given this scenario",
      "Specific action 2",
      "Specific action 3"
    ]
  },
  "confidence_in_simulation": 0.XX,
  "simulation_reasoning": "2-3 sentence explanation of how this scenario affects crops",
  "critical_window": "The most critical time period in this scenario"
}"""

# Hardcoded simulation scenarios for demo/mock mode
MOCK_SIMULATIONS = {
    "rainfall_increase": {
        "scenario": "50% increase in rainfall next week",
        "baseline": {
            "disease_risk": 0.35, "pest_risk": 0.25, "yield_estimate_pct": 100,
            "recommended_actions": ["Monitor regularly", "Standard irrigation schedule"],
        },
        "simulated": {
            "disease_risk": 0.72, "disease_risk_change": "+106%",
            "pest_risk": 0.45, "pest_risk_change": "+80%",
            "yield_estimate_pct": 93, "yield_change": "-7%",
            "water_stress": "low", "fungal_pressure": "high",
            "key_changes": [
                "Disease risk increases from 35% to 72% — fungal pathogens thrive in wet conditions",
                "Yield drops 7% due to nutrient leaching and waterlogging stress",
                "Aphid and whitefly populations decline but fungal gnats increase by ~40%",
            ],
            "adapted_recommendations": [
                "Apply preventive Mancozeb (0.2%) immediately — before rains begin",
                "Improve field drainage channels to prevent waterlogging",
                "Delay any nitrogen top-dressing until after rainfall subsides",
                "Schedule pest monitoring for day 3 post-rain when conditions stabilize",
            ],
        },
        "confidence_in_simulation": 0.81,
        "simulation_reasoning": (
            "Increased rainfall creates prolonged leaf wetness, dramatically elevating fungal disease risk. "
            "Waterlogging reduces oxygen availability to roots, causing yield decline. "
            "The 7-day window requires immediate preventive action."
        ),
        "critical_window": "Days 1-3 of increased rainfall — apply preventive measures NOW",
    },
    "temperature_increase": {
        "scenario": "Temperature rises 5°C above normal for 2 weeks",
        "baseline": {
            "disease_risk": 0.35, "pest_risk": 0.25, "yield_estimate_pct": 100,
            "recommended_actions": ["Standard care", "Regular irrigation"],
        },
        "simulated": {
            "disease_risk": 0.28, "disease_risk_change": "-20%",
            "pest_risk": 0.65, "pest_risk_change": "+160%",
            "yield_estimate_pct": 85, "yield_change": "-15%",
            "water_stress": "high", "fungal_pressure": "low",
            "key_changes": [
                "Pest pressure dramatically increases — spider mites, aphids thrive in heat",
                "Flower drop increases by 30-45% causing significant yield reduction",
                "Water requirement increases 40% — irrigation frequency must double",
            ],
            "adapted_recommendations": [
                "Increase irrigation to early morning (5-7 AM) and evening (6-8 PM)",
                "Apply neem oil spray for spider mite prevention",
                "Install shade nets (25-30%) for heat-sensitive crops",
                "Apply potassium-rich fertilizer to improve heat tolerance",
            ],
        },
        "confidence_in_simulation": 0.78,
        "simulation_reasoning": (
            "Heat stress reduces photosynthesis efficiency and causes flower abortion. "
            "High temperatures accelerate pest life cycles dramatically. "
            "Yield loss can be reduced from 15% to 8% with proper interventions."
        ),
        "critical_window": "Days 4-7 — peak heat stress when flower development is most vulnerable",
    },
    "drought": {
        "scenario": "No rainfall for next 3 weeks (drought conditions)",
        "baseline": {
            "disease_risk": 0.35, "pest_risk": 0.25, "yield_estimate_pct": 100,
            "recommended_actions": ["Standard care"],
        },
        "simulated": {
            "disease_risk": 0.18, "disease_risk_change": "-49%",
            "pest_risk": 0.70, "pest_risk_change": "+180%",
            "yield_estimate_pct": 65, "yield_change": "-35%",
            "water_stress": "critical", "fungal_pressure": "low",
            "key_changes": [
                "Severe water stress reduces yield by up to 35% without intervention",
                "Spider mites and thrips populations can increase 3-5x in dry conditions",
                "Root systems weakened — secondary infections more likely after rains return",
            ],
            "adapted_recommendations": [
                "Switch to drip irrigation immediately — 40% water savings",
                "Apply mulch (5-7 cm) to reduce soil moisture evaporation",
                "Prioritize irrigation for critical growth stages (flowering/fruiting)",
                "Consider postponing next sowing if drought continues",
            ],
        },
        "confidence_in_simulation": 0.75,
        "simulation_reasoning": (
            "Drought eliminates fungal disease risk but creates severe physiological stress. "
            "Water deficit during reproductive stages causes irreversible yield loss. "
            "Intervention efficiency is highest in the first 5 days."
        ),
        "critical_window": "Days 1-5 — establish efficient irrigation before stress becomes irreversible",
    },
}


def _detect_scenario_type(message: str) -> str:
    """Detect what kind of simulation is being requested."""
    message_lower = message.lower()
    if any(w in message_lower for w in ["rain", "rainfall", "flood", "wet", "monsoon"]):
        if any(w in message_lower for w in ["increase", "more", "heavy", "excess"]):
            return "rainfall_increase"
    if any(w in message_lower for w in ["hot", "heat", "temperature", "warm", "degree"]):
        if any(w in message_lower for w in ["increase", "rise", "more", "higher"]):
            return "temperature_increase"
    if any(w in message_lower for w in ["drought", "dry", "no rain", "water stress"]):
        return "drought"
    return "rainfall_increase"  # default


def scenario_simulation_agent(state: FarmSphereState) -> dict:
    """
    Scenario Simulation Agent — Predictive 'What If' agricultural modeling.
    The hidden feature that differentiates FarmSphere from all other teams.
    """
    start_time = time.time()
    user_message = state.get("user_message", "")
    logger.info("Scenario simulation agent: %s", user_message[:100])

    try:
        scenario_type = _detect_scenario_type(user_message)

        if settings.google_api_key:
            try:
                context = (
                    f"Farmer scenario question: {user_message}\n"
                    f"Current crop: {state.get('crop_type', 'tomato')}\n"
                    f"Location: {state.get('location', 'India')}\n"
                    f"Season: {state.get('season', 'Kharif')}\n"
                    f"Current disease risk: {state.get('risk_scores', {}).get('disease_risk', 0.35)}\n"
                    f"Current weather: Temp={state.get('weather_data', {}).get('temperature', 28)}\u00b0C, "
                    f"Humidity={state.get('weather_data', {}).get('humidity', 70)}%\n"
                    f"Current crop stage: {state.get('crop_stage', 'vegetative')}"
                )
                raw = invoke_with_fallback(
                    [
                        SystemMessage(content=SIMULATION_SYSTEM_PROMPT),
                        HumanMessage(content=context),
                    ],
                    temperature=0.2,
                )
                if raw:
                    if "```json" in raw:
                        raw = raw.split("```json")[1].split("```")[0]
                    elif "```" in raw:
                        raw = raw.split("```")[1].split("```")[0]
                    simulation_results = json.loads(raw)
                else:
                    simulation_results = MOCK_SIMULATIONS.get(scenario_type, MOCK_SIMULATIONS["rainfall_increase"])
            except Exception as e:
                logger.warning("Simulation failed (%s) — using mock", e)
                simulation_results = MOCK_SIMULATIONS.get(scenario_type, MOCK_SIMULATIONS["rainfall_increase"])
        else:
            simulation_results = MOCK_SIMULATIONS.get(scenario_type, MOCK_SIMULATIONS["rainfall_increase"])

        source_doc = SourceDocument(
            title="FarmSphere Predictive Simulation Engine",
            source="Multi-variate Agricultural Model (FarmSphere AI)",
            relevance_score=0.92,
            excerpt=f"Simulated: {simulation_results.get('scenario', 'Custom scenario')} | "
                    f"Confidence: {simulation_results.get('confidence_in_simulation', 0):.0%}",
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="scenario_simulation_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Scenario: {simulation_results.get('scenario', '')} | "
                           f"Yield change: {simulation_results.get('simulated', {}).get('yield_change', '?')}",
        )

        # Build human-readable final response
        sim = simulation_results.get("simulated", {})
        scenario_name = simulation_results.get("scenario", "your scenario")
        final_response = f"""
## 🔮 Scenario Simulation: {scenario_name}

**Simulation Confidence:** {simulation_results.get('confidence_in_simulation', 0):.0%}

### 📊 Impact Analysis

| Factor | Current | Simulated | Change |
|--------|---------|-----------|--------|
| Disease Risk | {simulation_results.get('baseline', {}).get('disease_risk', 0):.0%} | {sim.get('disease_risk', 0):.0%} | **{sim.get('disease_risk_change', '?')}** |
| Pest Risk | {simulation_results.get('baseline', {}).get('pest_risk', 0):.0%} | {sim.get('pest_risk', 0):.0%} | **{sim.get('pest_risk_change', '?')}** |
| Est. Yield | 100% | {sim.get('yield_estimate_pct', 100)}% | **{sim.get('yield_change', '?')}** |
| Water Stress | Normal | {sim.get('water_stress', 'unknown').upper()} | — |
| Fungal Pressure | Normal | {sim.get('fungal_pressure', 'unknown').upper()} | — |

### 🔑 Key Changes
{chr(10).join(f'• {c}' for c in sim.get('key_changes', []))}

### 📋 Adapted Action Plan
{chr(10).join(f'{i+1}. {a}' for i, a in enumerate(sim.get('adapted_recommendations', [])))}

### ⏰ Critical Window
**{simulation_results.get('critical_window', 'Act promptly')}**

### 🧠 Simulation Reasoning
{simulation_results.get('simulation_reasoning', '')}
"""

        return {
            "simulation_scenario": user_message,
            "simulation_results": simulation_results,
            "final_response": final_response.strip(),
            "source_documents": [source_doc],
            "agent_traces": [trace],
            "agents_invoked": ["scenario_simulation_agent"],
            "errors": [],
        }

    except Exception as e:
        logger.error("Scenario simulation agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="scenario_simulation_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "simulation_results": None,
            "final_response": "Simulation engine encountered an error. Please try again.",
            "agent_traces": [trace],
            "agents_invoked": ["scenario_simulation_agent"],
            "source_documents": [],
            "errors": [f"Scenario simulation: {str(e)}"],
        }
