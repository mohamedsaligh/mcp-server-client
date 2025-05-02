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
            await asyncio.sleep(0.5)  # Prevent early timeout
            
            # Process the orchestration steps and yield updates
            async for update in orchestrator.run_user_prompt("user123", request.session_id, request.prompt):
                update_type = update.get("type", "status")
                update_data = update.get("data")
                
                if update_type == "error":
                    yield f"event:error\ndata:{json.dumps({'message': update_data})}\n\n"
                    return
                elif update_type == "result":
                    yield f"event:result\ndata:{json.dumps(update_data)}\n\n"
                elif update_type == "plan":
                    yield f"event:plan\ndata:{json.dumps(update_data)}\n\n"
                elif update_type == "task_complete":
                    yield f"event:step\ndata:{json.dumps(update_data.__dict__)}\n\n"
                else:
                    yield f"event:{update_type}\ndata:{json.dumps({'message': update_data})}\n\n"
                
                # Small delay to ensure browser receives events separately
                await asyncio.sleep(0.05)
                
        except asyncio.CancelledError:
            print("⚠️ SSE Stream was cancelled by client or timeout.")
            return
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Error in stream processing: {error_msg}")
            yield f"event:error\ndata:{json.dumps({'message': error_msg})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")