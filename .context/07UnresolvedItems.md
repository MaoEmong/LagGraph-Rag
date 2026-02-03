# 07UnresolvedItems.md — 결정/잔여 항목 정리 v1.2

> 목적: RAG 프로젝트의 결정 사항을 최신 구현 상태에 맞춰 정리하고, 잔여 논의를 명확히 한다.
> 기준 문서: 00Info.md, 01Architecture.md, 02ApiSpec.md, 03CliSpec.md, 04GraphSpec.md, 05IngestionSpec.md, 06WorkPlan.md
> 작성일: 2026-02-03

---

## 1. 개요

본 문서는 과거 “미해결 항목” 목록을 유지하되, **현재 구현과 문서 상태를 동기화한 결정 사항 요약**으로 업데이트한다.

2026-02-03 기준: **미해결 항목 없음** (필요 시 신규 항목 추가)

---

## 2. 결정 사항 요약

1) Embedding 모델
- OpenAI 임베딩 사용 확정
- 모델: `text-embedding-3-small`

2) Thread 관리
- 단일 thread 우선 운영
- 구조는 다중 thread 확장 가능

3) Chunking 정책
- 500~800 tokens, overlap 100 유지
- **토큰 기반 청킹 전환 완료 (tiktoken 기준)**

4) Reranker
- 기본 미도입(reranker_on=false)
- 필요 시 `auto`/`always` 모드로 전환 가능
- 기본 설정: distance threshold 0.6, rerank_top_k 20

5) Web UI
- `/web` 단순 SPA 제공 완료
- 질문/답변/출처, thread 조회/초기화, 인제스트 실행 지원

6) OCR/이미지 인제스트
- 이미지 파일 OCR 인제스트 지원
- OCR 활성화 시 이미지 텍스트를 문서 청크로 저장

---

## 3. 향후 개선 후보(선택)

* 평가셋 70+ 확장 및 난이도 다양화
* CI 자동화(스모크 + 야간 배치 + analyzer 게이트)
* OCR 전처리 옵션 고도화(이진화/리사이즈 등)
* reranker 조건부 활성화 전략 고도화

---

## 4. 변경 메모

- 기존 “토큰 기반 청킹 전환 여부” 미결 항목은 **완료로 전환**
- “Web UI 프레임워크”는 단순 SPA로 확정 및 구현 완료
- 이미지 OCR 인제스트는 구현 완료 상태로 반영

---

작성자: 김해준
버전: v1.2
