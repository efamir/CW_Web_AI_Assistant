from abc import ABC, abstractmethod

class LLMBase(ABC):
    @abstractmethod
    def answer(self, prompt) -> str:
        pass
