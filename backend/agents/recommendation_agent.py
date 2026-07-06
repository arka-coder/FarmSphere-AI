"""
FarmSphere AI — Recommendation Agent (Layer 1)
Synthesizes outputs from all upstream agents into a unified, structured recommendation.
"""
import time
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace
from config import settings
from agents.llm_helper import invoke_with_fallback

logger = logging.getLogger(__name__)

RECOMMENDATION_SYSTEM_PROMPT = """You are FarmSphere AI — a global agricultural intelligence assistant.

## Non-Negotiable Rules:
1. **ENGLISH ONLY** — always respond in English, regardless of the user's location or language
2. **Be concise** — give precise, direct answers. No padding, no unnecessary repetition
3. **Location-aware** — use the farmer's country/state/district to give locally relevant advice. If no location is provided, give general globally applicable guidance
4. **Do not assume India** — only use India-specific references (APMC, MSP, ICAR, KVK, ₹) when the user's location is India
5. **Never invent prices** — all price data is reference only; always tell users to verify locally

## Response Structure:
Adapt structure to the query type. Keep total response under 300 words.

**For farming/disease/agronomy queries:**
- 🎯 **Answer** — 1-2 direct sentences
- 📋 **Details** — bullet points, max 5 items
- ✅ **Next Steps** — 2-3 actionable items
- 📌 **Source** — 1-2 references (FAO / USDA / ICAR / local extension)

**For market/price queries:**
- 📊 **Price** — current reference price with source
- 📍 **Where to sell** — local market/exchange options
- 📈 **Trend** — brief market outlook (1-2 sentences)
- ✅ **Recommendation** — sell now / wait / store

## Location-Based References:
- **India**: ICAR, APMC mandi, MSP, Agmarknet, eNAM, KVK, ₹/quintal
- **USA**: USDA, CME/CBOT prices, Extension Service, $/bushel or $/ton
- **UK/EU**: AHDB, EU CAP, Defra, £/tonne or €/tonne
- **Africa**: FAO, local Ministry of Agriculture, local currency/unit
- **No location**: FAO, globally applicable guidance, USD pricing"""

HITL_TEMPLATE = """
## 🔍 Additional Information Needed

I've analyzed your plant image, but the diagnosis confidence is **{confidence:.0%}** — below our 75% threshold for a confident recommendation.

**Top Possibilities:**
{alternatives}

To provide an accurate diagnosis, please share:
1. 📸 **Front of the leaf** — close-up of the spots/lesions
2. 📸 **Back of the leaf** — underside where spores are often visible
3. 📸 **Stem/branch** — to check for stem lesions

In the meantime, as a precaution:
• Avoid wetting leaves during irrigation
• Do not apply any treatment until confirmed
• Isolate affected plants from healthy ones

👨‍🌾 **Recommended:** Consult your nearest KVK (Krishi Vigyan Kendra) for expert confirmation.
"""


def recommendation_agent(state: FarmSphereState) -> dict:
    """
    Recommendation Agent — Final synthesis of all agent outputs.
    """
    start_time = time.time()
    logger.info("Recommendation agent synthesizing outputs")

    try:
        # Handle HITL case
        if state.get("hitl_required"):
            alternatives_text = ""
            for alt in (state.get("disease_alternatives") or [])[:3]:
                conf = alt.get("confidence", 0)
                alternatives_text += f"• **{alt.get('name')}** — {conf:.0%} probability\n"

            final_response = HITL_TEMPLATE.format(
                confidence=state.get("disease_confidence", 0.5),
                alternatives=alternatives_text or "• Multiple possibilities detected\n",
            )

            duration_ms = (time.time() - start_time) * 1000
            trace = AgentTrace(
                agent_name="recommendation_agent",
                started_at=start_time,
                ended_at=time.time(),
                duration_ms=round(duration_ms, 2),
                status="success",
                output_summary="HITL response generated — requesting additional images",
            )
            return {
                "final_response": final_response,
                "agent_traces": [trace],
                "agents_invoked": ["recommendation_agent"],
                "errors": [],
            }

        # Normal synthesis path
        intent = state.get("intent", "general_farming")

        # ── Fast-path: pure market query — skip LLM, return market_advice directly ──
        if intent in ("market_query", "price_query_statewise", "export_market"):
            market_advice = state.get("market_advice", "")
            if market_advice:
                duration_ms = (time.time() - start_time) * 1000
                trace = AgentTrace(
                    agent_name="recommendation_agent",
                    started_at=start_time,
                    ended_at=time.time(),
                    duration_ms=round(duration_ms, 2),
                    status="success",
                    output_summary="Market fast-path — direct price response",
                )
                return {
                    "final_response": market_advice,
                    "agent_traces": [trace],
                    "agents_invoked": ["recommendation_agent"],
                    "errors": [],
                }

        if settings.google_api_key:
            try:
                # Build context from all agents
                context_parts = []

                if state.get("disease_name"):
                    context_parts.append(
                        f"DISEASE DETECTED: {state['disease_name']} "
                        f"(confidence: {state.get('disease_confidence', 0):.0%}, "
                        f"severity: {state.get('disease_severity', 'unknown')})"
                    )
                    if state.get("disease_symptoms"):
                        context_parts.append(f"SYMPTOMS: {', '.join(state['disease_symptoms'])}")
                    if state.get("disease_alternatives"):
                        alts = [f"{a['name']} ({a['confidence']:.0%})" for a in state.get("disease_alternatives", [])]
                        context_parts.append(f"ALTERNATIVES: {', '.join(alts)}")

                if state.get("knowledge_context"):
                    context_parts.append(f"KNOWLEDGE BASE:\n{state['knowledge_context']}")

                if state.get("weather_advice"):
                    context_parts.append(f"WEATHER ADVISORY: {state['weather_advice']}")

                if state.get("seasonal_advice"):
                    context_parts.append(f"SEASONAL CONTEXT: {state['seasonal_advice']}")

                if state.get("risk_summary"):
                    context_parts.append(f"RISK ASSESSMENT: {state['risk_summary']}")

                if state.get("preventive_actions"):
                    actions = "\n".join(f"- {a}" for a in state.get("preventive_actions", []))
                    context_parts.append(f"PREVENTIVE ACTIONS:\n{actions}")

                if state.get("applicable_schemes"):
                    context_parts.append(f"GOVT SCHEMES: {state.get('applicable_schemes', [])}")

                if state.get("market_advice"):
                    context_parts.append(f"MARKET INTELLIGENCE: {state['market_advice']}")

                # Source list
                sources = []
                for doc in (state.get("source_documents") or []):
                    if doc.get("source") and doc["source"] not in sources:
                        sources.append(doc["source"])

                context = "\n\n".join(context_parts)
                farmer_name = state.get("farmer_name", "Farmer")
                crop = state.get("crop_type", "your crop")
                location = state.get("location") or "Not specified"
                country = state.get("country") or ""

                full_prompt = (
                    f"FARMER: {farmer_name} | CROP: {crop} | "
                    f"LOCATION: {location}{' | COUNTRY: ' + country if country else ''}\n"
                    f"QUESTION: {state.get('user_message', '')}\n\n"
                    f"AVAILABLE DATA:\n{context}\n\n"
                    f"SOURCES AVAILABLE: {', '.join(sources) or 'Internal knowledge base'}\n\n"
                    f"IMPORTANT: Respond in English only. Be concise."
                )

                ai_response = invoke_with_fallback(
                    [
                        SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT),
                        HumanMessage(content=full_prompt),
                    ],
                    temperature=0.4,
                )
                final_response = ai_response if ai_response else _build_fallback_response(state)
            except Exception as e:
                logger.warning("Synthesis failed (%s) — using fallback", e)
                final_response = _build_fallback_response(state)
        else:
            final_response = _build_fallback_response(state)

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="recommendation_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary="Unified recommendation synthesized",
        )

        return {
            "final_response": final_response,
            "agent_traces": [trace],
            "agents_invoked": ["recommendation_agent"],
            "errors": [],
        }

    except Exception as e:
        logger.error("Recommendation agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="recommendation_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "final_response": "I'm processing your request. Please try again.",
            "agent_traces": [trace],
            "agents_invoked": ["recommendation_agent"],
            "errors": [f"Recommendation agent: {str(e)}"],
        }


def _build_fallback_response(state: FarmSphereState) -> str:
    """Fallback when LLM synthesis fails — assembles all available agent data directly."""
    parts = []

    # Market data — most common failure case, show this prominently
    if state.get("market_advice"):
        parts.append(state["market_advice"])

    # Knowledge context (disease treatment, crop advice, soil info)
    elif state.get("knowledge_context"):
        parts.append(state["knowledge_context"][:800])

    # Disease diagnosis
    if state.get("disease_name"):
        conf = state.get("disease_confidence", 0)
        parts.append(f"**Diagnosis**: {state['disease_name']} (Confidence: {conf:.0%})")
        if state.get("disease_symptoms"):
            symptoms = ", ".join(state["disease_symptoms"])
            parts.append(f"**Symptoms**: {symptoms}")

    # Weather
    if state.get("weather_advice"):
        parts.append(f"**Weather**: {state['weather_advice']}")

    # Risk
    if state.get("risk_summary"):
        parts.append(f"**Risk**: {state['risk_summary']}")

    # Preventive actions
    if state.get("preventive_actions"):
        actions = "\n".join(f"• {a}" for a in state["preventive_actions"])
        parts.append(f"**Actions**:\n{actions}")

    # If nothing at all
    if not parts:
        parts.append(
            "I was unable to generate a complete response. "
            "Please check your crop type and location, then try again."
        )

    # Sources (deduplicated, no Nashik/state hardcoding)
    unique_sources = []
    seen = set()
    for doc in (state.get("source_documents") or []):
        src = doc.get("source", "")
        # Strip generic mandi-location suffixes that add no value
        clean = src.split(" — ")[0] if " — " in src else src
        if clean and clean not in seen:
            seen.add(clean)
            unique_sources.append(clean)

    if unique_sources:
        parts.append("\n*Source: " + " | ".join(unique_sources) + "*")

    return "\n\n".join(parts)
