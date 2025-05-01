from sqlalchemy.orm import Session
from backend.database import models
import uuid


# ---- Users ----
def create_user(db: Session, data: dict):
    user = models.User(id=str(uuid.uuid4()), **data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, user_id: str, data: dict):
    user = get_user(db, user_id)
    if not user: return None
    for k, v in data.items(): setattr(user, k, v)
    db.commit(); db.refresh(user)
    return user

def delete_user(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user: db.delete(user); db.commit(); return True
    return False