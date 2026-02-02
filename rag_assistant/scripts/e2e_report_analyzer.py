import argparse
import json
import math
import statistics
import sys
from collections import Counter
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


def _classify_failure(item: Dict[str, Any]) -> str:
    success = bool(item.get("success"))
    keyword_pass = bool(item.get("keyword_pass"))
    citation_pass = bool(item.get("citation_pass"))
    error = str(item.get("error") or "").lower()

    if not success:
        if any(token in error for token in ["connection", "winerror 10061", "10054", "timeout", "refused", "aborted"]):
            return "request_failure"
        if error:
            return "response_failure"
        return "unknown_failure"

    if success and not keyword_pass and not citation_pass:
        return "keyword_and_citation_miss"
    if success and not keyword_pass:
        return "keyword_miss"
    if success and not citation_pass:
        return "citation_miss"
    return "pass"


def _top_errors(details: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    counter: Counter[str] = Counter()
    for item in details:
        error = str(item.get("error") or "").strip()
        if error:
            counter[error] += 1
    return [{"error": err, "count": cnt} for err, cnt in counter.most_common(limit)]


def _source_distribution(details: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
    counter: Counter[str] = Counter()
    for item in details:
        srcs = item.get("citation_source_paths")
        if isinstance(srcs, list):
            for src in srcs:
                if src:
                    counter[str(src)] += 1
    return [{"source_path": src, "count": cnt} for src, cnt in counter.most_common(limit)]


def _analyze_details(details: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(details)
    success = sum(1 for d in details if d.get("success"))
    keyword_pass = sum(1 for d in details if d.get("keyword_pass"))
    citation_pass = sum(1 for d in details if d.get("citation_pass"))

    failure_types = Counter(_classify_failure(d) for d in details)
    client_latency = [float(d["elapsed_ms"]) for d in details if float(d.get("elapsed_ms", 0.0)) > 0]
    graph_latency = [float(d["graph_t_total_ms"]) for d in details if isinstance(d.get("graph_t_total_ms"), (int, float))]

    failed_items = [d for d in details if _classify_failure(d) != "pass"]

    return {
        "total_cases": total,
        "success_count": success,
        "success_rate": (success / total) if total else 0.0,
        "keyword_pass_count": keyword_pass,
        "keyword_pass_rate": (keyword_pass / total) if total else 0.0,
        "citation_pass_count": citation_pass,
        "citation_pass_rate": (citation_pass / total) if total else 0.0,
        "failure_type_counts": dict(failure_types),
        "top_errors": _top_errors(details),
        "failed_case_ids": [str(x.get("id", "")) for x in failed_items],
        "client_latency": _compute_latency(client_latency),
        "graph_total_latency": _compute_latency(graph_latency),
        "citation_source_distribution": _source_distribution(details),
    }


def _cycle_drift(cycles: List[Dict[str, Any]], threshold_pct: float) -> Dict[str, Any]:
    ok_cycles = [c for c in cycles if c.get("status") == "ok" and isinstance(c.get("summary"), dict)]
    means: List[Dict[str, Any]] = []
    for c in ok_cycles:
        cycle_no = c.get("cycle")
        summary = c.get("summary") or {}
        graph_mean = ((summary.get("graph_total_latency") or {}).get("mean_ms"))
        client_mean = ((summary.get("client_latency") or {}).get("mean_ms"))
        means.append(
            {
                "cycle": cycle_no,
                "graph_mean_ms": graph_mean,
                "client_mean_ms": client_mean,
            }
        )

    graph_values = [float(x["graph_mean_ms"]) for x in means if isinstance(x.get("graph_mean_ms"), (int, float))]
    if len(graph_values) < 2:
        return {"cycles": means, "drift": {}, "anomaly": False}

    first = graph_values[0]
    last = graph_values[-1]
    delta = last - first
    delta_pct = (delta / first * 100.0) if first else 0.0
    anomaly = abs(delta_pct) >= threshold_pct

    return {
        "cycles": means,
        "drift": {
            "first_graph_mean_ms": first,
            "last_graph_mean_ms": last,
            "delta_ms": delta,
            "delta_pct": delta_pct,
            "threshold_pct": threshold_pct,
        },
        "anomaly": anomaly,
    }


def analyze_report(payload: Dict[str, Any], drift_threshold_pct: float) -> Dict[str, Any]:
    details = payload.get("details")
    if isinstance(details, list):
        return {
            "report_type": "e2e",
            "analysis": _analyze_details(details),
            "meta": payload.get("meta", {}),
        }

    cycles = payload.get("cycles")
    if isinstance(cycles, list):
        flat_details: List[Dict[str, Any]] = []
        for c in cycles:
            if isinstance(c, dict) and isinstance(c.get("details"), list):
                flat_details.extend(c["details"])
        result = {
            "report_type": "soak",
            "analysis": _analyze_details(flat_details),
            "cycle_drift": _cycle_drift(cycles, drift_threshold_pct),
            "meta": payload.get("meta", {}),
        }
        return result

    raise ValueError("Unsupported report format: expected `details` or `cycles`.")


def _to_float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:  # pylint: disable=broad-except
        return default


def build_alerts(
    result: Dict[str, Any],
    min_success_rate: float,
    min_keyword_pass_rate: float,
    min_citation_pass_rate: float,
    max_p90_graph_ms: float,
    max_drift_pct: float,
) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    analysis = result.get("analysis", {})
    report_type = result.get("report_type", "")

    success_rate = _to_float(analysis.get("success_rate"), 0.0)
    keyword_rate = _to_float(analysis.get("keyword_pass_rate"), 0.0)
    citation_rate = _to_float(analysis.get("citation_pass_rate"), 0.0)
    p90_graph = _to_float((analysis.get("graph_total_latency") or {}).get("p90_ms"), 0.0)

    if success_rate < min_success_rate:
        alerts.append(
            {
                "code": "LOW_SUCCESS_RATE",
                "message": f"success_rate {success_rate:.4f} < threshold {min_success_rate:.4f}",
            }
        )
    if keyword_rate < min_keyword_pass_rate:
        alerts.append(
            {
                "code": "LOW_KEYWORD_PASS_RATE",
                "message": f"keyword_pass_rate {keyword_rate:.4f} < threshold {min_keyword_pass_rate:.4f}",
            }
        )
    if citation_rate < min_citation_pass_rate:
        alerts.append(
            {
                "code": "LOW_CITATION_PASS_RATE",
                "message": f"citation_pass_rate {citation_rate:.4f} < threshold {min_citation_pass_rate:.4f}",
            }
        )
    if p90_graph > max_p90_graph_ms:
        alerts.append(
            {
                "code": "HIGH_GRAPH_P90_LATENCY",
                "message": f"graph_p90_ms {p90_graph:.2f} > threshold {max_p90_graph_ms:.2f}",
            }
        )

    if report_type == "soak":
        cycle_drift = result.get("cycle_drift") or {}
        drift = cycle_drift.get("drift") or {}
        delta_pct = _to_float(drift.get("delta_pct"), 0.0)
        if abs(delta_pct) > max_drift_pct:
            alerts.append(
                {
                    "code": "HIGH_SOAK_DRIFT",
                    "message": f"soak_drift_pct {delta_pct:.4f} exceeds threshold ±{max_drift_pct:.4f}",
                }
            )

    return alerts


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze E2E/Soak report JSON.")
    parser.add_argument("--input", required=True, help="Input report JSON path.")
    parser.add_argument("--output", default="", help="Optional output JSON path.")
    parser.add_argument("--drift-threshold-pct", type=float, default=20.0, help="Drift anomaly threshold (%).")
    parser.add_argument("--min-success-rate", type=float, default=0.98)
    parser.add_argument("--min-keyword-pass-rate", type=float, default=0.98)
    parser.add_argument("--min-citation-pass-rate", type=float, default=0.98)
    parser.add_argument("--max-p90-graph-ms", type=float, default=4000.0)
    parser.add_argument("--max-soak-drift-pct", type=float, default=10.0)
    parser.add_argument("--fail-on-alert", action="store_true", help="Exit with code 2 if alerts exist.")

    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = analyze_report(payload, drift_threshold_pct=args.drift_threshold_pct)
    alerts = build_alerts(
        result=result,
        min_success_rate=args.min_success_rate,
        min_keyword_pass_rate=args.min_keyword_pass_rate,
        min_citation_pass_rate=args.min_citation_pass_rate,
        max_p90_graph_ms=args.max_p90_graph_ms,
        max_drift_pct=args.max_soak_drift_pct,
    )
    result["alerts"] = alerts
    result["alert_thresholds"] = {
        "min_success_rate": args.min_success_rate,
        "min_keyword_pass_rate": args.min_keyword_pass_rate,
        "min_citation_pass_rate": args.min_citation_pass_rate,
        "max_p90_graph_ms": args.max_p90_graph_ms,
        "max_soak_drift_pct": args.max_soak_drift_pct,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")

    print(text)
    if args.fail_on_alert and alerts:
        sys.exit(2)


if __name__ == "__main__":
    main()
