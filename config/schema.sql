-- Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Prompt Context
CREATE TABLE IF NOT EXISTS prompt_context (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    llm_api_id TEXT,
    request_instruction TEXT,
    response_instruction TEXT
);

-- LLM APIs
CREATE TABLE IF NOT EXISTS llm_apis (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_key TEXT,
    config TEXT
);

-- MCP Servers
CREATE TABLE IF NOT EXISTS mcp_servers (
    id TEXT PRIMARY KEY,
    name TEXT,
    keywords TEXT,
    endpoint_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

-- Chat History
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    session_title TEXT,
    user_id TEXT REFERENCES users(id),
    context_category_id TEXT REFERENCES prompt_context(id),
    original_prompt TEXT,
    refined_prompt TEXT,
    final_response TEXT,
    steps TEXT,
    requests TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
