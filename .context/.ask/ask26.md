# ask26.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: reranker auto 임계값 튜닝 기반 마련 + 벤치마크 스크립트 추가
- 목표:
  - reranker auto 임계값을 튜닝할 수 있는 근거(거리 분포/트리거율)를 수집
  - 실사용 데이터 기준으로 임계값을 조정할 수 있도록 스크립트와 운영 가이드 제공

- 변경 사항 요약:
  1) reranker auto/always 모드에서 초기 검색 크기 확장 로직 보완
     - 기존: RERANKER_ON=true일 때만 initial_top_k=max(top_k, rerank_top_k)
     - 변경: reranker_mode가 auto/always이고 reranker_model이 유효한 경우 확장
     - 목적: auto 모드에서도 충분한 후보를 확보해 rerank 품질을 평가/개선 가능
     - 파일: rag_assistant/app/nodes/retrieve.py

  2) 임계값 스윕 벤치마크 스크립트 추가
     - 파일: rag_assistant/scripts/reranker_sweep.py
     - 기능:
       - queries.txt(질의 1줄 1개) 입력
       - top_k / rerank_top_k 기준으로 initial_top_k 설정
       - 각 질의의 best_distance 분포 수집
       - threshold 후보별 rerank 트리거율과 원인(문서수 부족/점수 없음/거리 기준) 집계
       - 텍스트 요약 또는 JSON 출력 제공
     - 목적: 실제 질의 세트 기반으로 RERANKER_DISTANCE_THRESHOLD를 합리적으로 선택

  3) 운영 문서 업데이트
     - OPERATIONS.md에 튜닝 절차 및 스크립트 실행 방법 추가
     - 파일: OPERATIONS.md

  4) 그래프 명세 업데이트
     - reranker_mode=auto/always 모두 initial_top_k 확장 명시
     - 파일: .context/04GraphSpec.md

- 스크립트 사용 방법(요약):
  - 질의 리스트 작성: queries.txt (한 줄에 하나씩)
  - 실행 예시:
    - python .\scripts\reranker_sweep.py --queries .\queries.txt --thresholds 0.2,0.25,0.3,0.35,0.4
  - 출력 해석:
    - best_distance 분포(p50/p75/p90)와 threshold별 trigger_rate를 비교
    - trigger_rate가 과도하면 임계값을 올리고, 부족하면 내림

- 주의/전제:
  - 스크립트는 OpenAI 임베딩 호출이 필요하므로 OPENAI_API_KEY 설정 필요
  - Chroma DB에 충분한 문서가 인제스트되어 있어야 유효한 분포 확보 가능

- 다음 작업 제안:
  - 실제 질의 세트로 스윕 실행 후 적정 임계값 결정
  - 결과에 따라 RERANKER_DISTANCE_THRESHOLD 기본값 업데이트
  - 필요 시 threshold 후보 구간 재탐색(예: 0.22~0.33 구간 세분화)