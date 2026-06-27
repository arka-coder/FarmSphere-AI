"""
FarmSphere AI — Layer 3 Advanced Agents (Optional Modules)
Satellite Intelligence, Community Knowledge, Sustainability.
Demo-ready with mock data + real API stubs.
"""
import time
import logging
import math
from datetime import datetime, timedelta
from typing import Optional

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# Agent: Satellite Intelligence Agent
# ════════════════════════════════════════════════════════════════════════════

def _generate_mock_ndvi_timeseries(crop: str, days: int = 30) -> list[dict]:
    """Generate realistic NDVI timeseries based on crop growth stage."""
    base_ndvi = {"tomato": 0.55, "wheat": 0.65, "rice": 0.60}.get((crop or "").lower(), 0.50)
    data = []
    today = datetime.now()
    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        # Simulate realistic NDVI variation with growth trend
        growth_factor = 1 + (days - i) / (days * 3)
        noise = (hash(str(date.date())) % 100 - 50) / 1000
        ndvi = min(0.95, max(0.10, base_ndvi * growth_factor + noise))
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "ndvi": round(ndvi, 3),
            "health": "Healthy" if ndvi > 0.55 else "Stressed" if ndvi > 0.35 else "Critical",
        })
    return data


def satellite_agent(state: FarmSphereState) -> dict:
    """
    Satellite Intelligence Agent — NDVI vegetation health monitoring.
    Uses GEE REST API when available, falls back to realistic mock data.
    """
    start_time = time.time()
    crop = state.get("crop_type", "unknown")
    logger.info("Satellite agent: GEE_MODE=%s, crop=%s", settings.gee_mode, crop)

    try:
        if settings.gee_mode == "live" and settings.gee_service_account:
            # Real GEE call would go here
            # For now, use mock with a note
            satellite_data = _build_mock_satellite_data(crop, "GEE Live (stub)")
        else:
            satellite_data = _build_mock_satellite_data(crop, "Simulated (Demo Mode)")

        source_doc = SourceDocument(
            title="Satellite Vegetation Analysis (NDVI)",
            source=f"Google Earth Engine — {satellite_data.get('source', 'Demo')}",
            relevance_score=0.85,
            excerpt=f"Current NDVI: {satellite_data['current_ndvi']} | Status: {satellite_data['vegetation_health']}",
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="satellite_agent", started_at=start_time, ended_at=time.time(),
            duration_ms=round(duration_ms, 2), status="success",
            output_summary=f"NDVI={satellite_data['current_ndvi']} | {satellite_data['vegetation_health']}",
        )
        return {
            "satellite_data": satellite_data, "source_documents": [source_doc],
            "agent_traces": [trace], "agents_invoked": ["satellite_agent"], "errors": [],
        }
    except Exception as e:
        logger.error("Satellite agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(agent_name="satellite_agent", started_at=start_time, ended_at=time.time(),
                          duration_ms=round(duration_ms, 2), status="error", output_summary=str(e))
        return {"satellite_data": None, "agent_traces": [trace],
                "agents_invoked": ["satellite_agent"], "source_documents": [],
                "errors": [f"Satellite agent: {str(e)}"]}


def _build_mock_satellite_data(crop: str, source: str) -> dict:
    ndvi_series = _generate_mock_ndvi_timeseries(crop, 30)
    current_ndvi = ndvi_series[-1]["ndvi"]
    avg_ndvi = sum(d["ndvi"] for d in ndvi_series) / len(ndvi_series)
    trend = "improving" if ndvi_series[-1]["ndvi"] > ndvi_series[-7]["ndvi"] else "declining"

    return {
        "current_ndvi": current_ndvi,
        "average_ndvi_30d": round(avg_ndvi, 3),
        "vegetation_health": "Healthy" if current_ndvi > 0.55 else "Moderate Stress" if current_ndvi > 0.35 else "High Stress",
        "ndvi_trend": trend,
        "drought_stress": "low" if current_ndvi > 0.55 else "moderate" if current_ndvi > 0.40 else "high",
        "water_stress_index": round(max(0, 1 - current_ndvi), 2),
        "crop_coverage_pct": round(min(100, current_ndvi * 140), 1),
        "anomaly_detected": current_ndvi < 0.35,
        "anomaly_description": "Significant vegetation stress detected in northeast quadrant" if current_ndvi < 0.35 else None,
        "ndvi_timeseries": ndvi_series,
        "satellite_image_url": None,  # Would be GEE map tile URL in live mode
        "source": source,
        "last_updated": datetime.utcnow().isoformat(),
    }


# ════════════════════════════════════════════════════════════════════════════
# Agent: Community Knowledge Agent
# ════════════════════════════════════════════════════════════════════════════

COMMUNITY_KNOWLEDGE = [
    {
        "title": "Neem oil spray for tomato early blight",
        "content": "Mix 5ml neem oil + 2ml liquid soap per liter water. Spray every 7 days on lower leaves. Works best when applied early morning. Reduced early blight spread by 60% in my field in Nashik.",
        "author": "Ramesh K., Nashik", "upvotes": 234, "crop": "tomato", "verified": True,
    },
    {
        "title": "Banana peel compost improves tomato fruiting",
        "content": "Dry banana peels, grind them, mix with soil at base of plant. Rich in potassium — increased my tomato fruit size by 15%. Apply once per month.",
        "author": "Sunita D., Pune", "upvotes": 189, "crop": "tomato", "verified": False,
    },
    {
        "title": "Wheat rust — early warning signs",
        "content": "Check undersides of lower leaves for orange powder from December. If found, apply Propiconazole within 48 hours. Don't wait — rust spreads in 3-4 days in fog conditions.",
        "author": "Harpreet S., Ludhiana", "upvotes": 412, "crop": "wheat", "verified": True,
    },
]


def community_agent(state: FarmSphereState) -> dict:
    start_time = time.time()
    crop = (state.get("crop_type") or "").lower()
    relevant = [k for k in COMMUNITY_KNOWLEDGE if not crop or k.get("crop") == crop][:3]
    source_doc = SourceDocument(title="Community Farmer Knowledge Base",
                                 source="FarmSphere Community + ICAR Verified Tips",
                                 relevance_score=0.80,
                                 excerpt=f"Found {len(relevant)} community tips for {crop}")
    duration_ms = (time.time() - start_time) * 1000
    trace = AgentTrace(agent_name="community_agent", started_at=start_time, ended_at=time.time(),
                      duration_ms=round(duration_ms, 2), status="success",
                      output_summary=f"Retrieved {len(relevant)} community insights")
    return {"source_documents": [source_doc], "agent_traces": [trace],
            "agents_invoked": ["community_agent"], "errors": []}


# ════════════════════════════════════════════════════════════════════════════
# Agent: Sustainability Agent
# ════════════════════════════════════════════════════════════════════════════

SUSTAINABILITY_TIPS = {
    "tomato": [
        "Use drip irrigation — saves 40-50% water vs. flood irrigation",
        "Mulch with crop residues to reduce evaporation and suppress weeds",
        "Intercrop with basil — natural pest repellent, no chemicals needed",
        "Compost crop waste instead of burning — improves soil organic matter",
    ],
    "wheat": [
        "Zero-till sowing conserves soil moisture and reduces fuel by 60%",
        "Use crop residue mulching instead of burning to prevent air pollution",
        "Balanced fertilization based on soil testing reduces excess N₂O emissions",
    ],
    "default": [
        "Integrated Pest Management (IPM) reduces chemical pesticide use by 50%",
        "Install solar-powered irrigation pumps for zero-emission water management",
        "Crop rotation improves soil biodiversity and reduces disease pressure naturally",
        "Plant neem trees as windbreaks — provide shade and natural pesticide supply",
    ],
}

def sustainability_agent(state: FarmSphereState) -> dict:
    start_time = time.time()
    crop = (state.get("crop_type") or "").lower()
    tips = SUSTAINABILITY_TIPS.get(crop, SUSTAINABILITY_TIPS["default"])
    sustainability_advice = (
        f"**🌿 Sustainable Farming Recommendations for {crop.title() or 'Your Farm'}:**\n\n"
        + "\n".join(f"• {tip}" for tip in tips)
    )
    source_doc = SourceDocument(title="Sustainable Agriculture Practices",
                                 source="ICAR Organic Farming Guide + FAO Sustainability Framework",
                                 relevance_score=0.82, excerpt=sustainability_advice[:200])
    duration_ms = (time.time() - start_time) * 1000
    trace = AgentTrace(agent_name="sustainability_agent", started_at=start_time, ended_at=time.time(),
                      duration_ms=round(duration_ms, 2), status="success",
                      output_summary=f"{len(tips)} sustainability recommendations generated")
    return {"sustainability_advice": sustainability_advice, "source_documents": [source_doc],
            "agent_traces": [trace], "agents_invoked": ["sustainability_agent"], "errors": []}
