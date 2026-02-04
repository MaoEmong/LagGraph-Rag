# ask78.md 작업일지 (상세)

- 날짜: 2026-02-03
- 작업 주제: 문서 품질/구조 개선 가이드 정리 + 전처리(cleaning) 강화
- 사용자 요청: 데이터 품질/문서 구조 개선 작업 우선 진행

---

## 1) 목표

1. 문서 품질/구조 가이드 신규 문서화
2. 인제스트 전처리 규칙 강화
3. README 문서 목록 갱신
4. 테스트 수행

---

## 2) 변경 파일 목록

### 2.1 신규 파일

1. `.context/10DocQualitySpec.md`
2. `.context/.ask/ask78.md`

### 2.2 수정 파일

1. `rag_assistant/app/ingest/cleaning.py`
2. `.context/05IngestionSpec.md`
3. `README.md`

---

## 3) 구현 상세

### 3.1 cleaning 강화

- 개행 정규화(\r\n → \n)
- 탭 → 공백
- 연속 공백 축약
- 3줄 이상 연속 개행은 2줄로 축약
- 줄 단위 trim 후 앞/뒤 빈 줄 제거

### 3.2 문서 가이드(신규)

- 디렉터리 구조/파일명 규칙
- 제목/섹션/코드블록 권장
- 인제스트 품질 개선 팁

---

## 4) 문서 반영

- `05IngestionSpec.md` Cleaning 규칙 업데이트
- `README.md` 문서 목록에 `10DocQualitySpec.md` 추가

---

## 5) 테스트

```powershell
D:\ProjectRAG\rag_assistant\.venv\Scripts\python.exe -m compileall rag_assistant\app
```

결과: 정상 통과

