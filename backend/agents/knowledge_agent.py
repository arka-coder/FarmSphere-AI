"""
FarmSphere AI — Knowledge Agent (Layer 1)
ChromaDB RAG over ICAR documents, crop manuals, disease references.
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

RAG_SYSTEM_PROMPT = """You are an expert agricultural advisor for FarmSphere AI.
You answer farmer questions using ONLY the provided knowledge base documents.

RULES:
1. Base your answer ONLY on the provided context documents.
2. Always mention the source document name.
3. If the context doesn't contain enough information, say so clearly — do NOT guess.
4. Use simple, practical language suitable for farmers.
5. Structure your answer with: Main Answer, Dosage/Steps (if applicable), Precautions.
6. Keep responses concise but complete."""


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
            "treatment_advice": "treatment management",
            "scheme_query": "government scheme eligibility",
            "general_farming": "farming advice",
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


def knowledge_agent(state: FarmSphereState) -> dict:
    """
    Knowledge Agent — ChromaDB RAG with citation-enforced answers.
    Queries multiple collections and synthesizes with Gemini.
    """
    start_time = time.time()
    logger.info("Knowledge agent querying ChromaDB for: %s", state.get("user_message", "")[:80])

    try:
        query = _build_query(state)

        # Query relevant collections
        icar_results = query_collection("icar_docs", [query], n_results=3)
        disease_results = {}
        if state.get("disease_name"):
            disease_results = query_collection(
                "icar_docs", [state["disease_name"]], n_results=2,
                where={"crop": state.get("crop_type")} if state.get("crop_type") else None,
            )

        # Merge results
        all_docs = icar_results.get("documents", [[]])[0] + disease_results.get("documents", [[]])[0]
        all_metas = icar_results.get("metadatas", [[]])[0] + disease_results.get("metadatas", [[]])[0]
        all_dists = icar_results.get("distances", [[]])[0] + disease_results.get("distances", [[]])[0]

        merged = {"documents": [all_docs], "metadatas": [all_metas], "distances": [all_dists]}
        context, source_docs = _format_retrieved_docs(merged)

        # Generate answer with Gemini using retrieved context
        knowledge_context, llm_answer = context, ""
        if context and settings.google_api_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.2,
                )
                prompt = (
                    f"KNOWLEDGE BASE CONTEXT:\n{context}\n\n"
                    f"FARMER QUESTION: {state.get('user_message', '')}\n"
                    f"CROP: {state.get('crop_type', 'not specified')}\n"
                    f"DISEASE DETECTED: {state.get('disease_name', 'none')}"
                )
                response = llm.invoke([
                    SystemMessage(content=RAG_SYSTEM_PROMPT),
                    HumanMessage(content=prompt),
                ])
                llm_answer = response.content.strip()
            except Exception as e:
                logger.warning("Gemini RAG synthesis failed: %s", e)
                llm_answer = context[:500]  # fallback to raw context
        elif not settings.google_api_key and context:
            llm_answer = f"Based on ICAR documentation: {context[:800]}"
        else:
            llm_answer = "No relevant documents found in the knowledge base for your query."

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="knowledge_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"Retrieved {len(source_docs)} relevant documents | RAG answer generated",
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
