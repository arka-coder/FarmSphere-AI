"""
FarmSphere AI — Layer 2 Supporting Agents
All 6 supporting agents in one file for clean organization.
"""
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Optional

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# Agent: Translation Agent
# ════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════════════════
# Agent: Translation Agent — DISABLED (English only)
# ════════════════════════════════════════════════════════════════════════════

def translation_agent(state: FarmSphereState) -> dict:
    """Translation agent — disabled. FarmSphere AI responds in English only."""
    start_time = time.time()
    final_response = state.get("final_response", "")
    trace = AgentTrace(
        agent_name="translation_agent",
        started_at=start_time,
        ended_at=time.time(),
        duration_ms=0,
        status="skipped",
        output_summary="English-only mode — no translation",
    )
    return {
        "translated_response": final_response,
        "agent_traces": [trace],
        "agents_invoked": ["translation_agent"],
        "errors": [],
    }


# ════════════════════════════════════════════════════════════════════════════
# Agent: Memory Agent
# ════════════════════════════════════════════════════════════════════════════

def memory_agent(state: FarmSphereState) -> dict:
    """Persists conversation turn to PostgreSQL for long-term memory."""
    start_time = time.time()
    try:
        from database.postgres import SessionLocal, ConversationRecord, AgentMetrics
        db = SessionLocal()
        try:
            # Save conversation record
            record = ConversationRecord(
                farmer_id=state.get("farmer_id", "anonymous"),
                session_id=state.get("farmer_id", "session_" + str(int(time.time()))),
                user_message=state.get("user_message", ""),
                assistant_response=state.get("translated_response") or state.get("final_response", ""),
                intent=state.get("intent"),
                language=state.get("language", "en"),
                agents_invoked=state.get("agents_invoked", []),
                latency_ms=state.get("total_latency_ms"),
            )
            db.add(record)

            # Save agent metrics
            for trace in (state.get("agent_traces") or []):
                metric = AgentMetrics(
                    session_id=state.get("farmer_id", "unknown"),
                    agent_name=trace.get("agent_name", ""),
                    duration_ms=trace.get("duration_ms", 0),
                    status=trace.get("status", "unknown"),
                )
                db.add(metric)

            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning("Memory agent DB write failed: %s", e)

    duration_ms = (time.time() - start_time) * 1000
    conv_history_entry = {
        "role": "user", "content": state.get("user_message", ""),
        "timestamp": datetime.utcnow().isoformat(),
    }
    trace = AgentTrace(agent_name="memory_agent", started_at=start_time,
                      ended_at=time.time(), duration_ms=round(duration_ms, 2), status="success",
                      output_summary="Conversation persisted to PostgreSQL")
    return {"conversation_history": [conv_history_entry], "agent_traces": [trace],
            "agents_invoked": ["memory_agent"], "errors": []}


# ════════════════════════════════════════════════════════════════════════════
# Agent: Government Scheme Agent
# ════════════════════════════════════════════════════════════════════════════

SCHEMES_DB = [
    {
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "benefit": "₹6,000/year income support in 3 installments of ₹2,000",
        "eligibility": "All landholding farmer families with cultivable land",
        "exclusions": "Income tax payers, government employees, constitutional post holders",
        "apply": "pmkisan.gov.in",
        "online_apply_url": "https://pmkisan.gov.in",
        "documents": ["Aadhaar card", "Bank account details", "Land ownership records"],
        "category": "income_support",
    },
    {
        "name": "PMFBY",
        "full_name": "Pradhan Mantri Fasal Bima Yojana",
        "benefit": "Crop insurance covering natural calamities, pests, diseases and post-harvest losses",
        "eligibility": "All farmers growing notified crops",
        "exclusions": "None — voluntary scheme open to all farmers",
        "apply": "pmfby.gov.in or nearest bank",
        "online_apply_url": "https://pmfby.gov.in",
        "documents": ["Aadhaar", "Bank account", "Land records", "Sowing certificate"],
        "category": "insurance",
        "premium": "2% Kharif | 1.5% Rabi | 5% commercial crops",
    },
    {
        "name": "Kisan Credit Card",
        "full_name": "Kisan Credit Card Scheme",
        "benefit": "Short-term credit up to ₹3 lakh at 4% effective interest rate per annum",
        "eligibility": "Farmers with land, share croppers, tenant farmers, SHG members",
        "apply": "Any nationalized bank, RRB, or cooperative bank",
        "online_apply_url": None,
        "documents": ["Aadhaar", "Land records", "Passport photo", "Bank statement"],
        "category": "credit",
        "note": "Apply at your nearest bank branch — not available online",
    },
    {
        "name": "Soil Health Card",
        "full_name": "Soil Health Card Scheme",
        "benefit": "Free soil testing every 2 years and crop-specific fertilizer recommendations",
        "eligibility": "All farmers across India",
        "apply": "soilhealth.dac.gov.in or nearest KVK",
        "online_apply_url": "https://soilhealth.dac.gov.in",
        "documents": ["Land details", "Farmer ID", "Aadhaar"],
        "category": "soil",
    },
    {
        "name": "PM Kisan Maandhan",
        "full_name": "Pradhan Mantri Kisan Maandhan Yojana",
        "benefit": "₹3,000/month pension guaranteed after age 60",
        "eligibility": "Small and marginal farmers aged 18-40 years",
        "apply": "maandhan.in or CSC centers",
        "online_apply_url": "https://maandhan.in",
        "documents": ["Aadhaar", "Bank account", "Age proof", "Land records"],
        "category": "pension",
    },
    {
        "name": "eNAM",
        "full_name": "National Agriculture Market",
        "benefit": "Online trading platform for APMC mandis — better price discovery, reduced middlemen",
        "eligibility": "All farmers",
        "apply": "enam.gov.in",
        "online_apply_url": "https://enam.gov.in",
        "documents": ["Aadhaar", "Bank account", "Mobile number"],
        "category": "market",
    },
    {
        "name": "PKVY",
        "full_name": "Paramparagat Krishi Vikas Yojana",
        "benefit": "₹50,000/hectare for 3 years for organic farming transition and certification",
        "eligibility": "Farmers willing to adopt organic farming in clusters of 50 acres",
        "apply": "pgsindia.net or state agriculture department",
        "online_apply_url": "https://pgsindia.net",
        "documents": ["Aadhaar", "Land records", "Cluster formation certificate"],
        "category": "organic",
    },
    {
        "name": "Agriculture Infrastructure Fund",
        "full_name": "Agriculture Infrastructure Fund (AIF)",
        "benefit": "3% interest subvention on loans up to ₹2 crore for post-harvest infrastructure",
        "eligibility": "Farmers, FPOs, PACs, co-ops, start-ups",
        "apply": "agriinfra.dac.gov.in",
        "online_apply_url": "https://agriinfra.dac.gov.in",
        "documents": ["Aadhaar", "Business plan", "Bank account", "Project details"],
        "category": "infrastructure",
    },
    {
        "name": "Kisan Rath App",
        "full_name": "Kisan Rath Mobile Application",
        "benefit": "Free app to connect farmers directly with transport providers for produce movement",
        "eligibility": "All farmers",
        "apply": "Play Store / App Store: 'Kisan Rath'",
        "online_apply_url": "https://play.google.com/store/apps/details?id=com.kisanrath",
        "documents": ["Mobile number only"],
        "category": "market",
    },
]


def scheme_agent(state: FarmSphereState) -> dict:
    start_time = time.time()
    # Return all schemes (lightweight — no complex filtering needed for demo)
    source_doc = SourceDocument(title="Government Agricultural Schemes 2024",
                                 source="Ministry of Agriculture & Farmers Welfare",
                                 relevance_score=0.90,
                                 excerpt="PM-KISAN, PMFBY, KCC and more schemes available")
    duration_ms = (time.time() - start_time) * 1000
    trace = AgentTrace(agent_name="scheme_agent", started_at=start_time, ended_at=time.time(),
                      duration_ms=round(duration_ms, 2), status="success",
                      output_summary=f"Returned {len(SCHEMES_DB)} government schemes")
    return {"applicable_schemes": SCHEMES_DB, "source_documents": [source_doc],
            "agent_traces": [trace], "agents_invoked": ["scheme_agent"], "errors": []}


# ════════════════════════════════════════════════════════════════════════════
# Agent: Market Intelligence Agent
# ════════════════════════════════════════════════════════════════════════════

# ── Market Data: Now powered by agriculture_kb ──────────────────────────────
# Legacy MOCK_MARKET_DATA kept for API backward-compatibility (imported by main.py)
# New state-aware logic uses agriculture_kb directly in market_agent
MOCK_MARKET_DATA = {
    "tomato":     {"price_per_quintal": 2000,  "trend": "rising",  "change_pct": 12.5, "best_market": "Azadpur Mandi, Delhi",         "harvest_recommendation": "Sell within 3-5 days",                           "msp": None, "unit": "quintal"},
    "wheat":      {"price_per_quintal": 2275,  "trend": "stable",  "change_pct": 1.2,  "best_market": "Khanna Mandi, Punjab",         "harvest_recommendation": "MSP guaranteed — use government procurement",    "msp": 2275, "unit": "quintal"},
    "rice":       {"price_per_quintal": 2183,  "trend": "falling", "change_pct": -3.4, "best_market": "Karnal Mandi, Haryana",        "harvest_recommendation": "Consider storing 2 weeks — prices expected to recover", "msp": 2183, "unit": "quintal"},
    "onion":      {"price_per_quintal": 2200,  "trend": "rising",  "change_pct": 18.0, "best_market": "Lasalgaon Mandi, Nashik",      "harvest_recommendation": "Excellent time to sell — peak prices",            "msp": None, "unit": "quintal"},
    "potato":     {"price_per_quintal": 1250,  "trend": "stable",  "change_pct": 0.5,  "best_market": "Agra Mandi, Uttar Pradesh",   "harvest_recommendation": "Average market — sell in next 10 days",           "msp": None, "unit": "quintal"},
    "cotton":     {"price_per_quintal": 7200,  "trend": "rising",  "change_pct": 5.2,  "best_market": "Rajkot APMC, Gujarat",          "harvest_recommendation": "Good prices — sell in next 15 days",               "msp": 7121, "unit": "quintal"},
    "sugarcane":  {"price_per_quintal": 340,   "trend": "stable",  "change_pct": 0.0,  "best_market": "FRP — sell to nearest sugar mill", "harvest_recommendation": "FRP guaranteed ₹340/q by CCEA",              "msp": 340,  "unit": "quintal"},
    "soybean":    {"price_per_quintal": 4892,  "trend": "rising",  "change_pct": 8.3,  "best_market": "Indore Mandi, Madhya Pradesh", "harvest_recommendation": "Rising trend — consider selling now",             "msp": 4892, "unit": "quintal"},
    "maize":      {"price_per_quintal": 2090,  "trend": "stable",  "change_pct": 2.1,  "best_market": "Davangere Mandi, Karnataka",   "harvest_recommendation": "Stable prices — sell as needed",                  "msp": 2090, "unit": "quintal"},
    "groundnut":  {"price_per_quintal": 6900,  "trend": "rising",  "change_pct": 6.7,  "best_market": "Junagadh APMC, Gujarat",        "harvest_recommendation": "High demand — sell in bulk",                      "msp": 6783, "unit": "quintal"},
    "chilli":     {"price_per_quintal": 9500,  "trend": "rising",  "change_pct": 14.2, "best_market": "Guntur APMC, Andhra Pradesh",  "harvest_recommendation": "Peak season prices — sell immediately",           "msp": None, "unit": "quintal"},
    "banana":     {"price_per_quintal": 1600,  "trend": "stable",  "change_pct": -1.5, "best_market": "Jalgaon Mandi, Maharashtra",   "harvest_recommendation": "Sell to local aggregators",                     "msp": None, "unit": "quintal"},
    "mustard":    {"price_per_quintal": 5700,  "trend": "stable",  "change_pct": 1.5,  "best_market": "Bharatpur Mandi, Rajasthan",   "harvest_recommendation": "Price near MSP — consider government procurement", "msp": 5650, "unit": "quintal"},
    "arhar":      {"price_per_quintal": 7600,  "trend": "rising",  "change_pct": 4.2,  "best_market": "Gulbarga Mandi, Karnataka",    "harvest_recommendation": "Good prices above MSP — sell now",               "msp": 7550, "unit": "quintal"},
    "gram":       {"price_per_quintal": 5500,  "trend": "stable",  "change_pct": 0.8,  "best_market": "Bikaner Mandi, Rajasthan",     "harvest_recommendation": "Stable near MSP — monitor for 2 weeks",          "msp": 5440, "unit": "quintal"},
    "turmeric":   {"price_per_quintal": 12000, "trend": "rising",  "change_pct": 22.0, "best_market": "Erode Market, Tamil Nadu",      "harvest_recommendation": "Record high prices — excellent time to sell",     "msp": None, "unit": "quintal"},
    "garlic":     {"price_per_quintal": 8000,  "trend": "rising",  "change_pct": 15.0, "best_market": "Neemuch Mandi, Madhya Pradesh", "harvest_recommendation": "Strong prices — sell in graded lots",             "msp": None, "unit": "quintal"},
    "ginger":     {"price_per_quintal": 6500,  "trend": "stable",  "change_pct": 3.0,  "best_market": "Cochin Spice Exchange, Kerala", "harvest_recommendation": "Average prices — dry ginger fetches 3x premium",   "msp": None, "unit": "quintal"},
}


def market_agent(state: FarmSphereState) -> dict:
    """
    Market Intelligence Agent — State-aware price reporting.
    Uses agriculture_kb for state-specific prices, MSP comparison, mandi names.
    Falls back to MOCK_MARKET_DATA for uncovered crops.
    """
    start_time = time.time()
    crop = (state.get("crop_type") or "").lower().strip()
    # Only use explicitly provided state/province — NOT the free-text location string
    state_name = (state.get("state_name") or "").strip()
    country = (state.get("country") or "").strip()
    intent = state.get("intent", "")

    market_data = {}
    market_advice_parts = []
    source_name = "Agmarknet / eNAM Price Data" if not country or country.lower() == "india" else "Local Market Reference Data"

    try:
        from agents.agriculture_kb import (
            get_statewise_price, get_msp, NATIONAL_BASELINE_PRICES,
            GLOBAL_BENCHMARKS, get_global_benchmark, STATE_MAJOR_MANDIS
        )

        # If state isn't explicitly set in the profile, try to extract it from the user message
        if not state_name:
            user_msg = state.get("user_message", "").lower()
            # Map common major cities to their states as well
            city_to_state = {"kolkata": "West Bengal", "delhi": "Delhi", "mumbai": "Maharashtra", "pune": "Maharashtra", "bangalore": "Karnataka", "hyderabad": "Telangana", "chennai": "Tamil Nadu"}
            
            for city, s in city_to_state.items():
                if city in user_msg:
                    state_name = s
                    break
            
            if not state_name:
                for known_state in STATE_MAJOR_MANDIS.keys():
                    if known_state.lower() in user_msg:
                        state_name = known_state
                        break

        if crop:

            # ── State-specific pricing ────────────────────────────────────────
            if state_name:
                price_data = get_statewise_price(crop, state_name)
                price = price_data.get("price_per_quintal")
                national_avg = price_data.get("national_average")
                mandi = price_data.get("major_mandi", "Nearest APMC mandi")

                if price:
                    market_data = {
                        "price_per_quintal": price,
                        "national_average": national_avg,
                        "state": state_name,
                        "trend": price_data.get("trend_vs_national", "stable"),
                        "change_pct": round((price - national_avg) / national_avg * 100, 1) if national_avg else 0,
                        "best_market": mandi,
                        "harvest_recommendation": _get_harvest_recommendation(crop, price, price_data.get("msp_2024_25")),
                        "unit": "quintal",
                    }
                    market_advice_parts.append(
                        f"**{crop.title()} price in {state_name}**: ₹{price}/quintal"
                    )
                    market_advice_parts.append(
                        f"National average: ₹{national_avg}/quintal "
                        f"({price_data.get('trend_vs_national', 'at national average')})"
                    )
                    market_advice_parts.append(f"Major mandi: {mandi}")

                    if price_data.get("msp_2024_25"):
                        msp_val = price_data["msp_2024_25"]
                        market_data["msp"] = msp_val
                        vs_msp = price_data.get("vs_msp", "")
                        market_advice_parts.append(
                            f"MSP 2024-25: ₹{msp_val}/quintal — Current price is {vs_msp}"
                        )
                        if price < msp_val:
                            market_advice_parts.append(
                                "⚠️ **Price below MSP** — approach your nearest government procurement centre (FCI/NAFED/State agency)"
                            )
                    source_name = f"Agmarknet / eNAM — {state_name} mandi data"

            # ── National fallback if no state ─────────────────────────────────
            if not market_data:
                fallback = MOCK_MARKET_DATA.get(crop)
                if fallback:
                    market_data = fallback
                    market_advice_parts.append(
                        f"**{crop.title()} national average**: ₹{fallback['price_per_quintal']}/quintal"
                    )
                    market_advice_parts.append(f"Major market: {fallback.get('best_market', 'Nearest APMC mandi')}")
                    if fallback.get("msp"):
                        market_advice_parts.append(f"MSP 2024-25: ₹{fallback['msp']}/quintal")
                else:
                    national = NATIONAL_BASELINE_PRICES.get(crop)
                    if national:
                        market_data = {
                            "price_per_quintal": national, "trend": "stable",
                            "change_pct": 0, "best_market": "Nearest APMC mandi",
                            "harvest_recommendation": "Check local mandi before selling", "unit": "quintal"
                        }
                        market_advice_parts.append(
                            f"**{crop.title()} national reference price**: ₹{national}/quintal"
                        )
                    else:
                        market_data = {
                            "price_per_quintal": 0, "trend": "unknown", "change_pct": 0,
                            "best_market": "Nearest APMC mandi",
                            "harvest_recommendation": "Check Agmarknet (agmarknet.gov.in) or eNAM (enam.gov.in) for real-time prices",
                            "unit": "quintal"
                        }
                        market_advice_parts.append(
                            f"Price data for '{crop}' not in reference database. "
                            f"Check Agmarknet (agmarknet.gov.in) or contact nearest APMC for current rates."
                        )

            # ── Global benchmark (for export crops) ───────────────────────────
            if intent == "export_market" or any(c in crop for c in ["cotton", "wheat", "rice", "soybean", "coffee", "pepper"]):
                global_data = get_global_benchmark(crop)
                if global_data:
                    market_data["global_benchmark"] = global_data
                    market_advice_parts.append(
                        f"\n**Global benchmark ({global_data['exchange']})**: "
                        f"{global_data.get('reference_range_usd') or global_data.get('reference_range_usd_mt', 'N/A')} "
                        f"{global_data['unit']}"
                    )
                    market_advice_parts.append(f"India equivalent: {global_data.get('india_equivalent_inr_per_quintal', 'N/A')} ₹/quintal")
                    if global_data.get("note"):
                        market_advice_parts.append(f"ℹ️ {global_data['note']}")
                    if global_data.get("india_export_status"):
                        market_advice_parts.append(f"🚢 **Export status**: {global_data['india_export_status']}")

        else:
            # No crop specified
            market_advice_parts.append(
                "Please specify your crop for price information. "
                "For real-time prices: **agmarknet.gov.in** or **enam.gov.in**"
            )

        # ── Add standard notes ────────────────────────────────────────────────
        market_advice_parts.append(
            "\n📊 *Prices are reference rates (Agmarknet/eNAM 2024). Actual prices vary daily — verify before selling.*"
        )

    except Exception as e:
        logger.warning("Market agent KB lookup failed: %s", e)
        # Full fallback
        fallback = MOCK_MARKET_DATA.get(crop, {
            "price_per_quintal": 1500, "trend": "stable", "change_pct": 0,
            "best_market": "Your nearest APMC mandi",
            "harvest_recommendation": "Check local mandi rates before selling",
        })
        market_data = fallback
        market_advice_parts = [
            f"Current {crop or 'crop'} price: ₹{fallback['price_per_quintal']}/quintal | "
            f"Trend: {fallback['trend'].upper()} ({fallback['change_pct']:+.1f}%). "
            f"Recommendation: {fallback['harvest_recommendation']}."
        ]

    market_advice = "\n".join(market_advice_parts)
    excerpt = f"{crop.title()} — ₹{market_data.get('price_per_quintal', 0)}/quintal | {state_name or 'National'}"

    source_doc = SourceDocument(
        title=f"Market Intelligence — {crop.title() or 'Crops'}",
        source=source_name,
        relevance_score=0.88,
        excerpt=excerpt,
    )
    duration_ms = (time.time() - start_time) * 1000
    trace = AgentTrace(
        agent_name="market_agent", started_at=start_time, ended_at=time.time(),
        duration_ms=round(duration_ms, 2), status="success",
        output_summary=f"Price: ₹{market_data.get('price_per_quintal', 0)}/q | State: {state_name or 'national'}",
    )
    return {
        "market_prices": market_data,
        "market_advice": market_advice,
        "source_documents": [source_doc],
        "agent_traces": [trace],
        "agents_invoked": ["market_agent"],
        "errors": [],
    }


def _get_harvest_recommendation(crop: str, price: int, msp: int | None) -> str:
    """Generate a smart harvest/selling recommendation based on price vs MSP."""
    if msp:
        if price < msp * 0.95:
            return f"Price below MSP (₹{msp}/q) — approach government procurement centre"
        elif price < msp * 1.05:
            return f"Price near MSP (₹{msp}/q) — consider government procurement for security"
        else:
            pct_above = round((price - msp) / msp * 100)
            return f"Price {pct_above}% above MSP — good time to sell in open market"
    else:
        if price > 5000:
            return "Strong prices — sell in graded lots for best returns"
        elif price > 2000:
            return "Average prices — monitor market for 1-2 weeks before selling"
        else:
            return "Lower prices — check if storing is viable (cold storage subsidy under NHB)"


# ════════════════════════════════════════════════════════════════════════════
# Agent: Crop Calendar Agent
# ════════════════════════════════════════════════════════════════════════════

CROP_CALENDARS = {
    "tomato": [
        {"task": "Nursery preparation", "type": "sowing", "days_from_now": -30, "description": "Prepare nursery beds"},
        {"task": "Transplanting", "type": "sowing", "days_from_now": 0, "description": "Transplant 25-day-old seedlings"},
        {"task": "First irrigation", "type": "irrigation", "days_from_now": 2, "description": "Light irrigation after transplanting"},
        {"task": "Basal fertilizer", "type": "fertilizer", "days_from_now": 7, "description": "Apply NPK 75:50:50 kg/ha"},
        {"task": "Weeding", "type": "maintenance", "days_from_now": 20, "description": "First weeding operation"},
        {"task": "Stake installation", "type": "maintenance", "days_from_now": 30, "description": "Install stakes for vine support"},
        {"task": "Top dressing 1", "type": "fertilizer", "days_from_now": 35, "description": "Apply 37.5 kg N/ha"},
        {"task": "Flowering check", "type": "monitoring", "days_from_now": 45, "description": "Monitor for flower drop"},
        {"task": "Top dressing 2", "type": "fertilizer", "days_from_now": 65, "description": "Apply remaining N dose"},
        {"task": "Harvest begins", "type": "harvest", "days_from_now": 75, "description": "First harvest — green stage"},
    ],
    "wheat": [
        {"task": "Soil preparation", "type": "sowing", "days_from_now": -10, "description": "Deep ploughing and leveling"},
        {"task": "Sowing", "type": "sowing", "days_from_now": 0, "description": "Sow at 100-125 kg seed/ha in rows"},
        {"task": "Crown root irrigation", "type": "irrigation", "days_from_now": 21, "description": "Critical first irrigation at crown root stage"},
        {"task": "Tillering irrigation", "type": "irrigation", "days_from_now": 40, "description": "Tillering stage irrigation — most important"},
        {"task": "Top dressing", "type": "fertilizer", "days_from_now": 21, "description": "Apply 65 kg Urea/ha at first node stage"},
        {"task": "Jointing irrigation", "type": "irrigation", "days_from_now": 60, "description": "Irrigation at jointing stage"},
        {"task": "Rust monitoring", "type": "monitoring", "days_from_now": 60, "description": "Check undersides of leaves for yellow rust"},
        {"task": "Flag leaf irrigation", "type": "irrigation", "days_from_now": 80, "description": "Irrigation at flag leaf emergence"},
        {"task": "Milky grain check", "type": "monitoring", "days_from_now": 100, "description": "Check grain filling — avoid irrigation"},
        {"task": "Harvest", "type": "harvest", "days_from_now": 120, "description": "Harvest when grains are hard and golden"},
    ],
    "rice": [
        {"task": "Nursery preparation", "type": "sowing", "days_from_now": -30, "description": "Prepare nursery beds, soak seeds for 24h"},
        {"task": "Transplanting", "type": "sowing", "days_from_now": 0, "description": "Transplant 25-day seedlings at 20x15 cm spacing"},
        {"task": "Weed control", "type": "maintenance", "days_from_now": 7, "description": "Apply pre-emergence herbicide or manual weeding"},
        {"task": "Basal fertilizer", "type": "fertilizer", "days_from_now": 7, "description": "Apply NPK 80:40:40 kg/ha at transplanting"},
        {"task": "First top dressing", "type": "fertilizer", "days_from_now": 21, "description": "Apply 40 kg N/ha at tillering stage"},
        {"task": "Second top dressing", "type": "fertilizer", "days_from_now": 45, "description": "Apply 40 kg N/ha at panicle initiation"},
        {"task": "Blast monitoring", "type": "monitoring", "days_from_now": 40, "description": "Check for neck blast — spray tricyclazole if found"},
        {"task": "Grain filling check", "type": "monitoring", "days_from_now": 75, "description": "Check grain filling — keep water level at 5 cm"},
        {"task": "Drain field", "type": "maintenance", "days_from_now": 100, "description": "Drain water 10 days before harvest"},
        {"task": "Harvest", "type": "harvest", "days_from_now": 110, "description": "Harvest at 85% grain ripening"},
    ],
    "cotton": [
        {"task": "Land preparation", "type": "sowing", "days_from_now": -7, "description": "Deep ploughing, FYM application 10 t/ha"},
        {"task": "Sowing", "type": "sowing", "days_from_now": 0, "description": "Sow Bt cotton at 1 seed/hill, 90x60 cm"},
        {"task": "Thinning", "type": "maintenance", "days_from_now": 14, "description": "Thin to 1 plant/hill after 2 weeks"},
        {"task": "First irrigation", "type": "irrigation", "days_from_now": 21, "description": "Irrigation after 3 weeks if dry"},
        {"task": "Basal fertilizer", "type": "fertilizer", "days_from_now": 7, "description": "Apply NPK 150:75:75 kg/ha"},
        {"task": "Top dressing 1", "type": "fertilizer", "days_from_now": 45, "description": "Apply 50 kg N/ha at squaring"},
        {"task": "Boll worm monitoring", "type": "monitoring", "days_from_now": 60, "description": "Check for boll worm — install pheromone traps"},
        {"task": "Top dressing 2", "type": "fertilizer", "days_from_now": 75, "description": "Apply 50 kg N/ha at boll formation"},
        {"task": "First picking", "type": "harvest", "days_from_now": 130, "description": "Pick open bolls — repeat every 15 days"},
        {"task": "Final harvest", "type": "harvest", "days_from_now": 175, "description": "Final picking — remove crop residue"},
    ],
    "onion": [
        {"task": "Nursery sowing", "type": "sowing", "days_from_now": -45, "description": "Sow seeds in raised nursery beds"},
        {"task": "Transplanting", "type": "sowing", "days_from_now": 0, "description": "Transplant 6-week seedlings at 15x10 cm"},
        {"task": "First irrigation", "type": "irrigation", "days_from_now": 2, "description": "Light irrigation immediately after transplanting"},
        {"task": "Basal fertilizer", "type": "fertilizer", "days_from_now": 7, "description": "Apply NPK 50:50:50 kg/ha"},
        {"task": "Weeding", "type": "maintenance", "days_from_now": 20, "description": "Hand weeding to reduce competition"},
        {"task": "Top dressing", "type": "fertilizer", "days_from_now": 30, "description": "Apply 25 kg N/ha at bulb initiation"},
        {"task": "Irrigation schedule", "type": "irrigation", "days_from_now": 45, "description": "Weekly irrigation during bulb development"},
        {"task": "Purple blotch check", "type": "monitoring", "days_from_now": 50, "description": "Check for purple blotch — spray mancozeb"},
        {"task": "Withhold water", "type": "irrigation", "days_from_now": 90, "description": "Stop irrigation 10 days before harvest for curing"},
        {"task": "Harvest", "type": "harvest", "days_from_now": 100, "description": "Harvest when 50% tops fall over"},
    ],
    "potato": [
        {"task": "Seed treatment", "type": "sowing", "days_from_now": -5, "description": "Treat seed pieces with Captan/Mancozeb"},
        {"task": "Planting", "type": "sowing", "days_from_now": 0, "description": "Plant at 60x20 cm, 5-7 cm deep"},
        {"task": "First irrigation", "type": "irrigation", "days_from_now": 3, "description": "Light irrigation after planting"},
        {"task": "Earthing up", "type": "maintenance", "days_from_now": 25, "description": "Hill up soil to prevent greening"},
        {"task": "Top dressing", "type": "fertilizer", "days_from_now": 25, "description": "Apply 60 kg N/ha at earthing up"},
        {"task": "Late blight monitoring", "type": "monitoring", "days_from_now": 35, "description": "Daily check — spray Mancozeb at first sign"},
        {"task": "Irrigation (critical)", "type": "irrigation", "days_from_now": 40, "description": "Critical irrigation during tuber initiation"},
        {"task": "Vine killing", "type": "maintenance", "days_from_now": 80, "description": "Cut vines 10 days before harvest to harden skin"},
        {"task": "Harvest", "type": "harvest", "days_from_now": 90, "description": "Dig when skin is firm — store in cool dark place"},
    ],
    "maize": [
        {"task": "Land preparation", "type": "sowing", "days_from_now": -5, "description": "Plough, harrow and form ridges"},
        {"task": "Sowing", "type": "sowing", "days_from_now": 0, "description": "Sow 2 seeds/hill at 60x20 cm, thin to 1"},
        {"task": "Thinning & gap filling", "type": "maintenance", "days_from_now": 14, "description": "Thin to 1 plant/hill, fill gaps"},
        {"task": "Earthing up", "type": "maintenance", "days_from_now": 25, "description": "Hill up to support plants and control weeds"},
        {"task": "Top dressing 1", "type": "fertilizer", "days_from_now": 25, "description": "Apply 60 kg N/ha at knee-high stage"},
        {"task": "Top dressing 2", "type": "fertilizer", "days_from_now": 45, "description": "Apply 60 kg N/ha before tasseling"},
        {"task": "Fall armyworm check", "type": "monitoring", "days_from_now": 20, "description": "Check whorls for fall armyworm — spray early morning"},
        {"task": "Irrigation at silking", "type": "irrigation", "days_from_now": 55, "description": "Critical irrigation at silking stage"},
        {"task": "Grain filling", "type": "monitoring", "days_from_now": 70, "description": "Check grain filling — avoid water stress"},
        {"task": "Harvest", "type": "harvest", "days_from_now": 100, "description": "Harvest when husks are dry and grains hard"},
    ],
    "soybean": [
        {"task": "Seed inoculation", "type": "sowing", "days_from_now": -1, "description": "Inoculate seeds with Rhizobium + PSB culture"},
        {"task": "Sowing", "type": "sowing", "days_from_now": 0, "description": "Sow at 45x5 cm, 3-4 cm deep"},
        {"task": "Pre-emergence herbicide", "type": "maintenance", "days_from_now": 2, "description": "Apply pendimethalin for weed control"},
        {"task": "First irrigation", "type": "irrigation", "days_from_now": 15, "description": "Irrigation at flowering if dry"},
        {"task": "Weeding", "type": "maintenance", "days_from_now": 20, "description": "Hand weeding or inter-cultivation"},
        {"task": "Flowering check", "type": "monitoring", "days_from_now": 35, "description": "Monitor for girdle beetle and stem fly"},
        {"task": "Pod filling irrigation", "type": "irrigation", "days_from_now": 60, "description": "Critical irrigation at pod filling"},
        {"task": "Yellow mosaic monitoring", "type": "monitoring", "days_from_now": 45, "description": "Check for yellow mosaic virus — control whiteflies"},
        {"task": "Harvest", "type": "harvest", "days_from_now": 95, "description": "Harvest when 90% pods turn yellow-brown"},
    ],
}


def crop_calendar_agent(state: FarmSphereState) -> dict:
    start_time = time.time()
    crop = (state.get("crop_type") or "tomato").lower()
    calendar_tasks = CROP_CALENDARS.get(crop, CROP_CALENDARS["tomato"])
    today = datetime.now()
    upcoming = []
    for task in calendar_tasks:
        task_date = today + timedelta(days=task["days_from_now"])
        upcoming.append({**task, "date": task_date.strftime("%Y-%m-%d"),
                         "is_due": task["days_from_now"] <= 7 and task["days_from_now"] >= 0})
    # Next 3 upcoming tasks
    next_tasks = [t for t in upcoming if t["days_from_now"] >= 0][:3]
    duration_ms = (time.time() - start_time) * 1000
    trace = AgentTrace(agent_name="crop_calendar_agent", started_at=start_time, ended_at=time.time(),
                      duration_ms=round(duration_ms, 2), status="success",
                      output_summary=f"Generated {len(upcoming)} calendar entries for {crop}")
    return {"crop_calendar": {"crop": crop, "tasks": upcoming},
            "upcoming_tasks": next_tasks,
            "agent_traces": [trace], "agents_invoked": ["crop_calendar_agent"], "errors": []}


# ════════════════════════════════════════════════════════════════════════════
# Agent: Proactive Alert Agent
# ════════════════════════════════════════════════════════════════════════════

def alert_agent(state: FarmSphereState) -> dict:
    start_time = time.time()
    alerts = []

    # Weather-based alerts
    weather = state.get("weather_data", {})
    if weather:
        rain_chance = weather.get("forecast", [{}])[0].get("rain_chance", 0) if weather.get("forecast") else 0
        humidity = weather.get("humidity", 60)
        temp = weather.get("temperature", 25)

        if rain_chance > 70:
            alerts.append({"type": "weather", "severity": "high", "title": "🌧️ Heavy Rain Expected",
                           "message": f"{rain_chance}% chance of rain tomorrow. Avoid pesticide spraying today.",
                           "action": "Postpone any planned chemical applications"})
        if humidity > 85:
            alerts.append({"type": "disease", "severity": "medium", "title": "🍄 High Disease Risk",
                           "message": f"Humidity at {humidity}% — ideal conditions for fungal growth.",
                           "action": "Apply preventive fungicide within 24 hours"})
        if temp > 40:
            alerts.append({"type": "weather", "severity": "high", "title": "🌡️ Extreme Heat Alert",
                           "message": f"Temperature {temp}°C — heat stress risk for crops.",
                           "action": "Irrigate in early morning or evening"})

    # Disease-based alerts
    disease_conf = state.get("disease_confidence", 0)
    if disease_conf and disease_conf > 0.7:
        alerts.append({"type": "disease", "severity": "critical",
                       "title": f"🦠 Disease Detected: {state.get('disease_name', '')}",
                       "message": f"Confidence: {disease_conf:.0%}. Immediate treatment recommended.",
                       "action": "Apply prescribed fungicide/treatment today"})

    # Market opportunity alerts
    market = state.get("market_prices", {})
    if market.get("trend") == "rising" and market.get("change_pct", 0) > 10:
        alerts.append({"type": "market", "severity": "low",
                       "title": "📈 Good Selling Opportunity",
                       "message": f"Crop prices up {market['change_pct']:.0f}% — consider selling soon.",
                       "action": f"Contact {market.get('best_market', 'nearest mandi')}"})

    duration_ms = (time.time() - start_time) * 1000
    trace = AgentTrace(agent_name="alert_agent", started_at=start_time, ended_at=time.time(),
                      duration_ms=round(duration_ms, 2), status="success",
                      output_summary=f"Generated {len(alerts)} proactive alerts")
    return {"active_alerts": alerts, "agent_traces": [trace],
            "agents_invoked": ["alert_agent"], "errors": []}
