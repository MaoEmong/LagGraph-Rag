import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests

DEFAULT_API_URL = "http://localhost:8000"
CONFIG_DIR = Path.home() / ".rag_assistant"
CONFIG_PATH = CONFIG_DIR / "config.json"


def _load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_config(config: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_api_url(config: Dict[str, Any]) -> str:
    return os.environ.get("RAG_API_URL") or config.get("api_url") or DEFAULT_API_URL


def _request_json(method: str, url: str, api_key: Optional[str], payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.request(method, url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def _print_response(data: Dict[str, Any], json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    success = data.get("success")
    if not success:
        error = data.get("error") or {}
        print("[ERROR]")
        print(f"{error.get('code')}: {error.get('message')}")
        return

    payload = data.get("data") or {}
    if "answer" in payload:
        print("[AI]")
        print(payload.get("answer", ""))
        citations = payload.get("citations") or []
        if citations:
            print("\n[Sources]")
            for item in citations:
                source_path = item.get("source_path") or ""
                if source_path:
                    print(f"- {source_path}")
        return

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_chat(args: argparse.Namespace) -> None:
    config = _load_config()
    api_url = _get_api_url(config)
    thread_id = args.thread or config.get("default_thread", "default")

    payload = {"thread_id": thread_id, "question": args.question}
    result = _request_json("POST", f"{api_url}/chat", args.api_key, payload)
    _print_response(result, args.json)


def cmd_ingest(args: argparse.Namespace) -> None:
    config = _load_config()
    api_url = _get_api_url(config)

    payload = {
        "path": args.path,
        "recursive": args.recursive,
        "dry_run": args.dry_run,
    }
    result = _request_json("POST", f"{api_url}/ingest", args.api_key, payload)
    _print_response(result, args.json)


def cmd_threads(args: argparse.Namespace) -> None:
    config = _load_config()
    api_url = _get_api_url(config)

    result = _request_json("GET", f"{api_url}/threads", args.api_key)
    _print_response(result, args.json)


def cmd_reset(args: argparse.Namespace) -> None:
    config = _load_config()
    api_url = _get_api_url(config)

    if not args.force:
        confirm = input(f"thread '{args.thread_id}'를 초기화할까요? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("취소됨")
            return

    payload = {"thread_id": args.thread_id}
    result = _request_json("POST", f"{api_url}/threads/reset", args.api_key, payload)
    _print_response(result, args.json)


def cmd_stats(args: argparse.Namespace) -> None:
    config = _load_config()
    api_url = _get_api_url(config)

    result = _request_json("GET", f"{api_url}/health", args.api_key)
    _print_response(result, args.json)


def cmd_config_show(args: argparse.Namespace) -> None:
    config = _load_config()
    print(json.dumps(config, ensure_ascii=False, indent=2))


def cmd_config_set(args: argparse.Namespace) -> None:
    config = _load_config()
    config[args.key] = args.value
    _save_config(config)
    print("OK")


def cmd_config_reset(args: argparse.Namespace) -> None:
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
    print("OK")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="assistant", description="RAG Assistant CLI")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.add_argument("--json", action="store_true", help="JSON 원본 응답 출력")
    parser.add_argument("--api-key", dest="api_key", help="API 키 지정")

    subparsers = parser.add_subparsers(dest="command", required=True)

    chat_parser = subparsers.add_parser("chat", help="대화 시작 / 질문")
    chat_parser.add_argument("question", help="질문 내용")
    chat_parser.add_argument("--thread", dest="thread", help="thread ID", default=None)
    chat_parser.add_argument("--stream", action="store_true", help="스트리밍 출력 (미지원)")
    chat_parser.set_defaults(func=cmd_chat)

    ingest_parser = subparsers.add_parser("ingest", help="문서 인제스트")
    ingest_parser.add_argument("path", help="인제스트 대상 경로")
    recursive_group = ingest_parser.add_mutually_exclusive_group()
    recursive_group.add_argument("--recursive", dest="recursive", action="store_true", help="하위 폴더 포함")
    recursive_group.add_argument("--no-recursive", dest="recursive", action="store_false", help="하위 폴더 미포함")
    ingest_parser.set_defaults(recursive=True)
    ingest_parser.add_argument("--dry-run", action="store_true", help="저장 없이 테스트")
    ingest_parser.set_defaults(func=cmd_ingest)

    threads_parser = subparsers.add_parser("threads", help="thread 목록 조회")
    threads_parser.set_defaults(func=cmd_threads)

    reset_parser = subparsers.add_parser("reset", help="thread 초기화")
    reset_parser.add_argument("thread_id", help="thread ID")
    reset_parser.add_argument("--force", action="store_true", help="확인 없이 실행")
    reset_parser.set_defaults(func=cmd_reset)

    stats_parser = subparsers.add_parser("stats", help="서버 상태 정보")
    stats_parser.set_defaults(func=cmd_stats)

    config_parser = subparsers.add_parser("config", help="CLI 설정 관리")
    config_sub = config_parser.add_subparsers(dest="config_command", required=True)

    config_show = config_sub.add_parser("show", help="현재 설정 출력")
    config_show.set_defaults(func=cmd_config_show)

    config_set = config_sub.add_parser("set", help="설정 변경")
    config_set.add_argument("key", help="설정 키")
    config_set.add_argument("value", help="설정 값")
    config_set.set_defaults(func=cmd_config_set)

    config_reset = config_sub.add_parser("reset", help="설정 초기화")
    config_reset.set_defaults(func=cmd_config_reset)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if getattr(args, "stream", False):
        print("[WARN] 스트리밍 출력은 아직 지원하지 않습니다.")

    try:
        args.func(args)
    except requests.HTTPError as exc:
        print("[ERROR]")
        print(f"HTTP 오류: {exc}")
        return 1
    except requests.RequestException as exc:
        print("[ERROR]")
        print(f"요청 실패: {exc}")
        return 1
    except Exception as exc:
        print("[ERROR]")
        print(f"실행 실패: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
