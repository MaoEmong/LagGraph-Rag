# ask85.md — 작업일지 (상세)

- 날짜: 2026-02-04
- 작업 주제: 답변 품질 강화(근거 기반 응답 제한) 1차
- 기준: 11QualityRagPlan.md (Phase E)

---

## 1) 변경 내용

### 1.1 설정 추가
- 파일: `rag_assistant/app/config.py`
- 추가 항목:
  - `require_context_for_answer` (default: true)
  - `no_context_message` (default: "제공된 근거가 없어 답변할 수 없습니다.")

### 1.2 프롬프트/응답 로직 강화
- 파일: `rag_assistant/app/nodes/generate.py`
- 변경:
  - system 지시문에 근거 단서 포함을 명시
  - docs/DB 결과가 모두 없으면 즉시 `no_context_message` 반환
  - 근거가 없는 상태에서 모델이 임의 추측하는 경로를 차단

### 1.3 환경 변수 예시 추가
- 파일: `rag_assistant/.env.example`
- 추가:
  - `REQUIRE_CONTEXT_FOR_ANSWER`
  - `NO_CONTEXT_MESSAGE`

### 1.4 문서 반영
- 파일: `.context/04GraphSpec.md`
  - generate 단계에 “근거 없으면 답변 제한” 명시

---

## 2) 테스트

### 2.1 compileall 테스트
- 실행:
  - `D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall D:\ProjectRAG\rag_assistant\app`
- 확인된 출력(요약):
  - `app/config.py` 컴파일 성공
  - `app/nodes/generate.py` 컴파일 성공
  - 기타 모듈 컴파일 정상
- 판정 근거:
  - SyntaxError/ImportError 없이 종료됨 → 테스트 통과

---

## 3) 비고

- 실제 응답 품질 검증은 /ingest + /chat E2E에서 “근거 없음” 케이스로 확인 필요
- 현재 단계는 코드/설정/문서 정합성까지 확보

---

## 4) 다음 작업

- 하이브리드 검색 + parent 확장 + 로컬 리랭커를 통합한 E2E 검증
- 필요 시 re-query(재질의) 노드 추가 검토

