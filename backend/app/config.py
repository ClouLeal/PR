from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # LLM
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    anthropic_api_key: str
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_max_context_messages: int = 20

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"


    # OpenAI
    openai_api_key: str = ""
    openai_review_model: str = "gpt-4o"
    openai_review_max_tokens: int = 1024
    openai_review_temperature: float = 0.2

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # RAG
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50
    rag_max_results: int = 5
    rag_score_threshold: float = 0.5

    # PostgreSQL
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_host_port: int = 5433
    postgres_db: str = "petregister"
    postgres_user: str = "petregister"
    postgres_password: str

    # ChromaDB
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_host_port: int = 8001
    chroma_collection_prefix: str = "petregister"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # MCP
    mcp_enabled: bool = True
    mcp_port: int = 8002

    # Frontend
    next_public_api_url: str = "http://localhost:8000"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def chroma_url(self) -> str:
        return f"http://{self.chroma_host}:{self.chroma_port}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
