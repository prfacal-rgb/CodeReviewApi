import json
import logging
import re  # ← agregar
from typing import Union, cast

import anthropic
from anthropic.types import TextBlock
from openai import OpenAI
import openai as openai_lib

from core.config import settings, AIProvider
from core.exceptions import AIAuthenticationError, AIRateLimitError, AIUnavailableError
from features.explain.models import ExplainRequest, ExplainResponse
from features.explain.prompts import SYSTEM_PROMPT, build_prompt

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:  # ← función nueva, igual que en code_review
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


class ExplainService:
    def __init__(
        self, client: Union[anthropic.Anthropic, OpenAI], provider: AIProvider
    ):
        self.client = client
        self.provider = provider
        self.is_anthropic = provider == AIProvider.anthropic

    def _get_model(self, deep: bool) -> str:
        if self.is_anthropic:
            return settings.anthropic_model
        return settings.ollama_model_deep if deep else settings.ollama_model_fast

    def explain(self, request: ExplainRequest) -> ExplainResponse:
        model = self._get_model(request.deep)
        logger.info(f"Explain | provider={self.provider} | model={model}")
        prompt = build_prompt(
            request.suggestion, request.original_code, request.language
        )

        if self.is_anthropic:
            raw = self._call_anthropic(prompt, model)
        else:
            raw = self._call_ollama(prompt, model)

        logger.debug(f"Raw explain response:\n{raw}")  # ← útil para debug
        data = json.loads(_extract_json(raw))  # ← antes era json.loads(raw.strip())
        return ExplainResponse(**data)

    def _call_anthropic(self, prompt: str, model: str) -> str:
        client = cast(anthropic.Anthropic, self.client)
        try:
            message = client.messages.create(
                model=model,
                max_tokens=settings.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text_block = next(b for b in message.content if isinstance(b, TextBlock))
            return text_block.text
        except anthropic.AuthenticationError:
            raise AIAuthenticationError("Invalid Anthropic API key")
        except anthropic.RateLimitError:
            raise AIRateLimitError("Anthropic rate limit exceeded")
        except anthropic.APIConnectionError:
            raise AIUnavailableError("Cannot connect to Anthropic API")

    def _call_ollama(self, prompt: str, model: str) -> str:
        client = cast(OpenAI, self.client)
        try:
            completion = client.chat.completions.create(
                model=model,
                max_tokens=settings.max_tokens,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            return completion.choices[0].message.content or ""
        except openai_lib.AuthenticationError:
            raise AIAuthenticationError("Invalid API key")
        except openai_lib.RateLimitError:
            raise AIRateLimitError("Rate limit exceeded")
        except openai_lib.APIConnectionError:
            raise AIUnavailableError(
                f"Cannot connect to Ollama at {settings.ollama_base_url}"
            )
