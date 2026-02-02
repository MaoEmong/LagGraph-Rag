import argparse
import json
import math
from typing import Dict, List

from app.config import settings
from app.nodes.retrieve import _embed_query_with_model
from app.storage.vector_db import VectorDB


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    if pct <= 0:
        return values[0]
    if pct >= 1:
        return values[-1]
    idx = int(math.ceil(pct * len(values))) - 1
    idx = max(0, min(idx, len(values) - 1))
    return values[idx]


def _load_queries(path: str) -> List[str]:
    queries: List[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            query = line.strip()
            if query:
                queries.append(query)
    return queries


def _summarize_distances(best_distances: List[float]) -> Dict[str, float]:
    if not best_distances:
        return {}
    values = sorted(best_distances)
    total = sum(values)
    count = len(values)
    mean = total / count
    median = values[count // 2] if count % 2 == 1 else (values[count // 2 - 1] + values[count // 2]) / 2
    return {
        "count": count,
        "min": values[0],
        "p50": median,
        "p75": _percentile(values, 0.75),
        "p90": _percentile(values, 0.9),
        "max": values[-1],
        "mean": mean,
    }


def _evaluate_thresholds(
    records: List[Dict[str, object]],
    thresholds: List[float],
    top_k: int,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []

    for threshold in thresholds:
        triggered = 0
        reason_low_count = 0
        reason_no_scores = 0
        reason_distance = 0

        for record in records:
            count = int(record.get("doc_count", 0))
            has_scores = bool(record.get("has_scores"))
            best_distance = record.get("best_distance")

            if count < top_k:
                triggered += 1
                reason_low_count += 1
                continue
            if not has_scores:
                triggered += 1
                reason_no_scores += 1
                continue
            if best_distance is None:
                continue
            if float(best_distance) >= threshold:
                triggered += 1
                reason_distance += 1

        results.append(
            {
                "threshold": threshold,
                "triggered": triggered,
                "total": len(records),
                "trigger_rate": (triggered / len(records)) if records else 0.0,
                "reasons": {
                    "low_count": reason_low_count,
                    "no_scores": reason_no_scores,
                    "distance": reason_distance,
                },
            }
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Reranker auto threshold sweep.")
    parser.add_argument("--queries", required=True, help="Path to a text file with one query per line.")
    parser.add_argument("--thresholds", default="0.2,0.25,0.3,0.35,0.4", help="Comma-separated thresholds.")
    parser.add_argument("--top-k", type=int, default=settings.top_k, help="top_k for the decision rule.")
    parser.add_argument("--rerank-top-k", type=int, default=settings.rerank_top_k, help="initial retrieval size.")
    parser.add_argument("--model", default=settings.embedding_model, help="Embedding model for query vectors.")
    parser.add_argument("--json", action="store_true", help="Output JSON summary.")

    args = parser.parse_args()
    thresholds = [float(item.strip()) for item in args.thresholds.split(",") if item.strip()]
    initial_top_k = max(args.top_k, args.rerank_top_k)

    queries = _load_queries(args.queries)
    if not queries:
        raise SystemExit("No queries found.")

    vdb = VectorDB()
    records: List[Dict[str, object]] = []

    for query in queries:
        embedding = _embed_query_with_model(query, args.model)
        result = vdb.query([embedding], top_k=initial_top_k)
        distances = (result.get("distances") or [[]])[0]
        ids = (result.get("ids") or [[]])[0]

        best_distance = min(distances) if distances else None
        has_scores = any(dist is not None for dist in distances) if distances else False

        records.append(
            {
                "query": query,
                "doc_count": len(ids),
                "has_scores": has_scores,
                "best_distance": best_distance,
            }
        )

    best_distances = [record["best_distance"] for record in records if record.get("best_distance") is not None]
    distance_summary = _summarize_distances(best_distances)
    sweep = _evaluate_thresholds(records, thresholds, args.top_k)

    payload = {
        "queries": len(queries),
        "top_k": args.top_k,
        "initial_top_k": initial_top_k,
        "distance_summary": distance_summary,
        "threshold_sweep": sweep,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("Reranker auto threshold sweep")
    print(f"queries: {len(queries)}")
    print(f"top_k: {args.top_k}")
    print(f"initial_top_k: {initial_top_k}")

    if distance_summary:
        print("best_distance stats:")
        print(
            "  min={min:.4f} p50={p50:.4f} p75={p75:.4f} p90={p90:.4f} max={max:.4f} mean={mean:.4f}".format(
                **distance_summary
            )
        )
    else:
        print("best_distance stats: no scores")

    print("\nthreshold sweep:")
    for item in sweep:
        threshold = item["threshold"]
        trigger_rate = item["trigger_rate"] * 100
        reasons = item["reasons"]
        print(
            f"  {threshold:.2f} -> {trigger_rate:.1f}% (low_count={reasons['low_count']}, no_scores={reasons['no_scores']}, distance={reasons['distance']})"
        )


if __name__ == "__main__":
    main()