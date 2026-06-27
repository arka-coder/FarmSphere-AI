"""
FarmSphere AI — Observability & Monitoring
Traces, metrics, logs, health checks, Redis caching, retry manager.
"""
import time
import logging
import functools
import asyncio
from typing import Callable, Any, Optional
from datetime import datetime

import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ════════════════════════════════════════════════════════════════════════════
# Structured Logging (structlog)
# ════════════════════════════════════════════════════════════════════════════

def configure_logging(log_level: str = "INFO"):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))


log = structlog.get_logger("farmsphere")


# ════════════════════════════════════════════════════════════════════════════
# Prometheus Metrics
# ════════════════════════════════════════════════════════════════════════════

REQUEST_COUNT = Counter(
    "farmsphere_requests_total",
    "Total chat requests processed",
    ["intent", "language", "status"],
)
REQUEST_LATENCY = Histogram(
    "farmsphere_request_duration_seconds",
    "End-to-end request latency",
    ["intent"],
    buckets=[0.5, 1, 2, 5, 10, 20, 30],
)
AGENT_LATENCY = Histogram(
    "farmsphere_agent_duration_seconds",
    "Per-agent execution time",
    ["agent_name", "status"],
    buckets=[0.1, 0.25, 0.5, 1, 2, 5],
)
DISEASE_CONFIDENCE = Histogram(
    "farmsphere_disease_confidence",
    "Disease detection confidence scores",
    buckets=[0.1, 0.3, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0],
)
HITL_TRIGGERED = Counter(
    "farmsphere_hitl_triggered_total",
    "Times Human-in-the-Loop was triggered (confidence < 75%)",
)
ACTIVE_SESSIONS = Gauge(
    "farmsphere_active_sessions",
    "Currently active farmer sessions",
)
RAG_DOCS_RETRIEVED = Histogram(
    "farmsphere_rag_docs_retrieved",
    "Number of documents retrieved per RAG query",
    buckets=[0, 1, 2, 3, 4, 5, 10],
)


def record_request_metrics(state: dict, duration_s: float):
    """Record Prometheus metrics from a completed request."""
    intent = state.get("intent", "unknown")
    language = state.get("language", "en")
    errors = state.get("errors") or []
    status = "error" if errors else "success"

    REQUEST_COUNT.labels(intent=intent, language=language, status=status).inc()
    REQUEST_LATENCY.labels(intent=intent).observe(duration_s)

    disease_conf = state.get("disease_confidence")
    if disease_conf is not None:
        DISEASE_CONFIDENCE.observe(disease_conf)

    if state.get("hitl_required"):
        HITL_TRIGGERED.inc()

    retrieved = state.get("retrieved_documents") or []
    if retrieved:
        RAG_DOCS_RETRIEVED.observe(len(retrieved))

    for trace in (state.get("agent_traces") or []):
        AGENT_LATENCY.labels(
            agent_name=trace.get("agent_name", "unknown"),
            status=trace.get("status", "unknown"),
        ).observe(trace.get("duration_ms", 0) / 1000)


def get_prometheus_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


# ════════════════════════════════════════════════════════════════════════════
# Agent Execution Timeline (for frontend explainability panel)
# ════════════════════════════════════════════════════════════════════════════

def build_execution_timeline(agent_traces: list[dict]) -> list[dict]:
    """Build a structured timeline from agent traces for the frontend."""
    if not agent_traces:
        return []

    # Sort by start time
    sorted_traces = sorted(agent_traces, key=lambda t: t.get("started_at", 0))
    timeline = []

    for trace in sorted_traces:
        status_icon = {"success": "✅", "error": "❌", "skipped": "⏭️"}.get(
            trace.get("status", ""), "🔄"
        )
        timeline.append({
            "agent": trace.get("agent_name", "unknown"),
            "display_name": trace.get("agent_name", "").replace("_", " ").title(),
            "duration_ms": round(trace.get("duration_ms", 0), 1),
            "status": trace.get("status", "unknown"),
            "status_icon": status_icon,
            "output_summary": trace.get("output_summary", ""),
            "started_at": trace.get("started_at", 0),
        })

    return timeline


# ════════════════════════════════════════════════════════════════════════════
# Redis Cache
# ════════════════════════════════════════════════════════════════════════════

_redis_client = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            from config import settings
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            _redis_client.ping()
            log.info("Redis connected")
        except Exception as e:
            log.warning("Redis unavailable — caching disabled", error=str(e))
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Optional[str]:
    r = get_redis()
    if r:
        try:
            return r.get(key)
        except Exception:
            return None
    return None


def cache_set(key: str, value: str, ttl_seconds: int = 300):
    r = get_redis()
    if r:
        try:
            r.setex(key, ttl_seconds, value)
        except Exception:
            pass


def cache_weather(lat: float, lon: float, data: dict, ttl: int = 600):
    """Cache weather data for 10 minutes."""
    import json
    key = f"weather:{lat:.3f}:{lon:.3f}"
    cache_set(key, json.dumps(data), ttl)


def get_cached_weather(lat: float, lon: float) -> Optional[dict]:
    import json
    key = f"weather:{lat:.3f}:{lon:.3f}"
    cached = cache_get(key)
    return json.loads(cached) if cached else None


# ════════════════════════════════════════════════════════════════════════════
# Retry Manager (with exponential backoff)
# ════════════════════════════════════════════════════════════════════════════

def with_retry(max_attempts: int = 3, base_delay: float = 0.5, exceptions=(Exception,)):
    """Decorator: retry a function with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        delay = base_delay * (2 ** (attempt - 1))
                        log.warning("Retry attempt", func=func.__name__,
                                   attempt=attempt, delay=delay, error=str(e))
                        time.sleep(delay)
            log.error("All retry attempts failed", func=func.__name__, error=str(last_exc))
            raise last_exc
        return wrapper
    return decorator


# ════════════════════════════════════════════════════════════════════════════
# Fallback Manager
# ════════════════════════════════════════════════════════════════════════════

class FallbackManager:
    """Manages graceful fallbacks when services are unavailable."""

    @staticmethod
    def get_weather_fallback() -> dict:
        """Return mock weather when OpenWeather is unavailable."""
        return {
            "location": "Demo Location",
            "temperature": 28.0,
            "humidity": 68,
            "weather_condition": "Partly Cloudy",
            "rainfall_24h": 0,
            "wind_speed": 3.0,
            "forecast": [
                {"day": "Tomorrow", "condition": "Sunny", "temp_max": 31, "temp_min": 22,
                 "humidity": 65, "rain_chance": 15},
            ],
            "source": "Mock Data (API unavailable)",
        }

    @staticmethod
    def get_llm_fallback(context: str) -> str:
        """Return context-based fallback when Gemini is unavailable."""
        return (
            f"Based on agricultural knowledge: {context[:400]}...\n\n"
            "⚠️ Note: AI model temporarily unavailable. Please consult your local KVK for expert advice."
        )

    @staticmethod
    def get_rag_fallback() -> dict:
        """Return empty results when ChromaDB is unavailable."""
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}


# ════════════════════════════════════════════════════════════════════════════
# Health Check
# ════════════════════════════════════════════════════════════════════════════

async def check_service_health() -> dict:
    """Check health of all dependent services."""
    health = {"status": "healthy", "services": {}, "timestamp": datetime.utcnow().isoformat()}

    # PostgreSQL
    try:
        from database.postgres import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health["services"]["postgres"] = "healthy"
    except Exception as e:
        health["services"]["postgres"] = f"unhealthy: {str(e)[:50]}"
        health["status"] = "degraded"

    # ChromaDB
    try:
        from database.chromadb_client import get_chroma_client
        client = get_chroma_client()
        client.heartbeat()
        health["services"]["chromadb"] = "healthy"
    except Exception as e:
        health["services"]["chromadb"] = f"unhealthy: {str(e)[:50]}"
        health["status"] = "degraded"

    # Redis
    try:
        r = get_redis()
        if r:
            r.ping()
            health["services"]["redis"] = "healthy"
        else:
            health["services"]["redis"] = "unavailable (caching disabled)"
    except Exception as e:
        health["services"]["redis"] = f"unhealthy: {str(e)[:50]}"

    # Gemini
    from config import settings
    health["services"]["gemini"] = "configured" if settings.google_api_key else "⚠️ No API key"
    health["services"]["openweather"] = "configured" if settings.openweather_api_key else "⚠️ No API key"

    return health
