from abc import ABC, abstractmethod

class ConfigService(ABC):

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id: str):
        pass

    @abstractmethod
    def create_or_update(self, data: dict):
        pass

    @abstractmethod
    def delete(self, id: str):
        pass
