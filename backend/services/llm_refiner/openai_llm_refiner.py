import json

from backend.adapter.llm_factory import get_llm_client
from backend.services.llm_refiner.base_llm_refiner import LLMRefiner


class OpenAILLMRefiner(LLMRefiner):
    def __init__(self, api_key: str):
        self.client = get_llm_client("openai-a", api_key)

    def refine(self, prompt: str, context: dict) -> str:
        return self.client.complete(prompt, context)

    def post_process(self, output: str, context: dict) -> str:
        return self.client.complete(output, context)

    def pick_prompt_context(self, prompt_text: str, context_list: dict) -> str:
        """LLM picks the best matching prompt_context id based on prompt_text"""
        system_instruction = (
            "You are a smart summarizer. Given a series of steps and responses, "
            "generate a friendly natural language summary for the user. "
            "Do NOT include JSON. Just explain the final result simply."
        )

        prompt = f"""
        User Prompt: {prompt_text}
        
        Available Contexts:
        {json.dumps(context_list, indent=2)}
        """

        response = self.refine(prompt, {
            "system": system_instruction
        })

        result = response.strip().replace('"', '')  # In case LLM returns the id wrapped in quotes
        return result
