from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_WEB_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RAG Assistant 웹 MVP</title>
  <style>
    :root {
      --bg: #f6f3ed;
      --paper: #fffaf2;
      --ink: #1f1d1a;
      --muted: #72695f;
      --brand: #0f6b4d;
      --line: #dbd1c4;
      --ok: #0a7c5a;
      --err: #b62323;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 16% 14%, rgba(228, 87, 46, .20), transparent 36%),
        radial-gradient(circle at 88% 20%, rgba(15, 107, 77, .18), transparent 34%),
        linear-gradient(160deg, #f8f4ec 0%, #f2ece1 44%, #efe6d7 100%);
      font-family: "Segoe UI", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
      padding: 24px;
    }
    .shell {
      max-width: 980px;
      margin: 0 auto;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
      box-shadow: 0 12px 36px rgba(31, 29, 26, 0.10);
    }
    .head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(90deg, rgba(15, 107, 77, .08), rgba(228, 87, 46, .08));
    }
    .title { margin: 0; font-size: 20px; letter-spacing: .2px; }
    .hint { margin: 4px 0 0; color: var(--muted); font-size: 13px; }
    .status { font-size: 12px; color: var(--muted); }
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      padding: 16px 20px 20px;
    }
    @media (min-width: 860px) {
      .grid { grid-template-columns: 1.2fr .8fr; }
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      background: #fffdf9;
    }
    label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 6px; }
    input, textarea, button, select {
      width: 100%;
      font: inherit;
      border-radius: 10px;
    }
    input, textarea, select {
      border: 1px solid var(--line);
      padding: 10px 11px;
      background: #fff;
      color: var(--ink);
    }
    textarea { min-height: 112px; resize: vertical; }
    .row { display: grid; grid-template-columns: 1fr; gap: 10px; }
    @media (min-width: 640px) { .row { grid-template-columns: 1fr 1fr; } }
    button {
      border: none;
      background: linear-gradient(90deg, var(--brand), #17825f);
      color: #fff;
      padding: 11px 12px;
      cursor: pointer;
      font-weight: 600;
      margin-top: 10px;
    }
    button:hover { filter: brightness(1.03); }
    .ghost {
      background: #fff;
      color: var(--ink);
      border: 1px solid var(--line);
    }
    .msg {
      margin-top: 10px;
      font-size: 13px;
      min-height: 18px;
    }
    .ok { color: var(--ok); }
    .err { color: var(--err); }
    .answer {
      white-space: pre-wrap;
      line-height: 1.45;
      font-size: 14px;
      min-height: 84px;
    }
    .sources {
      margin: 8px 0 0;
      padding-left: 18px;
      font-size: 13px;
    }
    .mono { font-family: Consolas, "Courier New", monospace; font-size: 12px; color: var(--muted); }
    .mono-block { font-family: Consolas, "Courier New", monospace; font-size: 12px; color: var(--muted); white-space: pre-wrap; }
    details.advanced {
      margin-top: 10px;
      border: 1px dashed var(--line);
      border-radius: 10px;
      padding: 8px 10px 10px;
      background: #fff;
    }
    details.advanced > summary {
      cursor: pointer;
      font-size: 13px;
      color: var(--muted);
      user-select: none;
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="head">
      <div>
        <h1 class="title">RAG Assistant 웹 MVP</h1>
        <p class="hint">질문을 입력하고 /chat 결과와 출처를 확인하세요.</p>
      </div>
      <div class="status" id="healthStatus">상태 확인 중...</div>
    </section>
    <section class="grid">
      <article class="card">
        <div>
          <label for="threadSelect">저장된 스레드</label>
          <select id="threadSelect"></select>
        </div>

        <details class="advanced">
          <summary>고급 설정 (스레드 ID 직접 입력)</summary>
          <div style="margin-top:8px;">
            <label for="threadId">스레드 ID</label>
            <input id="threadId" value="web-mvp" />
          </div>
        </details>

        <div style="margin-top:10px;">
          <label for="question">질문</label>
          <textarea id="question">ProjectRAG 개요 문서에서 사용한 API 프레임워크는 무엇인가요?</textarea>
        </div>
        <div class="row">
          <button id="sendBtn">/chat 요청 보내기</button>
          <button id="refreshBtn" class="ghost">스레드 새로고침</button>
        </div>
        <div class="row">
          <button id="resetBtn" class="ghost">현재 스레드 초기화</button>
          <button id="clearBtn" class="ghost">결과 영역 비우기</button>
        </div>
        <div class="msg" id="msg"></div>
      </article>

      <article class="card">
        <label for="ingestPath">인제스트 경로</label>
        <input id="ingestPath" value="./evals/docs" />
        <div class="row" style="margin-top:10px;">
          <div>
            <label for="ingestRecursive">하위 폴더 포함</label>
            <select id="ingestRecursive">
              <option value="true" selected>예 (true)</option>
              <option value="false">아니오 (false)</option>
            </select>
          </div>
          <div>
            <label for="ingestDryRun">드라이런</label>
            <select id="ingestDryRun">
              <option value="false" selected>실제 실행 (false)</option>
              <option value="true">검증만 (true)</option>
            </select>
          </div>
        </div>
        <button id="ingestBtn">/ingest 실행</button>
        <div class="msg" id="ingestMsg"></div>
        <div id="ingestMeta" class="mono"></div>
      </article>

      <article class="card">
        <label>답변</label>
        <div id="answer" class="answer"></div>
        <label style="margin-top:10px;">출처</label>
        <ul id="sources" class="sources"></ul>
        <label style="margin-top:10px;">DB 결과</label>
        <div id="dbResult" class="mono-block"></div>
        <div id="meta" class="mono"></div>
      </article>
    </section>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);
    const msg = (text, isErr = false) => {
      const el = $("msg");
      el.className = "msg " + (isErr ? "err" : "ok");
      el.textContent = text || "";
    };
    const ingestMsg = (text, isErr = false) => {
      const el = $("ingestMsg");
      el.className = "msg " + (isErr ? "err" : "ok");
      el.textContent = text || "";
    };

    async function checkHealth() {
      try {
        const res = await fetch("/health");
        const data = await res.json();
        $("healthStatus").textContent = data?.success ? "상태: 정상" : "상태: 실패";
      } catch (_) {
        $("healthStatus").textContent = "상태: 실패";
      }
    }

    async function loadThreads() {
      try {
        const res = await fetch("/threads");
        const data = await res.json();
        const threads = data?.data?.threads || [];
        const select = $("threadSelect");
        select.innerHTML = "";
        for (const t of threads) {
          const opt = document.createElement("option");
          opt.value = t;
          opt.textContent = t;
          select.appendChild(opt);
        }
        if (threads.length > 0) {
          $("threadId").value = threads[0];
        }
      } catch (err) {
        msg("스레드 목록 조회 실패: " + err, true);
      }
    }

    async function sendChat() {
      const threadId = $("threadId").value.trim() || "web-mvp";
      const question = $("question").value.trim();
      if (!question) {
        msg("질문을 입력해 주세요.", true);
        return;
      }
      msg("질문 전송 중...");
      $("sendBtn").disabled = true;
      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ thread_id: threadId, question }),
        });
        const data = await res.json();
        if (!data?.success) {
          $("answer").textContent = "";
          $("sources").innerHTML = "";
          $("meta").textContent = "";
          $("dbResult").textContent = "";
          msg("chat 요청 실패: " + (data?.error?.message || "알 수 없는 오류"), true);
          return;
        }

        const payload = data.data || {};
        $("answer").textContent = payload.answer || "";
        const sources = payload.citations || [];
        $("sources").innerHTML = "";
        for (const s of sources) {
          const li = document.createElement("li");
          li.textContent = (s.source_path || "알 수 없음") + " (" + (s.chunk_id || "") + ")";
          $("sources").appendChild(li);
        }
        const total = payload?.tokens?.total ?? "-";
        const tTotal = payload?.timing?.t_total_ms ?? "-";
        const dbCount = payload?.db_result?.row_count ?? "-";
        $("meta").textContent = `tokens.total=${total} | timing.t_total_ms=${tTotal} | db.row_count=${dbCount}`;
        $("dbResult").textContent = payload?.db_result
          ? JSON.stringify(payload.db_result, null, 2)
          : "";
        msg("완료");
      } catch (err) {
        msg("요청 오류: " + err, true);
      } finally {
        $("sendBtn").disabled = false;
      }
    }

    async function runIngest() {
      const path = $("ingestPath").value.trim();
      const recursive = $("ingestRecursive").value === "true";
      const dryRun = $("ingestDryRun").value === "true";
      if (!path) {
        ingestMsg("인제스트 경로를 입력해 주세요.", true);
        return;
      }
      ingestMsg("인제스트 실행 중...");
      $("ingestBtn").disabled = true;
      try {
        const res = await fetch("/ingest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path, recursive, dry_run: dryRun }),
        });
        const data = await res.json();
        if (!data?.success) {
          $("ingestMeta").textContent = "";
          ingestMsg("ingest 실패: " + (data?.error?.message || "알 수 없는 오류"), true);
          return;
        }
        const m = data.data || {};
        $("ingestMeta").textContent =
          `files_processed=${m.files_processed ?? "-"} | chunks_created=${m.chunks_created ?? "-"} | duration_ms=${m.duration_ms ?? "-"}`;
        ingestMsg("인제스트 완료");
      } catch (err) {
        ingestMsg("인제스트 요청 오류: " + err, true);
      } finally {
        $("ingestBtn").disabled = false;
      }
    }

    async function resetThread() {
      const threadId = $("threadId").value.trim();
      if (!threadId) {
        msg("스레드 ID가 필요합니다.", true);
        return;
      }
      if (!confirm(`스레드 '${threadId}' 를 초기화할까요?`)) {
        return;
      }

      msg("스레드 초기화 중...");
      $("resetBtn").disabled = true;
      try {
        const res = await fetch("/threads/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ thread_id: threadId }),
        });
        const data = await res.json();
        if (!data?.success) {
          msg("초기화 실패: " + (data?.error?.message || "알 수 없는 오류"), true);
          return;
        }
        msg("스레드 초기화 완료");
        await loadThreads();
      } catch (err) {
        msg("초기화 요청 오류: " + err, true);
      } finally {
        $("resetBtn").disabled = false;
      }
    }

    function clearOutput() {
      $("answer").textContent = "";
      $("sources").innerHTML = "";
      $("meta").textContent = "";
      $("dbResult").textContent = "";
      msg("출력 영역을 비웠습니다.");
    }

    $("sendBtn").addEventListener("click", sendChat);
    $("ingestBtn").addEventListener("click", runIngest);
    $("refreshBtn").addEventListener("click", loadThreads);
    $("resetBtn").addEventListener("click", resetThread);
    $("clearBtn").addEventListener("click", clearOutput);
    $("threadSelect").addEventListener("change", (e) => {
      $("threadId").value = e.target.value;
    });

    checkHealth();
    loadThreads();
  </script>
</body>
</html>
"""


@router.get("/web", response_class=HTMLResponse)
def web_index() -> HTMLResponse:
    return HTMLResponse(_WEB_HTML)
