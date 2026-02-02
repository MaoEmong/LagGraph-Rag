import argparse
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


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


def _compute_latency(values: List[float]) -> Dict[str, float]:
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


def _run_one_cycle(
    python_exec: str,
    batch_runner: Path,
    cycle: int,
    args: argparse.Namespace,
    output_dir: Path,
) -> Dict[str, Any]:
    cycle_out = output_dir / f"soak_cycle_{cycle:03d}.json"
    cycle_fail = output_dir / f"soak_cycle_{cycle:03d}.failure.json"
    cycle_batches = output_dir / "batches" / f"cycle_{cycle:03d}"
    cycle_server_logs = output_dir / "server_logs" / f"cycle_{cycle:03d}"

    cmd = [
        python_exec,
        str(batch_runner),
        "--cases",
        args.cases,
        "--ingest-path",
        args.ingest_path,
        "--batch-size",
        str(args.batch_size),
        "--api-host",
        args.api_host,
        "--api-port",
        str(args.api_port),
        "--thread-prefix",
        f"{args.thread_prefix}-c{cycle:03d}",
        "--max-retries",
        str(args.max_retries),
        "--retry-backoff-sec",
        str(args.retry_backoff_sec),
        "--health-timeout-sec",
        str(args.health_timeout_sec),
        "--batch-output-dir",
        str(cycle_batches),
        "--server-log-dir",
        str(cycle_server_logs),
        "--failure-summary-path",
        str(cycle_fail),
        "--failure-tail-lines",
        str(args.failure_tail_lines),
        "--output",
        str(cycle_out),
    ]
    if args.auto_port:
        cmd.extend(
            [
                "--auto-port",
                "--auto-port-max-tries",
                str(args.auto_port_max_tries),
                "--port-step",
                str(args.port_step),
            ]
        )
    if cycle > 1 and args.skip_ingest_after_first:
        cmd.append("--no-first-batch-ingest")

    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
    result: Dict[str, Any] = {
        "cycle": cycle,
        "return_code": proc.returncode,
        "output_path": str(cycle_out),
        "failure_summary_path": str(cycle_fail),
    }
    if proc.returncode != 0:
        result["status"] = "failed"
        result["stdout_tail"] = (proc.stdout or "").splitlines()[-40:]
        result["stderr_tail"] = (proc.stderr or "").splitlines()[-40:]
        if cycle_fail.exists():
            try:
                result["failure_summary"] = json.loads(cycle_fail.read_text(encoding="utf-8"))
            except Exception:  # pylint: disable=broad-except
                result["failure_summary"] = {"error": "failed to parse failure summary"}
        return result

    payload = json.loads(cycle_out.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    result["status"] = "ok"
    result["summary"] = summary
    result["details"] = payload.get("details", [])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated E2E batch-runner cycles (soak test).")
    parser.add_argument("--cycles", type=int, default=4, help="Number of soak cycles.")
    parser.add_argument("--cases", default="./evals/e2e_eval_cases.jsonl")
    parser.add_argument("--ingest-path", default="./evals/docs")
    parser.add_argument("--batch-size", type=int, default=12)
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8080)
    parser.add_argument("--auto-port", action="store_true")
    parser.add_argument("--auto-port-max-tries", type=int, default=50)
    parser.add_argument("--port-step", type=int, default=1)
    parser.add_argument("--thread-prefix", default="soak")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-backoff-sec", type=float, default=1.0)
    parser.add_argument("--health-timeout-sec", type=float, default=30.0)
    parser.add_argument("--failure-tail-lines", type=int, default=20)
    parser.add_argument("--skip-ingest-after-first", action="store_true")
    parser.add_argument("--output-dir", default="./evals/results/soak")
    parser.add_argument("--output", default="./evals/results/e2e_soak_summary.json")
    parser.add_argument("--python-exec", default=sys.executable)
    parser.add_argument("--stop-on-failure", action="store_true")

    args = parser.parse_args()
    if args.cycles <= 0:
        raise ValueError("--cycles must be > 0")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    batch_runner = (Path(".") / "scripts" / "e2e_eval_batch_runner.py").resolve()

    cycle_results: List[Dict[str, Any]] = []
    all_details: List[Dict[str, Any]] = []

    for cycle in range(1, args.cycles + 1):
        cycle_result = _run_one_cycle(
            python_exec=args.python_exec,
            batch_runner=batch_runner,
            cycle=cycle,
            args=args,
            output_dir=output_dir,
        )
        cycle_results.append(cycle_result)

        if cycle_result.get("status") == "ok":
            all_details.extend(cycle_result.get("details", []))
        elif args.stop_on_failure:
            break

    total_cycles = len(cycle_results)
    ok_cycles = [c for c in cycle_results if c.get("status") == "ok"]
    failed_cycles = [c for c in cycle_results if c.get("status") != "ok"]

    total_requests = len(all_details)
    success_count = sum(1 for d in all_details if d.get("success"))
    keyword_pass = sum(1 for d in all_details if d.get("keyword_pass"))
    citation_pass = sum(1 for d in all_details if d.get("citation_pass"))
    client_latency = [float(d["elapsed_ms"]) for d in all_details if float(d.get("elapsed_ms", 0.0)) > 0]
    graph_latency = [float(d["graph_t_total_ms"]) for d in all_details if isinstance(d.get("graph_t_total_ms"), (int, float))]

    payload = {
        "summary": {
            "cycles_total": total_cycles,
            "cycles_ok": len(ok_cycles),
            "cycles_failed": len(failed_cycles),
            "requests_total": total_requests,
            "success_count": success_count,
            "success_rate": (success_count / total_requests) if total_requests else 0.0,
            "keyword_pass_count": keyword_pass,
            "keyword_pass_rate": (keyword_pass / total_requests) if total_requests else 0.0,
            "citation_pass_count": citation_pass,
            "citation_pass_rate": (citation_pass / total_requests) if total_requests else 0.0,
            "client_latency": _compute_latency(client_latency),
            "graph_total_latency": _compute_latency(graph_latency),
        },
        "cycles": cycle_results,
        "meta": {
            "mode": "soak-runner",
            "cases": args.cases,
            "ingest_path": args.ingest_path,
            "batch_size": args.batch_size,
            "cycles_requested": args.cycles,
            "api_host": args.api_host,
            "api_port": args.api_port,
            "auto_port": bool(args.auto_port),
            "skip_ingest_after_first": bool(args.skip_ingest_after_first),
            "output_dir": str(output_dir),
        },
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    output_path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

