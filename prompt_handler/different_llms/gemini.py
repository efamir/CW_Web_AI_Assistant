from prompt_handler.api_keys import gemini as gemini_key
from google import genai
from prompt_handler.different_llms.base import LLMBase


class GeminiFlash2(LLMBase):
    def __init__(self):
        self.__client = genai.Client(api_key=gemini_key)

    def answer(self, prompt) -> str:
        response = self.__client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
