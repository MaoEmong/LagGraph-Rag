# ask38.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: E2E 평가 스크립트 재시도(backoff) 로직 추가 + 재테스트
- 목표:
  - `/chat` 연속 호출 중 일시적 연결 실패에 대한 내성 강화
  - 동일 평가셋으로 재실행하여 완주율/지표 개선 여부 확인

---

## 1) 변경 배경

- 이전 실행(`ask37`)에서 case-005 이후 연결 끊김(`10054`, `10061`)이 발생하여 12케이스를 완주하지 못함.
- 평가 스크립트가 단일 실패에 취약했기 때문에, 요청 단에 재시도/백오프를 넣어 신뢰도를 높이기로 결정.

---

## 2) 코드 변경 사항

- 수정 파일:
  - `rag_assistant/scripts/e2e_eval.py`

- 핵심 변경:
  1) 공통 HTTP 호출 함수 `_post_json(...)` 확장
     - 입력 인자 추가:
       - `max_retries`
       - `retry_backoff_sec`
     - 동작:
       - `requests` 예외 발생 시 재시도
       - 재시도 간 대기 시간은 지수 백오프(`base * 2^attempt`)
       - 재시도 초과 시 마지막 예외를 그대로 반환

  2) `ingest`/`chat` 호출 함수에 재시도 옵션 전달
     - `_run_ingest(...)`
     - `_run_chat(...)`

  3) 평가 실행 함수 `run_eval(...)` 시그니처 확장
     - `max_retries`, `retry_backoff_sec` 전달받아 케이스별 `/chat` 호출에 적용

  4) CLI 인자 추가
     - `--max-retries` (기본 2)
     - `--retry-backoff-sec` (기본 1.0)

  5) 결과 메타에 재시도 설정 포함
     - `meta.max_retries`
     - `meta.retry_backoff_sec`

---

## 3) 테스트 수행

### 3.1 실행 방식

- 서버와 평가를 **동일 PowerShell 실행 블록**에서 처리해 프로세스 생존성을 확보:
  1) uvicorn(`8061`) 시작
  2) `/health` 확인
  3) `e2e_eval.py` 실행
  4) 결과 확인 후 서버 종료

### 3.2 실행 커맨드(핵심)

- `python .\scripts\e2e_eval.py --api-url http://127.0.0.1:8061 --cases .\evals\e2e_eval_cases.jsonl --ingest-path .\evals\docs --thread-prefix eval2 --max-retries 2 --retry-backoff-sec 1.0 --output .\evals\results\e2e_eval_retry.json`

### 3.3 결과 요약

- 저장 결과 파일:
  - `rag_assistant/evals/results/e2e_eval_retry.json`

- summary:
  - `total_cases=12`
  - `success_count=12` (`success_rate=1.0`)
  - `keyword_pass_count=11` (`keyword_pass_rate=0.9167`)
  - `citation_pass_count=12` (`citation_pass_rate=1.0`)

- latency:
  - client mean: `2641.80ms`
  - graph t_total mean: `2524.25ms`

- ingest 결과:
  - `files_processed=0`, `chunks_created=0`
  - 해시 중복 스킵 정책 정상 동작(기존 eval docs 재사용)

---

## 4) 관찰 사항

- 완주율은 100%로 개선되어, 최소한 평가 파이프라인의 안정성은 확보됨.
- 단일 케이스(case-004)는 키워드(SQLite) 미매치:
  - 성공 응답은 반환했지만 답변 내용이 일반론으로 벗어남.
  - 즉, 시스템 장애 이슈와 별개로 LLM 정답성 편차는 여전히 존재.

---

## 5) 결론

- 재시도(backoff) 적용 후 평가 실행 안정성이 유의미하게 개선됨.
- 고정 평가셋 + 자동 평가 + 결과 파일 저장 흐름이 운영 가능한 수준으로 정착.
- 이후 과제는 안정성보다 **정답성(키워드 미스 케이스) 개선**으로 전환 가능.

---

## 6) 다음 작업 제안

1. case-004 같은 오답 케이스에 대해 프롬프트/컨텍스트 제한 정책 점검
2. `answer_preview` 외에 원문 답변 전체 저장 옵션 추가(오답 분석용)
3. 평가셋을 12 → 30+로 확장해 분산/신뢰구간 확보

