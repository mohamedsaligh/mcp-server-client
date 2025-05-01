from abc import ABC, abstractmethod

class LLMRefiner(ABC):
    @abstractmethod
    def refine(self, prompt: str, context: dict) -> str:
        pass

    @abstractmethod
    def post_process(self, output: str, context: dict) -> str:
        pass
