from sqlalchemy.orm import Session
from backend.database.models import ChatHistory
import uuid

def create_chat_history(db: Session, data: dict):
    record = ChatHistory(id=str(uuid.uuid4()), **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_chat_history(db: Session, session_id: str):
    return db.query(ChatHistory).filter(ChatHistory.id == session_id).first()

def get_all_chat_history(db: Session):
    return db.query(ChatHistory).all()

def get_chat_history_by_session(db: Session, session_id: str):
    return db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at).all()

def delete_chat_history(db: Session, session_id: str):
    record = get_chat_history(db, session_id)
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

