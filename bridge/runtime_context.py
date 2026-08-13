"""Per-turn runtime context shared across agent tools."""

from contextvars import ContextVar
from typing import Any

_SESSION_ENV: ContextVar[dict[str, Any] | None] = ContextVar("session_environment", default=None)
_CONVERSATION_ID: ContextVar[str] = ContextVar("conversation_id", default="")


def set_session_environment(env: dict[str, Any] | None):
    return _SESSION_ENV.set(env)


def reset_session_environment(token) -> None:
    _SESSION_ENV.reset(token)


def get_session_environment() -> dict[str, Any] | None:
    return _SESSION_ENV.get()


def set_conversation_id(conversation_id: str):
    return _CONVERSATION_ID.set(conversation_id or "")


def reset_conversation_id(token) -> None:
    _CONVERSATION_ID.reset(token)


def get_conversation_id() -> str:
    return _CONVERSATION_ID.get()
