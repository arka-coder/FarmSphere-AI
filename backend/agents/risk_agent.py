"""
FarmSphere AI — Risk Assessment Agent (Layer 1)
Calculates multi-dimensional risk scores and generates preventive action plans.
"""
import time
import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings

logger = logging.getLogger(__name__)

RISK_SYSTEM_PROMPT = """You are an agricultural risk assessment expert.
Given the following farmer context, generate a precise risk assessment.
Return ONLY valid JSON in this exact format:
{
  "risk_scores": {
    "disease_risk": 0.XX,
    "pest_risk": 0.XX,
    "weather_risk": 0.XX,
    "irrigation_risk": 0.XX,
    "market_risk": 0.XX,
    "overall_risk": 0.XX
  },
  "risk_summary": "2-sentence overall risk assessment",
  "preventive_actions": [
    "Specific action 1",
    "Specific action 2",
    "Specific action 3",
    "Specific action 4"
  ],
  "highest_risk_factor": "disease|pest|weather|irrigation|market",
  "alert_level": "low|medium|high|critical"
}"""


def _calculate_rule_based_risks(state: FarmSphereState) -> dict:
    """Rule-based risk scoring as fallback when Gemini is unavailable."""
    weather = state.get("weather_data", {})
    humidity = weather.get("humidity", 60)
    temp = weather.get("temperature", 25)
    disease_confidence = state.get("disease_confidence", 0.0)
    season = state.get("season", "Kharif")

    # Disease risk
    disease_risk = 0.1
    if disease_confidence and disease_confidence > 0.7:
        disease_risk = 0.85
    elif disease_confidence and disease_confidence > 0.5:
        disease_risk = 0.55
    elif humidity > 80:
        disease_risk = 0.65  # high humidity without detected disease
    elif humidity > 70:
        disease_risk = 0.40

    # Weather risk
    weather_risk = 0.1
    rain_chance = weather.get("forecast", [{}])[0].get("rain_chance", 0) if weather.get("forecast") else 0
    if rain_chance > 70:
        weather_risk = 0.65
    elif rain_chance > 50:
        weather_risk = 0.40
    if temp > 40 or temp < 5:
        weather_risk = max(weather_risk, 0.70)

    # Pest risk
    pest_risk = 0.2
    if season == "Kharif" and humidity > 75:
        pest_risk = 0.55  # Monsoon = high pest pressure
    elif temp > 30 and humidity < 50:
        pest_risk = 0.45  # Dry heat = spider mite / aphid risk

    # Irrigation risk
    rainfall_24h = weather.get("rainfall_24h", 0)
    irrigation_risk = 0.15
    if rainfall_24h > 30:
        irrigation_risk = 0.60  # Waterlogging risk
    elif rainfall_24h == 0 and temp > 35:
        irrigation_risk = 0.65  # Drought stress risk

    overall = (disease_risk * 0.35 + weather_risk * 0.25 + pest_risk * 0.20 + irrigation_risk * 0.20)

    return {
        "disease_risk": round(disease_risk, 2),
        "weather_risk": round(weather_risk, 2),
        "pest_risk": round(pest_risk, 2),
        "irrigation_risk": round(irrigation_risk, 2),
        "market_risk": 0.25,
        "overall_risk": round(overall, 2),
    }


def _generate_preventive_actions(risks: dict, state: FarmSphereState) -> list[str]:
    """Generate rule-based preventive actions."""
    actions = []
    crop = state.get("crop_type", "your crop")

    if risks["disease_risk"] > 0.6:
        actions.append(f"Apply preventive fungicide (Mancozeb 0.2%) to {crop} immediately")
    if risks["pest_risk"] > 0.5:
        actions.append("Set up yellow sticky traps to monitor pest populations")
    if risks["weather_risk"] > 0.6:
        actions.append("Avoid pesticide spraying — rain forecast may reduce efficacy")
    if risks["irrigation_risk"] > 0.5:
        weather = state.get("weather_data", {})
        if weather.get("rainfall_24h", 0) > 20:
            actions.append("Check field drainage to prevent waterlogging and root rot")
        else:
            actions.append("Increase irrigation frequency to combat heat stress")
    if not actions:
        actions.append(f"Monitor {crop} daily for any early signs of disease or pest")

    actions.append("Maintain field hygiene — remove infected plant debris promptly")
    return actions[:4]


def risk_agent(state: FarmSphereState) -> dict:
    """
    Risk Assessment Agent — Multi-dimensional risk scoring with preventive action plan.
    """
    start_time = time.time()
    logger.info("Risk agent activated for crop=%s", state.get("crop_type"))

    try:
        import json

        if settings.google_api_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                )
                weather = state.get("weather_data", {})
                context = (
                    f"Crop: {state.get('crop_type', 'unknown')}\n"
                    f"Season: {state.get('season', 'unknown')}\n"
                    f"Location: {state.get('location', 'India')}\n"
                    f"Disease detected: {state.get('disease_name', 'none')} "
                    f"(confidence: {state.get('disease_confidence', 0):.0%})\n"
                    f"Weather: Temp={weather.get('temperature', 25)}°C, "
                    f"Humidity={weather.get('humidity', 60)}%, "
                    f"Rainfall 24h={weather.get('rainfall_24h', 0)}mm\n"
                    f"Tomorrow rain chance: {weather.get('forecast', [{}])[0].get('rain_chance', 0) if weather.get('forecast') else 0}%\n"
                    f"Crop stage: {state.get('crop_stage', 'unknown')}"
                )
                response = llm.invoke([
                    SystemMessage(content=RISK_SYSTEM_PROMPT),
                    HumanMessage(content=context),
                ])
                raw = response.content.strip()
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]
                risk_data = json.loads(raw)
                risk_scores = risk_data.get("risk_scores", {})
                risk_summary = risk_data.get("risk_summary", "")
                preventive_actions = risk_data.get("preventive_actions", [])
                alert_level = risk_data.get("alert_level", "medium")
            except Exception as e:
                logger.warning("Gemini risk assessment failed (%s) — using rule-based", e)
                risk_scores = _calculate_rule_based_risks(state)
                preventive_actions = _generate_preventive_actions(risk_scores, state)
                risk_summary = _summarize_risks(risk_scores)
                alert_level = _get_alert_level(risk_scores.get("overall_risk", 0.3))
        else:
            risk_scores = _calculate_rule_based_risks(state)
            preventive_actions = _generate_preventive_actions(risk_scores, state)
            risk_summary = _summarize_risks(risk_scores)
            alert_level = _get_alert_level(risk_scores.get("overall_risk", 0.3))

        source_doc = SourceDocument(
            title="FarmSphere Risk Assessment Model",
            source="Multi-factor Agricultural Risk Engine",
            relevance_score=0.88,
            excerpt=f"Overall risk: {risk_scores.get('overall_risk', 0):.0%} | Alert: {alert_level}",
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="risk_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Overall risk={risk_scores.get('overall_risk', 0):.0%} | {alert_level.upper()} alert",
        )

        return {
            "risk_scores": risk_scores,
            "risk_summary": risk_summary,
            "preventive_actions": preventive_actions,
            "agent_traces": [trace],
            "agents_invoked": ["risk_agent"],
            "source_documents": [source_doc],
            "errors": [],
        }

    except Exception as e:
        logger.error("Risk agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="risk_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "risk_scores": {"overall_risk": 0.3},
            "risk_summary": "Risk assessment temporarily unavailable.",
            "preventive_actions": [],
            "agent_traces": [trace],
            "agents_invoked": ["risk_agent"],
            "source_documents": [],
            "errors": [f"Risk agent: {str(e)}"],
        }


def _summarize_risks(risks: dict) -> str:
    overall = risks.get("overall_risk", 0.3)
    highest = max(risks.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0)
    level = "HIGH" if overall > 0.65 else "MODERATE" if overall > 0.4 else "LOW"
    return (
        f"Overall farm risk is {level} ({overall:.0%}). "
        f"Primary concern is {highest[0].replace('_risk', '').replace('_', ' ')} risk at {highest[1]:.0%}. "
        f"Take preventive actions to protect your crop."
    )


def _get_alert_level(overall_risk: float) -> str:
    if overall_risk > 0.75:
        return "critical"
    elif overall_risk > 0.55:
        return "high"
    elif overall_risk > 0.35:
        return "medium"
    return "low"
