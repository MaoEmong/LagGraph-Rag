# ask41.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 배치 실행 + 자동 병합 러너 구현 및 36케이스 확실 검증
- 목표:
  - 긴 평가 실행에서 발생하던 서버 끊김 이슈를 운영 방식으로 흡수
  - 한 번의 명령으로 배치 실행/병합까지 처리
  - 36케이스 전체를 안정적으로 재검증

---

## 1) 구현 내용

### 1.1 신규 스크립트 추가
- 파일: `rag_assistant/scripts/e2e_eval_batch_runner.py`

### 1.2 핵심 기능
1) 케이스 개수 자동 파악 후 배치 분할
   - `--batch-size` 기준으로 `start/end` 범위 계산

2) 배치별 서버 생명주기 관리
   - 각 배치마다 `uvicorn` 신규 기동
   - `/health` 폴링으로 기동 확인
   - 배치 종료 후 프로세스 종료(terminate → kill fallback)

3) 배치별 평가 실행
   - 내부적으로 `scripts/e2e_eval.py`를 서브프로세스로 호출
   - `--start-index/--end-index` 전달
   - 첫 배치만 ingest 수행(기본), 이후 배치는 `--skip-ingest`

4) 결과 자동 병합
   - 배치 JSON들(`evals/results/batches/*.json`)을 모아
   - 단일 merged 결과(`--output`) 생성
   - merged summary는 기존 지표 체계와 동일:
     - success / keyword pass / citation pass
     - client latency / graph latency 통계

---

## 2) 추가 조정(평가셋 안정화)

- 파일: `rag_assistant/evals/e2e_eval_cases.jsonl`
- 수정 케이스:
  - case-007 질문 문구를 모호한 “storage component”에서
  - “metadata/checkpoint storage component”로 명확화
- 이유:
  - 기존 문구에서는 정답이 SQLite/Chroma 모두 가능해 단일 정답 키워드 기준과 충돌

---

## 3) 테스트 수행(확실 검증)

### 3.1 사전 확인
- `e2e_eval_batch_runner.py --help` 실행 확인

### 3.2 1차 전체 실행(36케이스, batch-size=12)
- 출력 파일:
  - `rag_assistant/evals/results/e2e_eval_36cases_batchrunner_v1.json`
- 결과:
  - success 36/36
  - keyword pass 35/36
  - citation pass 36/36
  - fail 1건(case-007, 질문 모호성 이슈)

### 3.3 케이스 문구 수정 후 2차 전체 재실행
- 실행 파라미터(요지):
  - batch-size=12, api-port=8072, retries/backoff 유지
- 출력 파일:
  - `rag_assistant/evals/results/e2e_eval_36cases_batchrunner_v2.json`
- 최종 결과:
  - `total_cases=36`
  - `success_count=36` (100%)
  - `keyword_pass_count=36` (100%)
  - `citation_pass_count=36` (100%)
  - `FAIL_COUNT=0`

---

## 4) 결론

- 배치 러너 도입으로 “확장 평가셋 + 실행 안정성 + 자동 병합”을 한 번에 해결.
- 현재 운영 기준:
  - 평가셋 36케이스
  - 배치 12개 단위 서버 재기동 방식
  - 최종 100% 통과 결과 확보

---

## 5) 다음 작업 제안

1. `README`/`OPERATIONS`에 batch runner 사용법 추가
2. 배치별 서버 stderr 파일 분리 저장(장애 원인 추적 강화)
3. 36 → 50케이스 확장(추론형/복합 질의 포함)


