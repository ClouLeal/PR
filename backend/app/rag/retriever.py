import chromadb
from app.config import settings

_collection = None

def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        _collection = client.get_or_create_collection(
            f"{settings.chroma_collection_prefix}_documents"
        )
    return _collection


def add_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    pet_id: str,
    document_id: str,
) -> None: 
    _collection = get_collection()
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"pet_id": pet_id, "document_id": document_id} for _ in chunks]
    _collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

def search(query_embedding: list[float], pet_id: str) -> list[str]:
    _collection = get_collection()
    results = _collection.query(
        query_embeddings = [query_embedding],
        n_results = settings.rag_max_results,
        where = {"pet_id": pet_id},
    )
    return results["documents"][0]
