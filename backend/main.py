from fastapi import FastAPI
from backend.routers.chat import chat
from backend.routers.config import config
from backend.routers.health import health
from backend.database.init_db import init_db_from_schema


def create_app():
    app = FastAPI(
        title="MCP Server API",
        description="LLM-driven Orchestration System",
        version="1.0.0"
    )
    init_db_from_schema()

    app.include_router(chat, prefix="/api/chat")
    app.include_router(config, prefix="/api/config")
    app.include_router(health, prefix="/api/health")
    return app


app = create_app()
