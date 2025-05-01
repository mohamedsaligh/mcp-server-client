from typing import Dict, Any

import httpx

from backend.services.mcp_executor.base_mcp_executor import MCPExecutor


class BasicMCPExecutor(MCPExecutor):

    async def execute(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(f"{endpoint}/process", json=payload)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            return {"error": f"Failed to call MCP server {endpoint}: {str(e)}"}

