from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.models.document import Document
from app.services.pdf_service import extract_text_from_pdf
from app.rag.chunk import chunk_text
from app.rag.embedder import embed_texts
from app.rag.retriever import add_chunks


router = APIRouter()    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{pet_id}/documents", status_code=201)
async def upload_document(
    pet_id: UUID,
    title: str = Form(...),
    doc_type:str = Form(...),
    file: UploadFile = File(None),
    text: str = Form(None),
    db: Session = Depends(get_db),
):
    # define o tipo do documento e extrai o texto bruto
    if doc_type == "pdf":
        if file is None:
            raise HTTPException(status_code=400, detail="PDF file is required for doc_type 'pdf'")
        file_bytes = await file.read()
        raw_text = extract_text_from_pdf(file_bytes)
    else:
        if not text:
            raise HTTPException(status_code=400, detail="Text is required for doc_type 'note'")
        raw_text = text
    
    #salva o documento no banco de dados, PostgreSQL
    db_doc = Document(
        pet_id=pet_id,
        type=doc_type,
        title=title,
        raw_text=raw_text,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    #pipeline do RAG - chunk, embed e indexa no chroma
    chunks = chunk_text(raw_text)
    embeddings = embed_texts(chunks)
    add_chunks(chunks, embeddings,str(pet_id), str(db_doc.id))

    return {"id": str(db_doc.id), "chunks_indexed": len(chunks)}
