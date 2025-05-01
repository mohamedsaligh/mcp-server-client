from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.configuration.llm_config_service import LLMConfigService
from backend.services.configuration.mcp_config_service import MCPConfigService

# This is a FastAPI router that defines API endpoints for the application.
config = APIRouter()

class UserPromptRequest(BaseModel):
    prompt: str
    session_id: str


@config.get("/llms")
def list_llms():
    service = LLMConfigService()
    return [{"id": llm.id, "name": llm.name, "api_key": llm.api_key, "base_url": llm.base_url} for llm in service.get_all()]

@config.delete("/llms/{llm_id}")
def delete_llm(llm_id: str):
    service = LLMConfigService()
    result = service.delete(llm_id)
    return {"message": "Deleted."} if result else {"message": "Not found."}

@config.post("/llms")
def save_llm(data: dict):
    service = LLMConfigService()
    updated = service.create_or_update(data)
    return {"id": updated.id, "message": "LLM API saved."}


@config.get("/mcp_servers")
def list_mcp_servers():
    service = MCPConfigService()
    return [{
        "id": s.id,
        "name": s.name,
        "keywords": s.keywords,
        "endpoint_url": s.endpoint_url
    } for s in service.get_all()]

@config.post("/mcp_servers")
def save_mcp_server(data: dict):
    service = MCPConfigService()
    updated = service.create_or_update(data)
    return {"id": updated.id, "message": "MCP Server saved."}

@config.delete("/mcp_servers/{mcp_id}")
def delete_mcp_server(mcp_id: str):
    service = MCPConfigService()
    result = service.delete(mcp_id)
    return {"message": "Deleted."} if result else {"message": "Not found."}



