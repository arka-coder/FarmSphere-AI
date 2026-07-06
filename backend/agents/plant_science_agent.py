"""
FarmSphere AI — Plant Science Expert Agent
Deep botanical, physiological, and agronomic knowledge engine.

Handles:
- Plant taxonomy & morphology
- Photosynthesis (C3/C4/CAM), transpiration, nutrient uptake
- Seed germination science & dormancy
- Soil microbiome & mycorrhizal associations
- Allelopathy & companion planting
- Plant growth regulators (NAA, GA3, Ethephon, CCC etc.)
- Organic farming: biofertilizers, vermicompost, SRI, natural pest control

Can be called:
  1. From knowledge_agent as a sub-specialist
  2. Directly from POST /api/plant-science endpoint
"""
import time
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings
from agents.llm_helper import invoke_with_thinking

logger = logging.getLogger(__name__)


PLANT_SCIENCE_SYSTEM_PROMPT = """You are FarmSphere AI's plant science expert — a botanist and plant physiologist with encyclopaedic knowledge of global crop biology.

## Non-Negotiable Rules:
1. **ENGLISH ONLY** — always respond in English regardless of location
2. **Be concise** — answer precisely, max 250 words unless deep detail is explicitly requested
3. **Global scope** — apply globally relevant science; reference region-specific institutes only when user's location is known

## Your Expertise:
- Plant physiology: photosynthesis (C3/C4/CAM), transpiration, water potential, nutrient uptake
- Plant hormones: IAA, GA3, cytokinins, ABA, ethylene, brassinosteroids
- Seed science: dormancy types, germination physiology, seed priming
- Soil biology: mycorrhizae (AM/ECM), rhizobium, azospirillum, PSB, actinomycetes
- Biofertilizers: mechanism and application of Rhizobium, Azotobacter, Azospirillum, VAM, BGA
- Allelopathy, companion planting, intercropping synergies
- Stress physiology: drought, salinity, heat, waterlogging responses

## Response Format:
- **Answer**: Direct explanation (1-2 sentences)
- **Mechanism**: How it works (bullet points, plain language by default; biochemical depth if requested)
- **Practical Application**: What this means for crop management
- **Source**: 1-2 references (ICAR for India users, FAO/peer-reviewed journals for others)

## Detect user type from query:
- Farmer question → simple analogy + practical steps
- Research/science question → full biochemical/molecular depth
- Ambiguous → start simple, offer "Want the science behind this?"

ALWAYS respond in English. Never translate your response."""


def plant_science_agent(state: FarmSphereState) -> dict:
    """
    Plant Science Expert Agent — handles deep botanical/agronomic queries.
    Uses thinking-mode LLM for best scientific accuracy.
    """
    start_time = time.time()
    logger.info("Plant science agent processing: %s", state.get("user_message", "")[:80])

    try:
        from agents.agriculture_kb import (
            PHOTOSYNTHESIS_TYPES, PLANT_GROWTH_REGULATORS,
            BIOFERTILIZERS, COMPANION_PLANTING, ALLELOPATHY,
            CROP_ENCYCLOPEDIA, KB_SUMMARY,
        )

        user_message = state.get("user_message", "")
        crop = state.get("crop_type", "")

        # Build enriched context from KB
        context_parts = [f"KB SUMMARY:\n{KB_SUMMARY}"]

        # Inject relevant KB sections based on message keywords
        msg_lower = user_message.lower()

        if any(w in msg_lower for w in ["photosynthesis", "c3", "c4", "cam", "photorespiration", "rubisco", "hatch-slack"]):
            context_parts.append(f"PHOTOSYNTHESIS DATA:\n{_format_dict(PHOTOSYNTHESIS_TYPES)}")

        if any(w in msg_lower for w in ["hormone", "pgr", "auxin", "gibberellin", "cytokinin", "ethylene", "aba", "naa", "ga3", "ethephon", "brassinosteroid", "growth regulator"]):
            context_parts.append(f"PLANT GROWTH REGULATORS:\n{_format_dict(PLANT_GROWTH_REGULATORS)}")

        if any(w in msg_lower for w in ["biofertilizer", "rhizobium", "azospirillum", "mycorrhiza", "vam", "trichoderma", "psb", "azolla", "bga", "nitrogen fixing"]):
            context_parts.append(f"BIOFERTILIZERS:\n{_format_dict(BIOFERTILIZERS)}")

        if any(w in msg_lower for w in ["companion", "intercrop", "allelopathy", "mixed crop"]):
            context_parts.append(f"COMPANION PLANTING:\n{_format_dict(COMPANION_PLANTING)}")
            context_parts.append(f"ALLELOPATHY:\n{_format_dict(ALLELOPATHY)}")

        if crop:
            crop_data = CROP_ENCYCLOPEDIA.get(crop.lower())
            if crop_data:
                context_parts.append(f"CROP DATA ({crop.upper()}):\n{_format_dict(crop_data)}")

        kb_context = "\n\n---\n\n".join(context_parts)

        full_prompt = (
            f"KNOWLEDGE BASE CONTEXT:\n{kb_context}\n\n"
            f"FARMER/USER QUESTION: {user_message}\n"
            f"CROP CONTEXT: {crop or 'Not specified'}\n"
            f"LOCATION: {state.get('location', 'India')}\n"
            f"SEASON: {state.get('season', 'Not specified')}"
        )

        if settings.google_api_key:
            # Use thinking mode for deep scientific accuracy
            response = invoke_with_thinking(
                [
                    SystemMessage(content=PLANT_SCIENCE_SYSTEM_PROMPT),
                    HumanMessage(content=full_prompt),
                ],
                temperature=0.2,
            )
            plant_science_answer = response if response else _build_fallback_plant_science(user_message)
        else:
            plant_science_answer = _build_fallback_plant_science(user_message)

        source_doc = SourceDocument(
            title="Plant Science Knowledge Base",
            source="ICAR-IARI New Delhi / Indian Journal of Agricultural Sciences",
            relevance_score=0.92,
            excerpt=plant_science_answer[:200] + "..." if len(plant_science_answer) > 200 else plant_science_answer,
        )

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="plant_science_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary="Plant science expert response generated",
        )

        return {
            "knowledge_context": plant_science_answer,
            "source_documents": [source_doc],
            "agent_traces": [trace],
            "agents_invoked": ["plant_science_agent"],
            "errors": [],
        }

    except Exception as e:
        logger.error("Plant science agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="plant_science_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "knowledge_context": "Plant science expert temporarily unavailable. Please try again.",
            "source_documents": [],
            "agent_traces": [trace],
            "agents_invoked": ["plant_science_agent"],
            "errors": [f"Plant science agent: {str(e)}"],
        }


def _format_dict(d: dict, indent: int = 0) -> str:
    """Simple dict → readable string for LLM context."""
    lines = []
    for k, v in d.items():
        if isinstance(v, dict):
            lines.append(f"{'  ' * indent}{k}:")
            lines.append(_format_dict(v, indent + 1))
        elif isinstance(v, list):
            lines.append(f"{'  ' * indent}{k}: {', '.join(str(i) for i in v)}")
        else:
            lines.append(f"{'  ' * indent}{k}: {v}")
    return "\n".join(lines)


def _build_fallback_plant_science(query: str) -> str:
    """Structured fallback when LLM is unavailable."""
    return (
        "## 🌿 Plant Science Response\n\n"
        f"**Your question:** {query}\n\n"
        "I'm currently unable to reach the AI model for a detailed response. "
        "Here are some quick resources:\n\n"
        "- **ICAR Knowledge Portal**: [icar.org.in](https://icar.org.in)\n"
        "- **IARI Publications**: [iari.res.in/publications](https://iari.res.in)\n"
        "- **Krishi Vigyan Kendra (KVK)**: Contact your nearest KVK for local expert advice\n"
        "- **AgriJunction**: [agrijunction.com](https://agrijunction.com)\n\n"
        "📚 **Source**: ICAR-IARI New Delhi"
    )


# ── Standalone query function for API endpoint ────────────────────────────────

def query_plant_science(question: str, crop: str = "", location: str = "India") -> str:
    """
    Convenience function to query plant science knowledge without a full FarmSphereState.
    Used by /api/plant-science endpoint.
    """
    mock_state = {
        "user_message": question,
        "crop_type": crop,
        "location": location,
        "season": None,
        "farmer_id": "api_direct",
        "farmer_name": "User",
        "language": "en",
        "image_base64": None,
        "image_path": None,
        "conversation_history": [],
        "hitl_required": False,
        "agent_traces": [],
        "agents_invoked": [],
        "source_documents": [],
        "errors": [],
    }
    result = plant_science_agent(mock_state)
    return result.get("knowledge_context", "No response generated.")
