# MCP Server-Client Project

### Todos:
- replace all requests, httpx with single http client  
- 

## Overview
This project consists of a backend, frontend, and MCP server setup designed for extensibility and ease of use.

## Structure
```
mcp-server-client/
├── backend/
│   ├── config/
│   ├── routers/
│   ├── services/
│   ├── models/
│   ├── database/
│   └── logs/
├── frontend/
│   ├── pages/
│   └── .streamlit/
├── mcp_servers/
│   ├── server1/
│   └── server2/
```

## Setup
Run the following commands:
```bash
./start_all.sh
```

## Dependencies
- Backend: FastAPI, YAML, OpenAI, SQLite3
- Frontend: Streamlit, Requests

## Running the Application

### Backend
Navigate to the backend directory and run:
```bash
uvicorn main:app --reload
```

### Frontend
Navigate to the frontend directory and run:
```bash
streamlit run main.py
```