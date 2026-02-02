# ask27.md — 작업일지 (상세)

- 날짜: 2026-01-30
- 작업 주제: reranker auto 임계값 스윕 테스트 실행
- 목표:
  - 실제 질의 세트 기준으로 best_distance 분포와 threshold별 rerank 트리거율 측정
  - RERANKER_DISTANCE_THRESHOLD 조정 근거 확보

- 사전 준비:
  - 질의 파일 생성: rag_assistant/queries.txt (총 10개)
  - OPENAI_API_KEY 설정 확인(사용자 설정 완료 상태)

- 실행 과정:
  1) python 실행 경로 확인
     - `python` 명령 미인식
     - `py -3.11`도 미인식
     - 프로젝트 venv 파이썬 사용: `.venv\Scripts\python.exe`
  2) 모듈 경로 오류 발생
     - `ModuleNotFoundError: No module named 'app'`
     - 해결: `PYTHONPATH=.` 설정 후 재실행
  3) 스윕 실행
     - 명령:
       - `PYTHONPATH=. .\.venv\Scripts\python.exe .\scripts\reranker_sweep.py --queries .\queries.txt --thresholds 0.2,0.25,0.3,0.35,0.4 --json`
     - 결과 출력 완료 (명령 자체는 타임아웃 경고 발생했으나 JSON 출력 정상 확보)

- 결과 요약:
  - queries: 10
  - top_k: 5
  - initial_top_k: 20
  - best_distance 분포:
    - min 0.5185 / p50 0.7814 / p75 0.7970 / p90 0.8097 / max 0.8256 / mean 0.7422
  - threshold sweep (0.2~0.4):
    - 모든 임계값에서 trigger_rate=100%
    - trigger 사유는 전부 low_count(문서 수 < top_k)

- 해석/관찰:
  - reranker auto 트리거가 전부 low_count로 발생 → 현재 컬렉션 문서 수가 top_k(5)보다 적은 상태로 추정
  - distance_threshold에 따른 트리거 차이를 보려면 문서 수를 충분히 늘려야 함

- 다음 작업 제안:
  - 실제 문서 인제스트를 충분히 수행(최소 top_k 이상)
  - 동일 스윕 재실행하여 distance 기반 트리거율 확인
  - 필요 시 threshold 후보 구간 재탐색