#!/usr/bin/env python3
import sys
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

SYSTEM_PROMPT = """Você é um code reviewer especializado no projeto PetRegister.

Contexto do projeto:
- Backend: Python + FastAPI
- Frontend: Next.js + TypeScript
- Bancos: PostgreSQL + ChromaDB (vetorial)
- Regra principal: NENHUM valor hardcoded — tudo via .env

Revise o git diff e verifique:
1. Valores hardcoded que deveriam estar no .env (API keys, URLs, senhas, nomes de modelos)
2. Problemas de segurança (secrets expostos, injeção, etc.)
3. Arquivos sensíveis sendo commitados (.env, credenciais)
4. Type hints ausentes no Python ou tipos ausentes no TypeScript
5. Padrões inconsistentes com a stack do projeto

Retorne um relatório estruturado em português:
- Status: APROVADO ✅  ou  REQUER MUDANÇAS ❌
- Lista de problemas encontrados (com arquivo e linha quando possível)
- Sugestão breve para cada problema
- Se aprovado, uma linha confirmando que está tudo certo

Seja conciso e direto."""


def review_diff(diff_content: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_REVIEW_MODEL", "gpt-4o"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Revise este diff:\n\n{diff_content}"},
        ],
        max_tokens=int(os.getenv("OPENAI_REVIEW_MAX_TOKENS", "1024")),
        temperature=float(os.getenv("OPENAI_REVIEW_TEMPERATURE", "0.2")),
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python review_commit.py <arquivo_diff>", file=sys.stderr)
        sys.exit(1)

    diff_file = Path(sys.argv[1])

    if not diff_file.exists():
        print(f"Arquivo não encontrado: {diff_file}", file=sys.stderr)
        sys.exit(1)

    diff_content = diff_file.read_text(encoding="utf-8")

    if not diff_content.strip():
        print("Nenhuma mudança staged para revisar.")
        sys.exit(0)

    print(review_diff(diff_content))
