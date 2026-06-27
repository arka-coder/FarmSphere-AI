"""
FarmSphere AI — FastAPI Application Entry Point
All routes, middleware, startup, and SSE streaming.
"""
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
    location: Optional[str] = None
    district: Optional[str] = None
    crop_type: Optional[str] = None
    season: Optional[str] = None
    language: str = Field(default="en", pattern="^(en|hi|bn)$")
    image_base64: Optional[str] = None  # base64-encoded image for disease detection


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
    return {
        "farmer_id": req.farmer_id or f"anon_{uuid.uuid4().hex[:8]}",
        "farmer_name": req.farmer_name or "Farmer",
        "location": req.location,
        "district": req.district,
        "crop_type": req.crop_type,
        "season": req.season,
        "language": req.language,
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

        # Run LangGraph workflow
        final_state = langgraph_app.invoke(initial_state)

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
    language: str = Form(default="en"),
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
        language=language,
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


# ── Market Data ───────────────────────────────────────────────────────────────

@app.get("/api/market", tags=["Market"])
async def get_market_data(crop: Optional[str] = None):
    """Get current market prices for crops."""
    from agents.supporting_agents import MOCK_MARKET_DATA
    if crop:
        data = MOCK_MARKET_DATA.get(crop.lower())
        if not data:
            raise HTTPException(status_code=404, detail=f"No market data for crop: {crop}")
        return {"crop": crop, **data}
    return {"markets": MOCK_MARKET_DATA}


# ── Government Schemes ────────────────────────────────────────────────────────

@app.get("/api/schemes", tags=["Schemes"])
async def get_schemes(category: Optional[str] = None):
    """Get list of government agricultural schemes."""
    from agents.supporting_agents import SCHEMES_DB
    if category:
        filtered = [s for s in SCHEMES_DB if s.get("category") == category]
        return {"schemes": filtered, "count": len(filtered)}
    return {"schemes": SCHEMES_DB, "count": len(SCHEMES_DB)}


# ── Satellite Data ────────────────────────────────────────────────────────────

@app.get("/api/satellite", tags=["Satellite"])
async def get_satellite_data(crop: Optional[str] = "tomato"):
    """Get NDVI and vegetation health data."""
    from agents.advanced_agents import _build_mock_satellite_data
    return _build_mock_satellite_data(crop, "Demo Mode")


# ── Alerts ────────────────────────────────────────────────────────────────────

@app.get("/api/alerts", tags=["Alerts"])
async def get_alerts(farmer_id: Optional[str] = None):
    """Get proactive alerts for a farmer."""
    # Return demo alerts
    from agents.advanced_agents import _build_mock_satellite_data
    alerts = [
        {"type": "weather", "severity": "high", "title": "🌧️ Heavy Rain Tomorrow",
         "message": "70% chance of rainfall. Avoid pesticide spraying.", "action": "Postpone spraying"},
        {"type": "disease", "severity": "medium", "title": "🍄 High Humidity Alert",
         "message": "Humidity above 80% — fungal disease risk elevated.", "action": "Apply preventive fungicide"},
        {"type": "market", "severity": "low", "title": "📈 Tomato Prices Rising",
         "message": "Tomato prices up 12% this week. Good selling opportunity.", "action": "Contact Azadpur Mandi"},
    ]
    return {"alerts": alerts, "count": len(alerts)}


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
