from typing import Dict, Any
import httpx


async def fetch_manifest(base_url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{base_url}/manifest.json")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"Manifest fetch failed for {base_url}: {str(e)}")
        return {}
