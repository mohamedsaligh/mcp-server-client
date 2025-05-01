
from backend.adapter.llm_factory import get_llm_client
from backend.services.llm_refiner.base_llm_refiner import LLMRefiner


class OpenAILLMRefiner(LLMRefiner):
    def __init__(self, api_key: str):
        self.client = get_llm_client("openai-b", api_key)

    def refine(self, prompt: str, context: dict) -> str:
        return self.client.complete(prompt, context)

    def post_process(self, output: str, context: dict) -> str:
        return self.client.complete(output, context)
