import json
import logging
import re
from typing import Generator, Union, cast

import anthropic
import openai
from anthropic.types import TextBlock
from openai import OpenAI

from core.config import settings, AIProvider
from core.exceptions import AIAuthenticationError, AIRateLimitError, AIUnavailableError
from features.code_review.models import (
    ReviewRequest,
    ReviewResponse,
    ImageReviewRequest,
)
from features.code_review.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Limpia markdown fences si el modelo envuelve el JSON en ```json ... ```"""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        logger.debug("JSON wrapped in markdown fences — stripping")
        return match.group(1)
    return text.strip()


class CodeReviewService:
    def __init__(
        self, client: Union[anthropic.Anthropic, OpenAI], provider: AIProvider
    ):  # ← provider explícito
        self.client = client
        self.provider = provider
        self.is_anthropic = provider == AIProvider.anthropic  # ← sin isinstance

    def _get_model(self, deep: bool) -> str:
        if self.is_anthropic:
            return settings.anthropic_model
        return settings.ollama_model_deep if deep else settings.ollama_model_fast

    # ── Review normal ────────────────────────────────────────────────

    def review(self, request: ReviewRequest) -> ReviewResponse:
        model = self._get_model(request.deep)
        logger.info(
            f"Review | provider={self.provider} | model={model} | deep={request.deep}"
        )
        raw = (
            self._call_anthropic(request, model)
            if self.is_anthropic
            else self._call_ollama(request, model)
        )
        logger.debug(f"Raw response:\n{raw}")
        data = json.loads(_extract_json(raw))
        return ReviewResponse(**data)

    def _call_anthropic(self, request: ReviewRequest, model: str) -> str:
        client = cast(anthropic.Anthropic, self.client)  # ← cast
        try:
            message = client.messages.create(
                model=model,
                max_tokens=settings.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": build_user_prompt(
                            request.code, request.language, request.context
                        ),
                    }
                ],
            )
            text_block = next(b for b in message.content if isinstance(b, TextBlock))
            return text_block.text
        except anthropic.AuthenticationError:
            raise AIAuthenticationError(
                "Invalid Anthropic API key — check ANTHROPIC_API_KEY in .env"
            )
        except anthropic.RateLimitError:
            raise AIRateLimitError("Anthropic rate limit exceeded — try again later")
        except anthropic.APIConnectionError:
            raise AIUnavailableError("Cannot connect to Anthropic API")

    def _call_ollama(self, request: ReviewRequest, model: str) -> str:
        client = cast(OpenAI, self.client)  # ← cast
        try:
            completion = client.chat.completions.create(
                model=model,
                max_tokens=settings.max_tokens,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_user_prompt(
                            request.code, request.language, request.context
                        ),
                    },
                ],
            )
            return completion.choices[0].message.content or ""
        except openai.AuthenticationError:
            raise AIAuthenticationError("Invalid API key")
        except openai.RateLimitError:
            raise AIRateLimitError("Rate limit exceeded")
        except openai.APIConnectionError:
            raise AIUnavailableError(
                f"Cannot connect to Ollama at {settings.ollama_base_url}"
                " — is it running?"
            )

    # ── Review from Image ──────────────────────────────────────────────
    def review_from_image(self, request: ImageReviewRequest) -> ReviewResponse:
        if not self.is_anthropic:
            raise AIUnavailableError(
                "Image review requires a vision model. Switch AI_PROVIDER=anthropic or"
                "install llava in Ollama."
            )
        model = self._get_model(request.deep)
        logger.info(f"Image review | model={model}")
        client = cast(anthropic.Anthropic, self.client)
        try:
            message = client.messages.create(
                model=model,
                max_tokens=settings.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[  # type: ignore[arg-type]
                    {
                        "role": "user",
                        "content": [
                            {  # type: ignore[arg-type]
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": request.mime_type,
                                    "data": request.image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Extract the code from this image and review"
                                " it. Respond with the JSON structure specified.",
                            },
                        ],
                    }
                ],
            )
            text_block = next(b for b in message.content if isinstance(b, TextBlock))
            data = json.loads(_extract_json(text_block.text))
            return ReviewResponse(**data)
        except anthropic.AuthenticationError:
            raise AIAuthenticationError("Invalid Anthropic API key")
        except anthropic.APIConnectionError:
            raise AIUnavailableError("Cannot connect to Anthropic API")

    # ── Streaming ────────────────────────────────────────────────────

    def review_stream(self, request: ReviewRequest) -> Generator[str, None, None]:
        model = self._get_model(request.deep)
        logger.info(f"Stream | model={model} | deep={request.deep}")
        if self.is_anthropic:
            yield from self._stream_anthropic(request, model)
        else:
            yield from self._stream_ollama(request, model)

    def _stream_anthropic(
        self, request: ReviewRequest, model: str
    ) -> Generator[str, None, None]:
        client = cast(anthropic.Anthropic, self.client)  # ← cast
        try:
            with client.messages.stream(
                model=model,
                max_tokens=settings.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": build_user_prompt(
                            request.code, request.language, request.context
                        ),
                    }
                ],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except anthropic.AuthenticationError:
            raise AIAuthenticationError("Invalid Anthropic API key")
        except anthropic.RateLimitError:
            raise AIRateLimitError("Anthropic rate limit exceeded")
        except anthropic.APIConnectionError:
            raise AIUnavailableError("Cannot connect to Anthropic API")

    def _stream_ollama(
        self, request: ReviewRequest, model: str
    ) -> Generator[str, None, None]:
        client = cast(OpenAI, self.client)  # ← cast
        try:
            stream = client.chat.completions.create(
                model=model,
                max_tokens=settings.max_tokens,
                stream=True,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_user_prompt(
                            request.code, request.language, request.context
                        ),
                    },
                ],
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except openai.AuthenticationError:
            raise AIAuthenticationError("Invalid API key")
        except openai.RateLimitError:
            raise AIRateLimitError("Rate limit exceeded")
        except openai.APIConnectionError:
            raise AIUnavailableError(
                f"Cannot connect to Ollama at {settings.ollama_base_url}"
            )
