from backend.database.connection import SessionLocal
from backend.database.repository import llm_api_repo
from backend.services.config_service_base import ConfigService

class LLMConfigService(ConfigService):

    def create_or_update(self, data: dict):
        db = SessionLocal()
        existing = None

        if data.get("id"):
            existing = llm_api_repo.get_llm_api(db, data.get("id"))
        if not existing and data.get("name"):
            existing = llm_api_repo.get_llm_api_by_name(db, data["name"])

        if existing:
            updated = llm_api_repo.update_llm_api(db, existing.id, data)
        else:
            updated = llm_api_repo.create_llm_api(db, data)

        db.close()
        return updated


    def get_all(self):
        db = SessionLocal()
        result = llm_api_repo.get_all_llm_apis(db)
        db.close()
        return result

    def get_by_id(self, api_id: str):
        db = SessionLocal()
        result = llm_api_repo.get_llm_api(db, api_id)
        db.close()
        return result

    def delete(self, api_id: str):
        db = SessionLocal()
        result = llm_api_repo.delete_llm_api(db, api_id)
        db.close()
        return result

