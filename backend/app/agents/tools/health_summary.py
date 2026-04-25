from sqlalchemy.orm import Session
from app.models.document import Document

def health_summary(pet_id: str, db: Session) -> str:
    documents = db.query(Document).filter(Document.pet_id == pet_id).all()
    if not documents:
        return "No health information available for this pet."
    lines = [f"[{doc.type.upper()}] {doc.title}: {doc.raw_text[:200]}..." for doc in documents]
    return "\n".join(lines)

HEALTH_SUMMARY_TOOL = {
    "name" : "health_summary",
    "description": (
        "Retorna um resumo de todos os documentos e exames cadastrados do pet. "
        "Use quando o usuário pedir um resumo geral de saúde ou histórico completo."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },

}