"""
FarmSphere AI — LLM Helper
Provides a Gemini LLM with automatic fallback from gemini-2.0-flash
to gemini-1.5-flash when quota (429) is hit.
"""
import logging
import time

logger = logging.getLogger(__name__)

# Models to try in order
FALLBACK_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]


def get_llm(temperature: float = 0.3):
    """Return a ChatGoogleGenerativeAI instance using the first available model."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from config import settings

    if not settings.google_api_key:
        return None

    for model in FALLBACK_MODELS:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=settings.google_api_key,
                temperature=temperature,
            )
            return llm
        except Exception as e:
            logger.warning("Could not init model %s: %s", model, e)

    return None


def invoke_with_fallback(messages: list, temperature: float = 0.3) -> str | None:
    """
    Invoke Gemini with automatic fallback across available models.
    Returns the response text, or None if all models fail.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from config import settings

    if not settings.google_api_key:
        return None

    for model in FALLBACK_MODELS:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=settings.google_api_key,
                temperature=temperature,
                request_timeout=30,
            )
            response = llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                logger.warning("Quota hit on %s, trying next model...", model)
                time.sleep(1)
                continue
            else:
                logger.error("LLM error on model %s: %s", model, e)
                return None

    logger.error("All Gemini models quota exhausted.")
    return None
