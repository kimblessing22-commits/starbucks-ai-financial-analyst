# Starbucks AI Financial Analyst

**SEC Filing-Based Financial Performance Assistant** — an educational advisory-style AI web application analyzing Starbucks SEC financial facts.

## Features
- Data-backed AI conversation with loading indicator and automatic chat persistence
- Firestore `data` record CRUD, verified source metadata, Pydantic validation
- Firestore `conversations` save, list, load full messages, delete
- Financial summary, trends, operating margin, revenue line chart, JSON export and dark-mode toggle
- FastAPI Swagger at `/docs`; vanilla HTML/CSS/JavaScript frontend

## Data provenance and limitations
- `data/starbucks_2019_2025.csv`: **112 records** (FY2019–FY2025; 7 fiscal years × 4 quarters × Revenue, Operating Income, Net Income Attributable to Starbucks, Total Assets).
- Generated from the **user-uploaded** SEC Company Facts JSON (`data/sec_companyfacts_sbux_original.json`) using `scripts/extract_sec.py`, without network fetching. Reproduce: `python scripts/extract_sec.py data/sec_companyfacts_sbux_original.json --out data/starbucks_2019_2025.csv`.
- FY2024–FY2025 32 data values also matched separately uploaded company reports, with no discrepancies.
- Data amounts: USD **millions**. Revenue/Operating Income/Net Income are discrete fiscal-quarter flows; Total Assets is a quarter-end snapshot.
- Fiscal Q4 income amounts calculated as the fiscal year's annual amount minus fiscal Q3 year-to-date (9-month) amount. Source accession numbers, filing dates, calculation notes, and GAAP tags preserved.
- This is a research prototype, **not financial/investment advice**. Summary injection gives the AI aggregates and latest-quarter statistics, not every raw observation; questions about unavailable precise historical values should be qualified.
- Public SEC disclosures can be revised; re-validation against source filings is needed for production-quality use.

## Stack
Python 3.10+, FastAPI, Uvicorn, Pydantic, Firebase Admin / Firestore, OpenAI API, python-dotenv; vanilla HTML/CSS/JS; Render backend, Vercel frontend.

## Local setup

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
# add secrets locally, never commit .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

In a second terminal, from `backend` with the same venv and environment:

```bash
python seed.py ../data/starbucks_2019_2025.csv
```

This will idempotently upsert 112 records to `data`. The local frontend can be served via `python -m http.server 3000 --directory frontend` **from the project root**. Configure `frontend/config.js` for the local backend URL (default http://localhost:8000).

## Environment variables (secrets only in backend)
| Variable | Where | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Render + backend `.env` | Private GPT API key; billed separately |
| `OPENAI_MODEL` | Backend | Defaults to `gpt-4o-mini` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Render + backend | JSON service account, optionally base64 encoded |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | Local backend alternative | Absolute path to service account JSON file |
| `ALLOWED_ORIGINS` | Backend | Comma-separated trusted frontend origins, no trailing slash |
| `API_BASE_URL` | Vercel build time | HTTPS Render server base URL; generated into public `config.js` (not a secret) |

## Cloud deployment
1. Create Firebase Firestore database and least-privileged service account credential. Add Firebase credentials to Render **environment**, not code.
2. Push repository to GitHub. Deploy Render Python Web Service using `backend` root, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (or use root `backend/render.yaml` blueprint).
3. Set backend environment variables and `ALLOWED_ORIGINS=https://YOUR-VERCEL-APP.vercel.app`.
4. Seed 112 rows using local `python backend/seed.py data/starbucks_2019_2025.csv` after supplying Firebase credentials locally.
5. Deploy frontend from repository **root** to Vercel. Framework preset: **Other**. Set `API_BASE_URL=https://YOUR-RENDER-URL.onrender.com`; `vercel.json` runs a build that generates the frontend configuration. Output is `frontend`.
6. Visit backend `/docs` and frontend; test edit/delete, new chat, saved conversation loading. Render cold starts can delay initial requests.

## API specification
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/data` | Create validated record |
| GET | `/api/data` | List records |
| PUT | `/api/data/{id}` | Update record |
| DELETE | `/api/data/{id}` | Delete record |
| GET | `/api/data/summary` | Aggregate financial summary |
| POST | `/api/conversations` | Save conversation |
| GET | `/api/conversations` | List saved conversations (includes messages) |
| GET | `/api/conversations/{id}` | Load full conversation messages |
| DELETE | `/api/conversations/{id}` | Delete conversation |
| POST | `/api/chat` | GPT chat + automated conversation save |

## SECURITY WARNING
This coursework prototype does **not implement authentication or per-user Firestore isolation**. Do not publish unrestricted write endpoints in a real public production application, and do not store personal/sensitive data. Before public launch, introduce auth and rules/rate limiting (or an authenticated backend gateway), request quotas and spending caps. Never put OpenAI or service account keys in client-side code.

## Deployment URLs (fill after successful deployment)
Frontend: https://starbucks-ai-financial-analyst.vercel.app/
Backend: https://starbucks-ai-financial-analyst.onrender.com
Swagger: https://starbucks-ai-financial-analyst.onrender.com/docs

## Submission screenshots (capture after deployment)
- [ ] AI conversation including financial context and response
- [ ] Data manager showing one CREATE/EDIT/DELETE action
- [ ] Conversation history with successful loading

## Local checks
`python -m pytest tests -q` from project root after installing `pytest` for tests. Test actual connected API only once Firebase and OpenAI are configured; no external credentials were available when building this starter project.

## 프로젝트 배포 및 실행 URL

Starbucks AI Financial Analyst는 실제 웹 환경에 배포된 재무 분석 AI 서비스입니다.

- **Frontend (Vercel):** https://starbucks-ai-financial-analyst.vercel.app/
- **Backend (Render):** https://starbucks-ai-financial-analyst.onrender.com
- **Swagger API Documentation:** https://starbucks-ai-financial-analyst.onrender.com/docs
- **Health Check:** https://starbucks-ai-financial-analyst.onrender.com/api/health
- **Financial Summary API:** https://starbucks-ai-financial-analyst.onrender.com/api/data/summary

Frontend와 Backend는 별도로 배포되며, 환경 변수 `API_BASE_URL`을 통해 연결됩니다.

Render 무료 인스턴스는 비활성 상태 이후 처음 요청을 처리할 때 응답이 지연될 수 있습니다.

## 시스템 아키텍처 및 설계

### 1. FastAPI 백엔드 구조

현재 프로젝트는 소규모 AI 비서 프로토타입에 적합한 구조로, API 엔드포인트는 `backend/app/main.py`에 구성되어 있습니다.

- `main.py`: HTTP API 엔드포인트, 요청 처리, 데이터 관리 및 AI 채팅 흐름
- `models.py`: Pydantic을 활용한 요청 데이터 구조 정의 및 검증
- `database.py`: Firebase Admin SDK 초기화 및 Firestore 연결
- `services.py`: 재무 데이터 집계와 요약 비즈니스 로직
- `config.py`: 환경 변수 및 CORS 허용 출처 설정

별도의 `APIRouter` 파일로 라우터를 분리하지는 않았지만, 데이터베이스 연결과 요약 계산 로직을 별도 모듈로 분리했습니다.

향후 API 규모가 확대되면 `data`, `chat`, `conversations` 단위로 라우터를 분리할 수 있습니다.

### 2. Firestore 데이터 설계

Firestore는 목적이 서로 다른 두 컬렉션을 중심으로 사용합니다.

**data 컬렉션**

Starbucks의 분기별 재무 수치를 저장합니다. 날짜, 회계연도, 회계분기, 재무지표 종류, 값 등의 정보를 구분해 관리합니다.

이를 통해 연도별·분기별 재무 데이터를 조회하고, 재무 요약 및 추세 분석에 재사용할 수 있습니다.

**conversations 컬렉션**

사용자 질문과 AI 답변을 포함한 대화 메시지 및 생성·수정 시점 등을 저장합니다.

재무 데이터와 대화 기록을 분리한 이유는 데이터의 성격과 사용 목적이 다르기 때문입니다. 재무 수치는 분석에 사용하고, 대화 기록은 이전 AI 질의응답을 다시 확인하는 데 사용합니다.

### 3. Pydantic 데이터 검증

`backend/app/models.py`의 Pydantic 모델은 사용자가 API에 제출하는 데이터의 구조와 입력 조건을 검증합니다.

- `DataIn`: 재무 데이터 입력 구조 검증
- `ChatIn`: AI 질문 메시지 검증
- `ConversationIn`: 대화 저장 요청의 구조 검증

특히 채팅 질문에는 입력 길이 제한을 적용하여 잘못된 요청이나 지나치게 긴 입력을 제한합니다.

검증에 실패한 요청은 FastAPI에서 오류 응답으로 처리됩니다.

현재 구조에서 응답 데이터는 별도의 모든 엔드포인트용 응답 스키마로 표준화되어 있지는 않습니다. 향후 응답 스키마를 추가하면 API 문서의 일관성을 높일 수 있습니다.

### 4. 프론트엔드 데이터 흐름

프론트엔드는 HTML, CSS, JavaScript로 구현되며 백엔드 API와 통신합니다.

**재무 데이터 표시 흐름**

1. 웹페이지가 백엔드의 `/api/data` 및 `/api/data/summary`를 호출합니다.
2. 백엔드가 Firestore의 재무 데이터를 조회하고 요약합니다.
3. 프론트엔드가 최신 재무 수치와 매출 추세 그래프를 표시합니다.

**AI 채팅 흐름**

1. 사용자가 AI Assistant에서 재무 관련 질문을 입력합니다.
2. 프론트엔드가 질문을 `/api/chat`으로 전송합니다.
3. 백엔드가 재무 요약 데이터를 AI 요청에 포함합니다.
4. AI가 재무 데이터에 기초해 답변을 생성합니다.
5. 성공적인 대화는 Firestore에 저장됩니다.
6. 사용자는 Conversations 화면에서 저장된 대화를 조회하고 다시 불러올 수 있습니다.

이 구조는 재무 데이터의 수집·저장, 분석용 요약, AI 해석, 사용자 인터페이스를 연결하기 위한 것입니다.

### 5. 재무 요약 API를 분리한 이유

`/api/data/summary`는 개별 재무 데이터의 조회와 별개로 요약된 분석 정보를 제공하기 위해 구성했습니다.

요약 계산은 `backend/app/services.py`의 `summarize()` 함수에서 수행합니다.

이러한 분리의 장점은 다음과 같습니다.

- 프론트엔드 대시보드와 AI 채팅에서 같은 요약 기준 재사용
- 중복된 집계 코드 감소
- AI에 필요한 핵심 수치만 전달하여 입력 데이터 양 축소
- 집계 계산과 API 요청 처리의 역할 분리

다만 AI에 전체 원시 데이터가 아니라 요약 결과를 전달하므로, 제공되지 않은 특정 과거 기간의 세부 수치를 AI가 정확하게 답하지 못할 수 있습니다.

### 6. 요약 기준 변경 및 확장

재무 요약 계산 기준은 `backend/app/services.py`의 `summarize(rows)` 함수에서 관리합니다.

현재 요약 대상은 다음 네 가지입니다.

- `revenue`
- `operating_income`
- `net_income`
- `total_assets`

집계는 회계연도 및 분기를 기준으로 이루어지며, 최신 분기의 재무 수치와 직전 분기 대비 변화율 등을 계산합니다.

**요약 기준 변경 위치**

- 재무지표 종류 변경: `summarize()`의 `metrics` 목록
- 데이터 집계 범위 변경: `summarize()`에 전달되는 데이터 및 기간 선택 로직
- 최신 분기 판단 기준 변경: 정렬된 기간 목록과 `latest` 계산 부분

예를 들어 최근 4개 분기만 분석하려면 전체 분기를 정렬한 뒤 최근 4개 기간에 해당하는 데이터를 선택하여 집계하도록 수정할 수 있습니다.

이 기능은 현재 구현된 설정 옵션이 아니라 향후 확장 가능한 변경 지점입니다.

또한 `total_assets`는 특정 시점의 잔액이므로 매출액이나 순이익처럼 기간별로 합산하지 않습니다.

### 7. 무료 서버 지연 및 운영 대응

Render 무료 인스턴스는 비활성 상태에서 다시 시작될 때 첫 API 요청의 응답이 지연될 수 있습니다.

현재 프론트엔드에는 서버 응답이 늦어질 수 있다는 안내를 제공하고 있습니다.

추가로 고려할 수 있는 개선 방안은 다음과 같습니다.

- 첫 요청 중 로딩 상태 명확히 표시
- 재무 요약 결과에 대한 적절한 캐싱
- 서버 응답 실패 시 재시도 안내
- 서비스 상태 확인용 `/api/health` 활용

캐싱이나 자동 서버 워밍은 현재 완성된 기능이 아닌 향후 운영 개선 방안입니다.

## 실제 실행 검증 결과

2026년 10월, 배포된 서비스에서 주요 기능을 테스트했습니다.

| 테스트 항목 | 확인 결과 |
|---|---|
| Vercel 웹사이트 접속 | 성공 |
| Render FastAPI 서버 실행 | 성공 |
| `/api/health` | 정상 응답 |
| `/api/data/summary` | 112개 재무 기록의 요약 반환 |
| 재무 대시보드 표시 | 성공 |
| AI 질문 및 답변 | 성공 |
| Firestore 재무 데이터 조회 | 성공 |
| 대화 저장 및 목록 조회 | 성공 |

**AI 질의응답 예시**

질문: What was Starbucks' operating income in fiscal 2025 Q4?

답변: Starbucks' operating income in fiscal 2025 Q4 was USD 278.2 million.

본 수치는 제공된 재무 데이터 기준이며 단위는 USD millions입니다.

## 보안 및 운영상 한계

API 키와 Firebase 서비스 계정 인증 정보는 프론트엔드 소스코드가 아니라 백엔드 환경 변수에서 관리합니다.

CORS는 허용된 프론트엔드 주소에서의 브라우저 요청을 제어하기 위한 설정이며 사용자 인증을 대신하지 않습니다.

현재 시연 버전에는 서버 측 접근 제어를 강화해야 하는 운영상 한계가 있습니다. 특히 AI 호출 및 데이터 생성·수정·삭제 API에는 인증과 요청 제한이 필요합니다.

대화는 성공적인 AI 응답 이후 저장됩니다. 개인정보 최소 수집, 보관 기간, 기록 삭제 정책 등은 실제 운영 전에 추가로 정해야 합니다.

본 프로젝트는 교육 및 기술 검증 목적으로 제작되었습니다.
