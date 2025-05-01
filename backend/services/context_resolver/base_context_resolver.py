from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class ContextResolver(ABC):
    @abstractmethod
    def resolve(self, db: Session, prompt: str):
        pass
