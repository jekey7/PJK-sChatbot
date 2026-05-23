from __future__ import annotations

import streamlit as st

from src.chain import answer_question, to_langchain_history
from src.config import get_config
from src.vectorstore import (
    has_indexed_documents,
    index_docs_folder,
    index_uploaded_files,
    search_documents,
)


st.set_page_config(page_title="PJK's Chatbot", page_icon="AI", layout="centered")


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "indexed_chunks" not in st.session_state:
        st.session_state.indexed_chunks = 0


def render_sidebar(config):
    st.sidebar.header("설정")
    model_name = st.sidebar.text_input("Ollama 모델", value=config.ollama_model)
    history_turns = st.sidebar.slider(
        "대화 기억 턴 수",
        min_value=1,
        max_value=20,
        value=config.chat_history_turns,
    )
    use_document_rag = st.sidebar.checkbox("문서 RAG 사용", value=True)
    doc_k = st.sidebar.slider(
        "문서 검색 결과 수",
        min_value=1,
        max_value=10,
        value=config.doc_retrieval_k,
    )

    st.sidebar.divider()
    st.sidebar.subheader("문서 업로드")
    if st.sidebar.button("docs 폴더 인덱싱", use_container_width=True):
        try:
            chunk_count, file_count = index_docs_folder(config)
            st.session_state.indexed_chunks += chunk_count
            if file_count == 0:
                st.sidebar.info(f"{config.docs_dir} 폴더에 PDF/TXT/MD 문서를 넣어주세요.")
            else:
                st.sidebar.success(f"{file_count}개 파일에서 {chunk_count}개 문서 조각을 Chroma에 저장했습니다.")
        except Exception as exc:
            st.sidebar.error(f"docs 폴더 인덱싱 실패: {exc}")

    uploaded_files = st.sidebar.file_uploader(
        "PDF, TXT, MD 파일",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    if st.sidebar.button("업로드 문서 인덱싱", use_container_width=True):
        if uploaded_files:
            try:
                chunk_count = index_uploaded_files(uploaded_files, config)
                st.session_state.indexed_chunks += chunk_count
                st.sidebar.success(f"{chunk_count}개 문서 조각을 Chroma에 저장했습니다.")
            except Exception as exc:
                st.sidebar.error(f"문서 인덱싱 실패: {exc}")
        else:
            st.sidebar.info("먼저 문서를 업로드하세요.")

    st.sidebar.caption(f"Ollama URL: {config.ollama_base_url}")
    st.sidebar.caption(f"Embedding 모델: {config.embedding_model}")
    st.sidebar.caption(f"docs 폴더: {config.docs_dir}")
    indexed_status = "있음" if has_indexed_documents(config) else "없음"
    st.sidebar.caption(f"Chroma 문서: {indexed_status}")
    if st.sidebar.button("대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    return model_name, history_turns, use_document_rag, doc_k


def render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("document_sources"):
                with st.expander("문서 출처"):
                    for index, source in enumerate(message["document_sources"], start=1):
                        page = f", page {source['page'] + 1}" if source.get("page") is not None else ""
                        st.markdown(f"{index}. {source['source']}{page}")


def main() -> None:
    init_state()
    config = get_config()
    model_name, history_turns, use_document_rag, doc_k = render_sidebar(config)

    st.title("PJK's Chatbot")

    render_messages()

    question = st.chat_input("질문을 입력하세요")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("답변을 생성하는 중...")
        try:
            history = to_langchain_history(st.session_state.messages[:-1], turns=history_turns)
            document_sources = (
                search_documents(question, config=config, k=doc_k)
                if use_document_rag and has_indexed_documents(config)
                else []
            )
            answer = answer_question(
                question,
                history=history,
                config=config,
                model_name=model_name,
                document_sources=document_sources,
            )
        except Exception as exc:
            answer = f"오류가 발생했습니다: `{exc}`"
            document_sources = []

        placeholder.markdown(answer)
        if document_sources:
            with st.expander("문서 출처"):
                for index, source in enumerate(document_sources, start=1):
                    page = f", page {source.page + 1}" if source.page is not None else ""
                    st.markdown(f"{index}. {source.source}{page}")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "document_sources": [
                {"source": source.source, "page": source.page, "content": source.content}
                for source in document_sources
            ],
        }
    )


if __name__ == "__main__":
    main()
