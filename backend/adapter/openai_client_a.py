import openai
from backend.adapter.llm_client_base import LLMClient
from typing import Dict, Any


class OpenAIClientA(LLMClient):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def complete(self, prompt: str, context: Dict[str, Any]) -> str:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=context.get("temperature", 0.7),
            max_tokens=context.get("max_tokens", 512),
        )
        return response["choices"][0]["text"].strip()

