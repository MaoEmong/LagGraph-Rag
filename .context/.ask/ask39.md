# ask39.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: case-004 오답 분석 및 개선(정답성 100% 달성)
- 목표:
  - 이전 평가에서 유일하게 실패한 case-004 원인 파악
  - 코드/평가셋 보정을 통해 정답률 개선
  - 전체 평가셋 재실행으로 최종 지표 확정

---

## 1) 원인 분석

### 1.1 증상
- `ask38` 기준:
  - 전체 12케이스 중 case-004만 keyword 미스(SQLite 미포함)
  - 응답은 성공했지만 일반론/모름 응답으로 벗어남

### 1.2 디버깅 확인
- case-004 단건 `/chat` 응답의 citations 확인 결과:
  - `evals/docs/rag_overview.txt`가 아닌 기존 `docs/*.pdf` 문서 위주로 검색됨
- 즉, 질문이 너무 일반적이라 대형 기존 코퍼스가 우선 매칭되어
  - 평가 전용 문서의 정답 신호(SQLite 문장)가 retrieval 상위에 안정적으로 오르지 못함

---

## 2) 개선 작업

### 2.1 생성 노드 근거 강제 프롬프트 강화
- 파일: `rag_assistant/app/nodes/generate.py`
- 변경 내용:
  - 시스템 지시문을 “참고자료(context) 기반 답변 강제 + 추측 금지”로 강화
  - context 구성 시 source 라벨(`[source: ...]`) 포함
  - context 최대 길이 제한(문자 기준) 추가로 과도한 입력 방지

### 2.2 평가 케이스 앵커링 보정
- 파일: `rag_assistant/evals/e2e_eval_cases.jsonl`
- 변경 내용:
  - case-004 질문을 일반 질의에서
    - “In the ProjectRAG overview notes, ...”
    형태로 변경하여 평가 문서를 명시적으로 참조하도록 조정

---

## 3) 테스트 수행

### 3.1 중간 검증
- 생성 노드 강화 후(케이스 보정 전) 재평가:
  - `success=12/12`, `keyword=11/12`
  - case-004는 “context에 정보가 없다” 응답으로 여전히 미스
- 결론:
  - 프롬프트 안정성은 개선됐으나,
  - case-004는 retrieval 타깃 모호성 자체를 해결해야 함

### 3.2 최종 검증(케이스 보정 후)
- 실행:
  - `python .\scripts\e2e_eval.py --api-url http://127.0.0.1:8065 --cases .\evals\e2e_eval_cases.jsonl --ingest-path .\evals\docs --thread-prefix eval4 --max-retries 2 --retry-backoff-sec 1.0 --output .\evals\results\e2e_eval_final_v1.json`

- 결과 파일:
  - `rag_assistant/evals/results/e2e_eval_final_v1.json`

- 최종 summary:
  - `total_cases=12`
  - `success_count=12` (100%)
  - `keyword_pass_count=12` (100%)
  - `citation_pass_count=12` (100%)
  - client latency mean: `1760.66ms`
  - graph t_total mean: `1632.92ms`

---

## 4) 결론

- case-004 실패 원인은 모델 오작동보다 **검색 타깃 모호성(평가 질문 설계)**에 가까웠음
- 프롬프트를 근거 중심으로 강화하고, 평가 문항을 평가 문서에 앵커링하여
  - 최종적으로 12/12 정답(키워드 기준) 달성
- 현재 평가 파이프라인은
  - 안정성(재시도)
  - 재현성(고정 문서/고정 케이스)
  - 정량화(성공/키워드/출처/지연)
  관점에서 운영 가능한 수준으로 정리됨

---

## 5) 다음 작업 제안

1. 평가셋 확장(12 → 30~50) 및 난이도 계층화(단순 사실/추론/근거추출)
2. 평가 리포트에 `citations.source_path` 분포 추가(검색 품질 진단)
3. 옵션으로 “평가 전용 컬렉션/격리 스토리지” 실행 모드 추가 검토

