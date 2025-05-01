from openai import OpenAI

from backend.adapter.llm_client_base import LLMClient
from typing import Dict, Any


class OpenAIClientB(LLMClient):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def complete(self, prompt: str, context: Dict[str, Any]) -> str:
        messages = [
            {"role": "system", "content": context.get("system", "")},
            {"role": "user", "content": prompt}
        ]
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."}
            ],
            temperature=0,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()

