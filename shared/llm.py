"""Shared LLM client for Google Gemini.

Used by summary_service and prompt_service. Also exposes a mock mode
so the pipeline can be exercised end-to-end without an API key.
"""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any

from shared.config import get_settings

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Result type
# -----------------------------------------------------------------------------

@dataclass
class LLMResult:
    """Result of an LLM call."""
    text: str
    model: str
    latency_ms: int
    mocked: bool = False


# -----------------------------------------------------------------------------
# Client
# -----------------------------------------------------------------------------

class GeminiClient:
    """Thin wrapper around Google's Gemini API.

    Features:
    - Retries on transient failures.
    - Mock mode when no API key is available.
    - JSON mode for structured outputs.
    """

    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 20.0

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key if api_key is not None else settings.gemini_api_key
        self._model_name = model or settings.gemini_model
        self._mock = not bool(self._api_key)
        self._client: Any = None

        if self._mock:
            logger.warning(
                "GeminiClient running in MOCK mode (no API key). "
                "Responses will be placeholders."
            )
        else:
            self._ensure_client()

    # -- public API ----------------------------------------------------------

    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.4,
    ) -> LLMResult:
        """Generate text from a prompt."""
        if self._mock:
            return self._mock_generate(prompt)

        return self._call(
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=False,
        )

    def generate_json(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> tuple[dict[str, Any], LLMResult]:
        """Generate text and parse it as JSON.

        Returns (parsed_dict, LLMResult). If JSON parsing fails, raises ValueError.
        """
        if self._mock:
            result = self._mock_generate(prompt, json_mode=True)
            return {"_mock": True, "prompt": prompt[:200]}, result

        result = self._call(
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )
        parsed = _extract_json(result.text)
        if parsed is None:
            logger.error("failed to parse JSON from LLM output: %r", result.text[:200])
            raise ValueError("LLM did not return valid JSON")
        return parsed, result

    # -- internals -----------------------------------------------------------

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        try:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(self._model_name)
            logger.info("Gemini client initialized: model=%s", self._model_name)
        except Exception:
            logger.exception("failed to initialize Gemini client")
            self._mock = True

    def _call(
        self,
        prompt: str,
        system: str | None,
        max_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> LLMResult:
        full_prompt = prompt if not system else f"{system}\n\n{prompt}"

        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            start = time.perf_counter()
            try:
                response = self._client.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )
                latency_ms = int((time.perf_counter() - start) * 1000)
                text = _response_text(response)
                logger.info(
                    "gemini call ok: model=%s latency=%dms chars=%d",
                    self._model_name,
                    latency_ms,
                    len(text),
                )
                return LLMResult(
                    text=text,
                    model=self._model_name,
                    latency_ms=latency_ms,
                    mocked=False,
                )
            except Exception as e:
                last_error = e
                logger.warning(
                    "gemini call failed (attempt %d/%d): %s",
                    attempt,
                    self.MAX_RETRIES,
                    str(e)[:200],
                )
                if attempt < self.MAX_RETRIES:
                    # If rate-limited, wait longer
                    delay = self.RETRY_DELAY_SECONDS
                    if "429" in str(e) or "quota" in str(e).lower():
                        delay = 30.0
                    time.sleep(delay)
        logger.error("gemini call exhausted retries: %s", last_error)
        raise RuntimeError(f"Gemini call failed after {self.MAX_RETRIES} attempts") from last_error

    def _mock_generate(self, prompt: str, json_mode: bool = False) -> LLMResult:
        start = time.perf_counter()
        time.sleep(0.05)  # simulate latency
        latency_ms = int((time.perf_counter() - start) * 1000)

        if json_mode:
            text = json.dumps({"mock": True, "note": "No API key configured."})
        else:
            text = (
                "[MOCK LLM] No GEMINI_API_KEY configured. "
                f"Received prompt of {len(prompt)} chars. "
                "Set GEMINI_API_KEY in .env to enable real responses."
            )
        return LLMResult(
            text=text,
            model="mock",
            latency_ms=latency_ms,
            mocked=True,
        )


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _response_text(response: Any) -> str:
    """Extract text from a Gemini response, defensively."""
    try:
        if hasattr(response, "text"):
            return response.text or ""
    except Exception:
        pass
    try:
        parts = response.candidates[0].content.parts
        return "".join(getattr(p, "text", "") for p in parts)
    except Exception:
        return ""


def _extract_json(text: str) -> dict[str, Any] | None:
    """Extract a JSON object from a possibly-fenced or truncated LLM response."""
    if not text or not text.strip():
        return None

    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try stripping ```json fences
    m = _JSON_FENCE_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding the outermost {...} and parse
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Truncated JSON — try to close it
    if start != -1:
        candidate = text[start:]
        # Count unclosed braces/brackets
        opens = candidate.count("{") - candidate.count("}")
        brackets = candidate.count("[") - candidate.count("]")

        # If it ends mid-string, close the string
        if candidate.count('"') % 2 == 1:
            candidate += '"'

        # Close unclosed brackets and braces in reverse order
        candidate += "]" * brackets
        candidate += "}" * opens

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None


# -----------------------------------------------------------------------------
# Convenience
# -----------------------------------------------------------------------------

_client_singleton: GeminiClient | None = None


def get_llm() -> GeminiClient:
    """Return a shared GeminiClient instance."""
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = GeminiClient()
    return _client_singleton
