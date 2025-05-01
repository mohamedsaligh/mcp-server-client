import openai
from backend.adapter.llm_client_base import LLMClient
from typing import Dict, Any


class OpenAIClientB(LLMClient):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def complete(self, prompt: str, context: Dict[str, Any]) -> str:
        messages = [
            {"role": "system", "content": context.get("system", "")},
            {"role": "user", "content": prompt}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=context.get("temperature", 0.7),
            max_tokens=context.get("max_tokens", 512),
        )
        return response["choices"][0]["message"]["content"].strip()
