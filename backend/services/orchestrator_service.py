import uuid
from typing import Dict, Any
from backend.database.connection import SessionLocal
from backend.database.repository import (
    mcp_server_repo, llm_api_repo, chat_history_repo
)

import json

from backend.services.context_resolver.keyword_context_resolver import KeywordContextResolver
from backend.services.llm_refiner.openai_llm_refiner import OpenAILLMRefiner
from backend.services.mcp_executor.basic_mcp_executor import BasicMCPExecutor
from backend.services.response_formatter.markdown_response_formatter import MarkdownResponseFormatter


class OrchestratorService:

    def __init__(self):
        self.db = SessionLocal()
        self.context_resolver = KeywordContextResolver()
        self.mcp_executor = BasicMCPExecutor()
        self.response_formatter = MarkdownResponseFormatter()

    def run_user_prompt(self, user_id: str, prompt_text: str) -> Dict[str, Any]:
        context = self.context_resolver.resolve(self.db, prompt_text)
        if not context:
            raise Exception("No prompt context matched")

        llm_api = llm_api_repo.get_llm_api(self.db, context.llm_api_id)
        llm_refiner = OpenAILLMRefiner(llm_api.api_key)

        mcp_manifests = [s.manifest for s in mcp_server_repo.get_all_mcp_servers(self.db)]

        enriched_prompt = llm_refiner.refine(prompt_text, {
            "system": context.request_instruction,
            "mcp_manifests": mcp_manifests
        })

        try:
            mcp_plan = json.loads(enriched_prompt)
        except:
            raise Exception("Failed to parse LLM-generated plan")

        intermediate = []
        for task in mcp_plan:
            payload = task["payload"]
            if task.get("refine_previous") and intermediate:
                payload["previous_result"] = intermediate[-1]

            result = self.mcp_executor.execute(
                endpoint=task["endpoint"],
                payload=payload
            )

            if task.get("refine_llm"):
                result = llm_refiner.post_process(str(result), {
                    "system": task.get("refine_instruction", "")
                })

            intermediate.append(result)

        final = llm_refiner.post_process(str(intermediate[-1]), {
            "system": context.response_instruction
        })

        formatted = self.response_formatter.format(final, {})

        chat_history_repo.create_chat_history(self.db, {
            "session_id": str(uuid.uuid4()),
            "session_title": prompt_text[:40],
            "user_id": user_id,
            "context_category_id": context.id,
            "original_prompt": prompt_text,
            "refined_prompt": enriched_prompt,
            "final_response": formatted,
            "steps": intermediate,
            "requests": mcp_plan
        })

        return {
            "response": formatted,
            "raw": final,
            "steps": intermediate
        }
