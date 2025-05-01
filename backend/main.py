from fastapi import FastAPI
from backend.routers.api import router
from backend.database.init_db import init_db_models, init_db_from_schema


def create_app():
    app = FastAPI(
        title="MCP Server API",
        description="LLM-driven Orchestration System",
        version="1.0.0"
    )
    init_db_from_schema()
    app.include_router(router, prefix="/api")
    return app


app = create_app()
