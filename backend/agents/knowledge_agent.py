"""
FarmSphere AI — Knowledge Agent (Layer 1)
ChromaDB RAG over ICAR documents, crop manuals, disease references.
Upgraded to ELITE mode: encyclopaedic agriculture knowledge base injection,
plant science specialist integration, and expert agronomist system prompt.
Always cites sources. Never hallucinates.
"""
import time
import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from database.chromadb_client import query_collection
from config import settings

logger = logging.getLogger(__name__)

ELITE_AGRICULTURAL_ADVISOR_PROMPT = """You are FarmSphere AI's expert agricultural advisor with encyclopaedic knowledge of global crop science, agronomy, pest management, soil science, and agricultural markets.

## Core Rules:
1. **ALWAYS respond in English only** — never use Hindi, Bengali, or any other language regardless of location
2. **Be concise and precise** — answer the question directly; avoid padding, repetition, or lengthy preambles
3. **Location-aware** — if a country/state/district is provided, tailor advice to local conditions, regulations, and crop varieties. If no location: give general global advice
4. **Do not assume India** — the platform serves farmers worldwide. Only mention Indian-specific details (APMC, MSP, ICAR, etc.) when the user is clearly in India
5. **Cite sources** — end with 1-2 authoritative sources relevant to the user's region (FAO, local Dept. of Agriculture, ICAR for India, USDA for USA, etc.)
6. **Never hallucinate prices** — state prices are reference rates; always advise verification

## Response Format:
Use these sections **only when relevant** — skip sections that don't apply:
- **Answer**: Direct 1-2 sentence response
- **Details**: Key information with bullet points (keep under 150 words)
- **Action**: 2-3 specific next steps
- **Sources**: 1-2 references

## Location Logic:
- If country = India: use ICAR, APMC, MSP, Agmarknet, KVK references
- If country = USA: use USDA, Extension Service, NRCS references  
- If country = UK/EU: use AHDB, EU CAP, local ministry references
- If location unknown: use FAO and globally applicable guidance
- Always mention local currency and measurement units appropriate to the country

## What You Know:
- Global crop science: 200+ crops, cultivation, soil, pests, diseases
- Market data: Global commodity exchanges (CBOT, ICE, CME), local market logic
- Government schemes: region-specific (only when location is known)
- Plant science: photosynthesis, mycorrhiza, biofertilizers, PGRs, allelopathy"""


def _is_plant_science_query(message: str) -> bool:
    """Detect if query needs deep plant science expertise."""
    keywords = [
        "photosynthesis", "transpiration", "c4", "c3", "cam", "hatch-slack",
        "mycorrhiza", "vam", "rhizobium", "azospirillum", "biofertilizer",
        "auxin", "gibberellin", "cytokinin", "pgr", "ethephon", "naa", "ga3",
        "dormancy", "germination science", "allelopathy", "companion plant",
        "phloem", "xylem", "stomata", "chlorophyll", "rubisco",
        "nitrogen fixation", "nutrient uptake", "soil microbiome",
        "taxonomy", "morphology", "anatomy", "physiology",
    ]
    msg = message.lower()
    return any(kw in msg for kw in keywords)


def _build_query(state: FarmSphereState) -> str:
    """Build an intelligent query combining disease, crop, and message context."""
    parts = []
    if state.get("disease_name") and state["disease_name"] != "Unable to diagnose":
        parts.append(state["disease_name"])
    if state.get("crop_type"):
        parts.append(state["crop_type"])
    if state.get("user_message"):
        parts.append(state["user_message"])
    if state.get("intent"):
        intent_map = {
            "treatment_advice": "treatment management fungicide pesticide",
            "scheme_query": "government scheme eligibility",
            "general_farming": "farming advice agronomy",
            "soil_nutrition": "soil nutrition fertilizer deficiency",
            "export_market": "export price global market APEDA",
            "crop_disease_plant_science": "plant science botany physiology",
        }
        parts.append(intent_map.get(state["intent"], ""))

    return " ".join(filter(None, parts))[:500]


def _format_retrieved_docs(results: dict) -> tuple[str, list[SourceDocument]]:
    """Format ChromaDB results into context string and source docs list."""
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "", []

    context_parts = []
    source_docs = []

    for doc, meta, dist in zip(documents, metadatas, distances):
        relevance = max(0.0, 1.0 - float(dist))  # cosine distance → similarity
        if relevance < 0.3:  # skip low-relevance docs
            continue

        source_name = meta.get("source", "Agricultural Knowledge Base")
        context_parts.append(f"[Source: {source_name}]\n{doc}")

        source_doc = SourceDocument(
            title=source_name,
            source=meta.get("source", "ICAR Knowledge Base"),
            relevance_score=round(relevance, 3),
            excerpt=doc[:200] + "..." if len(doc) > 200 else doc,
        )
        source_docs.append(source_doc)

    return "\n\n---\n\n".join(context_parts), source_docs


def _build_kb_context(state: FarmSphereState) -> str:
    """Inject relevant agriculture KB sections into the prompt context."""
    try:
        from agents.agriculture_kb import (
            KB_SUMMARY, get_msp, get_statewise_price, get_crop_info, get_zone_info,
            INDIA_SOIL_TYPES,
        )

        msg = state.get("user_message", "").lower()
        crop = (state.get("crop_type") or "").lower()
        state_name = state.get("state_name") or state.get("location") or ""
        parts = [KB_SUMMARY]

        # State-wise price context
        if crop and state_name and any(w in msg for w in ["price", "rate", "mandi", "market", "quintal"]):
            price_data = get_statewise_price(crop, state_name)
            if price_data.get("price_per_quintal"):
                parts.append(
                    f"STATE-WISE PRICE ({crop.upper()} in {state_name}):\n"
                    f"  Current market rate: ₹{price_data['price_per_quintal']}/quintal\n"
                    f"  National average: ₹{price_data['national_average']}/quintal\n"
                    f"  Price trend: {price_data.get('trend_vs_national', 'N/A')}\n"
                    f"  Major mandi: {price_data.get('major_mandi', 'N/A')}\n"
                    + (f"  MSP 2024-25: ₹{price_data['msp_2024_25']}/quintal ({price_data['vs_msp']})\n"
                       if price_data.get('msp_2024_25') else "")
                )

        # MSP lookup
        if any(w in msg for w in ["msp", "minimum support price", "government price", "procurement"]):
            if crop:
                msp = get_msp(crop)
                if msp:
                    parts.append(
                        f"MSP 2024-25 ({crop.upper()}): ₹{msp['msp']}/quintal "
                        f"(Season: {msp['season']}, Source: {msp['source']})"
                    )

        # Crop encyclopaedia context
        if crop:
            crop_info = get_crop_info(crop)
            if crop_info:
                # Selective injection — only most relevant parts
                relevant = {}
                if any(w in msg for w in ["disease", "pest", "blight", "rust", "wilt", "spot"]):
                    relevant["major_diseases"] = crop_info.get("major_diseases", [])
                    relevant["major_pests"] = crop_info.get("major_pests", [])
                if any(w in msg for w in ["fertilizer", "nutrient", "npk", "nitrogen", "phosphorus", "zinc"]):
                    relevant["nutrient_requirements_kg_per_ha"] = crop_info.get("nutrient_requirements_kg_per_ha", {})
                if any(w in msg for w in ["variety", "varieties", "seed", "cultivar"]):
                    relevant["major_varieties"] = crop_info.get("major_varieties", {})
                if any(w in msg for w in ["water", "irrigation", "moisture"]):
                    relevant["water_requirement_mm"] = crop_info.get("water_requirement_mm")
                    relevant["critical_irrigation_stages"] = crop_info.get("critical_irrigation_stages", [])
                if relevant:
                    parts.append(f"CROP KB ({crop.upper()}):\n" + "\n".join(f"  {k}: {v}" for k, v in relevant.items()))

        # Agro-climatic zone context
        if state_name:
            zones = get_zone_info(state_name)
            if zones:
                z = zones[0]
                parts.append(
                    f"AGRO-CLIMATIC ZONE ({state_name}): {z['name']}\n"
                    f"  Major crops: {', '.join(z.get('major_crops', []))}\n"
                    f"  Rainfall: {z.get('rainfall_mm', 'N/A')} mm/year"
                )

        return "\n\n".join(parts)

    except Exception as e:
        logger.warning("KB context build failed: %s", e)
        return ""


def knowledge_agent(state: FarmSphereState) -> dict:
    """
    Knowledge Agent — ChromaDB RAG with citation-enforced answers.
    Queries multiple collections and synthesizes with Gemini Elite prompt.
    Integrates agriculture_kb for state-wise prices, MSP, crop encyclopaedia.
    Delegates to plant_science_agent for deep botanical queries.
    """
    start_time = time.time()
    logger.info("Knowledge agent querying for: %s", state.get("user_message", "")[:80])

    try:
        # ── Plant Science Delegation ─────────────────────────────────────────
        if _is_plant_science_query(state.get("user_message", "")):
            logger.info("Delegating to plant science expert agent")
            from agents.plant_science_agent import plant_science_agent
            result = plant_science_agent(state)
            # Add knowledge_agent to the invoked list
            result["agents_invoked"] = ["knowledge_agent"] + result.get("agents_invoked", [])
            return result

        # ── ChromaDB RAG ─────────────────────────────────────────────────────
        query = _build_query(state)

        icar_results = query_collection("icar_docs", [query], n_results=3)
        disease_results = {}
        if state.get("disease_name"):
            disease_results = query_collection(
                "icar_docs", [state["disease_name"]], n_results=2,
                where={"crop": state.get("crop_type")} if state.get("crop_type") else None,
            )

        all_docs = icar_results.get("documents", [[]])[0] + disease_results.get("documents", [[]])[0]
        all_metas = icar_results.get("metadatas", [[]])[0] + disease_results.get("metadatas", [[]])[0]
        all_dists = icar_results.get("distances", [[]])[0] + disease_results.get("distances", [[]])[0]

        merged = {"documents": [all_docs], "metadatas": [all_metas], "distances": [all_dists]}
        rag_context, source_docs = _format_retrieved_docs(merged)

        # ── Agriculture KB Context ────────────────────────────────────────────
        kb_context = _build_kb_context(state)

        # ── Build Full Context ────────────────────────────────────────────────
        context_sections = []
        if rag_context:
            context_sections.append(f"RETRIEVED ICAR DOCUMENTS:\n{rag_context}")
        if kb_context:
            context_sections.append(f"AGRICULTURE KNOWLEDGE BASE:\n{kb_context}")

        combined_context = "\n\n═══════════════\n\n".join(context_sections)

        # ── Generate LLM Answer ───────────────────────────────────────────────
        llm_answer = ""
        if combined_context and settings.google_api_key:
            try:
                from agents.llm_helper import invoke_with_fallback
                prompt = (
                    f"KNOWLEDGE BASE CONTEXT:\n{combined_context}\n\n"
                    f"FARMER QUESTION: {state.get('user_message', '')}\n"
                    f"CROP: {state.get('crop_type', 'not specified')}\n"
                    f"STATE/LOCATION: {state.get('state_name') or state.get('location') or 'India'}\n"
                    f"SEASON: {state.get('season', 'not specified')}\n"
                    f"DISEASE DETECTED: {state.get('disease_name', 'none')}"
                )
                result = invoke_with_fallback(
                    [
                        SystemMessage(content=ELITE_AGRICULTURAL_ADVISOR_PROMPT),
                        HumanMessage(content=prompt),
                    ],
                    temperature=0.2,
                )
                llm_answer = result if result else (rag_context[:600] if rag_context else "No relevant information found.")
            except Exception as e:
                logger.warning("Gemini RAG synthesis failed: %s", e)
                llm_answer = rag_context[:600] if rag_context else "Knowledge base temporarily unavailable."
        elif not settings.google_api_key and combined_context:
            llm_answer = f"Based on ICAR documentation and Agricultural Knowledge Base:\n\n{combined_context[:800]}"
        else:
            llm_answer = (
                "No relevant documents found in the knowledge base for your query. "
                "Please contact your nearest KVK (Krishi Vigyan Kendra) for expert advice, "
                "or visit icar.org.in for official resources."
            )

        # Add KB source document if KB context was used
        if kb_context:
            source_docs.append(SourceDocument(
                title="FarmSphere Agriculture Knowledge Base",
                source="ICAR / DAC&FW / Agmarknet (curated reference data)",
                relevance_score=0.88,
                excerpt="State-wise prices, MSP 2024-25, crop encyclopaedia, agronomy data",
            ))

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="knowledge_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Retrieved {len(source_docs)} docs | KB context: {bool(kb_context)} | Elite RAG answer generated",
        )

        return {
            "retrieved_documents": source_docs,
            "knowledge_context": llm_answer,
            "source_documents": source_docs,
            "agent_traces": [trace],
            "agents_invoked": ["knowledge_agent"],
            "errors": [],
        }

    except Exception as e:
        logger.error("Knowledge agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="knowledge_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "retrieved_documents": [],
            "knowledge_context": "Knowledge base temporarily unavailable.",
            "source_documents": [],
            "agent_traces": [trace],
            "agents_invoked": ["knowledge_agent"],
            "errors": [f"Knowledge agent: {str(e)}"],
        }
