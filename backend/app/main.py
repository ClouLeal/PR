from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import pets, documents, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    yield
    print("Shutting down the application...")

app = FastAPI(
    title="PetRegister",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(pets.router, prefix="/pets", tags=["pets"])
app.include_router(documents.router, prefix="/pets", tags=["documents"])
app.include_router(chat.router, tags=["chat"])


@app.get("/health")
def health():
    return {"status": "ok"}
