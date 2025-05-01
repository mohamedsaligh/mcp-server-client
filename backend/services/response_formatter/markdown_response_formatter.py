from backend.services.response_formatter.base_response_formatter import ResponseFormatter


class MarkdownResponseFormatter(ResponseFormatter):
    def format(self, raw_response: str, context: dict) -> str:
        return f"{raw_response.strip()}"
