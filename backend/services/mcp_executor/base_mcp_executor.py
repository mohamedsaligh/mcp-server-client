from abc import ABC, abstractmethod
from typing import Any

class MCPExecutor(ABC):
    @abstractmethod
    def execute(self, endpoint: str, payload: dict) -> Any:
        pass
