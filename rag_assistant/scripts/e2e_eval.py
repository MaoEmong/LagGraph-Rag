import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
from requests import Response


def _load_cases(path: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {lineno}: {exc}") from exc
            if "id" not in row or "question" not in row:
                raise ValueError(f"Missing required keys (id/question) at line {lineno}")
            cases.append(row)
    if not cases:
        raise ValueError("No evaluation cases found.")
    return cases


def _slice_cases(cases: List[Dict[str, Any]], start_index: int, end_index: int) -> List[Dict[str, Any]]:
    if start_index < 1:
        raise ValueError("--start-index must be >= 1")
    if end_index > 0 and end_index < start_index:
        raise ValueError("--end-index must be >= --start-index")
    start = start_index - 1
    end = end_index if end_index > 0 else len(cases)
    sliced = cases[start:end]
    if not sliced:
        raise ValueError("No cases selected by the given start/end range.")
    return sliced


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    if pct <= 0:
        return min(values)
    if pct >= 1:
        return max(values)
    ordered = sorted(values)
    idx = int(math.ceil(pct * len(ordered))) - 1
    idx = max(0, min(idx, len(ordered) - 1))
    return ordered[idx]


def _compute_latency_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {}
    return {
        "count": len(values),
        "min_ms": min(values),
        "p50_ms": statistics.median(values),
        "p90_ms": _percentile(values, 0.90),
        "max_ms": max(values),
        "mean_ms": statistics.fmean(values),
    }


def _contains_keyword(answer: str, keyword: str) -> bool:
    return keyword.lower() in answer.lower()


def _score_keyword(answer: str, keywords: List[str], mode: str) -> Tuple[bool, int]:
    if not keywords:
        return True, 0
    hits = sum(1 for kw in keywords if _contains_keyword(answer, kw))
    mode = (mode or "any").lower()
    if mode == "all":
        return hits == len(keywords), hits
    return hits >= 1, hits


def _post_json(
    base_url: str,
    path: str,
    payload: Dict[str, Any],
    timeout: float,
    max_retries: int,
    retry_backoff_sec: float,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + path
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            response: Response = requests.post(url, json=payload, timeout=timeout)
            # Retry only on transient server-side failures.
            if response.status_code >= 500:
                response.raise_for_status()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            sleep_sec = retry_backoff_sec * (2**attempt)
            time.sleep(sleep_sec)

    if last_error is not None:
        raise last_error
    raise RuntimeError("Unexpected request failure without exception.")


def _run_ingest(
    base_url: str,
    ingest_path: str,
    timeout: float,
    max_retries: int,
    retry_backoff_sec: float,
) -> Dict[str, Any]:
    payload = {
        "path": ingest_path,
        "recursive": True,
        "dry_run": False,
    }
    return _post_json(base_url, "/ingest", payload, timeout, max_retries, retry_backoff_sec)


def _run_chat(
    base_url: str,
    thread_id: str,
    question: str,
    timeout: float,
    max_retries: int,
    retry_backoff_sec: float,
) -> Tuple[Dict[str, Any], float]:
    payload = {
        "thread_id": thread_id,
        "question": question,
    }
    start = time.perf_counter()
    result = _post_json(base_url, "/chat", payload, timeout, max_retries, retry_backoff_sec)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result, elapsed_ms


def run_eval(
    base_url: str,
    cases: List[Dict[str, Any]],
    thread_prefix: str,
    timeout: float,
    max_retries: int,
    retry_backoff_sec: float,
) -> Dict[str, Any]:
    details: List[Dict[str, Any]] = []
    total = len(cases)
    success_count = 0
    keyword_pass_count = 0
    citation_pass_count = 0
    latency_values: List[float] = []
    graph_latency_values: List[float] = []

    for idx, case in enumerate(cases, start=1):
        case_id = str(case["id"])
        question = str(case["question"])
        expected_keywords = [str(x) for x in case.get("expected_keywords", [])]
        keyword_mode = str(case.get("keyword_match", "any"))
        min_citations = int(case.get("min_citations", 0))
        thread_id = f"{thread_prefix}-{idx:03d}"

        success = False
        error: str = ""
        answer = ""
        citations: List[Dict[str, Any]] = []
        timing_total = None
        elapsed_ms = 0.0
        keyword_pass = False
        keyword_hits = 0
        citation_pass = False

        try:
            response, elapsed_ms = _run_chat(
                base_url=base_url,
                thread_id=thread_id,
                question=question,
                timeout=timeout,
                max_retries=max_retries,
                retry_backoff_sec=retry_backoff_sec,
            )
            success = bool(response.get("success"))
            if success:
                data = response.get("data") or {}
                answer = str(data.get("answer") or "")
                citations = data.get("citations") or []
                timing = data.get("timing") or {}
                timing_total = timing.get("t_total_ms")
                keyword_pass, keyword_hits = _score_keyword(answer, expected_keywords, keyword_mode)
                citation_pass = len(citations) >= min_citations
            else:
                err_obj = response.get("error") or {}
                error = str(err_obj.get("message") or "unknown error")
        except Exception as exc:  # pylint: disable=broad-except
            error = str(exc)

        if success:
            success_count += 1
            if keyword_pass:
                keyword_pass_count += 1
            if citation_pass:
                citation_pass_count += 1
        if elapsed_ms > 0:
            latency_values.append(elapsed_ms)
        if isinstance(timing_total, (int, float)):
            graph_latency_values.append(float(timing_total))

        details.append(
            {
                "id": case_id,
                "thread_id": thread_id,
                "question": question,
                "success": success,
                "error": error,
                "expected_keywords": expected_keywords,
                "keyword_mode": keyword_mode,
                "keyword_hits": keyword_hits,
                "keyword_pass": keyword_pass,
                "min_citations": min_citations,
                "citation_count": len(citations),
                "citation_source_paths": sorted(
                    {
                        str(citation.get("source_path") or "")
                        for citation in citations
                        if isinstance(citation, dict) and citation.get("source_path")
                    }
                ),
                "citation_pass": citation_pass,
                "elapsed_ms": round(elapsed_ms, 2),
                "graph_t_total_ms": timing_total,
                "answer_preview": answer[:160],
            }
        )

    return {
        "summary": {
            "total_cases": total,
            "success_count": success_count,
            "success_rate": (success_count / total) if total else 0.0,
            "keyword_pass_count": keyword_pass_count,
            "keyword_pass_rate": (keyword_pass_count / total) if total else 0.0,
            "citation_pass_count": citation_pass_count,
            "citation_pass_rate": (citation_pass_count / total) if total else 0.0,
            "client_latency": _compute_latency_stats(latency_values),
            "graph_total_latency": _compute_latency_stats(graph_latency_values),
        },
        "details": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="E2E evaluation for /chat responses.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000", help="Base API URL.")
    parser.add_argument(
        "--cases",
        default="./evals/e2e_eval_cases.jsonl",
        help="JSONL file path for evaluation cases.",
    )
    parser.add_argument(
        "--ingest-path",
        default="./evals/docs",
        help="Path to ingest before evaluation.",
    )
    parser.add_argument("--skip-ingest", action="store_true", help="Skip ingest step.")
    parser.add_argument("--thread-prefix", default="eval", help="Thread ID prefix.")
    parser.add_argument("--timeout-sec", type=float, default=60.0, help="HTTP timeout in seconds.")
    parser.add_argument("--max-retries", type=int, default=2, help="Max retries on request failures.")
    parser.add_argument(
        "--retry-backoff-sec",
        type=float,
        default=1.0,
        help="Base backoff seconds. Actual wait is exponential.",
    )
    parser.add_argument("--output", default="", help="Write JSON result to this path.")
    parser.add_argument("--start-index", type=int, default=1, help="1-based start index of cases to run.")
    parser.add_argument("--end-index", type=int, default=0, help="1-based end index of cases to run (0 means all).")

    args = parser.parse_args()
    cases = _slice_cases(_load_cases(Path(args.cases)), args.start_index, args.end_index)

    ingest_result = None
    if not args.skip_ingest:
        ingest_result = _run_ingest(
            base_url=args.api_url,
            ingest_path=args.ingest_path,
            timeout=args.timeout_sec,
            max_retries=args.max_retries,
            retry_backoff_sec=args.retry_backoff_sec,
        )
        if not ingest_result.get("success"):
            raise SystemExit(f"Ingest failed: {json.dumps(ingest_result, ensure_ascii=False)}")

    result = run_eval(
        base_url=args.api_url,
        cases=cases,
        thread_prefix=args.thread_prefix,
        timeout=args.timeout_sec,
        max_retries=args.max_retries,
        retry_backoff_sec=args.retry_backoff_sec,
    )
    result["meta"] = {
        "api_url": args.api_url,
        "cases_path": str(Path(args.cases)),
        "ingest_path": args.ingest_path,
        "skip_ingest": bool(args.skip_ingest),
        "max_retries": args.max_retries,
        "retry_backoff_sec": args.retry_backoff_sec,
        "start_index": args.start_index,
        "end_index": args.end_index,
        "ingest_result": ingest_result,
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")

    print(text)


if __name__ == "__main__":
    main()
