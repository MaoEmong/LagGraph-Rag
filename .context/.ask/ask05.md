# ask05.md — 작업일지

- 날짜: 2026-01-28
- Phase: 3 (LangGraph Core)
- 작업 요약:
  - State 스키마 정의: `app/schemas.py`
  - LangGraph 그래프 구성: `app/graph.py`
  - 노드 구현: route/retrieve/generate/finalize
  - 설정 확장: LLM/Embedding 파라미터 추가
  - requirements.txt에 openai/langgraph 추가
- 테스트:
  - 그래프 invoke 스모크 테스트 실행
  - OPENAI_API_KEY 미설정 시 에러 응답 확인
- 다음 작업:
  - Phase4(API Layer)에서 그래프 호출 및 checkpoint 연동
  - OpenAI 키 설정 후 정상 응답 테스트
