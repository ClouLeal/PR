from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.base import SessionLocal
from app.agents.pet_agent import run_agent


class ChatRequest(BaseModel):
    pet_id: UUID
    message: str

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    answer = run_agent(request.message, str(request.pet_id), db)
    return {"answer": answer}