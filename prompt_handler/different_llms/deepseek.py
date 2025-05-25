import ollama
from ollama import GenerateResponse
from prompt_handler.different_llms.base import LLMBase


class LocalDeepseek(LLMBase):
    def answer(self, prompt) -> str:
        response: GenerateResponse = ollama.generate(
            model="deepseek-r1:8b", contents=prompt
        )
        return response.response
