# 03CliSpec.md — CLI 명세서 v1.1

> 기준 문서: `00Info.md`, `01Architecture.md`, `02ApiSpec.md`

---

## 1. 목적

본 문서는 개인용 AI 비서 RAG 시스템의 **CLI(Command Line Interface) 동작 규격**을 정의한다.

목표:

* API 서버(FastAPI)를 사용하는 표준 클라이언트 제공
* 반복 작업 최소화
* 자동화 및 Codex CLI 기반 개발에 적합한 인터페이스 제공

---

## 2. 기본 정보

### 2.1 실행 파일

```
assistant
```

### 2.2 기본 구조

```
assistant <command> [options]
```

### 2.3 서버 설정

기본 서버 주소:

```
http://localhost:8000
```

환경 변수로 변경 가능:

```
RAG_API_URL
```

---

## 3. 전역 옵션

| 옵션        | 설명            |
| --------- | ------------- |
| --help    | 도움말 출력        |
| --version | CLI 버전 출력     |
| --json    | JSON 원본 응답 출력 |
| --api-key | API 키 지정      |

---

## 4. 명령어 목록

| 명령어     | 설명           |
| ------- | ------------ |
| chat    | 대화 시작 / 질문   |
| ingest  | 문서 인제스트      |
| threads | thread 목록 조회 |
| reset   | thread 초기화   |
| stats   | 서버 상태 정보     |
| config  | CLI 설정 관리    |

---

## 5. chat 명령어

### 5.1 설명

서버에 질문을 전송하고 답변을 출력한다.

### 5.2 사용법

```
assistant chat "질문 내용"
```

### 5.3 옵션

| 옵션       | 설명        | 기본값     |
| -------- | --------- | ------- |
| --thread | thread ID | default |
| --stream | 스트리밍 출력   | false   |

### 5.4 동작 예시

```
$ assistant chat "이 프로젝트 구조 설명해줘"

[AI]
이 프로젝트는 FastAPI, LangGraph, Chroma 기반으로...
```

### 5.5 내부 처리

* POST /chat 호출
* thread_id 전달
* 응답 파싱 후 포맷팅 출력

---

## 6. ingest 명령어

### 6.1 설명

로컬 파일 또는 디렉토리를 RAG 데이터 소스로 등록한다.

### 6.2 사용법

```
assistant ingest ./docs
```

### 6.3 옵션

| 옵션          | 설명           | 기본값   |
| ----------- | ------------ | ----- |
| --recursive | 하위 폴더 포함     | true  |
| --dry-run   | 실제 저장 없이 테스트 | false |

### 6.4 동작 예시

```
$ assistant ingest ./docs

✔ Files processed: 12
✔ Chunks created: 248
✔ Time: 5.2s
```

### 6.5 내부 처리

* POST /ingest 호출

---

## 7. threads 명령어

### 7.1 설명

저장된 thread 목록 조회

### 7.2 사용법

```
assistant threads
```

### 7.3 내부 처리

* GET /threads 호출

---

## 8. reset 명령어

### 8.1 설명

특정 thread 상태 초기화

### 8.2 사용법

```
assistant reset default
```

### 8.3 옵션

| 옵션      | 설명       |
| ------- | -------- |
| --force | 확인 없이 실행 |

### 8.4 내부 처리

* POST /threads/reset 호출

---

## 9. stats 명령어

### 9.1 설명

서버 상태 출력

### 9.2 사용법

```
assistant stats
```

### 9.3 내부 처리

* GET /health 호출

---

## 10. config 명령어

### 10.1 설명

CLI 설정 관리

### 10.2 하위 명령어

| 명령어                      | 설명       |
| ------------------------ | -------- |
| config show              | 현재 설정 출력 |
| config set <key> <value> | 설정 변경    |
| config reset             | 초기화      |

### 10.3 설정 항목

| 키              | 설명          |
| -------------- | ----------- |
| api_url        | 서버 주소       |
| default_thread | 기본 thread   |
| output_format  | text / json |

### 10.4 저장 위치

```
~/.rag_assistant/config.json
```

---

## 11. 출력 포맷

### 11.1 기본(text)

```
[AI]
답변 내용

[Sources]
- /docs/architecture.md
```

### 11.2 JSON 모드

```
assistant chat "질문" --json
```

---

## 12. 오류 처리

| 상황     | 동작             |
| ------ | -------------- |
| 서버 미응답 | 재시도 2회 후 오류 출력 |
| 인증 실패  | 오류 메시지 출력      |
| 잘못된 입력 | 도움말 출력         |

---

## 13. 비기능 요구사항

* Windows / macOS / Linux 지원
* Python 기반 실행 파일 패키징 가능 구조
* UTF-8 출력

운영 메모:

* Windows PowerShell 환경에서 한글 출력이 깨질 수 있음
* 테스트 시에는 질문에 "Answer in English"를 붙여 영어 응답을 받으면 가독성 확보 가능

---

작성자: 김해준
작성일: 2026-01-29
버전: v1.1
