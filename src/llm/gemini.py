import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .base import BaseModel

load_dotenv()


class GeminiModel(BaseModel):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate(self, prompt: str) -> str:
        response: types.GenerateContentResponse = self.client.models.generate_content(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction="Bạn là chuyên gia pháp luật."
            ),
            contents=prompt,
        )

        if not response.candidates or not response.candidates[0].content:
            raise ValueError(
                "Invalid response structure: Missing candidates or content"
            )
        content = response.candidates[0].content

        if (
            not hasattr(content, "parts")
            or not content.parts
            or not hasattr(content.parts[0], "text")
            or not content.parts[0].text
        ):
            raise ValueError(
                "Invalid response structure: Missing content, parts, or text"
            )
        return content.parts[0].text
