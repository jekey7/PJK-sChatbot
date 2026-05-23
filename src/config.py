from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    ollama_model: str = "deepseek-r1"
    ollama_base_url: str = "http://localhost:11434"
    chat_history_turns: int = 8
    embedding_model: str = "nomic-embed-text"
    chroma_dir: str = "./chroma_db"
    docs_dir: str = "./docs"
    doc_retrieval_k: int = 4


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(parsed, 1)


def get_config() -> AppConfig:
    return AppConfig(
        ollama_model=os.getenv("OLLAMA_MODEL", "deepseek-r1").strip() or "deepseek-r1",
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
        or "http://localhost:11434",
        chat_history_turns=_int_env("CHAT_HISTORY_TURNS", 8),
        embedding_model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text").strip()
        or "nomic-embed-text",
        chroma_dir=os.getenv("CHROMA_DIR", "./chroma_db").strip() or "./chroma_db",
        docs_dir=os.getenv("DOCS_DIR", "./docs").strip() or "./docs",
        doc_retrieval_k=_int_env("DOC_RETRIEVAL_K", 4),
    )
