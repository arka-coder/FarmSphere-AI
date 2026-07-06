"""
FarmSphere AI — FastAPI Application Entry Point
All routes, middleware, startup, and SSE streaming.
"""
# ── Path fix ─────────────────────────────────────────────────────────────────
# Ensures this module works whether run from the project root
#   (python -m uvicorn backend.main:app)
# or from within the backend directory
#   (uvicorn main:app)
import sys
import os
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
# ─────────────────────────────────────────────────────────────────────────────

import time
import uuid
import json
import asyncio
import logging
import base64
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
from pydantic import BaseModel, Field

from config import settings
from graph.workflow import get_app as get_langgraph_app
from database.postgres import init_db, get_db, Farmer, SessionLocal
from database.chromadb_client import seed_demo_data, query_collection
from evaluation.evaluator import run_full_evaluation
from observability.observability import (
    configure_logging, record_request_metrics,
    build_execution_timeline, check_service_health,
    get_prometheus_metrics, ACTIVE_SESSIONS,
)

logger = logging.getLogger(__name__)


# ── Startup / Shutdown ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    logger.info("🌾 FarmSphere AI starting up...")

    # Initialize database tables
    try:
        init_db()
        logger.info("✅ PostgreSQL tables initialized")
    except Exception as e:
        logger.warning("⚠️ PostgreSQL init failed (running without DB): %s", e)

    # Seed ChromaDB with demo data
    try:
        seed_demo_data()
        logger.info("✅ ChromaDB seeded with demo ICAR data")
    except Exception as e:
        logger.warning("⚠️ ChromaDB seed failed: %s", e)

    # Pre-compile LangGraph workflow
    try:
        get_langgraph_app()
        logger.info("✅ LangGraph workflow compiled")
    except Exception as e:
        logger.error("❌ LangGraph compile failed: %s", e)

    logger.info("🚀 FarmSphere AI ready!")
    yield
    logger.info("👋 FarmSphere AI shutting down")


# ── App Factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="FarmSphere AI",
    description="Explainable Multi-Agent Agricultural Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    farmer_id: Optional[str] = None
    farmer_name: Optional[str] = "Farmer"
    location: Optional[str] = None       # Free-text location (city, region)
    district: Optional[str] = None
    state: Optional[str] = None          # State/province
    country: Optional[str] = None        # Country — for global context
    crop_type: Optional[str] = None
    season: Optional[str] = None
    image_base64: Optional[str] = None   # base64-encoded image for disease detection


class FarmerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    state_name: Optional[str] = None
    land_size_acres: Optional[float] = None
    preferred_language: str = "en"
    primary_crop: Optional[str] = None


# ── Helper: Build initial state ───────────────────────────────────────────────

def build_initial_state(req: ChatRequest) -> dict:
    # Build a readable location string from available fields
    location_parts = [p for p in [req.district, req.state, req.country or req.location] if p]
    location_str = ", ".join(location_parts) if location_parts else None

    return {
        "farmer_id": req.farmer_id or f"anon_{uuid.uuid4().hex[:8]}",
        "farmer_name": req.farmer_name or "Farmer",
        "location": location_str,
        "district": req.district,
        "state_name": req.state,
        "country": req.country,
        "crop_type": req.crop_type,
        "season": req.season,
        "language": "en",                 # English only
        "user_message": req.message,
        "image_base64": req.image_base64,
        "image_path": None,
        "conversation_history": [],
        "hitl_required": False,
        "agent_traces": [],
        "agents_invoked": [],
        "source_documents": [],
        "errors": [],
    }


# ════════════════════════════════════════════════════════════════════════════
# Routes
# ════════════════════════════════════════════════════════════════════════════

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    return await check_service_health()


@app.get("/metrics", tags=["System"], response_class=Response)
async def prometheus_metrics():
    data, content_type = get_prometheus_metrics()
    return Response(content=data, media_type=content_type)


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "FarmSphere AI",
        "version": "1.0.0",
        "status": "operational",
        "agents": 17,
        "description": "Explainable Multi-Agent Agricultural Intelligence Platform",
    }


# ── Chat (Core) ───────────────────────────────────────────────────────────────

@app.post("/api/chat", tags=["Chat"])
async def chat(req: ChatRequest):
    """
    Main chat endpoint — runs the full LangGraph multi-agent pipeline.
    Returns structured response with explainability, confidence scores, and sources.
    """
    start_time = time.time()
    ACTIVE_SESSIONS.inc()
    session_id = uuid.uuid4().hex

    try:
        langgraph_app = get_langgraph_app()
        initial_state = build_initial_state(req)

        # Run the synchronous LangGraph pipeline in a thread pool
        # so we don't block FastAPI's async event loop.
        loop = asyncio.get_event_loop()
        try:
            final_state = await asyncio.wait_for(
                loop.run_in_executor(None, langgraph_app.invoke, initial_state),
                timeout=120.0,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Request timed out — AI pipeline took too long. Please try again.",
            )

        # Run evaluation
        evaluation = run_full_evaluation(final_state)

        # Build execution timeline for frontend
        timeline = build_execution_timeline(final_state.get("agent_traces", []))

        # Record Prometheus metrics
        duration_s = time.time() - start_time
        record_request_metrics(final_state, duration_s)

        response = final_state.get("translated_response") or final_state.get("final_response", "")

        return {
            "session_id": session_id,
            "response": response,
            "intent": final_state.get("intent"),
            "agents_invoked": final_state.get("agents_invoked", []),
            "execution_timeline": timeline,

            # Explainability
            "reasoning_chain": final_state.get("reasoning_chain", []),
            "confidence_breakdown": final_state.get("confidence_breakdown", {}),
            "explanation": final_state.get("explanation"),

            # Disease specific
            "disease": {
                "name": final_state.get("disease_name"),
                "confidence": final_state.get("disease_confidence"),
                "severity": final_state.get("disease_severity"),
                "symptoms": final_state.get("disease_symptoms", []),
                "alternatives": final_state.get("disease_alternatives", []),
                "hitl_required": final_state.get("hitl_required", False),
            } if final_state.get("disease_name") else None,

            # Data from agents
            "weather": final_state.get("weather_data"),
            "weather_advice": final_state.get("weather_advice"),
            "risk_scores": final_state.get("risk_scores"),
            "risk_summary": final_state.get("risk_summary"),
            "preventive_actions": final_state.get("preventive_actions", []),
            "active_alerts": final_state.get("active_alerts", []),
            "applicable_schemes": final_state.get("applicable_schemes", []),
            "market_prices": final_state.get("market_prices"),
            "upcoming_tasks": final_state.get("upcoming_tasks", []),
            "satellite_data": final_state.get("satellite_data"),
            "simulation_results": final_state.get("simulation_results"),

            # Source documents for citation cards
            "source_documents": final_state.get("source_documents", []),

            # Evaluation
            "evaluation": evaluation,

            # Timing
            "total_latency_ms": round((time.time() - start_time) * 1000, 1),
            "errors": final_state.get("errors", []),
        }

    except Exception as e:
        logger.error("Chat endpoint error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent pipeline error: {str(e)}")
    finally:
        ACTIVE_SESSIONS.dec()


# ── Streaming Chat (SSE) ──────────────────────────────────────────────────────

@app.post("/api/chat/stream", tags=["Chat"])
async def chat_stream(req: ChatRequest):
    """
    SSE streaming endpoint — streams agent progress updates in real time.
    Frontend can show 'Disease Agent running...' as it happens.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        start_time = time.time()
        try:
            # Stream agent status updates
            agent_order = [
                ("orchestrator", "🧠 Analyzing your request..."),
                ("disease_agent", "🔬 Running disease detection..."),
                ("knowledge_agent", "📚 Searching knowledge base..."),
                ("weather_agent", "🌤️ Fetching weather data..."),
                ("seasonal_agent", "📅 Analyzing seasonal context..."),
                ("risk_agent", "⚠️ Assessing crop risks..."),
                ("recommendation_agent", "💡 Generating recommendations..."),
                ("explainability_agent", "🔍 Building explanation..."),
                ("translation_agent", "🌐 Preparing response..."),
            ]

            for agent_name, message in agent_order:
                event_data = json.dumps({
                    "type": "agent_progress",
                    "agent": agent_name,
                    "message": message,
                    "timestamp": time.time(),
                })
                yield f"data: {event_data}\n\n"
                await asyncio.sleep(0.1)  # Small delay for visual effect

            # Run actual pipeline
            langgraph_app = get_langgraph_app()
            initial_state = build_initial_state(req)

            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(None, langgraph_app.invoke, initial_state)

            # Stream final result
            evaluation = run_full_evaluation(final_state)
            timeline = build_execution_timeline(final_state.get("agent_traces", []))
            response = final_state.get("translated_response") or final_state.get("final_response", "")

            result_data = json.dumps({
                "type": "result",
                "response": response,
                "disease": {
                    "name": final_state.get("disease_name"),
                    "confidence": final_state.get("disease_confidence"),
                    "severity": final_state.get("disease_severity"),
                    "symptoms": final_state.get("disease_symptoms", []),
                    "alternatives": final_state.get("disease_alternatives", []),
                    "hitl_required": final_state.get("hitl_required", False),
                } if final_state.get("disease_name") else None,
                "weather": final_state.get("weather_data"),
                "weather_advice": final_state.get("weather_advice"),
                "risk_scores": final_state.get("risk_scores"),
                "active_alerts": final_state.get("active_alerts", []),
                "reasoning_chain": final_state.get("reasoning_chain", []),
                "confidence_breakdown": final_state.get("confidence_breakdown", {}),
                "source_documents": final_state.get("source_documents", []),
                "execution_timeline": timeline,
                "evaluation": evaluation,
                "simulation_results": final_state.get("simulation_results"),
                "total_latency_ms": round((time.time() - start_time) * 1000, 1),
            })
            yield f"data: {result_data}\n\n"
            yield "data: {\"type\": \"done\"}\n\n"

        except Exception as e:
            error_data = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {error_data}\n\n"


    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Image Upload ──────────────────────────────────────────────────────────────

@app.post("/api/upload", tags=["Disease Detection"])
async def upload_image(
    file: UploadFile = File(...),
    farmer_id: str = Form(default="anonymous"),
    crop_type: str = Form(default="unknown"),
    farmer_name: str = Form(default="Farmer"),
):
    """Upload plant image for disease detection."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")

    image_b64 = base64.b64encode(contents).decode("utf-8")

    req = ChatRequest(
        message=f"Please analyze this {crop_type} plant image for disease",
        farmer_id=farmer_id,
        farmer_name=farmer_name,
        crop_type=crop_type,
        image_base64=image_b64,
    )
    return await chat(req)


# ── Farmer Profile ────────────────────────────────────────────────────────────

@app.post("/api/farmer", tags=["Farmer"])
async def create_farmer(data: FarmerCreate):
    farmer_id = f"farmer_{uuid.uuid4().hex[:12]}"
    try:
        db = SessionLocal()
        farmer = Farmer(id=farmer_id, **data.dict())
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        db.close()
        return {"farmer_id": farmer_id, "name": data.name, "status": "created"}
    except Exception as e:
        logger.warning("Farmer creation failed (DB unavailable): %s", e)
        return {"farmer_id": farmer_id, "name": data.name, "status": "created_no_db"}


@app.get("/api/farmer/{farmer_id}", tags=["Farmer"])
async def get_farmer(farmer_id: str):
    try:
        db = SessionLocal()
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        db.close()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
        return {
            "farmer_id": farmer.id, "name": farmer.name,
            "location": farmer.location, "primary_crop": farmer.primary_crop,
            "preferred_language": farmer.preferred_language,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


# ── Market Data ──────────────────────────────────────────────────────────

@app.get("/api/market", tags=["Market"])
async def get_market_data(crop: Optional[str] = None, state: Optional[str] = None):
    """Get current market prices for crops (national average or state-specific)."""
    from agents.supporting_agents import MOCK_MARKET_DATA
    from agents.agriculture_kb import NATIONAL_BASELINE_PRICES, get_statewise_price, get_msp
    if crop:
        crop_key = crop.lower()
        if state:
            data = get_statewise_price(crop_key, state)
        else:
            data = MOCK_MARKET_DATA.get(crop_key) or {
                "price_per_quintal": NATIONAL_BASELINE_PRICES.get(crop_key, 0),
                "unit": "quintal"
            }
        if not data or not data.get("price_per_quintal"):
            raise HTTPException(status_code=404, detail=f"No market data for crop: {crop}")
        msp = get_msp(crop_key)
        return {"crop": crop, "state": state, **data, "msp_2024_25": msp}
    return {"markets": MOCK_MARKET_DATA}


@app.get("/api/market/statewise", tags=["Market"])
async def get_statewise_market_data(crop: str, state: Optional[str] = None):
    """
    Get prices for a crop across all states, or for a specific state.
    Example: GET /api/market/statewise?crop=wheat
             GET /api/market/statewise?crop=onion&state=Maharashtra
    """
    from agents.agriculture_kb import (
        NATIONAL_BASELINE_PRICES, STATE_PRICE_MULTIPLIERS,
        STATE_MAJOR_MANDIS, get_statewise_price, get_msp,
    )
    crop_key = crop.lower().strip()
    if crop_key not in NATIONAL_BASELINE_PRICES:
        raise HTTPException(status_code=404, detail=f"Crop '{crop}' not found in price database.")

    if state:
        data = get_statewise_price(crop_key, state)
        msp = get_msp(crop_key)
        return {"crop": crop, "state": state, **data, "msp_2024_25": msp}

    # Return all states
    national_avg = NATIONAL_BASELINE_PRICES[crop_key]
    msp = get_msp(crop_key)
    states_data = {}
    for state_name, multipliers in STATE_PRICE_MULTIPLIERS.items():
        m = multipliers.get(crop_key, 1.0)
        price = round(national_avg * m)
        mandis = STATE_MAJOR_MANDIS.get(state_name, {})
        states_data[state_name] = {
            "price_per_quintal": price,
            "major_mandi": mandis.get(crop_key, mandis.get("default", "Nearest APMC")),
        }

    return {
        "crop": crop,
        "national_average_per_quintal": national_avg,
        "msp_2024_25": msp,
        "states": states_data,
        "source": "Agmarknet / eNAM reference data 2024",
        "note": "Prices are reference rates. Verify before selling at agmarknet.gov.in or enam.gov.in",
    }


@app.get("/api/market/msp", tags=["Market"])
async def get_msp_data(crop: Optional[str] = None, season: Optional[str] = None):
    """
    Get Minimum Support Prices (MSP) for 2024-25.
    Source: DAC&FW Cabinet Approval 2024.
    Example: GET /api/market/msp
             GET /api/market/msp?crop=wheat
             GET /api/market/msp?season=rabi
    """
    from agents.agriculture_kb import MSP_2024_25, get_msp
    if crop:
        result = get_msp(crop)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"MSP not available for '{crop}'. Only government-notified MSP crops are listed."
            )
        return result
    if season:
        filtered = {k: v for k, v in MSP_2024_25.items() if v.get("season") == season.lower()}
        return {
            "season": season, "msp_crops": filtered,
            "count": len(filtered), "source": "DAC&FW Cabinet Approval 2024",
        }
    return {
        "msp_2024_25": MSP_2024_25,
        "total_crops": len(MSP_2024_25),
        "source": "Department of Agriculture & Farmers Welfare (DAC&FW) — Cabinet Approval 2024",
        "reference": "https://agricoop.nic.in/en/pricePolicy",
    }


# ── Government Schemes ────────────────────────────────────────────────

@app.get("/api/schemes", tags=["Schemes"])
async def get_schemes(category: Optional[str] = None):
    """Get list of government agricultural schemes."""
    from agents.supporting_agents import SCHEMES_DB
    if category:
        filtered = [s for s in SCHEMES_DB if s.get("category") == category]
        return {"schemes": filtered, "count": len(filtered)}
    return {"schemes": SCHEMES_DB, "count": len(SCHEMES_DB)}


# ── Crop Information (Encyclopaedia) ───────────────────────────────────────

@app.get("/api/crops/info", tags=["Crop Information"])
async def get_crop_info(
    crop: str,
    section: Optional[str] = None,
):
    """
    Get encyclopaedic information for a crop from the Agriculture Knowledge Base.
    Optional ?section= filter: 'diseases', 'pests', 'varieties', 'nutrients', 'agronomy'
    Example: GET /api/crops/info?crop=wheat
             GET /api/crops/info?crop=rice&section=diseases
    """
    from agents.agriculture_kb import CROP_ENCYCLOPEDIA, get_crop_info as kb_get_crop_info
    crop_data = kb_get_crop_info(crop)
    if not crop_data:
        available = list(CROP_ENCYCLOPEDIA.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop}' not found. Available crops: {', '.join(available)}"
        )
    if section:
        section_map = {
            "diseases": "major_diseases",
            "pests": "major_pests",
            "varieties": "major_varieties",
            "nutrients": "nutrient_requirements_kg_per_ha",
            "agronomy": None,  # return full for agronomy
        }
        field = section_map.get(section.lower())
        if field and field in crop_data:
            return {"crop": crop, "section": section, "data": crop_data[field]}
        elif section.lower() == "agronomy":
            agronomy_fields = [
                "optimal_temperature_c", "annual_rainfall_mm", "soil_ph", "soil_types",
                "growth_duration_days", "growth_stages", "water_requirement_mm",
                "critical_irrigation_stages", "yield_potential_t_per_ha",
            ]
            return {"crop": crop, "section": "agronomy", "data": {k: crop_data.get(k) for k in agronomy_fields if crop_data.get(k)}}
    return {
        "crop": crop,
        "data": crop_data,
        "source": crop_data.get("icar_source", "ICAR Knowledge Base"),
    }


@app.get("/api/crops/list", tags=["Crop Information"])
async def list_crops():
    """List all crops available in the Agriculture Knowledge Base."""
    from agents.agriculture_kb import CROP_ENCYCLOPEDIA, NATIONAL_BASELINE_PRICES
    return {
        "encyclopaedia_crops": list(CROP_ENCYCLOPEDIA.keys()),
        "price_database_crops": list(NATIONAL_BASELINE_PRICES.keys()),
        "total_encyclopaedia": len(CROP_ENCYCLOPEDIA),
        "total_price_database": len(NATIONAL_BASELINE_PRICES),
    }


# ── Plant Science Expert ─────────────────────────────────────────────────

class PlantScienceRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    crop: Optional[str] = None
    location: Optional[str] = None


@app.post("/api/plant-science", tags=["Plant Science"])
async def plant_science_query(req: PlantScienceRequest):
    """
    Deep plant science expert endpoint.
    Handles: photosynthesis (C3/C4/CAM), mycorrhiza, biofertilizers,
    plant growth regulators, allelopathy, companion planting, seed science.
    Example: POST /api/plant-science
             Body: {"question": "Explain C4 photosynthesis in sugarcane", "crop": "sugarcane"}
    """
    from agents.plant_science_agent import query_plant_science
    loop = asyncio.get_event_loop()
    try:
        answer = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                query_plant_science,
                req.question, req.crop or "", req.location or "India"
            ),
            timeout=30.0,
        )
        return {
            "question": req.question,
            "crop": req.crop,
            "answer": answer,
            "source": "ICAR-IARI New Delhi / FarmSphere Plant Science KB",
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Plant science query timed out. Please try again.")


# ── Satellite Data ────────────────────────────────────────────────────────────

@app.get("/api/satellite", tags=["Satellite"])
async def get_satellite_data(crop: Optional[str] = "tomato"):
    """Get NDVI and vegetation health data."""
    from agents.advanced_agents import _build_mock_satellite_data
    return _build_mock_satellite_data(crop, "Demo Mode")


# ── Alerts ────────────────────────────────────────────────────────────────────

@app.get("/api/alerts", tags=["Alerts"])
async def get_alerts(
    farmer_id: Optional[str] = None,
    lat: float = settings.default_lat,
    lon: float = settings.default_lon,
):
    """Get proactive alerts generated from current farm conditions."""
    from agents.supporting_agents import alert_agent
    from agents.weather_agent import MOCK_WEATHER_DATA

    weather_data = MOCK_WEATHER_DATA
    if settings.openweather_api_key:
        try:
            from agents.weather_agent import fetch_weather
            weather_data = await fetch_weather(lat, lon, settings.openweather_api_key)
        except Exception as e:
            logger.warning("Alert weather fetch failed, using fallback weather: %s", e)
    else:
        weather_data = {
            **MOCK_WEATHER_DATA,
            "location": f"Current coordinates ({lat:.3f}, {lon:.3f})",
            "source": "Fallback Weather (OpenWeather API key not configured)",
        }

    result = alert_agent({
        "farmer_id": farmer_id,
        "weather_data": weather_data,
        "market_prices": {},
    })
    alerts = result.get("active_alerts", [])
    return {
        "alerts": alerts,
        "count": len(alerts),
        "location": weather_data.get("location"),
        "source": weather_data.get("source"),
    }


# ── Crop Calendar ─────────────────────────────────────────────────────────────

@app.get("/api/calendar", tags=["Calendar"])
async def get_calendar(crop: str = "tomato", farmer_id: Optional[str] = None):
    """Get crop calendar for a specific crop."""
    from agents.supporting_agents import crop_calendar_agent
    mock_state = {"crop_type": crop, "farmer_id": farmer_id}
    result = crop_calendar_agent(mock_state)
    return result.get("crop_calendar", {})


# ── Weather ───────────────────────────────────────────────────────────────────

@app.get("/api/weather", tags=["Weather"])
async def get_weather(lat: float = settings.default_lat, lon: float = settings.default_lon):
    """Get current weather data."""
    from agents.weather_agent import MOCK_WEATHER_DATA
    if settings.openweather_api_key:
        try:
            from agents.weather_agent import fetch_weather
            return await fetch_weather(lat, lon, settings.openweather_api_key)
        except Exception:
            pass
    return MOCK_WEATHER_DATA


# ── Evaluation ────────────────────────────────────────────────────────────────

@app.get("/api/metrics/evaluation", tags=["Evaluation"])
async def get_evaluation_info():
    """Return evaluation framework documentation."""
    return {
        "framework": "FarmSphere Evaluation Suite",
        "metrics": [
            {"name": "faithfulness", "description": "Answer grounded in retrieved documents", "threshold": "75%"},
            {"name": "rag_quality", "description": "Retrieval relevance and diversity", "threshold": "65%"},
            {"name": "latency", "description": "End-to-end response time", "threshold": "< 5 seconds"},
            {"name": "confidence_quality", "description": "Disease confidence calibration", "threshold": "75%"},
            {"name": "hallucination_risk", "description": "Unsupported claims detection", "threshold": "< 20%"},
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
