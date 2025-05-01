from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, context: Dict[str, Any]) -> str:
        pass

