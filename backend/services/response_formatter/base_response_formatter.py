from abc import ABC, abstractmethod

class ResponseFormatter(ABC):
    @abstractmethod
    def format(self, raw_response: str, context: dict) -> str:
        pass
