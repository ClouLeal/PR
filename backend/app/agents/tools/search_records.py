from app.rag.embedder import embed_texts
from app.rag.retriever import search

def search_records(query: str, pet_id: str) -> str:
    query_embedding = embed_texts([query])[0]
    chunks = search(query_embedding, pet_id)
    if not chunks:
        return "No relevant information found."
    return "\n\n---\n\n".join(chunks)


SEARCH_RECORDS_TOOL = {
    "name": "search_records",
    "description": ("Busca informações nos documentos e exames do pet. "
        "Use quando o usuário fizer perguntas específicas sobre saúde, "
        "exames, diagnósticos ou histórico médico."
        ),
    "input_schema" :{
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "O que buscar nos documentos do pet",
            },
        },
        "required": ["query"],
    },
}