
from backend.database.repository import prompt_context_repo
from backend.services.context_resolver.base_context_resolver import ContextResolver


class KeywordContextResolver(ContextResolver):
    def resolve(self, db, prompt: str):
        for ctx in prompt_context_repo.get_all_prompt_contexts(db):
            if ctx.name.lower() in prompt.lower():
                return ctx
        return None

