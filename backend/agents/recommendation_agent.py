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

RECOMMENDATION_SYSTEM_PROMPT = """You are FarmSphere AI's final recommendation synthesizer.
Combine all available agricultural intelligence into one clear, actionable response for the farmer.

STRUCTURE YOUR RESPONSE as follows (use markdown):
## 🌱 Diagnosis (if disease detected)
## 💊 Treatment Recommendations
## 🌤️ Weather Advisory
## ⚠️ Risk Alert
## 📅 Immediate Actions (next 48 hours)
## 📌 Sources

RULES:
1. Speak directly to the farmer in a supportive, confident tone
2. Prioritize the most urgent actions first
3. Always explain WHY you recommend something (the reasoning)
4. Mention confidence scores where relevant
5. If HITL is required, clearly ask for additional images
6. Keep total response under 400 words
7. Use farmer-friendly language (avoid heavy jargon)"""

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

                full_prompt = (
                    f"FARMER: {farmer_name} | CROP: {crop} | LOCATION: {state.get('location', 'India')}\n"
                    f"FARMER QUESTION: {state.get('user_message', '')}\n\n"
                    f"AVAILABLE INTELLIGENCE:\n{context}\n\n"
                    f"CITED SOURCES: {', '.join(sources) or 'Internal knowledge base'}"
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
    parts = ["# FarmSphere AI Recommendation\n"]

    if state.get("disease_name"):
        conf = state.get("disease_confidence", 0)
        parts.append(f"## 🌱 Diagnosis\n**{state['disease_name']}** (Confidence: {conf:.0%})\n")
        if state.get("disease_symptoms"):
            symptoms = "\n".join(f"• {s}" for s in state["disease_symptoms"])
            parts.append(f"**Symptoms observed:**\n{symptoms}\n")

    if state.get("knowledge_context"):
        parts.append(f"## 💊 Treatment\n{state['knowledge_context'][:600]}\n")

    if state.get("weather_advice"):
        parts.append(f"## 🌤️ Weather Advisory\n{state['weather_advice']}\n")

    if state.get("risk_summary"):
        parts.append(f"## ⚠️ Risk Alert\n{state['risk_summary']}\n")

    if state.get("preventive_actions"):
        actions = "\n".join(f"• {a}" for a in state["preventive_actions"])
        parts.append(f"## 📅 Immediate Actions\n{actions}\n")

    sources = list({doc["source"] for doc in (state.get("source_documents") or []) if doc.get("source")})
    if sources:
        parts.append(f"## 📌 Sources\n" + "\n".join(f"• {s}" for s in sources))

    return "\n".join(parts)
