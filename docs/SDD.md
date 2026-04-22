# SDD — PetRegister

**Versão:** 0.1  
**Data:** 2026-04-22  
**Status:** Em desenvolvimento

---

## 1. Visão do produto

Sistema para gerenciar a saúde de múltiplos pets. Permite fazer upload de laudos em PDF e adicionar notas de texto. Um agente de IA responde perguntas **exclusivamente com base nos dados inseridos** e gera resumos de saúde.

Objetivo secundário: aprender na prática os conceitos de **RAG, Agents, Skills/Tools e MCP**.

---

## 2. Stack

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | Python + FastAPI | Padrão de mercado para IA; ecossistema LangChain/RAG |
| Frontend | Next.js + TypeScript | Stack web mais pedida em vagas; TypeScript similar ao C# |
| Banco relacional | PostgreSQL | Padrão de mercado |
| Banco vetorial | ChromaDB | Open-source, simples, ideal para aprender RAG |
| LLM | Claude API (Anthropic) | Configurável via .env; provedor trocável |
| Embeddings | sentence-transformers | Gratuito, roda local |
| Containers | Docker Compose | Um comando para subir tudo |

---

## 3. Arquitetura

```
┌──────────────────────┐
│   Next.js (frontend) │
│   TypeScript + React │
└──────────┬───────────┘
           │ HTTP REST
┌──────────▼───────────────────────────────────────┐
│              FastAPI (backend)                    │
│                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────┐  │
│  │    Agent    │  │ RAG Pipeline │  │   MCP   │  │
│  │  (Claude)   │  │              │  │ Server  │  │
│  │             │  │  ingest →    │  │         │  │
│  │  tools:     │  │  chunk  →    │  │ expõe   │  │
│  │  - search   │  │  embed  →    │  │ dados   │  │
│  │  - summary  │  │  retrieve    │  │ do pet  │  │
│  │  - add_note │  │              │  │         │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┘  │
│         │                │                         │
└─────────┼────────────────┼─────────────────────────┘
          │                │
    ┌─────▼──────┐   ┌─────▼──────┐
    │ PostgreSQL │   │  ChromaDB  │
    │ (metadata) │   │  (vetores) │
    └────────────┘   └────────────┘
          │
    Claude API (via .env)
```

---

## 4. Estrutura de pastas

```
PetRegister/
├── docker-compose.yml
├── .env                     ← nunca commitar
├── .env.example             ← template com todas as variáveis
├── docs/
│   └── SDD.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          ← entry point FastAPI
│       ├── config.py        ← carrega e valida todo o .env
│       │
│       ├── api/
│       │   └── routes/
│       │       ├── pets.py        ← CRUD de pets
│       │       ├── documents.py   ← upload e listagem de PDFs/notas
│       │       └── chat.py        ← endpoint do chatbot
│       │
│       ├── agents/
│       │   ├── pet_agent.py       ← loop do agente Claude
│       │   └── tools/
│       │       ├── search_records.py   ← busca vetorial no ChromaDB
│       │       ├── health_summary.py   ← gera resumo de saúde
│       │       └── add_note.py         ← adiciona nota via agente
│       │
│       ├── rag/
│       │   ├── ingestion.py       ← extrai texto de PDFs
│       │   ├── chunker.py         ← divide texto em chunks
│       │   ├── embedder.py        ← gera embeddings
│       │   └── retriever.py       ← busca no ChromaDB
│       │
│       ├── mcp/
│       │   └── server.py          ← servidor MCP dos dados do pet
│       │
│       ├── models/
│       │   ├── pet.py             ← modelo DB de Pet
│       │   └── document.py        ← modelo DB de Document
│       │
│       └── services/
│           ├── pdf_service.py     ← lê e extrai texto de PDFs
│           └── llm_service.py     ← adapter para trocar LLM via .env
│
└── frontend/                ← fase 2
    ├── Dockerfile
    └── (Next.js app)
```

---

## 5. Variáveis de ambiente (.env.example)

```dotenv
# ── LLM ──────────────────────────────────────────
LLM_PROVIDER=anthropic          # anthropic | openai | ollama
LLM_MODEL=claude-sonnet-4-6
ANTHROPIC_API_KEY=sk-ant-...
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_MAX_CONTEXT_MESSAGES=20

# ── Embeddings ───────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2  # modelo local sentence-transformers
EMBEDDING_DEVICE=cpu               # cpu | cuda

# ── RAG ──────────────────────────────────────────
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_MAX_RESULTS=5
RAG_SCORE_THRESHOLD=0.5

# ── PostgreSQL ───────────────────────────────────
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=petregister
POSTGRES_USER=petregister
POSTGRES_PASSWORD=changeme

# ── ChromaDB ─────────────────────────────────────
CHROMA_HOST=chromadb
CHROMA_PORT=8000
CHROMA_COLLECTION_PREFIX=petregister

# ── App ──────────────────────────────────────────
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# ── MCP ──────────────────────────────────────────
MCP_ENABLED=true
MCP_PORT=8001

# ── Frontend ─────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 6. Modelo de dados (PostgreSQL)

```
pets
────
id          UUID  PK
name        TEXT
species     TEXT        (dog, cat, etc.)
breed       TEXT
birth_date  DATE
created_at  TIMESTAMP

documents
─────────
id          UUID  PK
pet_id      UUID  FK → pets.id
type        TEXT        (pdf, note)
title       TEXT
raw_text    TEXT        (texto extraído)
file_path   TEXT        (path do PDF, se aplicável)
created_at  TIMESTAMP

chunks (rastreia o que foi vetorizado)
──────
id           UUID  PK
document_id  UUID  FK → documents.id
chroma_id    TEXT        (ID no ChromaDB)
content      TEXT
chunk_index  INT
```

---

## 7. Fases de desenvolvimento

### Fase 1 — Backend foundation
- [ ] Docker Compose (FastAPI + PostgreSQL + ChromaDB)
- [ ] `config.py` carregando todo o .env com Pydantic Settings
- [ ] Models + migrations (SQLAlchemy + Alembic)
- [ ] CRUD de Pets (`POST /pets`, `GET /pets`, `GET /pets/{id}`)
- [ ] Upload de documentos (`POST /pets/{id}/documents`)

**Conceitos:** FastAPI, ORM, migrations, REST design

---

### Fase 2 — RAG Pipeline
- [ ] `pdf_service.py`: extrai texto de PDF (pdfplumber)
- [ ] `chunker.py`: divide texto em chunks configuráveis
- [ ] `embedder.py`: gera embeddings com sentence-transformers
- [ ] Salva chunks no ChromaDB com metadados do pet
- [ ] `retriever.py`: busca semântica por pet_id + query

**Conceitos:** chunking, embeddings, similaridade vetorial, RAG

---

### Fase 3 — Agent + Tools
- [ ] `llm_service.py`: adapter Claude com tool use
- [ ] Tool `search_records`: busca no ChromaDB
- [ ] Tool `health_summary`: consolida histórico do pet
- [ ] Tool `add_note`: insere nota via agente
- [ ] `pet_agent.py`: loop de raciocínio do agente
- [ ] Endpoint `POST /chat` consumindo o agente

**Conceitos:** tool use, agent loop, prompt engineering, grounding

---

### Fase 4 — MCP Server
- [ ] `mcp/server.py`: expõe pets e documentos como resources MCP
- [ ] Registrar tools MCP: `get_pet_summary`, `search_pet_records`
- [ ] Testar com Claude Code consumindo o servidor

**Conceitos:** MCP protocol, resources, tools, server lifecycle

---

### Fase 5 — Frontend
- [ ] Setup Next.js + TypeScript
- [ ] Página de pets (lista + cadastro)
- [ ] Upload de PDF / adição de nota
- [ ] Chat interface
- [ ] Painel de saúde do pet

**Conceitos:** React, componentes, estado, fetch API, TypeScript

---

## 8. Decisões de arquitetura registradas

| Data | Decisão | Motivo |
|---|---|---|
| 2026-04-22 | ChromaDB como vector store | Simples, embedded, ideal para aprender RAG sem infra extra |
| 2026-04-22 | sentence-transformers para embeddings | Gratuito, roda local, não depende de API |
| 2026-04-22 | Sem OCR no MVP | Só laudos com texto selecionável por ora |
| 2026-04-22 | Backend primeiro, frontend depois | Foco em aprender AI antes de web |
| 2026-04-22 | Pydantic Settings para .env | Validação tipada de configuração, padrão FastAPI |
