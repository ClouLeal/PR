from app.config import settings


def chunk_text(text: str) -> list[str]:
    chunks = []
    step = settings.rag_chunk_size - settings.rag_chunk_overlap

    i = 0
    while i < len(text):
        chunk = text[i : i + settings.rag_chunk_size]
        if chunk.strip():
            chunks.append(chunk.strip())
        i += step

    return chunks
