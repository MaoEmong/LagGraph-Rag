# ask40.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 평가셋 36케이스 확장 + 안정 실행 방식 확정 + 최종 검증
- 목표:
  - 기존 12케이스를 최소 30+로 확장(요구사항 충족)
  - 확장된 평가셋을 실제로 실행해 결과 확보
  - 실행 중 서버 끊김 이슈를 우회/관리 가능한 운영 방식으로 정리

---

## 1) 평가셋 확장

### 1.1 변경 파일
- `rag_assistant/evals/e2e_eval_cases.jsonl`

### 1.2 변경 내용
- 기존 12케이스 → **36케이스**로 확장
- 구성:
  - case-001 ~ case-012: ProjectRAG overview 기반
  - case-013 ~ case-024: ingestion notes 기반
  - case-025 ~ case-036: reranker policy 기반
- 각 케이스는 다음 필드를 유지:
  - `id`
  - `question`
  - `expected_keywords`
  - `keyword_match`
  - `min_citations`

### 1.3 질문 설계 원칙
- 질문에 “In the ... notes/policy” 앵커 문구를 넣어 검색 타깃 명확화
- 키워드 매칭은 `all` 기준 유지해 검증 강도 유지
- 사실형 질의 위주로 구성해 정답 판정 자동화 가능성 확보

---

## 2) 평가 스크립트 보강

### 2.1 변경 파일
- `rag_assistant/scripts/e2e_eval.py`

### 2.2 추가 기능
- 케이스 구간 실행 인자 추가:
  - `--start-index` (1-based)
  - `--end-index` (1-based, 0이면 끝까지)
- 목적:
  - 대량 케이스 실행 시 배치 운영 가능
  - 긴 러닝에서 생길 수 있는 서버 불안정 상황 대응

---

## 3) 테스트 및 문제 대응

### 3.1 1차 단일 런(36케이스 연속)
- 실행 포트: 8066
- 결과:
  - case-001~014 성공 후 서버 연결 거부(10061) 재발
  - summary: 14/36 성공
- 관찰:
  - stderr/stdout상 명시적 파이썬 traceback은 없음
  - 운영상 “장시간 단일 서버 연속 평가”가 불안정한 패턴 재확인

### 3.2 대응 전략
- 36케이스를 12개씩 3배치로 분할 실행
- 배치마다 uvicorn 프로세스 신규 기동/종료
- 배치 결과를 병합해 최종 리포트 생성

### 3.3 배치 실행 산출물
- `rag_assistant/evals/results/e2e_eval_36_batch1.json` (1~12)
- `rag_assistant/evals/results/e2e_eval_36_batch2.json` (13~24)
- `rag_assistant/evals/results/e2e_eval_36_batch3.json` (25~36)
- 병합 리포트:
  - `rag_assistant/evals/results/e2e_eval_36cases_final_v2.json`

---

## 4) 최종 결과(병합 기준)

- total_cases: `36`
- success_count: `36` (100%)
- keyword_pass_count: `36` (100%)
- citation_pass_count: `36` (100%)
- client latency:
  - p50 `1950.75ms`
  - p90 `2504.44ms`
  - mean `1988.30ms`
- graph t_total latency:
  - p50 `1846.5ms`
  - p90 `2404ms`
  - mean `1881.78ms`
- fail_count: `0`

---

## 5) 결론

- “필수 작업”인 평가셋 30+ 확장을 완료했고, 36케이스로 확장 검증까지 완료.
- 실행 안정성 이슈는 배치 실행 방식으로 실무적으로 해소 가능함을 확인.
- 현재 평가 체계는
  - 케이스 규모(36),
  - 자동 실행,
  - 정량 리포트(성공/키워드/출처/지연),
  - 운영 우회(배치 분할)
  를 갖춘 상태.

---

## 6) 다음 작업 제안

1. `e2e_eval.py`에 `--batch-size`와 자동 병합 기능 내장(운영 편의화)
2. 실패 시 서버 상태/프로세스 상태를 추가 로깅해 근본 원인 추적
3. 다음 확장 단계로 36 → 50케이스(추론형/복합 질의 포함) 진행

