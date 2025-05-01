from sqlalchemy.orm import Session
from backend.database import models
import uuid


# ---- MCP Servers ----
def create_mcp_server(db: Session, data: dict):
    obj = models.MCPServer(id=str(uuid.uuid4()), **data)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def get_mcp_server(db: Session, mcp_id: str):
    return db.query(models.MCPServer).filter(models.MCPServer.id == mcp_id).first()

def get_all_mcp_servers(db: Session):
    return db.query(models.MCPServer).all()

def update_mcp_server(db: Session, mcp_id: str, data: dict):
    obj = get_mcp_server(db, mcp_id)
    if not obj: return None
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def delete_mcp_server(db: Session, mcp_id: str):
    obj = get_mcp_server(db, mcp_id)
    if obj: db.delete(obj); db.commit(); return True
    return False