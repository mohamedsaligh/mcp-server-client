from fastapi import APIRouter


health = APIRouter(tags=["Health Check"])

@health.get("/")
def health_check():
    return {"status": "ok"}