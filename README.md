# ProjectRAG

개인용 AI 비서 RAG 시스템 (LangGraph + FastAPI + Chroma + SQLite)

## 목차

- [빠른 시작](#빠른-시작)
- [주요 기능](#주요-기능)
- [프로젝트 구조](#프로젝트-구조)
- [API 예시](#api-예시)
- [중복 인제스트 정책](#중복-인제스트-정책)
- [이미지 OCR 지원](#이미지-ocr-지원)
- [리랭커 설정 (기본 OFF)](#리랭커-설정-기본-off)
- [인코딩 이슈 (Windows PowerShell)](#인코딩-이슈-windows-powershell)
- [서버 운영 스크립트 (Windows)](#서버-운영-스크립트-windows)
- [문서](#문서)
- [E2E 평가 (배치 러너 권장)](#e2e-평가-배치-러너-권장)

## 빠른 시작

1) 가상환경 활성화

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\Activate.ps1
```

2) 환경 변수 파일 생성

```powershell
Copy-Item .env.example .env
notepad .env
```

필수:

- `OPENAI_API_KEY`

3) 서버 실행

```powershell
python -m uvicorn app.main:app --port 8000
```

권장(Windows 운영 스크립트):

```powershell
.\scripts\run_server.ps1 -Action start -Port 8000 -Reload
```

4) 상태 확인

```powershell
curl http://127.0.0.1:8000/health
```

5) 웹 UI 접속

```text
http://127.0.0.1:8000/web
```

---

## 주요 기능

- 문서 인제스트: `/ingest`
- 질의응답: `/chat`
- 스레드 관리: `/threads`, `/threads/reset`
- 웹 클라이언트: `/web`
- 체크포인트/Docstore: SQLite
- 벡터 저장소: Chroma (Persistent)

---

## 프로젝트 구조

```text
ProjectRAG/
├─ README.md
├─ OPERATIONS.md
├─ .context/                  # 설계/작업기록 문서
│  ├─ 00info.md ~ 07UnresolvedItems.md
│  ├─ .ask/                   # ask00~ 작업일지
│  └─ .Mid_inspec/            # 중간 점검 정리
└─ rag_assistant/
   ├─ app/                    # FastAPI + LangGraph 핵심 코드
   │  ├─ main.py              # 앱 엔트리포인트
   │  ├─ graph.py             # route→retrieve→generate→finalize
   │  ├─ routes/              # /chat /ingest /threads /web
   │  ├─ ingest/              # discovery/loaders/chunking/OCR
   │  ├─ nodes/               # 그래프 노드 로직
   │  └─ storage/             # chroma/docstore/checkpoint
   ├─ cli/assistant.py        # CLI 엔트리
   ├─ scripts/                # e2e/soak/analyzer/run_server
   ├─ evals/                  # 케이스/평가용 문서/결과물(로컬)
   │  ├─ e2e_eval_cases.jsonl
   │  └─ docs/
   ├─ docs/                   # 일반 문서 샘플
   ├─ data/                   # 로컬 DB/벡터 저장소 (git ignore)
   ├─ logs/                   # 런타임 로그 (git ignore)
   ├─ .env.example            # 환경변수 템플릿
   └─ .env                    # 로컬 비밀키 (git ignore)
```

---

## API 예시

### Ingest

```json
POST /ingest
{
  "path": "./docs",
  "recursive": true,
  "dry_run": false
}
```

### Chat

```json
POST /chat
{
  "thread_id": "default",
  "question": "이 프로젝트 구조 설명해줘"
}
```

응답에는 `tokens`, `timing`이 포함될 수 있습니다.

---

## 중복 인제스트 정책

- 동일 `source_path` + 동일 내용 해시(`content_hash`)는 스킵
- 내용 변경 시 기존 문서/벡터 삭제 후 재저장

---

## 이미지 OCR 지원

- 지원 확장자: `png`, `jpg`, `jpeg`, `webp`, `bmp`, `tif`, `tiff`
- 동작 방식: 이미지 자체 검색이 아니라, OCR로 추출한 텍스트를 인제스트해 RAG 검색에 사용
- 필요 설정: `.env`에서 `OCR_ENABLED=true` + 시스템 Tesseract 설치

---

## 리랭커 설정 (기본 OFF)

```env
RERANKER_ON=false  # deprecated (use RERANKER_MODE)
RERANKER_MODE=off  # off | auto | always
RERANK_TOP_K=20
RERANKER_MODEL=none
RERANKER_TIMEOUT_SEC=10
RERANKER_SCORE_THRESHOLD=-1.0
RERANKER_DISTANCE_THRESHOLD=0.6
RERANKER_BATCH_SIZE=16
```

테스트 기준으로 reranker_on은 지연만 증가했고 품질 개선은 뚜렷하지 않았습니다.
조건부 활성화는 `RERANKER_MODE=auto`로 설정하세요.

---

## 인코딩 이슈 (Windows PowerShell)

- PowerShell 5.1에서 한글 응답이 깨질 수 있습니다.
- 테스트 시 질문에 "Answer in English"를 붙이면 영어 응답으로 우회 가능합니다.

---

## 서버 운영 스크립트 (Windows)

`rag_assistant/scripts/run_server.ps1`로 서버 시작/중지/상태 확인을 표준화할 수 있습니다.

```powershell
cd D:\ProjectRAG\rag_assistant

# 상태 확인 (실행 중이면 exit code 0, 아니면 1)
.\scripts\run_server.ps1 -Action status -Port 8000

# 서버 시작
.\scripts\run_server.ps1 -Action start -Port 8000 -Reload

# 서버 중지
.\scripts\run_server.ps1 -Action stop -Port 8000

# 서버 재시작
.\scripts\run_server.ps1 -Action restart -Port 8000 -Reload
```

---

## 문서

- `.context/00info.md` — 설계서
- `.context/01Architecture.md` — 아키텍처
- `.context/02ApiSpec.md` — API 명세
- `.context/03CliSpec.md` — CLI 명세
- `.context/04GraphSpec.md` — 그래프 명세
- `.context/05IngestionSpec.md` — 인제스트 명세
- `.context/06WorkPlan.md` — 작업 계획
- `.context/07UnresolvedItems.md` — 결정/운영 메모

---

## E2E 평가 (배치 러너 권장)

36케이스 이상처럼 긴 평가는 `e2e_eval_batch_runner.py` 사용을 권장합니다.  
배치마다 서버를 재기동하고 결과를 자동 병합해 안정적으로 리포트를 생성합니다.

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 12 `
  --api-host 127.0.0.1 `
  --api-port 8072 `
  --thread-prefix eval-main `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --server-log-dir .\evals\results\server_logs `
  --failure-summary-path .\evals\results\e2e_eval_failure_summary.json `
  --failure-tail-lines 20 `
  --output .\evals\results\e2e_eval_36cases_batchrunner.json
```

산출물:
- 배치별 결과: `evals/results/batches/*.json`
- 병합 결과: `evals/results/e2e_eval_36cases_batchrunner.json`
- 배치별 서버 로그(옵션 사용 시): `evals/results/server_logs/*.server.stderr.log`, `*.server.stdout.log`
- 실패 요약 리포트(옵션 사용 시): `evals/results/e2e_eval_failure_summary.json`

### 실행 프리셋

빠른 검증(12케이스 1배치):

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 12 `
  --api-host 127.0.0.1 `
  --api-port 8073 `
  --thread-prefix eval-quick `
  --output .\evals\results\e2e_eval_quick.json
```

전체 검증(36케이스 배치 병합):

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 12 `
  --api-host 127.0.0.1 `
  --api-port 8074 `
  --thread-prefix eval-full `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --health-timeout-sec 30 `
  --batch-output-dir .\evals\results\batches `
  --server-log-dir .\evals\results\server_logs `
  --output .\evals\results\e2e_eval_full.json
```

포트 충돌 시(예: `Only one usage of each socket address`), 자동 포트 선택:

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_eval_batch_runner.py `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 12 `
  --api-host 127.0.0.1 `
  --api-port 8072 `
  --auto-port `
  --auto-port-max-tries 50 `
  --port-step 1 `
  --output .\evals\results\e2e_eval_autoport.json
```

권장 규칙:
- 빠른 검증: `8073`
- 전체 검증: `8074`
- 충돌 시: `--auto-port` 사용

### Soak Test (장시간 안정성)

144요청(36케이스 × 4사이클) 예시:

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_soak_runner.py `
  --cycles 4 `
  --cases .\evals\e2e_eval_cases.jsonl `
  --ingest-path .\evals\docs `
  --batch-size 12 `
  --api-host 127.0.0.1 `
  --api-port 8080 `
  --auto-port `
  --thread-prefix soak-main `
  --max-retries 2 `
  --retry-backoff-sec 1.0 `
  --skip-ingest-after-first `
  --output-dir .\evals\results\soak `
  --output .\evals\results\e2e_soak_144.json
```

산출물:
- 사이클별 결과/실패요약: `evals/results/soak/`
- 최종 요약 리포트: `evals/results/e2e_soak_144.json`

### 리포트 분석(고도화)

E2E/Soak 결과를 자동 분석(실패 유형, top error, source 분포, soak 드리프트):

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_report_analyzer.py `
  --input .\evals\results\e2e_eval_36cases_batchrunner_v2.json `
  --output .\evals\results\analysis_e2e_36.json
```

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_report_analyzer.py `
  --input .\evals\results\e2e_soak_144_v1.json `
  --drift-threshold-pct 10 `
  --output .\evals\results\analysis_soak_144.json
```

자동 경고/실패 처리(임계치 미달 시 exit code 2):

```powershell
cd D:\ProjectRAG\rag_assistant
.\.venv\Scripts\python.exe .\scripts\e2e_report_analyzer.py `
  --input .\evals\results\e2e_eval_36cases_batchrunner_v2.json `
  --min-success-rate 0.98 `
  --min-keyword-pass-rate 0.98 `
  --min-citation-pass-rate 0.98 `
  --max-p90-graph-ms 4000 `
  --fail-on-alert `
  --output .\evals\results\analysis_e2e_alerts.json
```


