"""
FarmSphere AI — Weather Agent (Layer 1)
Fetches real-time weather from OpenWeatherMap and generates agricultural advice.
"""
import time
import logging
import httpx
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings
from agents.llm_helper import invoke_with_fallback

logger = logging.getLogger(__name__)

WEATHER_ADVICE_PROMPT = """You are an expert agricultural meteorologist.
Given the weather data and farmer context, provide specific, actionable agricultural advice.
Keep it practical, short (3-4 sentences), and directly relevant to the crop and season.
Focus on: spraying conditions, irrigation needs, disease risk from humidity, frost protection."""

MOCK_WEATHER_DATA = {
    "location": "Nashik, Maharashtra",
    "temperature": 28.5,
    "feels_like": 31.2,
    "humidity": 72,
    "wind_speed": 3.4,
    "weather_condition": "Partly Cloudy",
    "rainfall_1h": 0,
    "rainfall_24h": 12.4,
    "pressure": 1010,
    "visibility": 9000,
    "uv_index": 6,
    "forecast": [
        {"day": "Tomorrow", "condition": "Light Rain", "temp_max": 30, "temp_min": 22, "humidity": 80, "rain_chance": 70},
        {"day": "Day After", "condition": "Thunderstorm", "temp_max": 27, "temp_min": 21, "humidity": 90, "rain_chance": 85},
        {"day": "Day 3", "condition": "Partly Cloudy", "temp_max": 32, "temp_min": 24, "humidity": 65, "rain_chance": 20},
    ],
    "source": "OpenWeatherMap (Demo)",
    "timestamp": datetime.utcnow().isoformat(),
}


async def fetch_weather(lat: float, lon: float, api_key: str) -> dict:
    """Fetch current weather + 3-day forecast from OpenWeatherMap."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Current weather
        current_url = "https://api.openweathermap.org/data/2.5/weather"
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}

        curr_resp = await client.get(current_url, params=params)
        curr_resp.raise_for_status()
        curr = curr_resp.json()

        fore_resp = await client.get(forecast_url, params=params)
        fore_resp.raise_for_status()
        fore = fore_resp.json()

        # Parse current
        weather = {
            "location": curr.get("name", ""),
            "temperature": curr["main"]["temp"],
            "feels_like": curr["main"]["feels_like"],
            "humidity": curr["main"]["humidity"],
            "wind_speed": curr["wind"]["speed"],
            "weather_condition": curr["weather"][0]["description"].title(),
            "rainfall_1h": curr.get("rain", {}).get("1h", 0),
            "rainfall_24h": curr.get("rain", {}).get("3h", 0) * 8,  # estimate
            "pressure": curr["main"]["pressure"],
            "visibility": curr.get("visibility", 0),
            "source": "OpenWeatherMap API",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Parse 3-day forecast (every 8th item = 24h)
        forecast = []
        days = ["Tomorrow", "Day After", "Day 3"]
        for i, label in enumerate(days):
            idx = min((i + 1) * 8, len(fore["list"]) - 1)
            item = fore["list"][idx]
            forecast.append({
                "day": label,
                "condition": item["weather"][0]["description"].title(),
                "temp_max": item["main"]["temp_max"],
                "temp_min": item["main"]["temp_min"],
                "humidity": item["main"]["humidity"],
                "rain_chance": int(item.get("pop", 0) * 100),
            })
        weather["forecast"] = forecast

        return weather


def weather_agent(state: FarmSphereState) -> dict:
    """
    Weather Agent — Fetches real-time weather and generates farm-specific advice.
    """
    import asyncio
    start_time = time.time()
    logger.info("Weather agent activated for location: %s", state.get("location", "default"))

    try:
        lat = settings.default_lat
        lon = settings.default_lon

        if not settings.openweather_api_key:
            logger.warning("No OpenWeather API key — using mock weather data")
            weather_data = MOCK_WEATHER_DATA
        else:
            try:
                weather_data = asyncio.run(fetch_weather(lat, lon, settings.openweather_api_key))
            except Exception as e:
                logger.warning("Weather API call failed (%s) — using mock", e)
                weather_data = MOCK_WEATHER_DATA

        # Generate agricultural advice with Gemini
        weather_advice = _generate_weather_advice(state, weather_data)

        source_doc = SourceDocument(
            title=f"Weather Data — {weather_data.get('location', 'Your Location')}",
            source=weather_data.get("source", "OpenWeatherMap"),
            relevance_score=0.95,
            excerpt=f"Temp: {weather_data['temperature']}°C | Humidity: {weather_data['humidity']}% | {weather_data['weather_condition']}",
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="weather_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"{weather_data['temperature']}°C, {weather_data['weather_condition']}, humidity={weather_data['humidity']}%",
        )

        return {
            "weather_data": weather_data,
            "weather_advice": weather_advice,
            "agent_traces": [trace],
            "agents_invoked": ["weather_agent"],
            "source_documents": [source_doc],
            "errors": [],
        }

    except Exception as e:
        logger.error("Weather agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="weather_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "weather_data": MOCK_WEATHER_DATA,
            "weather_advice": "Weather data temporarily unavailable.",
            "agent_traces": [trace],
            "agents_invoked": ["weather_agent"],
            "source_documents": [],
            "errors": [f"Weather agent: {str(e)}"],
        }


def _generate_weather_advice(state: FarmSphereState, weather: dict) -> str:
    """Generate crop-specific weather advice using Gemini."""
    # Rule-based fallback always computed first
    advice_parts = []
    if weather["humidity"] > 80:
        advice_parts.append("⚠️ High humidity increases fungal disease risk — monitor crops closely.")
    if weather.get("rainfall_24h", 0) > 10:
        advice_parts.append("🌧️ Significant rainfall recorded — avoid pesticide spraying for 24 hours.")
    rain_chance = weather.get("forecast", [{}])[0].get("rain_chance", 0) if weather.get("forecast") else 0
    if rain_chance > 60:
        advice_parts.append(f"🌂 {rain_chance}% rain chance tomorrow — delay any planned spraying.")
    if weather["temperature"] > 35:
        advice_parts.append("🌡️ High temperature — ensure adequate irrigation and mulching.")
    rule_advice = " ".join(advice_parts) or "Weather conditions are favorable for farming activities."

    if not settings.google_api_key:
        return rule_advice

    try:
        context = (
            f"Crop: {state.get('crop_type', 'general')}, Season: {state.get('season', 'current')}, "
            f"Location: {state.get('location', 'India')}\n"
            f"Weather: {weather['temperature']}°C, Humidity: {weather['humidity']}%, "
            f"Condition: {weather['weather_condition']}, Wind: {weather['wind_speed']} m/s\n"
            f"Yesterday rainfall: {weather.get('rainfall_24h', 0)} mm\n"
            f"3-day forecast: {weather.get('forecast', [])}"
        )
        result = invoke_with_fallback(
            [
                SystemMessage(content=WEATHER_ADVICE_PROMPT),
                HumanMessage(content=context),
            ],
            temperature=0.3,
        )
        return result if result else rule_advice
    except Exception as e:
        logger.warning("Weather advice generation failed: %s", e)
        return rule_advice
