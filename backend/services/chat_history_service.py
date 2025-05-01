from typing import List, Dict, Any, Union
from backend.database.connection import SessionLocal
from backend.database.models import ChatHistory
from backend.database.repository import chat_history_repo
import json


class ChatHistoryService:

    @staticmethod
    def load_chat_history(session_id: str):
        db = SessionLocal()
        rows = chat_history_repo.get_chat_history_by_session(db, session_id)
        db.close()
        return [
            {
                "user_prompt": row.original_prompt,
                "steps": json.loads(row.steps) if row.steps and not isinstance(row.steps, list) else row.steps or [],
                "final_answer": row.final_response
            }
            for row in rows
        ]

    @staticmethod
    def list_chat_sessions() -> List[Dict[str, str]]:
        db = SessionLocal()
        rows = (
            db.query(ChatHistory.session_id, ChatHistory.session_title)
            .order_by(ChatHistory.created_at.desc())
            .distinct()
            .all()
        )
        db.close()

        return [
            {
                "session_id": row.session_id,
                "session_title": row.session_title or "(Untitled Session)"
            }
            for row in rows
        ]

