from backend.database.connection import SessionLocal
from backend.database.repository import prompt_context_repo
from backend.services.config_service_base import ConfigService



class PromptConfigService(ConfigService):

    def get_all(self):
        db = SessionLocal()
        result = prompt_context_repo.get_all_prompt_contexts(db)
        db.close()
        return result

    def get_by_id(self, context_id: str):
        db = SessionLocal()
        result = prompt_context_repo.get_prompt_context(db, context_id)
        db.close()
        return result

    def create_or_update(self, data: dict):
        db = SessionLocal()
        existing = None

        if data.get("id"):
            existing = prompt_context_repo.get_prompt_context(db, data["id"])
        if not existing and data.get("name"):
            existing = prompt_context_repo.get_prompt_context_by_name(db, data["name"])

        if existing:
            updated = prompt_context_repo.update_prompt_context(db, existing.id, data)
        else:
            updated = prompt_context_repo.create_prompt_context(db, data)

        db.close()
        return updated

    def delete(self, context_id: str):
        db = SessionLocal()
        result = prompt_context_repo.delete_prompt_context(db, context_id)
        db.close()
        return result
