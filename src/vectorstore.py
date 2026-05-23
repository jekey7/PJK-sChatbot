from __future__ import annotations

import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import AppConfig


COLLECTION_NAME = "uploaded_documents"
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


@dataclass(frozen=True)
class DocumentSource:
    source: str
    page: int | None
    content: str


def index_uploaded_files(uploaded_files: Iterable, config: AppConfig) -> int:
    documents: list[Document] = []
    for uploaded_file in uploaded_files:
        documents.extend(_load_uploaded_file(uploaded_file))

    if not documents:
        return 0

    chunks = _split_documents(documents)
    vectorstore = _get_vectorstore(config)
    ids = [_chunk_id(chunk) for chunk in chunks]
    vectorstore.add_documents(chunks, ids=ids)
    return len(chunks)


def index_docs_folder(config: AppConfig) -> tuple[int, int]:
    docs_dir = Path(config.docs_dir)
    if not docs_dir.exists():
        docs_dir.mkdir(parents=True, exist_ok=True)
        return 0, 0

    files = [
        path
        for path in docs_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    documents: list[Document] = []
    for path in files:
        documents.extend(_load_file(path, source=str(path.relative_to(docs_dir))))

    if not documents:
        return 0, len(files)

    chunks = _split_documents(documents)
    vectorstore = _get_vectorstore(config)
    ids = [_chunk_id(chunk) for chunk in chunks]
    vectorstore.add_documents(chunks, ids=ids)
    return len(chunks), len(files)


def search_documents(query: str, config: AppConfig, k: int | None = None) -> list[DocumentSource]:
    vectorstore = _get_vectorstore(config)
    results = vectorstore.similarity_search(query, k=k or config.doc_retrieval_k)
    return [_to_source(document) for document in results]


def has_indexed_documents(config: AppConfig) -> bool:
    try:
        vectorstore = _get_vectorstore(config)
        return vectorstore._collection.count() > 0
    except Exception:
        return False


def format_documents_for_prompt(sources: list[DocumentSource]) -> str:
    if not sources:
        return "No uploaded document context was found."

    blocks = []
    for index, source in enumerate(sources, start=1):
        page = f", page {source.page + 1}" if source.page is not None else ""
        blocks.append(
            "\n".join(
                [
                    f"[D{index}] {source.source}{page}",
                    f"Content: {source.content}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _get_vectorstore(config: AppConfig) -> Chroma:
    embeddings = OllamaEmbeddings(
        model=config.embedding_model,
        base_url=config.ollama_base_url,
    )
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.chroma_dir,
    )


def _load_uploaded_file(uploaded_file) -> list[Document]:
    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = Path(temp_file.name)

    try:
        if suffix == ".pdf":
            documents = PyPDFLoader(str(temp_path)).load()
        elif suffix in {".txt", ".md"}:
            documents = TextLoader(str(temp_path), encoding="utf-8").load()
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    finally:
        temp_path.unlink(missing_ok=True)

    for document in documents:
        document.metadata["source"] = uploaded_file.name
    return documents


def _load_file(path: Path, source: str | None = None) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        documents = PyPDFLoader(str(path)).load()
    elif suffix in {".txt", ".md"}:
        documents = TextLoader(str(path), encoding="utf-8").load()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    for document in documents:
        document.metadata["source"] = source or path.name
    return documents


def _split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def _chunk_id(document: Document) -> str:
    source = str(document.metadata.get("source", "unknown"))
    page = str(document.metadata.get("page", ""))
    content_hash = hashlib.sha256(document.page_content.encode("utf-8")).hexdigest()
    return hashlib.sha256(f"{source}:{page}:{content_hash}".encode("utf-8")).hexdigest()


def _to_source(document: Document) -> DocumentSource:
    page = document.metadata.get("page")
    return DocumentSource(
        source=str(document.metadata.get("source") or "uploaded document"),
        page=page if isinstance(page, int) else None,
        content=document.page_content.strip(),
    )
