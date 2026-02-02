import argparse
import json
import math
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import requests


def _load_case_count(cases_path: Path) -> int:
    count = 0
    with cases_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    if count == 0:
        raise ValueError("No evaluation cases found.")
    return count


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


def _wait_for_health(api_url: str, timeout_sec: float) -> None:
    url = api_url.rstrip("/") + "/health"
    deadline = time.time() + timeout_sec
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=3.0)
            if response.status_code == 200:
                body = response.json()
                if body.get("success"):
                    return
        except Exception as exc:  # pylint: disable=broad-except
            last_error = str(exc)
        time.sleep(0.5)
    raise RuntimeError(f"Health check timeout: {url} {last_error}")


def _tail_text(path_str: str, max_lines: int) -> List[str]:
    if not path_str:
        return []
    path = Path(path_str)
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:  # pylint: disable=broad-except
        return []
    if max_lines <= 0:
        return lines
    return lines[-max_lines:]


def _is_port_available(host: str, port: int) -> bool:
    # If connection succeeds, another process is already listening on the port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.3)
        if probe.connect_ex((host, port)) == 0:
            return False

    # If bind fails, the port cannot be safely used.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as binder:
        try:
            binder.bind((host, port))
            return True
        except OSError:
            return False


def _pick_available_port(host: str, base_port: int, max_tries: int, port_step: int) -> int:
    if max_tries <= 0:
        raise ValueError("--auto-port-max-tries must be > 0")
    if port_step <= 0:
        raise ValueError("--port-step must be > 0")

    for idx in range(max_tries):
        candidate = base_port + (idx * port_step)
        if _is_port_available(host, candidate):
            return candidate

    raise RuntimeError(f"Failed to find available port from {base_port} with tries={max_tries}, step={port_step}")


def _run_single_batch(
    python_exec: str,
    eval_script: Path,
    api_host: str,
    api_port: int,
    cases_path: Path,
    ingest_path: str,
    start_index: int,
    end_index: int,
    thread_prefix: str,
    timeout_sec: float,
    max_retries: int,
    retry_backoff_sec: float,
    batch_output_path: Path,
    do_ingest: bool,
    health_timeout_sec: float,
    server_log_dir: Path | None,
) -> Dict[str, Any]:
    api_url = f"http://{api_host}:{api_port}"
    server_stdout = subprocess.DEVNULL
    server_stderr = subprocess.DEVNULL
    stdout_handle = None
    stderr_handle = None

    stdout_path = ""
    stderr_path = ""
    if server_log_dir is not None:
        server_log_dir.mkdir(parents=True, exist_ok=True)
        stem = batch_output_path.stem
        stdout_log = server_log_dir / f"{stem}.server.stdout.log"
        stderr_log = server_log_dir / f"{stem}.server.stderr.log"
        stdout_path = str(stdout_log)
        stderr_path = str(stderr_log)
        stdout_handle = open(stdout_log, "w", encoding="utf-8", buffering=1)  # noqa: PTH123
        stderr_handle = open(stderr_log, "w", encoding="utf-8", buffering=1)  # noqa: PTH123
        server_stdout = stdout_handle
        server_stderr = stderr_handle

    server_proc = subprocess.Popen(  # noqa: S603
        [
            python_exec,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            api_host,
            "--port",
            str(api_port),
        ],
        stdout=server_stdout,
        stderr=server_stderr,
    )

    report: Dict[str, Any] = {
        "api_url": api_url,
        "start_index": start_index,
        "end_index": end_index,
        "batch_output_path": str(batch_output_path),
        "server_stdout_path": stdout_path,
        "server_stderr_path": stderr_path,
        "success": False,
        "stage": "",
        "error": "",
        "eval_return_code": None,
        "eval_stdout_tail": [],
        "eval_stderr_tail": [],
    }

    try:
        _wait_for_health(api_url, health_timeout_sec)
        report["stage"] = "eval"
        cmd = [
            python_exec,
            str(eval_script),
            "--api-url",
            api_url,
            "--cases",
            str(cases_path),
            "--ingest-path",
            ingest_path,
            "--thread-prefix",
            thread_prefix,
            "--timeout-sec",
            str(timeout_sec),
            "--max-retries",
            str(max_retries),
            "--retry-backoff-sec",
            str(retry_backoff_sec),
            "--start-index",
            str(start_index),
            "--end-index",
            str(end_index),
            "--output",
            str(batch_output_path),
        ]
        if not do_ingest:
            cmd.append("--skip-ingest")

        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
        report["eval_return_code"] = proc.returncode
        if proc.returncode != 0:
            report["error"] = f"eval script failed with code {proc.returncode}"
            report["eval_stdout_tail"] = (proc.stdout or "").splitlines()[-40:]
            report["eval_stderr_tail"] = (proc.stderr or "").splitlines()[-40:]
            return report
        report["success"] = True
        report["stage"] = "done"
        return report
    except Exception as exc:  # pylint: disable=broad-except
        report["stage"] = "server_start_or_health"
        report["error"] = str(exc)
        return report
    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            server_proc.kill()
            server_proc.wait(timeout=4)
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()


def _merge_results(batch_paths: List[Path]) -> Dict[str, Any]:
    details: List[Dict[str, Any]] = []
    for path in batch_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        details.extend(payload.get("details", []))

    total = len(details)
    success = sum(1 for item in details if item.get("success"))
    keyword_pass = sum(1 for item in details if item.get("keyword_pass"))
    citation_pass = sum(1 for item in details if item.get("citation_pass"))
    client_latency = [float(item["elapsed_ms"]) for item in details if float(item.get("elapsed_ms", 0.0)) > 0]
    graph_latency = [
        float(item["graph_t_total_ms"])
        for item in details
        if isinstance(item.get("graph_t_total_ms"), (int, float))
    ]

    return {
        "summary": {
            "total_cases": total,
            "success_count": success,
            "success_rate": (success / total) if total else 0.0,
            "keyword_pass_count": keyword_pass,
            "keyword_pass_rate": (keyword_pass / total) if total else 0.0,
            "citation_pass_count": citation_pass,
            "citation_pass_rate": (citation_pass / total) if total else 0.0,
            "client_latency": _compute_latency_stats(client_latency),
            "graph_total_latency": _compute_latency_stats(graph_latency),
        },
        "details": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run E2E eval in server-restart batches and merge results.")
    parser.add_argument("--cases", default="./evals/e2e_eval_cases.jsonl")
    parser.add_argument("--ingest-path", default="./evals/docs")
    parser.add_argument("--batch-size", type=int, default=12)
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8070)
    parser.add_argument("--auto-port", action="store_true", help="Pick an available port starting from --api-port.")
    parser.add_argument(
        "--auto-port-max-tries",
        type=int,
        default=50,
        help="Max port scan attempts when --auto-port is enabled.",
    )
    parser.add_argument("--port-step", type=int, default=1, help="Port increment step for auto-port scan.")
    parser.add_argument("--thread-prefix", default="eval-batch")
    parser.add_argument("--timeout-sec", type=float, default=60.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-backoff-sec", type=float, default=1.0)
    parser.add_argument("--health-timeout-sec", type=float, default=30.0)
    parser.add_argument("--batch-output-dir", default="./evals/results/batches")
    parser.add_argument("--output", default="./evals/results/e2e_eval_batched_merged.json")
    parser.add_argument(
        "--server-log-dir",
        default="",
        help="Optional directory to store per-batch uvicorn stdout/stderr logs.",
    )
    parser.add_argument("--python-exec", default=sys.executable)
    parser.add_argument("--no-first-batch-ingest", action="store_true")
    parser.add_argument(
        "--failure-summary-path",
        default="",
        help="Optional JSON path to write failure summary when a batch fails.",
    )
    parser.add_argument(
        "--failure-tail-lines",
        type=int,
        default=20,
        help="Number of tail lines to capture from server stderr log on failure.",
    )

    args = parser.parse_args()
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be > 0")

    root = Path(".")
    cases_path = (root / args.cases).resolve()
    eval_script = (root / "scripts" / "e2e_eval.py").resolve()
    batch_output_dir = (root / args.batch_output_dir).resolve()
    merged_output = (root / args.output).resolve()
    server_log_dir = (root / args.server_log_dir).resolve() if args.server_log_dir else None
    failure_summary_path = (root / args.failure_summary_path).resolve() if args.failure_summary_path else None
    batch_output_dir.mkdir(parents=True, exist_ok=True)
    merged_output.parent.mkdir(parents=True, exist_ok=True)
    if failure_summary_path is not None:
        failure_summary_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        total_cases = _load_case_count(cases_path)
        chosen_port = args.api_port
        if args.auto_port:
            chosen_port = _pick_available_port(
                host=args.api_host,
                base_port=args.api_port,
                max_tries=args.auto_port_max_tries,
                port_step=args.port_step,
            )
    except Exception as exc:  # pylint: disable=broad-except
        preflight_failure = {
            "error": "batch runner preflight failed",
            "stage": "preflight",
            "message": str(exc),
            "meta": {
                "cases_path": str(cases_path),
                "api_host": args.api_host,
                "api_port_requested": args.api_port,
                "auto_port": bool(args.auto_port),
            },
        }
        if failure_summary_path is not None:
            failure_summary_path.write_text(
                json.dumps(preflight_failure, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(preflight_failure, ensure_ascii=False, indent=2))
        raise

    batch_paths: List[Path] = []
    batch_reports: List[Dict[str, Any]] = []
    batch_no = 0
    start = 1

    while start <= total_cases:
        batch_no += 1
        end = min(total_cases, start + args.batch_size - 1)
        batch_path = batch_output_dir / f"e2e_eval_batch_{batch_no:02d}_{start:03d}_{end:03d}.json"
        batch_paths.append(batch_path)

        batch_report = _run_single_batch(
            python_exec=args.python_exec,
            eval_script=eval_script,
            api_host=args.api_host,
            api_port=chosen_port,
            cases_path=cases_path,
            ingest_path=args.ingest_path,
            start_index=start,
            end_index=end,
            thread_prefix=f"{args.thread_prefix}-{batch_no:02d}",
            timeout_sec=args.timeout_sec,
            max_retries=args.max_retries,
            retry_backoff_sec=args.retry_backoff_sec,
            batch_output_path=batch_path,
            do_ingest=(batch_no == 1 and not args.no_first_batch_ingest),
            health_timeout_sec=args.health_timeout_sec,
            server_log_dir=server_log_dir,
        )
        batch_reports.append(batch_report)
        if not batch_report.get("success"):
            failure_payload = {
                "error": "batch execution failed",
                "failed_batch": batch_report,
                "failed_batch_server_stderr_tail": _tail_text(
                    str(batch_report.get("server_stderr_path", "")),
                    args.failure_tail_lines,
                ),
                "completed_batches": batch_reports[:-1],
                "meta": {
                    "mode": "batch-runner-failure",
                    "cases_path": str(cases_path),
                    "batch_size": args.batch_size,
                    "api_host": args.api_host,
                    "api_port_requested": args.api_port,
                    "api_port_actual": chosen_port,
                },
            }
            if failure_summary_path is not None:
                failure_summary_path.write_text(
                    json.dumps(failure_payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            print(json.dumps(failure_payload, ensure_ascii=False, indent=2))
            raise RuntimeError("Batch runner failed. See failure summary for details.")

        start = end + 1

    merged = _merge_results(batch_paths)
    merged["meta"] = {
        "mode": "batch-runner",
        "cases_path": str(cases_path),
        "batch_size": args.batch_size,
        "batch_count": batch_no,
        "api_host": args.api_host,
        "api_port_requested": args.api_port,
        "api_port_actual": chosen_port,
        "auto_port": bool(args.auto_port),
        "auto_port_max_tries": args.auto_port_max_tries,
        "port_step": args.port_step,
        "batch_outputs": [str(path) for path in batch_paths],
        "batch_reports": batch_reports,
        "server_log_dir": str(server_log_dir) if server_log_dir is not None else "",
        "failure_summary_path": str(failure_summary_path) if failure_summary_path is not None else "",
    }

    text = json.dumps(merged, ensure_ascii=False, indent=2)
    merged_output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
