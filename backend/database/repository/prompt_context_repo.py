from sqlalchemy.orm import Session
from backend.database import models
import uuid



def get_prompt_context_by_name(db: Session, name: str):
    return db.query(models.PromptContext).filter(models.PromptContext.name == name).first()

def create_prompt_context(db: Session, data: dict):
    obj = models.PromptContext(id=str(uuid.uuid4()), **data)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def get_prompt_context(db: Session, context_id: str):
    return db.query(models.PromptContext).filter(models.PromptContext.id == context_id).first()

def get_all_prompt_contexts(db: Session):
    return db.query(models.PromptContext).all()

def update_prompt_context(db: Session, context_id: str, data: dict):
    obj = get_prompt_context(db, context_id)
    if not obj: return None
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def delete_prompt_context(db: Session, context_id: str):
    obj = get_prompt_context(db, context_id)
    if obj: db.delete(obj); db.commit(); return True
    return False

