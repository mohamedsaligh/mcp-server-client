import json

from backend.database.connection import SessionLocal
from backend.database.repository import mcp_server_repo
from backend.services.config_service_base import ConfigService

class MCPConfigService(ConfigService):

    def get_all(self):
        db = SessionLocal()
        result = mcp_server_repo.get_all_mcp_servers(db)
        db.close()
        return result

    def get_by_id(self, mcp_id: str):
        db = SessionLocal()
        result = mcp_server_repo.get_mcp_server(db, mcp_id)
        db.close()
        return result

    def create_or_update(self, data: dict):
        db = SessionLocal()
        existing = None

        if isinstance(data.get("manifest"), dict):
            data["manifest"] = json.dumps(data["manifest"])

        if data.get("id"):
            existing = mcp_server_repo.get_mcp_server(db, data["id"])
        if not existing and data.get("name"):
            existing = mcp_server_repo.get_mcp_server_by_name(db, data["name"])

        if existing:
            updated = mcp_server_repo.update_mcp_server(db, existing.id, data)
        else:
            updated = mcp_server_repo.create_mcp_server(db, data)

        db.close()
        return updated


    def delete(self, mcp_id: str):
        db = SessionLocal()
        result = mcp_server_repo.delete_mcp_server(db, mcp_id)
        db.close()
        return result
