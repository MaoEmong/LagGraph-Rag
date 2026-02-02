# 07UnresolvedItems.md — 미해결 항목 정리 v1.1

> 목적: RAG 프로젝트의 미결정 항목을 명확히 하고, 선택지/영향/추천안을 요약한다.
> 기준 문서: 00Info.md, 01Architecture.md, 02ApiSpec.md, 03CliSpec.md, 04GraphSpec.md, 05IngestionSpec.md, 06WorkPlan.md
> 작성일: 2026-01-29

---

## 1. 개요

현재 구현은 Phase 7(품질/안정화)까지 완료되어 핵심 기능은 동작한다. 다만 아래 항목은 문서상 “미결정” 상태이므로, 실제 운영 품질과 확장성을 위해 결정이 필요하다.

---

## 2. 미해결 항목 목록 (총 5개)

1) Embedding 모델
2) Thread 다중 관리 여부
3) Chunk size 최종값
4) Reranker 도입 여부
5) Web UI 프레임워크

---

## 3. 항목별 정리 (결정 반영)

### 3.1 Embedding 모델

- 현재 상태
  - 인제스트 파이프라인은 OpenAI embeddings 호출 구조만 존재.
- 결정 사항
  - OpenAI 임베딩 모델 사용으로 확정.
- 모델 선택
  - `text-embedding-3-small` (가성비 우선)
- 결정 필요 이유
  - 검색 품질과 비용/속도의 핵심 결정 요소.
- 선택지(예시)
  - OpenAI 최신 임베딩 모델(품질 안정, 비용 존재)
  - 오픈소스 임베딩(SBERT 계열 등, 비용 절감/로컬 가능)
- 고려 포인트
  - 문서 도메인(한국어 비중, 길이, 전문성)
  - 월간 인제스트/질의량, 비용 상한
  - 로컬 실행 요구 여부
- 비고
  - 가성비 우선 선택.

---

### 3.2 Thread 다중 관리 여부

- 현재 상태
  - 기본 thread_id 기반 저장/조회 구현됨.
- 결정 사항
  - 우선 단일 thread 운영.
- 결정 필요 이유
  - CLI/향후 Web UI에서 세션 경험과 데이터 관리 방식에 영향을 줌.
- 선택지(예시)
  - 단일 thread 고정(가장 단순, 개인 사용에 적합)
  - 다중 thread 지원(프로젝트/주제별 세션 분리)
- 고려 포인트
  - 실제 사용 패턴(주제 분리가 필요한지)
  - 스토리지 크기 증가와 회수 정책(보존 기간)
- 비고
  - 필요 시 다중 thread로 확장 가능하도록 API/CLI 구조는 유지.

---

### 3.3 Chunk size 최종값

- 현재 상태
  - 문서상 500~800 tokens/overlap 100 기준 제시. 현재 구현은 문자 길이 기준 청킹.
- 결정 사항
  - 청크 크기 값은 현행(500~800 tokens, overlap 100) 유지.
- 결정 필요 이유
  - 검색 품질/속도/비용에 직접 영향.
- 선택지(예시)
  - 500~800 tokens (정확도 우선)
  - 800~1200 tokens (속도/저장 효율 우선)
- 고려 포인트
  - 문서 유형(짧은 메모 vs 긴 보고서)
  - 쿼리 형태(요약/정의/근거 추출)
- 비고
  - 토큰 기반 청킹 전환 여부는 별도 논의.

---

### 3.4 Reranker 도입 여부

- 현재 상태
  - 미결정. 검색 단계는 Chroma top_k 기반.
- 설정 가능한 항목(예시)
  - reranker_on: true/false (기본 false)
  - rerank_top_k: 재정렬 대상 후보 수 (예: 20)
  - reranker_model: 모델명/엔진 선택
  - reranker_timeout_sec: 타임아웃
  - reranker_score_threshold: 최소 점수 기준
  - reranker_batch_size: 배치 크기
- 결정 사항
  - reranker_on=false (기본 미도입)
  - reranker_mode=off (off | auto | always)
  - rerank_top_k=20
  - reranker_model=none
  - reranker_timeout_sec=10
  - reranker_score_threshold=-1.0
  - reranker_distance_threshold=0.6
  - reranker_batch_size=16
- 결정 필요 이유
  - 검색 정확도 개선 가능. 비용/지연 증가.
- 선택지(예시)
  - 미도입: 단순하고 빠름
  - 도입: top_k 후보를 재정렬해 정확도 향상
- 고려 포인트
  - 실제 검색 정답률(현재 기준으로 만족하는지)
  - latency 허용 범위
- 비고
  - 품질 이슈 발견 시 reranker_on=true로 전환 검토.
  - 테스트 기준으로 reranker_on 시 지연 증가, 품질 개선은 뚜렷하지 않음.
  - 조건부 활성화는 reranker_mode=auto로 사용.

---

### 3.5 Web UI 프레임워크

- 현재 상태
  - 문서상 Target은 Web, 구체 프레임워크 미결정.
- 결정 사항
  - 단순 SPA 방식으로 진행.
- 결정 필요 이유
  - UI 개발 시작 시 기술 선택 필요.
- 선택지(예시)
  - React 기반(Next.js 등)
  - Vue 기반
  - 간단한 SPA/정적 페이지
- 고려 포인트
  - 개발 속도 vs 유지보수
  - 배포 환경(단일 서버/간단 호스팅)
- 비고
  - 초기 MVP는 단일 페이지(질의 입력/응답/소스 표시/threads 조회)로 제한.

---

## 4. 결정 체크리스트

- Embedding: OpenAI 사용 + `text-embedding-3-small` 확정
- Thread: 단일 thread 운영 확정
- Chunk: 현행 값 유지 확정, 토큰 기반 전환 여부만 남음
- Reranker: 기본 미도입 및 기본 설정값 확정
- Web UI: 단순 SPA로 진행 확정

---

## 5. 운영 메모(최근 변경)

- route 기본 동작: 질문이 비어있지 않으면 기본적으로 retrieval 경로로 진행
- 인제스트 중복 처리: 동일 파일 내용 해시가 동일하면 스킵, 변경 시 기존 문서/벡터 삭제 후 재저장
- 테스트 우회: PowerShell 한글 깨짐 이슈가 있어 테스트 질문을 영어로 하면 출력 가독성 확보 가능

---

## 6. 다음 액션(제안)

1) 실제 사용 패턴을 위한 샘플 문서 + 질의 세트 확보
2) chunk/embedding 조합 비교 테스트(간단 벤치마크)
3) reranker 조건부 활성화 전략(저품질 케이스에만 on)
4) 다중 thread UX 필요성 설문(자기 사용 기준)

---

작성자: Codex
버전: v1.1


