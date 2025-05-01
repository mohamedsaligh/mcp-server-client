from abc import ABC, abstractmethod
from typing import Any, Dict


class MCPExecutor(ABC):

    @abstractmethod
    async def execute(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
