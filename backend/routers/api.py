import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from backend.database.init_db import get_db
from backend.services.chat_history_service import ChatHistoryService
from backend.services.configuration.llm_config_service import LLMConfigService
from backend.services.orchestrator_service import OrchestratorService
from backend.services.configuration.prompt_config_service import PromptConfigService

# This is a FastAPI router that defines API endpoints for the application.
router = APIRouter()

class UserPromptRequest(BaseModel):
    prompt: str
    session_id: str


@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/prompt/run")
def run_prompt(user_id: str, prompt: str, db: Session = Depends(get_db)):
    service = OrchestratorService()
    return service.run_user_prompt(user_id, prompt)


@router.post("/prompt/stream")
async def stream_prompt(request: UserPromptRequest):
    orchestrator = OrchestratorService()
    async def event_generator():
        yield f"event:status\ndata:Running full orchestration...\n\n"
        # Simulate async from sync
        import asyncio
        result = await asyncio.to_thread(
            orchestrator.run_user_prompt,
            user_id="user123",
            prompt_text=request.prompt
        )
        yield f"event:status\ndata:Completed orchestration\n\n"
        yield f"event:steps\ndata:{json.dumps(result['steps'])}\n\n"
        yield f"event:requests\ndata:{json.dumps(result['requests'])}\n\n"
        yield f"event:result\ndata:{json.dumps({'session_id': result['session_id'], 'final': result['final_response']})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/config/llms")
def list_llms():
    service = LLMConfigService()
    return [{"id": llm.id, "name": llm.name, "api_key": llm.api_key, "base_url": llm.base_url} for llm in service.get_all()]

@router.post("/config/llms")
def save_llm(data: dict):
    service = LLMConfigService()
    updated = service.create_or_update(data)
    return {"id": updated.id, "message": "LLM API saved."}

@router.delete("/config/llms/{llm_id}")
def delete_llm(llm_id: str):
    service = LLMConfigService()
    result = service.delete(llm_id)
    return {"message": "Deleted."} if result else {"message": "Not found."}

@router.post("/config/llms")
def save_llm(data: dict):
    service = LLMConfigService()
    updated = service.create_or_update(data)
    return {"id": updated.id, "message": "LLM API saved."}




@router.get("/config/prompt_contexts")
def list_prompt_contexts():
    service = PromptConfigService()
    return [{
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "llm_api_id": c.llm_api_id,
        "request_instruction": c.request_instruction,
        "response_instruction": c.response_instruction
    } for c in service.get_all()]

@router.post("/config/prompt_contexts")
def save_prompt_context(data: dict):
    service = PromptConfigService()
    updated = service.create_or_update(data)
    return {"id": updated.id, "message": "Prompt Context saved."}

@router.delete("/config/prompt_contexts/{context_id}")
def delete_prompt_context(context_id: str):
    service = PromptConfigService()
    result = service.delete(context_id)
    return {"message": "Deleted."} if result else {"message": "Not found."}



@router.get("/chat_sessions")
def get_chat_sessions():
    return ChatHistoryService.list_chat_sessions()

@router.get("/chat_history/{session_id}")
def get_chat_history(session_id: str):
    return load_chat_history(session_id)


# @app.post("/config/mcp_server")
# async def add_mcp_server(config: MCPServerConfig):
#     manifest = await fetch_manifest(config.base_url)
#     mcp_id = add_mcp_server_db(config.name, config.base_url, manifest)
#     return {"message": "MCP server added", "mcp_id": mcp_id}
#
# @app.get("/config/mcp_servers")
# def list_mcp_servers():
#     servers = list_mcp_servers_db()
#     return [{"mcp_id": server["mcp_id"], "name": server["name"], "base_url": server["base_url"]} for server in servers]
#
# @app.delete("/config/mcp_server/{mcp_id}")
# def delete_mcp_server(mcp_id: str):
#     delete_mcp_server_db(mcp_id)
#     return {"message": "MCP server deleted successfully"}

