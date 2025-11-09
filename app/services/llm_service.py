"""
LLM Service with error resilience and retry logic
Demonstrates proper error handling for external service calls
"""
import json
from typing import Dict, Any, Optional
from functools import lru_cache
from openai import AsyncAzureOpenAI
from openai import (
    RateLimitError,
    APIConnectionError,
    AuthenticationError,
    APIError
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.core.config import get_settings
from app.core.exceptions import LLMGenerationError, LLMValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    Azure OpenAI service with error resilience

    Features:
    - Automatic retry on transient failures
    - Exponential backoff for rate limits
    - Proper error categorization
    - Timeout handling
    """

    def __init__(self, client: Optional[AsyncAzureOpenAI] = None):
        """
        Initialize LLM service

        Args:
            client: Optional Async Azure OpenAI client (for testing/DI)
        """
        self.settings = get_settings()

        if client is None:
            self.client = AsyncAzureOpenAI(
                api_key=self.settings.AZURE_OPENAI_API_KEY,
                api_version=self.settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT
            )
        else:
            self.client = client

    @retry(
        # Only retry transient errors
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        # Maximum 3 attempts
        stop=stop_after_attempt(3),
        # Exponential backoff: 2s, 4s, 8s
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def generate_completion(
        self,
        messages: list,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion with automatic retry

        Args:
            messages: OpenAI messages format
            temperature: Sampling temperature (defaults to config)
            max_tokens: Max tokens to generate (defaults to config)

        Returns:
            Generated text content

        Raises:
            LLMGenerationError: On permanent failures
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=temperature or self.settings.LLM_TEMPERATURE,
                max_tokens=max_tokens or self.settings.LLM_MAX_TOKENS,
                timeout=self.settings.LLM_REQUEST_TIMEOUT
            )

            content = response.choices[0].message.content

            if not content or len(content) < 5:
                logger.warning("LLM returned empty/very short response")
                raise LLMValidationError("LLM response too short or empty")

            return content

        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded, retrying... {e}")
            raise  # Re-raise to trigger retry

        except APIConnectionError as e:
            logger.warning(f"Network error, retrying... {e}")
            raise  # Re-raise to trigger retry

        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise LLMGenerationError(
                "Configuration error: Invalid API credentials"
            ) from e

        except APIError as e:
            logger.error(f"API error: {e}")
            raise LLMGenerationError(f"LLM API error: {str(e)}") from e

        except Exception as e:
            logger.exception(f"Unexpected error in LLM service: {e}")
            raise LLMGenerationError(
                "An unexpected error occurred with the LLM service"
            ) from e

    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse and validate JSON response from LLM

        Args:
            content: Raw LLM response

        Returns:
            Parsed JSON dictionary

        Raises:
            LLMValidationError: If parsing fails
        """
        try:
            # Strip markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            elif content.startswith("```"):
                content = content[3:]  # Remove ```

            if content.endswith("```"):
                content = content[:-3]  # Remove closing ```

            content = content.strip()

            data = json.loads(content)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {content[:200]}")
            raise LLMValidationError(
                f"LLM did not return valid JSON: {str(e)}"
            ) from e


@lru_cache()
def get_llm_service() -> LLMService:
    """
    Get cached LLM service instance (singleton)

    Returns:
        LLMService instance
    """
    return LLMService()
