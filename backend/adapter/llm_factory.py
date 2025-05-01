from backend.adapter.openai_client_a import OpenAIClientA
from backend.adapter.openai_client_b import OpenAIClientB
from backend.adapter.llm_client_base import LLMClient
from backend.adapter.openai_client_c import OpenAIClientC


def get_llm_client(client_type: str, api_key: str) -> LLMClient:
    if client_type == "openai-a":
        return OpenAIClientA(api_key)
    elif client_type == "openai-b":
        return OpenAIClientB(api_key)
    elif client_type == "openai-C":
        return OpenAIClientC(api_key)
    else:
        raise ValueError(f"Unknown LLM client type: {client_type}")
