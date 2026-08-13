"""Conversation-scoped environment selection for Teams bot.

Supports selecting a customer context (for example, prod=SP, delegated=device-code auth)
without changing the core query/Kusto implementation.
"""

import json
import os
import re
import unicodedata
from typing import Any

_BRIDGE_DIR = os.path.dirname(__file__)
_CUSTOMERS_FILE = os.path.join(_BRIDGE_DIR, "customers.json")
_SESSION_ENV_FILE = os.path.join(_BRIDGE_DIR, "session_environments.json")

_CONV_ENV: dict[str, dict[str, Any]] = {}
_ALIAS_MAP = {
    # Optional local aliases. Keep customer-specific aliases in local config/docs, not in public source.
    "prod": "sp-customer",
    "delegated": "delegated-customer",
}


def _normalize_profile_key(name: str) -> str:
    key = (name or "")
    # Normalize full-width/compatibility characters to ASCII equivalents when possible.
    key = unicodedata.normalize("NFKC", key)
    # Remove zero-width / format characters often injected by IM clients.
    key = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", key)
    key = key.strip().casefold()
    # Trim common trailing/leading punctuations from IM clients, e.g. "/env prod。"
    key = re.sub(r"^[\s'\"`.,;:!?。！？，；：]+|[\s'\"`.,;:!?。！？，；：]+$", "", key)
    return key


def _load_json_file(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _profiles_from_customers() -> list[dict[str, Any]]:
    data = _load_json_file(_CUSTOMERS_FILE)
    out: list[dict[str, Any]] = []
    for env in data.get("environments", []):
        name = (env.get("name") or "").strip()
        if not name:
            continue
        auth_mode = (env.get("auth_mode") or "sp").strip().lower() or "sp"
        if auth_mode not in {"sp", "delegated"}:
            auth_mode = "sp"
        out.append(
            {
                "name": name,
                "auth_mode": auth_mode,
                "tenant_id": env.get("tenant_id", ""),
                "subscriptions": env.get("subscriptions", []),
                "delegated_tenant_id": env.get("delegated_tenant_id", ""),
                "delegated_client_id": env.get("delegated_client_id", ""),
                "delegated_username": env.get("delegated_username", ""),
                "delegated_password": env.get("delegated_password", ""),
                "source": "customers.json",
            }
        )
    return out


def _profiles_from_session_file() -> list[dict[str, Any]]:
    data = _load_json_file(_SESSION_ENV_FILE)
    out: list[dict[str, Any]] = []
    for p in data.get("profiles", []):
        name = (p.get("name") or "").strip()
        if not name:
            continue
        auth_mode = (p.get("auth_mode") or "delegated").strip().lower() or "delegated"
        if auth_mode not in {"sp", "delegated"}:
            auth_mode = "delegated"
        out.append(
            {
                "name": name,
                "auth_mode": auth_mode,
                "tenant_id": p.get("tenant_id", ""),
                "subscriptions": p.get("subscriptions", []),
                "delegated_tenant_id": p.get("delegated_tenant_id", ""),
                "delegated_client_id": p.get("delegated_client_id", ""),
                "delegated_username": p.get("delegated_username", ""),
                "delegated_password": p.get("delegated_password", ""),
                "source": "session_environments.json",
            }
        )
    return out


def list_environment_profiles() -> list[dict[str, Any]]:
    # Merge by lower(name); session_environments.json overrides customers.json entry.
    merged: dict[str, dict[str, Any]] = {}
    for p in _profiles_from_customers():
        merged[p["name"].lower()] = p
    for p in _profiles_from_session_file():
        merged[p["name"].lower()] = p
    return sorted(merged.values(), key=lambda x: x["name"].lower())


def find_profile(name: str) -> dict[str, Any] | None:
    key = _normalize_profile_key(name)
    if not key:
        return None
    key = _normalize_profile_key(_ALIAS_MAP.get(key, key) or "")
    for p in list_environment_profiles():
        if p["name"].lower() == key:
            return p
    return None


def set_conversation_environment(conversation_id: str, profile_name: str) -> tuple[bool, str]:
    profile = find_profile(profile_name)
    if not profile:
        available = ", ".join(p.get("name", "") for p in list_environment_profiles()) or "(空)"
        return False, f"未找到环境: {profile_name}。可选环境: {available}。快捷别名: prod / delegated"
    _CONV_ENV[conversation_id] = profile
    return True, "ok"


def get_conversation_environment(conversation_id: str) -> dict[str, Any] | None:
    return _CONV_ENV.get(conversation_id)


def clear_conversation_environment(conversation_id: str) -> None:
    _CONV_ENV.pop(conversation_id, None)


def format_environment(profile: dict[str, Any] | None) -> str:
    if not profile:
        return "未选择会话环境"
    subs = profile.get("subscriptions") or []
    return (
        f"环境: {profile.get('name', '')}\n"
        f"模式: {profile.get('auth_mode', '')}\n"
        f"订阅数: {len(subs)}"
    )
