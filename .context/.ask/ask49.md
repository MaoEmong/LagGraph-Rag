# ask49.md — 작업일지 (상세)

- 날짜: 2026-02-02
- 작업 주제: 평가 리포트 분석 고도화(실패 유형/소스 분포/드리프트)
- 목표:
  - E2E/Soak 결과를 숫자만 보는 수준에서 원인 분석 가능한 형태로 확장
  - 실패 유형 분류, top error, citation source 분포, soak 드리프트 탐지 자동화

---

## 1) 변경 파일

1. `rag_assistant/scripts/e2e_report_analyzer.py` (신규)
2. `rag_assistant/scripts/e2e_eval.py` (상세 필드 확장)
3. `README.md`
4. `OPERATIONS.md`

---

## 2) 분석기 신규 추가

### 2.1 파일
- `scripts/e2e_report_analyzer.py`

### 2.2 지원 입력
- 일반 E2E 리포트(`details` 기반)
- Soak 리포트(`cycles` 기반)

### 2.3 분석 항목
- 공통:
  - success/keyword/citation pass 비율
  - 실패 유형 분류
    - `request_failure`
    - `response_failure`
    - `keyword_miss`
    - `citation_miss`
    - `keyword_and_citation_miss`
  - top error 목록
  - latency 통계(min/p50/p90/max/mean)
  - citation source_path 분포
- Soak 전용:
  - cycle별 평균 지연 추이
  - first vs last graph mean 기준 드리프트(%)
  - 임계치(`--drift-threshold-pct`) 기반 anomaly 판정

---

## 3) e2e_eval 상세 필드 확장

- 파일: `scripts/e2e_eval.py`
- 변경:
  - detail에 `citation_source_paths` 추가
  - citations에서 source_path를 unique+sorted로 저장
- 효과:
  - 후속 분석기에서 source 분포를 정확히 집계 가능

---

## 4) 테스트 수행

### 4.1 분석기 실행 테스트(기존 리포트)

1) E2E 분석:
- 입력: `evals/results/e2e_eval_36cases_batchrunner_v2.json`
- 출력: `evals/results/analysis_e2e_36_v1.json`
- 결과:
  - `report_type=e2e`
  - `success 36/36`
  - `failure_type_counts={'pass': 36}`

2) Soak 분석:
- 입력: `evals/results/e2e_soak_144_v1.json`
- 출력: `evals/results/analysis_soak_144_v1.json`
- 결과:
  - `report_type=soak`
  - `success 144/144`
  - `cycle drift delta_pct ≈ 5.037%`
  - `drift anomaly=False` (threshold 10%)

### 4.2 신규 필드 회귀 테스트

- 3케이스 스모크 리포트 재생성:
  - `evals/results/e2e_eval_smoke3_newfields.json`
- 확인:
  - `SMOKE3_OK 3/3`
  - `citation_source_paths` 필드 존재 및 list 타입 확인

---

## 5) 문서 반영

### 5.1 README.md
- “리포트 분석(고도화)” 섹션 추가
- E2E/Soak 분석 실행 예시 커맨드 추가

### 5.2 OPERATIONS.md
- `11) 리포트 분석(고도화)` 섹션 추가
- 분석 항목 및 커맨드 명시

---

## 6) 결론

- 평가 체계가 “통과율 확인” 단계에서 “원인 분석 가능한 관측 단계”로 고도화됨
- 운영 시 장애/품질 회귀가 발생하면
  - 실패 유형
  - top error
  - source 분포
  - cycle 드리프트
  기반으로 즉시 진단 가능

