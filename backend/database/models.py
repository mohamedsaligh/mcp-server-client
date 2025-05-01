from sqlalchemy import Column, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Text, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(Text, default=lambda: datetime.utcnow().isoformat())


class PromptContext(Base):
    __tablename__ = "prompt_context"

    id = Column(Text, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    llm_api_id = Column(Text)
    request_instruction = Column(Text)
    response_instruction = Column(Text)


class LLMAPI(Base):
    __tablename__ = "llm_apis"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    base_url = Column(Text, nullable=False)
    api_key = Column(Text)
    config = Column(Text)


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(Text, primary_key=True)
    name = Column(Text)
    keywords = Column(Text)  # NEW
    endpoint_url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Text, primary_key=True)
    session_id = Column(Text, nullable=False)
    session_title = Column(Text, nullable=True)
    user_id = Column(Text, ForeignKey("users.id"))
    context_category_id = Column(Text, ForeignKey("prompt_context.id"))
    original_prompt = Column(Text)
    refined_prompt = Column(Text)
    final_response = Column(Text)
    steps = Column(JSON)  # list of steps executed
    requests = Column(JSON)  # requests sent to MCPs
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
