import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import httpx
from backend.database.connection import SessionLocal
from backend.database.repository import (
    mcp_server_repo, llm_api_repo, chat_history_repo
)
from backend.services.llm_refiner.openai_llm_refiner import OpenAILLMRefiner
from backend.services.mcp_executor.basic_mcp_executor import BasicMCPExecutor
from backend.services.response_formatter.markdown_response_formatter import MarkdownResponseFormatter


logger = logging.getLogger(__name__)


@dataclass
class ExecutionStep:
    server_name: str
    request: Dict[str, Any]
    response: Any


class OrchestratorServiceError(Exception):
    """Base exception for OrchestratorService"""
    pass


class MCPServerError(OrchestratorServiceError):
    """Raised when there are issues with MCP servers"""
    pass


class LLMError(OrchestratorServiceError):
    """Raised when there are issues with LLM processing"""
    pass


class OrchestratorService:
    MANIFEST_TIMEOUT = 5
    MAX_TITLE_LENGTH = 40
    SHORT_TITLE_LENGTH = 25

    def __init__(self):
        self.db = SessionLocal()
        self.mcp_executor = BasicMCPExecutor()
        self.response_formatter = MarkdownResponseFormatter()

    
    async def run_user_prompt(self, user_id: str, session_id: str, prompt_text: str):
        """
        Process a user prompt through the orchestration pipeline.
        Returns an async generator that yields updates at various stages.
        """
        try:
            # Initial status update
            yield {"type": "status", "data": "Initializing LLM refiner"}
            llm_refiner = self._initialize_llm_refiner()
            
            yield {"type": "status", "data": "Gathering MCP server information"}
            mcp_info = await self._get_mcp_server_info()
            
            yield {"type": "status", "data": "Processing prompt"}
            enriched_prompt = self._process_prompt(prompt_text, llm_refiner, mcp_info)
            yield {"type": "status", "data": "Generating execution plan"}
            mcp_plan = self._parse_mcp_plan(enriched_prompt)
            yield {"type": "plan", "data": mcp_plan}
            
            # Execute tasks with progress updates
            steps = []
            for i, task in enumerate(mcp_plan):
                yield {"type": "task_start", "data": f"Executing task {i+1}/{len(mcp_plan)}: {task['server_name']}"}
                step = await self._execute_single_task_with_context(task, steps, llm_refiner)
                steps.append(step)
                yield {"type": "task_complete", "data": step}

            yield {"type": "status", "data": "Formatting final response"}
            formatted_response = self._format_final_response(steps, llm_refiner)

            self._save_chat_history(
                user_id=user_id,
                session_id=session_id,
                prompt_text=prompt_text,
                enriched_prompt=enriched_prompt,
                steps=steps,
                mcp_plan=mcp_plan,
                formatted_response=formatted_response
            )

            final_payload = self._create_final_payload(session_id, steps, formatted_response)
            yield {"type": "result", "data": final_payload}

        except Exception as e:
            logger.error(f"Error in orchestration process: {str(e)}", exc_info=True)
            yield {"type": "error", "data": f"Orchestration failed: {str(e)}"}

    def _initialize_llm_refiner(self) -> OpenAILLMRefiner:
        """Initialize LLM refiner with API configuration."""
        llm_api = self._get_llm_api()
        return OpenAILLMRefiner(llm_api.api_key)

    async def _get_mcp_server_info(self) -> List[Dict[str, Any]]:
        """Retrieve and validate MCP server information."""
        mcp_servers = mcp_server_repo.get_all_mcp_servers(self.db)
        mcp_info = await self._prepare_mcp_server_info(mcp_servers)
        
        if not mcp_info:
            raise MCPServerError("No MCP servers available")
        return mcp_info

    def _process_prompt(self, prompt_text: str, llm_refiner: OpenAILLMRefiner, 
                       mcp_info: List[Dict[str, Any]]) -> str:
        """Process the user prompt with system instructions and MCP server info."""
        system_instruction = self._get_system_instruction()
        return llm_refiner.refine(prompt_text, {
            "system": system_instruction,
            "mcp_servers": mcp_info
        })

    def _parse_mcp_plan(self, enriched_prompt: str) -> List[Dict[str, Any]]:
        """Parse the LLM-generated plan from the enriched prompt."""
        try:
            return json.loads(enriched_prompt)
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse LLM-generated plan: {str(e)}")

    async def _execute_mcp_plan(self, mcp_plan: List[Dict[str, Any]], 
                              llm_refiner: OpenAILLMRefiner) -> List[ExecutionStep]:
        """Execute the MCP plan and return execution steps."""
        intermediate_results = await self._execute_tasks(mcp_plan, llm_refiner)
        return [
            ExecutionStep(
                server_name=task["server_name"],
                request=task["payload"],
                response=result
            )
            for task, result in zip(mcp_plan, intermediate_results)
        ]

    async def _execute_tasks(self, mcp_plan: List[Dict[str, Any]], 
                           llm_refiner: OpenAILLMRefiner) -> List[Any]:
        """Execute individual tasks in the MCP plan."""
        results = []
        for task in mcp_plan:
            result = await self._execute_single_task(task, results, llm_refiner)
            results.append(result)
        return results

    async def _execute_single_task(self, task: Dict[str, Any], 
                                 previous_results: List[Any],
                                 llm_refiner: OpenAILLMRefiner) -> Any:
        """Execute a single task in the MCP plan."""
        payload = task["payload"].copy()
        if task.get("refine_previous") and previous_results:
            payload["previous_result"] = previous_results[-1]

        endpoint = self._get_server_endpoint(task["server_name"])
        result = await self.mcp_executor.execute(endpoint=endpoint, payload=payload)

        if task.get("refine_llm"):
            result = llm_refiner.post_process(
                str(result),
                {"system": task.get("refine_instruction", "")}
            )
        return result

    def _get_server_endpoint(self, server_name: str) -> str:
        """Get the endpoint URL for a given server name."""
        server = mcp_server_repo.get_mcp_server_by_name(self.db, server_name)
        if not server:
            raise MCPServerError(f"MCP Server '{server_name}' not found")
        return server.endpoint_url

    async def _prepare_mcp_server_info(self, mcp_servers) -> List[Dict[str, Any]]:
        """Prepare MCP server information including manifests."""
        mcp_info = []
        for server in mcp_servers:
            manifest = await self._fetch_manifest(server.endpoint_url)
            mcp_info.append({
                "server_name": server.name,
                "keywords": server.keywords,
                "endpoint": server.endpoint_url,
                "manifest": manifest
            })
        return mcp_info

    def _get_llm_api(self):
        """Retrieve LLM API configuration."""
        all_llms = llm_api_repo.get_all_llm_apis(self.db)
        if not all_llms:
            raise LLMError("No LLM APIs configured")
        return all_llms[0]

    def _get_system_instruction(self) -> str:
        """Read system instructions from configuration file."""
        try:
            with open("config/system_instruction.txt", "r", encoding="utf-8") as f:
                return f.read()
        except IOError as e:
            raise OrchestratorServiceError(f"Failed to read system instructions: {str(e)}")

    async def _fetch_manifest(self, base_url: str) -> Dict[str, Any]:
        """Fetch manifest from MCP server."""
        try:
            async with httpx.AsyncClient(timeout=self.MANIFEST_TIMEOUT) as client:
                resp = await client.get(f"{base_url}/manifest.json")
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.warning(f"Manifest fetch failed for {base_url}: {str(e)}")
            return {}

    def _format_final_response(self, steps: List[ExecutionStep], 
                             llm_refiner: OpenAILLMRefiner) -> str:
        """Format the final response using the execution steps."""
        final_context = str(steps[-1].response)
        steps_json = json.dumps([step.__dict__ for step in steps], indent=2)
        refined = llm_refiner.pick_prompt_context(
            final_context,
            f"Given the following steps:\n{steps_json}"
        )
        return self.response_formatter.format(refined, {})

    def _save_chat_history(self, user_id: str, session_id: str, prompt_text: str,
                          enriched_prompt: str, steps: List[ExecutionStep],
                          mcp_plan: List[Dict[str, Any]], formatted_response: str):
        """Save the chat interaction history."""
        session_title = self._get_or_create_session_title(session_id, prompt_text)
        chat_history_repo.create_chat_history(self.db, {
            "session_id": session_id,
            "session_title": session_title,
            "user_id": user_id,
            "context_category_id": None,
            "original_prompt": prompt_text,
            "refined_prompt": enriched_prompt,
            "final_response": formatted_response,
            "steps": [step.__dict__ for step in steps],
            "requests": mcp_plan
        })

    def _get_or_create_session_title(self, session_id: str, prompt_text: str) -> str:
        """Get existing session title or create a new one."""
        existing = chat_history_repo.get_chat_history_by_session(self.db, session_id)
        if existing and existing[0].session_title:
            return existing[0].session_title
        return (prompt_text[:self.MAX_TITLE_LENGTH] if existing 
                else prompt_text[:self.SHORT_TITLE_LENGTH])

    def _create_final_payload(self, session_id: str, steps: List[ExecutionStep],
                            formatted_response: str) -> Dict[str, Any]:
        """Create the final response payload."""
        payload = {
            "session_id": session_id,
            "steps": [step.__dict__ for step in steps],
            "final_answer": formatted_response
        }
        logger.debug(f"Final payload: {payload}")
        return payload
    
    async def _execute_single_task_with_context(self, task: Dict[str, Any], 
                                             previous_steps: List[ExecutionStep],
                                             llm_refiner: OpenAILLMRefiner) -> ExecutionStep:
        """Execute a single task and return the execution step."""
        payload = task["payload"].copy()
        previous_results = [step.response for step in previous_steps]
        
        if task.get("refine_previous") and previous_results:
            payload["previous_result"] = previous_results[-1]

        endpoint = self._get_server_endpoint(task["server_name"])
        result = await self.mcp_executor.execute(endpoint=endpoint, payload=payload)

        if task.get("refine_llm"):
            result = llm_refiner.post_process(
                str(result),
                {"system": task.get("refine_instruction", "")}
            )
        
        return ExecutionStep(
            server_name=task["server_name"],
            request=task["payload"],
            response=result
        )