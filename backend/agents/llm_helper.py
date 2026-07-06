"""
FarmSphere AI — LLM Helper
Provides a Gemini LLM with automatic fallback and enforced timeouts.
Uses a module-level ThreadPoolExecutor to avoid spawn overhead on every call.
Upgraded: Extended timeout (25s) + thinking-mode support for deep reasoning.
"""
import logging
import concurrent.futures

logger = logging.getLogger(__name__)

# Models to try in order — fastest first
FALLBACK_MODELS = [
    "gemini-2.5-flash",      # fastest, lowest latency; supports thinking mode
    "gemini-2.0-flash",      # solid fallback
    "gemini-2.0-flash-lite", # lightweight last resort
]

# Hard timeout per LLM call in seconds
# Increased to 25s to allow extended reasoning for deep agronomy / plant science queries
LLM_TIMEOUT = 25

# Shared executor — avoids spawning/tearing down threads on every call
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="llm_worker")


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
                max_retries=0,
            )
            return llm
        except Exception as e:
            logger.warning("Could not init model %s: %s", model, e)

    return None


def _call_llm(model: str, messages: list, temperature: float, api_key: str) -> str:
    """Synchronous call to the LLM — runs in the shared thread pool."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        max_retries=0,
    )
    response = llm.invoke(messages)
    return response.content.strip()


def invoke_with_fallback(messages: list, temperature: float = 0.3) -> str | None:
    """
    Invoke Gemini with automatic fallback across available models.
    Uses the shared ThreadPoolExecutor with a hard timeout to prevent hanging.
    Returns the response text, or None if all models fail.
    """
    from config import settings

    if not settings.google_api_key:
        return None

    for model in FALLBACK_MODELS:
        try:
            future = _executor.submit(
                _call_llm, model, messages, temperature, settings.google_api_key
            )
            result = future.result(timeout=LLM_TIMEOUT)
            return result
        except concurrent.futures.TimeoutError:
            logger.warning("LLM call timed out after %ds on model %s", LLM_TIMEOUT, model)
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                logger.warning("Quota hit on %s, trying next model...", model)
            elif "404" in err or "not found" in err.lower():
                logger.warning("Model %s not found, trying next...", model)
            else:
                logger.warning("LLM error on model %s: %s", model, e)
            continue

    logger.error("All Gemini models failed or timed out.")
    return None


def invoke_with_thinking(messages: list, temperature: float = 0.3) -> str | None:
    """
    Invoke Gemini with extended reasoning for complex queries.
    Prefers gemini-2.5-flash which supports thinking mode for deeper analysis.
    Used for: plant science, disease diagnosis, market analysis, agronomy.
    Falls back to invoke_with_fallback if thinking model is unavailable.
    """
    from config import settings

    if not settings.google_api_key:
        return None

    # gemini-2.5-flash supports thinking — try it first with extended timeout
    thinking_model = "gemini-2.5-flash"
    try:
        future = _executor.submit(
            _call_llm, thinking_model, messages, temperature, settings.google_api_key
        )
        result = future.result(timeout=LLM_TIMEOUT)
        if result:
            logger.debug("Thinking model (%s) responded successfully.", thinking_model)
            return result
    except concurrent.futures.TimeoutError:
        logger.warning("Thinking model timed out after %ds — falling back", LLM_TIMEOUT)
    except Exception as e:
        logger.warning("Thinking model error: %s — falling back", e)

    # Fallback to standard invoke
    return invoke_with_fallback(messages, temperature)
