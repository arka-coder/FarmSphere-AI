"""
FarmSphere AI — Orchestrator Agent (Layer 1)
Classifies intent, activates relevant agents, and manages LangGraph routing.
Upgraded: 4 new intents, 60+ expanded farming keywords, elite intent taxonomy.
"""
import time
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace
from config import settings
from agents.llm_helper import invoke_with_fallback

logger = logging.getLogger(__name__)

# Intent taxonomy — expanded with specialist agriculture intents
INTENTS = Literal[
    "disease_diagnosis",
    "treatment_advice",
    "weather_query",
    "market_query",
    "price_query_statewise",     # NEW: state-specific price queries
    "scheme_query",
    "crop_planning",
    "risk_assessment",
    "satellite_query",
    "scenario_simulation",
    "soil_nutrition",            # NEW: soil health, fertilizer, deficiency queries
    "export_market",             # NEW: global prices, APEDA, export opportunities
    "crop_disease_plant_science",# NEW: deep plant biology, physiology, botany
    "general_farming",
    "greeting",
]

INTENT_SYSTEM_PROMPT = """You are an elite agricultural intent classifier for FarmSphere AI.

Classify the farmer's message into EXACTLY ONE of these intents:

**Disease & Plant Health:**
- disease_diagnosis: farmer describes plant symptoms, uploads leaf/fruit image, asks "what disease is this?"
- treatment_advice: farmer asks HOW to treat a known disease, pest, or condition
- crop_disease_plant_science: deep plant biology questions — photosynthesis, C3/C4/CAM, mycorrhiza, biofertilizers, auxins, gibberellins, allelopathy, seed dormancy, nutrient uptake physiology, companion planting science

**Weather & Environment:**
- weather_query: weather forecast, rain probability, temperature, humidity, frost warning

**Market & Prices:**
- market_query: general crop prices, where to sell, market trend, mandi rates, MSP
- price_query_statewise: price in a SPECIFIC STATE ("tomato price in Maharashtra", "wheat rate in Punjab")
- export_market: global commodity prices (CBOT, ICE), export opportunities, APEDA, international markets, import/export

**Government & Schemes:**
- scheme_query: PM-KISAN, PMFBY, KCC, subsidies, government programmes, insurance, loans

**Planning:**
- crop_planning: what crop to plant, when to sow, crop calendar, harvest schedule, variety selection
- soil_nutrition: soil testing, pH, NPK, fertilizer dose, organic matter, soil health card, micronutrient deficiency, vermicompost, FYM

**Risk & Monitoring:**
- risk_assessment: disease risk, pest risk, yield risk, climate risk
- satellite_query: NDVI, vegetation health index, field stress mapping
- scenario_simulation: "what if" questions about rainfall, temperature, drought, flood scenarios

**General:**
- general_farming: irrigation, organic farming, general cultivation advice (when none of the above fit)
- greeting: hello, who are you, what can you do, introduction

Respond with ONLY the intent label. Nothing else. No explanation."""


# ── Expanded keyword matching — 120+ patterns ───────────────────────────────

# State names for detecting price_query_statewise
INDIA_STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "telangana", "tripura", "uttar pradesh", "up", "uttarakhand", "west bengal",
    "delhi", "jammu", "kashmir", "ladakh", "puducherry", "chandigarh",
    "andaman", "nicobar", "lakshadweep",
]

def _rule_based_intent(message: str) -> str:
    """Keyword fallback if Gemini is unavailable. Covers 80%+ of farming queries."""
    msg = message.lower()

    # Scenario simulation (check first — specific patterns)
    if any(w in msg for w in ["what if", "simulate", "scenario", "drought impact", "flood impact", "what happens if", "if rainfall", "if temperature"]):
        return "scenario_simulation"

    # Plant science (deep botany / physiology)
    if any(w in msg for w in [
        "photosynthesis", "c3 crop", "c4 crop", "cam plant", "hatch-slack",
        "transpiration rate", "stomata", "rubisco", "photorespiration",
        "mycorrhiza", "vam", "rhizobium", "azospirillum", "azotobacter",
        "biofertilizer", "nitrogen fixation", "phosphate solubilizing",
        "auxin", "gibberellin", "cytokinin", "abscisic", "ethephon",
        "naa ", "ga3", "growth regulator", "pgr",
        "seed dormancy", "germination physiology", "seed priming",
        "allelopathy", "companion planting science", "phloem transport",
        "xylem", "apoplast", "symplast", "nutrient uptake pathway",
        "soil microbiome", "actinomycetes", "rhizosphere",
        "plant anatomy", "plant morphology", "plant taxonomy",
        "bundle sheath", "kranz anatomy", "quantum yield",
    ]):
        return "crop_disease_plant_science"

    # Soil and nutrition (check BEFORE disease/treatment to catch fertilizer queries correctly)
    if any(w in msg for w in [
        "soil test", "soil ph", "soil health", "npk", "nitrogen dose", "phosphorus dose",
        "potassium", "zinc", "boron", "iron deficiency", "micronutrient",
        "organic matter", "fertilizer dose", "fertilizer schedule", "urea", "dap", "ssp", "mop",
        "vermicompost", "fym", "farmyard manure", "compost", "green manure",
        "soil card", "soil type", "soil sample", "alkaline soil", "acidic soil",
        "saline soil", "black soil", "red soil", "alluvial soil",
        "nitrogen deficiency", "phosphorus deficiency", "potassium deficiency",
        "basal dose", "top dressing", "split application",
    ]):
        return "soil_nutrition"

    # State-specific price queries
    if any(state in msg for state in INDIA_STATES) and any(w in msg for w in ["price", "rate", "mandi", "quintal", "cost", "sell"]):
        return "price_query_statewise"

    # Export / global market
    if any(w in msg for w in [
        "export", "apeda", "global price", "cbot", "ice futures", "international market",
        "chicago board", "london", "world price", "import", "customs duty",
        "foreign market", "dollar price", "usd", "global commodity",
    ]):
        return "export_market"

    # Disease diagnosis
    if any(w in msg for w in [
        "disease", "spot", "blight", "rust", "fungal", "leaf curl", "leaf roll",
        "yellow", "brown", "black", "white powder", "mold", "mould", "rot",
        "symptom", "lesion", "necrosis", "wilting", "drooping", "dieback",
        "mosaic", "virus", "bacterial", "nematode", "stunted growth",
    ]):
        return "disease_diagnosis"

    # Treatment advice
    if any(w in msg for w in [
        "treat", "treatment", "cure", "spray", "fungicide", "pesticide",
        "insecticide", "medicine", "chemical", "biological control", "how to control",
        "how to manage", "what to apply", "dosage", "dose",
    ]):
        return "treatment_advice"

    # Weather
    if any(w in msg for w in [
        "rain", "rainfall", "weather", "temperature", "humidity", "forecast",
        "wind", "sunny", "cloudy", "frost", "fog", "hail", "cyclone", "monsoon",
    ]):
        return "weather_query"

    # Market query (general)
    if any(w in msg for w in [
        "price", "market", "mandi", "sell", "rate", "quintal", "market trend",
        "where to sell", "apmc", "enam", "trading", "commodity",
        "msp", "minimum support", "msps", "procurement",
    ]):
        return "market_query"

    # Scheme query
    if any(w in msg for w in [
        "scheme", "pm-kisan", "pmkisan", "subsidy", "government", "insurance",
        "kisan", "pmfby", "fasal bima", "kcc", "kisan credit", "soil health card",
        "agriculture loan", "nabard", "pm kusum", "drip subsidy", "aif",
        "pkvy", "organic farming scheme", "fpo", "farmer producer",
    ]):
        return "scheme_query"

    # Crop planning
    if any(w in msg for w in [
        "calendar", "when to sow", "sowing time", "planting time", "harvest time",
        "which crop", "what to grow", "crop rotation", "crop schedule",
        "variety selection", "best variety", "seed rate", "spacing",
    ]):
        return "crop_planning"

    # Risk assessment
    if any(w in msg for w in ["risk", "pest", "outbreak", "alert", "danger", "probability of disease"]):
        return "risk_assessment"

    # Satellite
    if any(w in msg for w in ["ndvi", "satellite", "vegetation", "field health", "remote sensing", "drone survey"]):
        return "satellite_query"

    # Greeting
    if any(w in msg for w in ["hello", "hi", "who are you", "what can you", "help me", "namaste", "namaskar"]):
        return "greeting"

    return "general_farming"



def classify_intent(message: str) -> str:
    """Fast-path: rule-based first, LLM only for ambiguous messages."""
    # Fast path — covers >80% of farming queries without an LLM call
    fast_intent = _rule_based_intent(message)
    if fast_intent != "general_farming":
        return fast_intent

    # Ambiguous — use Gemini for accurate classification
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
                "market_query", "price_query_statewise", "scheme_query",
                "crop_planning", "risk_assessment", "satellite_query",
                "scenario_simulation", "soil_nutrition", "export_market",
                "crop_disease_plant_science", "general_farming", "greeting",
            ]
            for v_intent in valid_intents:
                if v_intent in intent:
                    return v_intent
            return "general_farming"
    except Exception as e:
        logger.warning("Intent classification failed: %s", e)
    return fast_intent


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
        "disease_diagnosis":        "disease_agent",
        "treatment_advice":         "knowledge_agent",
        "weather_query":            "weather_agent",
        "market_query":             "market_agent",
        "price_query_statewise":    "market_agent",     # state-wise → market agent (state-aware)
        "scheme_query":             "scheme_agent",
        "crop_planning":            "crop_calendar_agent",
        "risk_assessment":          "risk_agent",
        "satellite_query":          "satellite_agent",
        "scenario_simulation":      "scenario_simulation_agent",
        "soil_nutrition":           "knowledge_agent",  # KB has full soil science
        "export_market":            "market_agent",     # market agent handles global benchmarks
        "crop_disease_plant_science":"knowledge_agent", # knowledge_agent delegates to plant_science_agent
        "general_farming":          "knowledge_agent",
        "greeting":                 "recommendation_agent",
    }

    return routing_map.get(intent, "knowledge_agent")
