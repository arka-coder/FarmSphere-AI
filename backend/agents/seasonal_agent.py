"""
FarmSphere AI — Seasonal Crop Intelligence Agent (Layer 1)
Understands region + crop lifecycle stage + month to give season-aware advice.
"""
import time
import logging
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings

logger = logging.getLogger(__name__)

# Indian agricultural seasons
SEASONS = {
    (6, 7, 8, 9): "Kharif",       # June–September: Rice, Maize, Cotton, Soybean
    (10, 11): "Rabi_Sowing",       # Oct–Nov: Wheat, Mustard sowing
    (12, 1, 2): "Rabi",            # Dec–Feb: Wheat growing
    (3, 4, 5): "Zaid",             # Mar–May: Vegetables, Watermelon, Cucumbers
}

CROP_STAGES = {
    "tomato": {
        "Kharif": ["Nursery (Jun)", "Transplanting (Jul)", "Vegetative (Aug)", "Flowering (Aug-Sep)", "Fruiting (Sep-Oct)"],
        "Rabi": ["Nursery (Oct)", "Transplanting (Nov)", "Vegetative (Nov-Dec)", "Flowering (Dec-Jan)", "Harvest (Feb-Mar)"],
        "Zaid": ["Nursery (Feb)", "Transplanting (Mar)", "Fruiting (Apr-May)"],
    },
    "wheat": {
        "Rabi": ["Sowing (Oct-Nov)", "Tillering (Dec)", "Stem Extension (Jan)", "Heading (Feb)", "Grain Fill (Feb-Mar)", "Harvest (Mar-Apr)"],
        "Rabi_Sowing": ["Land Preparation", "Seed Treatment", "Sowing"],
    },
    "rice": {
        "Kharif": ["Nursery (Jun)", "Transplanting (Jul)", "Tillering (Jul-Aug)", "Panicle Initiation (Aug)", "Heading (Sep)", "Harvest (Oct)"],
    },
}

SEASONAL_RISKS = {
    ("Kharif", "high_humidity"): [
        "Fungal diseases (blast, blight) are at peak risk during monsoon with humidity >80%.",
        "Monitor for leaf spot diseases every 3-4 days.",
        "Ensure proper field drainage to prevent waterlogging.",
    ],
    ("Rabi", "cold"): [
        "Watch for frost damage if temperature drops below 4°C.",
        "Fog conditions increase rust disease risk in wheat.",
        "Delay irrigation before forecasted frost events.",
    ],
    ("Zaid", "heat"): [
        "High temperatures (>40°C) cause flower drop in vegetables.",
        "Increase irrigation frequency during heat waves.",
        "Apply mulch to conserve soil moisture.",
    ],
}

SEASONAL_SYSTEM_PROMPT = """You are an expert agricultural advisor specializing in Indian farming seasons.
Given the crop, current season, growth stage, and weather conditions, provide:
1. Current crop growth stage assessment
2. Top 3 critical tasks for this stage
3. Disease/pest risks specific to this season
4. Upcoming milestones to watch for

Be specific to the Indian agricultural calendar. Keep response practical and concise."""


def _detect_season(month: int = None) -> str:
    if month is None:
        month = datetime.now().month
    for months, season in SEASONS.items():
        if month in months:
            return season
    return "Kharif"


def _get_crop_stage(crop: str, season: str) -> str:
    crop = (crop or "").lower()
    stages = CROP_STAGES.get(crop, {}).get(season, [])
    if not stages:
        return f"Mid-season growth stage"
    # Return most relevant stage based on current month
    month = datetime.now().month
    idx = min(len(stages) - 1, month % max(len(stages), 1))
    return stages[idx]


def seasonal_agent(state: FarmSphereState) -> dict:
    """
    Seasonal Crop Intelligence Agent — Region + month + crop lifecycle awareness.
    """
    start_time = time.time()
    logger.info("Seasonal agent for crop=%s, location=%s", state.get("crop_type"), state.get("location"))

    try:
        crop = state.get("crop_type", "general")
        location = state.get("location", "India")
        current_month = datetime.now().month
        season = state.get("season") or _detect_season(current_month)
        crop_stage = _get_crop_stage(crop, season)

        # Get weather context for seasonal risk
        weather = state.get("weather_data", {})
        humidity = weather.get("humidity", 65)
        temperature = weather.get("temperature", 25)

        # Determine climate conditions
        conditions = []
        if humidity > 75:
            conditions.append("high_humidity")
        if temperature < 10:
            conditions.append("cold")
        if temperature > 38:
            conditions.append("heat")

        # Get seasonal risks
        seasonal_risks = []
        for condition in conditions:
            key = (season, condition)
            seasonal_risks.extend(SEASONAL_RISKS.get(key, []))

        # Generate comprehensive seasonal advice with Gemini
        if settings.google_api_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.3,
                )
                context = (
                    f"Crop: {crop}, Season: {season}, Current Stage: {crop_stage}\n"
                    f"Location: {location}, Month: {datetime.now().strftime('%B')}\n"
                    f"Weather: Temp={temperature}°C, Humidity={humidity}%\n"
                    f"Known seasonal risks: {'; '.join(seasonal_risks)}"
                )
                response = llm.invoke([
                    SystemMessage(content=SEASONAL_SYSTEM_PROMPT),
                    HumanMessage(content=context),
                ])
                seasonal_advice = response.content.strip()
            except Exception as e:
                logger.warning("Gemini seasonal advice failed: %s", e)
                seasonal_advice = _fallback_seasonal_advice(season, crop, crop_stage, seasonal_risks)
        else:
            seasonal_advice = _fallback_seasonal_advice(season, crop, crop_stage, seasonal_risks)

        source_doc = SourceDocument(
            title=f"Seasonal Intelligence — {season} Season",
            source="FarmSphere Crop Calendar & ICAR Seasonal Guidelines",
            relevance_score=0.90,
            excerpt=f"Crop: {crop} | Stage: {crop_stage} | Season: {season}",
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="seasonal_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Season={season} | Stage={crop_stage} | Risks={len(seasonal_risks)}",
        )

        return {
            "season": season,
            "crop_stage": crop_stage,
            "seasonal_advice": seasonal_advice,
            "agent_traces": [trace],
            "agents_invoked": ["seasonal_agent"],
            "source_documents": [source_doc],
            "errors": [],
        }

    except Exception as e:
        logger.error("Seasonal agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="seasonal_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "seasonal_advice": "Seasonal analysis temporarily unavailable.",
            "agent_traces": [trace],
            "agents_invoked": ["seasonal_agent"],
            "source_documents": [],
            "errors": [f"Seasonal agent: {str(e)}"],
        }


def _fallback_seasonal_advice(season: str, crop: str, stage: str, risks: list) -> str:
    advice = f"**{season} Season — {crop.title()}**\n\n"
    advice += f"**Current Stage:** {stage}\n\n"
    if risks:
        advice += "**Seasonal Risks:**\n"
        for risk in risks[:3]:
            advice += f"• {risk}\n"
    advice += f"\n**Recommended Actions:**\n"
    advice += "• Monitor crop daily for early signs of disease or pest damage\n"
    advice += "• Maintain proper irrigation schedule based on crop stage\n"
    advice += "• Keep records of all inputs applied for traceability\n"
    return advice
