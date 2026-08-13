"""Lightweight runtime event logger for development diagnostics.

Writes JSONL records under bridge/runtime to capture inputs, outputs, and errors.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ENABLED = os.environ.get("RUN_LOG_ENABLED", "true").lower() != "false"
_MAX_CHARS = int(os.environ.get("RUN_LOG_MAX_CHARS", "12000"))
_DEFAULT_PATH = Path(__file__).resolve().parent / "runtime" / "agent-run.log.jsonl"
_LOG_PATH = Path(os.environ.get("RUN_LOG_PATH", str(_DEFAULT_PATH)))
_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _clip(value: Any) -> tuple[Any, bool]:
    if value is None:
        return None, False
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= _MAX_CHARS:
        return text, False
    return text[:_MAX_CHARS], True


def log_event(
    event_type: str,
    *,
    status: str,
    inputs: Any = None,
    outputs: Any = None,
    error: Any = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    if not _ENABLED:
        return

    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        in_val, in_cut = _clip(inputs)
        out_val, out_cut = _clip(outputs)
        err_val, err_cut = _clip(error)

        record = {
            "ts": _utc_now(),
            "event_type": event_type,
            "status": status,
            "inputs": in_val,
            "outputs": out_val,
            "error": err_val,
            "truncated": {
                "inputs": in_cut,
                "outputs": out_cut,
                "error": err_cut,
            },
            "metadata": metadata or {},
        }

        with _LOCK:
            with _LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Never break main flow because of logging.
        return
