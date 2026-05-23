# PJK's Chatbot

## 프로젝트 설명

`PJK's Chatbot`은 로컬에서 실행되는 DeepSeek R1 기반 AI 챗봇입니다.
Streamlit으로 웹 UI를 제공하고, LangChain을 사용해 멀티턴 대화와 Chroma 기반 문서 RAG를 구성했습니다.

사용자는 `docs/` 폴더에 문서를 넣거나 PDF/TXT/MD 문서를 직접 업로드해 Chroma 벡터 데이터베이스에 저장하고, 인덱싱된 문서를 기반으로 질문할 수 있습니다.

## 기술 스택

- Python
- Streamlit
- LangChain
- Ollama
- DeepSeek R1
- Chroma
- python-dotenv
- pypdf

## 모델 정보

- 답변 생성 모델
  - Ollama 모델명: `deepseek-r1:latest`
  - 파라미터: `8.2B`
  - 아키텍처: `qwen3`
  - 컨텍스트 길이: `131072`
  - 양자화: `Q4_K_M`
  - 역할: 사용자 질문과 검색된 문서 컨텍스트를 바탕으로 최종 답변 생성

- 임베딩 모델
  - Ollama 모델명: `nomic-embed-text:latest`
  - 파라미터: `137M`
  - 아키텍처: `nomic-bert`
  - 컨텍스트 길이: `2048`
  - 임베딩 차원: `768`
  - 양자화: `F16`
  - 역할: 문서 청크와 사용자 질문을 벡터로 변환해 Chroma 유사도 검색에 사용

## 구현 요약

- `app.py`
  - Streamlit 기반 채팅 화면
  - 챗봇 이름, 입력창, 대화 메시지 표시
  - 모델명, docs 폴더 인덱싱, 문서 업로드, 문서 검색 결과 수, 대화 기억 턴 수 설정

- `src/llm.py`
  - Ollama에 연결해 DeepSeek R1 모델 호출

- `src/vectorstore.py`
  - `docs/` 폴더의 PDF/TXT/MD 문서 재귀 탐색
  - PDF/TXT/MD 업로드 문서 로딩
  - 문서 청크 분할
  - Ollama 임베딩 생성
  - Chroma 벡터 데이터베이스 저장 및 유사 문서 검색

- `src/chain.py`
  - 사용자 질문, 이전 대화 기록, 문서 검색 결과를 조합해 답변 생성
  - DeepSeek R1의 `<think>...</think>` 추론 태그 제거

- `src/config.py`
  - `.env` 기반 환경변수 로딩
  - 모델명, Ollama URL, Chroma 경로, 임베딩 모델, 대화 기억 턴 수 설정

## 로컬 실행 방법

### 1. 레포지토리 다운로드

```powershell
git clone https://github.com/jekey7/PJK-sChatbot.git
cd PJK-sChatbot
```

### 2. Python 가상환경 생성 및 패키지 설치

가상환경 사용은 필수는 아니지만 권장합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

이미 별도 Python 환경을 사용 중이라면 아래 명령만 실행해도 됩니다.

```powershell
pip install -r requirements.txt
```

### 3. Ollama 설치 및 모델 다운로드

Ollama가 설치되어 있어야 하며, 로컬에서 Ollama 서버가 실행 중이어야 합니다.

```powershell
ollama pull deepseek-r1
ollama pull nomic-embed-text
```

모델이 정상 설치되었는지는 아래 명령으로 확인할 수 있습니다.

```powershell
ollama list
```

이미 다른 DeepSeek R1 변형 모델을 사용 중이라면 `.env`의 `OLLAMA_MODEL` 값을 해당 모델명으로 바꾸면 됩니다.
문서 RAG 임베딩 모델을 바꾸려면 `.env`의 `EMBEDDING_MODEL` 값을 변경합니다.

### 4. 환경변수 파일 생성

```powershell
Copy-Item .env.example .env
```

`.env` 파일을 열고 Ollama 및 Chroma 설정을 입력합니다.

```env
OLLAMA_MODEL=deepseek-r1
OLLAMA_BASE_URL=http://localhost:11434
CHAT_HISTORY_TURNS=8
EMBEDDING_MODEL=nomic-embed-text
CHROMA_DIR=./chroma_db
DOCS_DIR=./docs
DOC_RETRIEVAL_K=4
```

macOS/Linux 환경에서는 다음 명령으로 복사할 수 있습니다.

```bash
cp .env.example .env
```

### 5. Streamlit 실행

```powershell
streamlit run app.py
```

실행 후 브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8501
```

### 6. 문서 인덱싱 후 테스트

앱을 처음 실행하면 Chroma 벡터 데이터베이스가 비어 있습니다. 질문하기 전에 문서를 먼저 인덱싱해야 합니다.

1. 사이드바에서 `docs 폴더 인덱싱` 버튼을 누릅니다.
2. 사이드바 하단의 `Chroma 문서: 있음` 상태를 확인합니다.
3. 아래와 같은 질문으로 테스트합니다.

```text
유니티의 하이어라키에 대해 설명해줘
GameObject와 Component의 차이를 알려줘
Prefab은 언제 사용해?
```

기본으로 포함된 `docs/unity-basic-guide.md` 문서가 인덱싱되면 위 질문에 문서 기반 답변을 받을 수 있습니다.

## 참고

- 폴더 기반 RAG를 사용하려면 `docs/` 폴더에 PDF/TXT/MD 파일을 넣고 사이드바에서 `docs 폴더 인덱싱` 버튼을 누릅니다.
- 업로드 기반 RAG를 사용하려면 사이드바에서 PDF/TXT/MD 파일을 업로드한 뒤 `업로드 문서 인덱싱` 버튼을 누릅니다.
- 업로드 문서는 Chroma 벡터 데이터베이스에 저장되며, 기본 저장 폴더는 `chroma_db/`입니다.
- `chroma_db/`는 실행 중 자동 생성되므로 레포지토리를 처음 받은 사용자는 직접 만들 필요가 없습니다.
- 과제 제출 시 원본 문서가 필요하면 `docs/` 폴더는 포함하고, `chroma_db/`와 `.env`는 제외합니다.
- 대화 기록은 현재 Streamlit 세션 안에서만 유지됩니다.
