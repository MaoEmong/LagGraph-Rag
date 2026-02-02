# ask08.md — 작업일지 (상세)

- 날짜: 2026-01-28
- Phase: 5 (Ingestion Pipeline)
- 목표:
  - 문서 인제스트 파이프라인 구현
  - /ingest API 연동
  - 실제 테스트로 동작 검증

- 작업 배경:
  - 05IngestionSpec.md 기준으로 파이프라인 단계(탐색→파싱→클리닝→청킹→메타→임베딩→저장)를 구현
  - Phase4에서 /ingest는 stub 상태였으므로 실제 파이프라인 연결 필요

- 구현 상세:
  1) 파일 탐색
     - 파일: `app/ingest/discovery.py`
     - 함수: discover_files(path, recursive)
     - 처리:
       - 파일 경로면 단일 반환
       - 디렉토리면 glob로 탐색
       - 확장자 필터: .txt/.md/.pdf/.docx
       - 숨김 파일 제외

  2) 파서
     - 파일: `app/ingest/loaders.py`
     - 함수: parse_file(path)
     - 처리:
       - txt/md: UTF-8 read_text
       - pdf: pdfplumber로 페이지 텍스트 추출
       - docx: python-docx 문단 텍스트 합산
       - ParseError 예외 래핑

  3) 클리닝
     - 파일: `app/ingest/cleaning.py`
     - 함수: clean_text(text)
     - 처리:
       - 연속 공백 제거 → 단일 공백으로 정규화
       - strip 적용

  4) 청킹
     - 파일: `app/ingest/chunking.py`
     - 함수: chunk_text(text, chunk_size=800, overlap=100)
     - 처리:
       - 단순 슬라이싱 기반 청킹
       - overlap 적용
       - 마지막 청크 도달 시 즉시 종료
     - 수정 이슈:
       - 종료 조건 누락으로 무한 루프 발생 → MemoryError
       - end >= length 시 break 추가로 해결

  5) 메타데이터/임베딩/저장
     - 파일: `app/ingest/ingest.py`
     - 함수: ingest_path(path, recursive, dry_run)
     - 처리:
       - UUID 기반 parent_id/chunk_id 생성
       - created_at 타임스탬프 기록
       - SHA256 해시 생성(중복 체크용 여지 확보)
       - OpenAI embeddings 호출
         - batch 처리(embedding_batch_size)
         - 오류 시 2회 재시도
         - timeout 설정 반영(openai_timeout_sec)
       - Chroma upsert (ids, embeddings, documents, metadatas)
       - Docstore.save_chunks 저장

  6) API 연동
     - 파일: `app/routes/ingest.py`
     - 변경:
       - dry_run 옵션 추가
       - ingest_path 호출로 stub 제거
       - 예외 발생 시 error 포맷 반환

- 설정/의존성 변경:
  - 설정: `app/config.py`
    - openai_timeout_sec, embedding_batch_size 추가
  - 의존성: `requirements.txt`
    - pdfplumber, python-docx 추가

- 테스트 상세:
  A) 로컬 단위 테스트 (dry_run)
     - 입력 파일: tmp_ingest_test.txt
     - 호출: ingest_path(..., dry_run=True)
     - 결과: IngestResult(files_processed=1, chunks_created=1)

  B) 로컬 단위 테스트 (실제 저장)
     - 입력 파일: tmp_ingest_test.txt
     - 호출: ingest_path(..., dry_run=False)
     - 결과: IngestResult(files_processed=1, chunks_created=1)
     - Chroma/Docstore 저장 성공 확인

  C) API 스모크 테스트
     - 서버: uvicorn app.main:app --port 8002
     - POST /ingest (dry_run=true) → success true
     - POST /chat → success true, citations 포함 확인

- 발생 이슈 및 해결:
  - 증상: ingest_path 실행 중 MemoryError
  - 원인: 청킹 루프 종료 조건 누락으로 무한 반복
  - 조치: chunk_text에서 end >= length 시 break 처리

- 잔여 리스크/메모:
  - 현재 청킹은 토큰 기준이 아니라 문자 길이 기준
  - 대용량 문서 성능/메모리 최적화 필요
  - 인코딩/출력에서 PowerShell 한글 깨짐 가능성 지속

- 다음 작업:
  - Phase6(CLI Client) 착수
