from sqlalchemy.orm import Session
from backend.database import models
import uuid


# ---- LLM APIs ----
def create_llm_api(db: Session, data: dict):
    obj = models.LLMAPI(id=str(uuid.uuid4()), **data)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def get_llm_api(db: Session, api_id: str):
    return db.query(models.LLMAPI).filter(models.LLMAPI.id == api_id).first()

def get_all_llm_apis(db: Session):
    return db.query(models.LLMAPI).all()

def update_llm_api(db: Session, api_id: str, data: dict):
    obj = get_llm_api(db, api_id)
    if not obj: return None
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def delete_llm_api(db: Session, api_id: str):
    obj = get_llm_api(db, api_id)
    if obj: db.delete(obj); db.commit(); return True
    return False

def get_llm_api_by_name(db: Session, name: str):
    return db.query(models.LLMAPI).filter(models.LLMAPI.name == name).first()
