# file: backend_server.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import asyncio
import uuid
from openai import OpenAI
import json

app = FastAPI(title="MCP Orchestration Backend")

# --- In-memory Config Storage ---
mcp_servers: Dict[str, Dict[str, Any]] = {}  # key = mcp_id, value = {name, url, manifest}
openai_api_key: str = ""

# --- Models ---
class MCPServerConfig(BaseModel):
    name: str
    base_url: str

class UserPromptRequest(BaseModel):
    prompt: str
    session_id: str
    selected_mcp_ids: List[str]

# --- Utils ---
async def fetch_manifest(base_url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{base_url}/manifest.json")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"Manifest fetch failed for {base_url}: {str(e)}")
        return {}

async def call_openai(refinement_prompt: str, manifest_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    client = OpenAI(api_key=openai_api_key)
    
    system_instruction = (
        "You are a smart orchestrator that prepares payloads for MCP servers based on the user's prompt. "
        "You are provided with available MCP servers, each with actions and their expected input models.\n\n"
        "Your task is:\n"
        "- Select correct server and action.\n"
        "- Prepare the correct payload matching the input_model exactly.\n\n"
        "IMPORTANT rules when interpreting numbers:\n"
        "- For 'circle' shapes:\n"
        "    - If user mentions 'diameter', 'cross section', or 'across', divide the value by 2 to compute radius.\n"
        "    - Example: 'a circle of diameter 8cm' → radius = 4.0.\n"
        "- If user directly mentions 'radius', use it as-is.\n"
        "- Always convert dimensions to numbers (floats).\n\n"
        "Special Rules:\n"
        "- When the user asks to perform calculations across multiple steps (e.g., calculate several areas then add), "
        "you must **carry forward the intermediate results**.\n"
        "- Accumulate results as needed and pass all accumulated results to the next step if requested.\n"
        "- Always extract numbers correctly.\n"
        "- Always respond with a pure JSON list. No extra explanations.\n\n"
        "Response format:\n"
        "- Only respond with a pure JSON list.\n"
        "- Each item must include:\n"
        "    - server_name (string)\n"
        "    - payload (dictionary matching the input model)\n"
        "No explanation. No extra text. Only clean JSON output."
    )


    full_prompt = f"""User Prompt: {refinement_prompt}

    Available MCP Servers:
    {json.dumps(manifest_data, indent=2)}

    Reply ONLY with a valid JSON list."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0,
            max_tokens=800,
        )

        print("OpenAI Response: ", response)

        content = response.choices[0].message.content.strip()
        if not content:
            raise HTTPException(status_code=500, detail="OpenAI returned empty response.")
        
        try:
            return json.loads(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI returned invalid JSON: {str(e)}\nContent was: {content}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {str(e)}")


async def call_openai_summary(summary_prompt: str) -> str:
    if not openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    client = OpenAI(api_key=openai_api_key)

    system_instruction = (
        "You are a smart summarizer. Given a series of steps and responses, "
        "generate a friendly natural language summary for the user. "
        "Do NOT include JSON. Just explain the final result simply."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        if not content:
            raise HTTPException(status_code=500, detail="OpenAI summarization returned empty response.")
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI summarization failed: {str(e)}")



async def call_mcp_server(mcp_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(f"{mcp_info['base_url']}/process", json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": f"Failed to call MCP server {mcp_info['name']}: {str(e)}"}

# --- API Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "Backend is healthy ✅"}

@app.post("/config/openai")
def configure_openai(api_key: str):
    global openai_api_key
    openai_api_key = api_key
    return {"message": "OpenAI API key configured successfully"}

@app.post("/config/mcp_server")
async def add_mcp_server(config: MCPServerConfig):
    mcp_id = str(uuid.uuid4())
    manifest = await fetch_manifest(config.base_url)
    mcp_servers[mcp_id] = {
        "name": config.name,
        "base_url": config.base_url,
        "manifest": manifest
    }
    return {"message": "MCP server added", "mcp_id": mcp_id}

@app.get("/config/mcp_servers")
def list_mcp_servers():
    return [{"mcp_id": k, "name": v["name"], "base_url": v["base_url"]} for k, v in mcp_servers.items()]

@app.post("/process_prompt")
async def process_prompt(request: UserPromptRequest):
    if not openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key missing")

    async def event_generator():
        try:
            # Step 1: Collect available servers
            available_servers = []
            for mcp_id in request.selected_mcp_ids:
                server_info = mcp_servers[mcp_id]
                server_summary = {
                    "name": server_info["name"],
                    "base_url": server_info["base_url"],
                    "actions": server_info.get("manifest", {}).get("actions", [])
                }
                available_servers.append(server_summary)

            yield f"event:status\ndata:Refining your prompt with OpenAI...\n\n"

            refined_response = await call_openai(request.prompt, available_servers)
            sequence = refined_response

            results = []
            current_data = {}

            # Step 2: Call MCP servers
            for step in sequence:
                server_name = step["server_name"]
                payload = step.get("payload", {})

                matching = [info for info in mcp_servers.values() if info["name"] == server_name]
                if not matching:
                    yield f"event:error\ndata:Server {server_name} not found\n\n"
                    continue

                payload = {k: v for k, v in payload.items() if v is not None}

                yield f"event:status\ndata:Calling MCP Server: {server_name}...\n\n"

                response = await call_mcp_server(matching[0], payload)
                current_data = response
                results.append({
                    "server_name": server_name,
                    "request": payload,
                    "response": response
                })

            # Step 3: Final summarization
            yield f"event:status\ndata:Summarizing final answer with OpenAI...\n\n"

            final_summary_prompt = (
                f"Given the following steps:\n{json.dumps(results, indent=2)}\n"
                f"Summarize the final result nicely for the user."
            )
            final_response = await call_openai_summary(final_summary_prompt)

            final_payload = {
                "session_id": request.session_id,
                "steps": results,
                "final_answer": final_response
            }
            yield f"event:result\ndata:{json.dumps(final_payload)}\n\n"
        except Exception as e:
            yield f"event:error\ndata:{str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# calculate the area of box 4cm and 5cm in size