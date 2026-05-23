from __future__ import annotations

from langchain_ollama import ChatOllama

from src.config import AppConfig


def build_llm(config: AppConfig, model_name: str | None = None) -> ChatOllama:
    return ChatOllama(
        model=model_name or config.ollama_model,
        base_url=config.ollama_base_url,
        temperature=0,
    )
