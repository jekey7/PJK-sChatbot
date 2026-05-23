from __future__ import annotations

import re
from typing import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.config import AppConfig
from src.llm import build_llm
from src.vectorstore import DocumentSource, format_documents_for_prompt


SYSTEM_PROMPT = """You are a Korean AI chatbot.
Use uploaded document context when it is relevant to the user's question.
If the document context is insufficient, say that clearly instead of inventing facts.
Answer in Korean unless the user explicitly asks for another language.
Keep the answer concise, practical, and grounded in the cited context."""


def answer_question(
    question: str,
    history: Sequence[BaseMessage],
    config: AppConfig,
    model_name: str | None = None,
    document_sources: list[DocumentSource] | None = None,
) -> str:
    document_context = format_documents_for_prompt(document_sources or [])

    messages: list[BaseMessage] = [
        SystemMessage(content=SYSTEM_PROMPT),
        *history,
        HumanMessage(
            content=(
                "User question:\n"
                f"{question}\n\n"
                "Uploaded document context:\n"
                f"{document_context}\n\n"
                "Instructions:\n"
                "- Prefer uploaded document context when the user asks about uploaded files.\n"
                "- Mention uncertainty when the context does not support an answer.\n"
                "- Preserve proper nouns, titles, dates, and numbers exactly as written in the provided context.\n"
                "- Do not include raw <think> reasoning."
            )
        ),
    ]

    response = build_llm(config, model_name=model_name).invoke(messages)
    return strip_deepseek_reasoning(str(response.content))


def trim_history(messages: Sequence[BaseMessage], turns: int) -> list[BaseMessage]:
    max_messages = max(turns, 1) * 2
    return list(messages)[-max_messages:]


def to_langchain_history(chat_messages: Sequence[dict[str, str]], turns: int) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for item in chat_messages:
        role = item.get("role")
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return trim_history(messages, turns)


def strip_deepseek_reasoning(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
