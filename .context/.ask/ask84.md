# ask84.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 로컬 리랭커(cross-encoder) 도입 1차
- 기준: 11QualityRagPlan.md (Phase D)

---

## 1) 변경 내용

### 1.1 설정 추가
- 파일: `rag_assistant/app/config.py`
- 추가 항목:
  - `reranker_cross_encoder_model` (default: `cross-encoder/ms-marco-MiniLM-L-6-v2`)
  - `reranker_device` (default: `cuda`)

### 1.2 의존성 추가
- 파일: `rag_assistant/requirements.txt`
- 추가:
  - `sentence-transformers`

### 1.3 환경 변수 예시 추가
- 파일: `rag_assistant/.env.example`
- 추가:
  - `RERANKER_CROSS_ENCODER_MODEL`
  - `RERANKER_DEVICE`

### 1.4 retrieve 로직 확장
- 파일: `rag_assistant/app/nodes/retrieve.py`
- 변경:
  - `RERANKER_MODEL=cross-encoder`일 때 로컬 CrossEncoder 사용
  - 모델은 1회 로드 후 캐시(`_CROSS_ENCODER`)
  - `predict()`로 점수 계산 후 `rerank_score` 부여
  - `reranker_score_threshold`로 필터링 가능
  - 기존 임베딩 기반 리랭커 경로는 유지

---

## 2) 테스트

### 2.1 compileall 테스트
- 실행:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall D:\ProjectRAG\rag_assistant\app`
- 확인된 출력(요약):
  - `app/config.py` 컴파일 성공
  - `app/nodes/retrieve.py` 컴파일 성공
  - `app/storage/*` 로딩 성공
- 결과:
  - SyntaxError/ImportError 없이 정상 종료 → 테스트 통과 처리

---

## 3) 비고

- 실제 리랭커 동작 검증은 `sentence-transformers` 설치 및 GPU 환경에서 별도 E2E 테스트 필요
- 현재 단계는 코드/설정/의존성 정합성까지 확보

---

## 4) 다음 작업

- Phase E: 답변 품질 강화(근거 기반 프롬프트 보강 및 재질의 여부 결정)

