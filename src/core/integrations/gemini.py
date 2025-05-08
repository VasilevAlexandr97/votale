from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key

        if not self.api_key:
            raise ValueError("API key is required for GeminiClient.")

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def generate_text_raw(
        self,
        prompt: str,
        *,
        temperature: float = 1,
    ) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
        return response.text

    def generate_structured(
        self,
        prompt: str,
        response_model_cls: type[T],
        *,
        temperature: float = 1,
    ) -> T:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_model_cls,
                temperature=temperature,
            ),
        )
        return response.parsed
