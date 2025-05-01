import httpx

from backend.services.mcp_executor.base_mcp_executor import MCPExecutor


class BasicMCPExecutor(MCPExecutor):
    def execute(self, endpoint: str, payload: dict):
        try:
            response = httpx.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
