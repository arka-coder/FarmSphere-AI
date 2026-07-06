"""
FarmSphere AI — Disease Detection Agent (Layer 1)
Uses Gemini Vision for multimodal plant disease diagnosis.
Activates Human-in-the-Loop if confidence < 75%.
"""
import time
import logging
import base64
import json
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import FarmSphereState, AgentTrace, SourceDocument
from config import settings

logger = logging.getLogger(__name__)

DISEASE_SYSTEM_PROMPT = """You are an expert plant pathologist AI assistant for FarmSphere AI.
Analyze the provided plant image and return a JSON diagnosis.

IMPORTANT RULES:
1. Never claim 100% certainty. Always express confidence as a probability.
2. If image quality is poor or the disease is unclear, reflect this in a lower confidence score.
3. Always provide exactly 3 alternative diagnoses (besides the primary).
4. Be specific about symptoms you observe in the image.

Return ONLY valid JSON in this exact format:
{
  "disease_name": "Primary disease name (or 'Healthy Plant' if no disease detected)",
  "confidence": 0.XX,
  "severity": "mild|moderate|severe|none",
  "symptoms_observed": ["symptom 1", "symptom 2", "symptom 3"],
  "crop_identified": "crop type (tomato/wheat/rice/unknown)",
  "alternatives": [
    {"name": "Alternative disease 1", "confidence": 0.XX},
    {"name": "Alternative disease 2", "confidence": 0.XX},
    {"name": "Alternative disease 3", "confidence": 0.XX}
  ],
  "reasoning": "Brief explanation of visual evidence that led to this diagnosis",
  "image_quality": "good|fair|poor"
}"""

DISEASE_TEXT_PROMPT = """You are an expert plant pathologist AI assistant for FarmSphere AI.
The farmer has described symptoms without providing an image. Analyze the description and return a JSON diagnosis.

IMPORTANT: Be more conservative with confidence scores when no image is provided (max 0.80).

Return ONLY valid JSON in this exact format:
{
  "disease_name": "Most likely disease name",
  "confidence": 0.XX,
  "severity": "mild|moderate|severe|unknown",
  "symptoms_observed": ["symptom from description 1", "symptom 2"],
  "crop_identified": "crop type",
  "alternatives": [
    {"name": "Alternative 1", "confidence": 0.XX},
    {"name": "Alternative 2", "confidence": 0.XX},
    {"name": "Alternative 3", "confidence": 0.XX}
  ],
  "reasoning": "Reasoning based on described symptoms",
  "image_quality": "none"
}"""

MOCK_DISEASE_RESPONSE = {
    "disease_name": "Early Blight (Alternaria solani)",
    "confidence": 0.87,
    "severity": "moderate",
    "symptoms_observed": [
        "Dark brown circular spots with yellow halos on lower leaves",
        "Target-board concentric ring pattern in lesions",
        "Progressive yellowing around infected areas",
    ],
    "crop_identified": "tomato",
    "alternatives": [
        {"name": "Septoria Leaf Spot", "confidence": 0.06},
        {"name": "Late Blight (Phytophthora infestans)", "confidence": 0.04},
        {"name": "Nutrient Deficiency (Magnesium)", "confidence": 0.03},
    ],
    "reasoning": "The concentric ring pattern and target-board appearance of lesions on lower leaves "
                 "is highly characteristic of Alternaria solani. The brown color without water-soaked "
                 "margins rules out Late Blight.",
    "image_quality": "good",
}


def _parse_disease_json(raw_response: str) -> dict:
    """Parse JSON from Gemini response, handling markdown code blocks."""
    text = raw_response.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)


def disease_agent(state: FarmSphereState) -> dict:
    """
    Disease Detection Agent — Multimodal diagnosis using Gemini Vision.
    Triggers HITL workflow if confidence < threshold.
    """
    start_time = time.time()
    logger.info("Disease agent activated for crop: %s", state.get("crop_type", "unknown"))

    diagnosis = {}
    used_mock = False

    try:
        image_b64 = state.get("image_base64")
        user_message = state.get("user_message", "")

        if not settings.google_api_key:
            logger.warning("No Google API key — using mock disease response")
            diagnosis = MOCK_DISEASE_RESPONSE
            used_mock = True
        elif image_b64:
            # Multimodal: use Gemini Vision (gemini-2.0-flash supports vision)
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                    max_retries=0,
                )
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": DISEASE_SYSTEM_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{image_b64}",
                        },
                    ]
                )
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(llm.invoke, [message])
                    response = future.result(timeout=30)
                diagnosis = _parse_disease_json(response.content)
            except Exception as e:
                logger.warning("Vision model failed: %s — using mock", e)
                diagnosis = MOCK_DISEASE_RESPONSE
                used_mock = True
        else:
            # Text-only: describe symptoms via invoke_with_fallback
            try:
                from agents.llm_helper import invoke_with_fallback
                raw = invoke_with_fallback([
                    SystemMessage(content=DISEASE_TEXT_PROMPT),
                    HumanMessage(content=f"Farmer says: {user_message}\nCrop: {state.get('crop_type', 'unknown')}"),
                ], temperature=0.1)
                diagnosis = _parse_disease_json(raw or "{}")
            except Exception as e:
                logger.warning("Disease text analysis failed: %s", e)
                diagnosis = MOCK_DISEASE_RESPONSE
                used_mock = True

        confidence = float(diagnosis.get("confidence", 0.5))
        hitl_required = (
            confidence < settings.disease_confidence_threshold
            and settings.hitl_enabled
        )

        source_doc = SourceDocument(
            title="Gemini Vision Plant Pathology Model",
            source="Google Gemini Vision API",
            relevance_score=confidence,
            excerpt=diagnosis.get("reasoning", ""),
        )

        if used_mock:
            source_doc["source"] = "FarmSphere Demo Mode (Mock)"

        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="disease_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="success",
            output_summary=f"{diagnosis.get('disease_name')} | conf={confidence:.0%} | hitl={hitl_required}",
        )

        return {
            "disease_name": diagnosis.get("disease_name"),
            "disease_confidence": confidence,
            "disease_symptoms": diagnosis.get("symptoms_observed", []),
            "disease_severity": diagnosis.get("severity"),
            "disease_alternatives": diagnosis.get("alternatives", []),
            "hitl_required": hitl_required,
            "crop_type": diagnosis.get("crop_identified") or state.get("crop_type"),
            "agent_traces": [trace],
            "agents_invoked": ["disease_agent"],
            "source_documents": [source_doc],
            "errors": [],
        }

    except Exception as e:
        logger.error("Disease agent error: %s", e)
        duration_ms = (time.time() - start_time) * 1000
        trace = AgentTrace(
            agent_name="disease_agent",
            started_at=start_time,
            ended_at=time.time(),
            duration_ms=round(duration_ms, 2),
            status="error",
            output_summary=str(e),
        )
        return {
            "disease_name": "Unable to diagnose",
            "disease_confidence": 0.0,
            "disease_symptoms": [],
            "disease_severity": "unknown",
            "disease_alternatives": [],
            "hitl_required": True,
            "agent_traces": [trace],
            "agents_invoked": ["disease_agent"],
            "source_documents": [],
            "errors": [f"Disease agent: {str(e)}"],
        }


def route_after_disease(state: FarmSphereState) -> str:
    """
    Conditional edge after disease detection.
    Always flows to knowledge agent for treatment context,
    regardless of HITL status.
    """
    return "knowledge_agent"
