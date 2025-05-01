import logging
import uuid
import json
from typing import Dict, Any

from backend.adapter.mcp_client import fetch_manifest
from backend.database.connection import SessionLocal
from backend.database.repository import (
    mcp_server_repo, llm_api_repo, chat_history_repo
)
from backend.services.llm_refiner.openai_llm_refiner import OpenAILLMRefiner
from backend.services.mcp_executor.basic_mcp_executor import BasicMCPExecutor
from backend.services.response_formatter.markdown_response_formatter import MarkdownResponseFormatter

import httpx

class OrchestratorService:

    def __init__(self):
        self.db = SessionLocal()
        self.mcp_executor = BasicMCPExecutor()
        self.response_formatter = MarkdownResponseFormatter()

    async def run_user_prompt(self, user_id: str, session_id: str, prompt_text: str) -> Dict[str, Any]:
        try:
            llm_api = self.get_llm_api()
            llm_refiner = OpenAILLMRefiner(llm_api.api_key)

            mcp_servers = mcp_server_repo.get_all_mcp_servers(self.db)
            mcp_info = await self.prepare_mcp_server_info(mcp_servers)

            if not mcp_info:
                raise Exception("No MCP servers available.")

            system_instruction = self.get_system_instruction()

            enriched_prompt = llm_refiner.refine(prompt_text, {
                "system": system_instruction,
                "mcp_servers": mcp_info
            })

            try:
                mcp_plan = json.loads(enriched_prompt)
            except Exception as e:
                raise Exception(f"Failed to parse LLM-generated plan.{str(e)}")

            intermediate = await self.execute_plan(mcp_plan, llm_refiner)

            steps = []
            for i, task in enumerate(mcp_plan):
                steps.append({
                    "server_name": task["server_name"],
                    "request": task["payload"],
                    "response": intermediate[i]
                })

            final = llm_refiner.pick_prompt_context(str(intermediate[-1]),f"Given the following steps:\n{json.dumps(steps, indent=2)}")
            formatted = self.response_formatter.format(final, {})

            # Construct steps like snippet.py expects: list of {server_name, request, response}
            steps = []
            for i, task in enumerate(mcp_plan):
                steps.append({
                    "server_name": task["server_name"],
                    "request": task["payload"],
                    "response": intermediate[i]
                })

            session_title = self.get_or_create_session_title(session_id, prompt_text)

            # Save to chat history
            chat_history_repo.create_chat_history(self.db, {
                "session_id": session_id,
                "session_title": session_title,
                "user_id": user_id,
                "context_category_id": None,
                "original_prompt": prompt_text,
                "refined_prompt": enriched_prompt,
                "final_response": formatted,
                "steps": steps,
                "requests": mcp_plan
            })

            final_payload = {
                "session_id": session_id,
                "steps": steps,
                "final_answer": formatted
            }

            print(f"Final payload: {final_payload}")
            return final_payload

        except Exception as e:
            raise Exception(f"Error in OrchestratorService: {str(e)}")


    def get_llm_api(self):
        all_llms = llm_api_repo.get_all_llm_apis(self.db)
        if not all_llms:
            raise Exception("No LLM APIs configured.")
        return all_llms[0]

    def get_or_create_session_title(self, session_id: str, prompt_text: str) -> str:
        existing = chat_history_repo.get_chat_history_by_session(self.db, session_id)
        if existing and len(existing) > 0:
            # Use the title from the first record
            return existing[0].session_title or prompt_text[:40]
        return prompt_text[:25]


    async def prepare_mcp_server_info(self, mcp_servers):
        mcp_info = []
        for server in mcp_servers:
            manifest = await self.fetch_manifest(server.endpoint_url)
            mcp_info.append({
                "server_name": server.name,
                "keywords": server.keywords,
                "endpoint": server.endpoint_url,
                "manifest": manifest
            })
        return mcp_info


    def get_system_instruction(self):
        with open("config/system_instruction.txt", "r", encoding="utf-8") as f:
            return f.read()


    async def fetch_manifest(self, base_url: str) -> Dict[str, Any]:
        try:
            async with httpx.Client(timeout=5) as client:
                resp = client.get(f"{base_url}/manifest.json")
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            print(f"Manifest fetch failed for {base_url}: {str(e)}")
            return {}

    async def execute_plan(self, mcp_plan, llm_refiner):
        intermediate = []
        for task in mcp_plan:
            payload = task["payload"]

            if task.get("refine_previous") and intermediate:
                payload["previous_result"] = intermediate[-1]

            endpoint = self.mcp_server_endpoint(task["server_name"])
            result = await self.mcp_executor.execute(endpoint=endpoint, payload=payload)

            if task.get("refine_llm"):
                result = llm_refiner.post_process(str(result), {
                    "system": task.get("refine_instruction", "")
                })

            intermediate.append(result)

        return intermediate

    def mcp_server_endpoint(self, server_name: str) -> str:
        # Lookup in DB
        server = mcp_server_repo.get_mcp_server_by_name(self.db, server_name)
        if not server:
            raise Exception(f"MCP Server '{server_name}' not found in DB.")

        return server.endpoint_url
