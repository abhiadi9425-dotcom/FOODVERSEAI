import os
import logging
from typing import Dict, Any
from app.core.config import settings
from app.services.ai.base import BaseAIProvider
from app.services.ai.groq_provider import GroqProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.rule_based_fallback import RuleBasedFallbackProvider

logger = logging.getLogger(__name__)


def get_ai_provider() -> BaseAIProvider:
    """
    Selects the active AI provider based on configuration and available API credentials.
    Priority:
    1. Groq if GROQ_API_KEY is provided
    2. Gemini if GEMINI_API_KEY is provided
    3. OpenAI if OPENAI_API_KEY is provided
    4. Rule-based / manual fallback provider with clear notices
    """
    groq_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "").strip()
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "").strip()
    openai_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "").strip()

    if (settings.LLM_PROVIDER.lower() == "groq" or not settings.LLM_PROVIDER) and groq_key:
        try:
            return GroqProvider(api_key=groq_key)
        except Exception as e:
            logger.warning(f"Failed to initialize GroqProvider: {e}")

    if settings.LLM_PROVIDER.lower() == "gemini" and gemini_key:
        try:
            return GeminiProvider(api_key=gemini_key)
        except Exception as e:
            logger.warning(f"Failed to initialize GeminiProvider: {e}")

    if settings.LLM_PROVIDER.lower() == "openai" and openai_key:
        try:
            return OpenAIProvider(api_key=openai_key)
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIProvider: {e}")

    # Auto-detection if provider was default or unspecified
    if groq_key:
        try:
            return GroqProvider(api_key=groq_key)
        except Exception as e:
            logger.warning(f"Failed to initialize auto-detected GroqProvider: {e}")

    if gemini_key:
        try:
            return GeminiProvider(api_key=gemini_key)
        except Exception as e:
            logger.warning(f"Failed to initialize auto-detected GeminiProvider: {e}")

    if openai_key:
        try:
            return OpenAIProvider(api_key=openai_key)
        except Exception as e:
            logger.warning(f"Failed to initialize auto-detected OpenAIProvider: {e}")

    return RuleBasedFallbackProvider()


def get_provider_status() -> Dict[str, Any]:
    groq_key = bool(settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "").strip())
    gemini_key = bool(settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "").strip())
    openai_key = bool(settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "").strip())
    usda_key = bool(settings.USDA_API_KEY or os.environ.get("USDA_API_KEY", "").strip())
    
    active_provider = "fallback"
    if groq_key:
        active_provider = "groq"
    elif gemini_key:
        active_provider = "gemini"
    elif openai_key:
        active_provider = "openai"

    return {
        "active_provider": active_provider,
        "groq_configured": groq_key,
        "gemini_configured": gemini_key,
        "openai_configured": openai_key,
        "usda_live_configured": usda_key,
        "verified_reference_db": "Active (USDA FoodData Central & ICMR Food Composition Database)"
    }
