import asyncio
import json

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from backend.routers.config import UserPromptRequest
from backend.services.chat_history_service import ChatHistoryService
from backend.services.orchestrator_service import OrchestratorService



chat = APIRouter()

@chat.get("/all")
def get_chat_sessions():
    return ChatHistoryService.list_chat_sessions()

@chat.get("/{session_id}")
def get_chat_history(session_id: str):
    response = ChatHistoryService.load_chat_history(session_id)
    print(">> chat history response: ", response)
    return response

@chat.post("/stream")
async def stream_prompt(request: UserPromptRequest):
    orchestrator = OrchestratorService()
    async def event_generator():
        try:
            yield f"event:status\ndata:Starting orchestration, please wait...\n\n"
            await asyncio.sleep(1)  # 🔥 Prevent early timeout

            result = await orchestrator.run_user_prompt("user123", request.session_id, request.prompt)

            # yield f"event:status\ndata:Completed orchestration\n\n"
            # yield f"event:steps\ndata:{json.dumps(result['steps'])}\n\n"
            # yield f"event:requests\ndata:{json.dumps(result['requests'])}\n\n"
            yield f"event:result\ndata:{json.dumps(result)}\n\n"

        except asyncio.CancelledError:
            print("⚠️ SSE Stream was cancelled by client or timeout.")
            return
        except Exception as e:
            yield f"event:error\ndata:{str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
