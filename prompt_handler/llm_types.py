from abc import ABC, abstractmethod
import api_keys
from google import genai

class LLMBase(ABC):
    @abstractmethod
    def answer(self, prompt) -> str:
        pass


class GeminiFlash2(LLMBase):
    def __init__(self):
        self.__client = genai.Client(api_key=api_keys.gemini)

    def answer(self, prompt) -> str:
        response = self.__client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text

