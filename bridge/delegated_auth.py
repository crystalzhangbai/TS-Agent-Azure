"""Delegated authentication manager for Teams conversation flows.

Implements a minimal device-code auth lifecycle:
- /auth login returns verification_uri + user_code
- bot polls token once user completes login
- credential is cached per conversation
"""

import threading
import time
import os
from dataclasses import dataclass
from typing import Any

from azure.identity import DeviceCodeCredential

_DEFAULT_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
_ARM_SCOPE = "https://management.azure.com/.default"
_AUTH_TTL_MINUTES = int(os.environ.get("DELEGATED_AUTH_TTL_MINUTES", "0"))
_AUTH_TTL_SECONDS = _AUTH_TTL_MINUTES * 60


class DelegatedAuthRequiredError(RuntimeError):
    def __init__(self, message: str, *, verification_uri: str = "", user_code: str = ""):
        super().__init__(message)
        self.verification_uri = verification_uri
        self.user_code = user_code


@dataclass
class DelegatedAuthState:
    profile_name: str
    tenant_id: str
    client_id: str
    status: str  # not_started | pending | authenticated | failed
    verification_uri: str = ""
    user_code: str = ""
    message: str = ""
    updated_at: float = 0.0
    authenticated_at: float = 0.0
    credential: DeviceCodeCredential | None = None


_LOCK = threading.Lock()
_STATE: dict[str, DelegatedAuthState] = {}


def _build_device_credential(*, tenant_id: str, client_id: str, sink: dict[str, str]) -> DeviceCodeCredential:
    def _prompt_callback(challenge: str):
        sink["raw_message"] = challenge

    return DeviceCodeCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        prompt_callback=_prompt_callback,
    )


def _extract_uri_and_code(raw_message: str) -> tuple[str, str]:
    text = raw_message or ""
    uri = ""
    code = ""
    for token in text.replace("\r", "\n").split():
        if token.startswith("https://") and "microsoft.com/devicelogin" in token:
            uri = token.strip()
            break
    for line in text.splitlines():
        l = line.strip()
        if "code" in l.lower() and ":" in l:
            candidate = l.split(":", 1)[1].strip()
            if candidate:
                code = candidate
    return uri, code


def start_device_login(conversation_id: str, profile: dict[str, Any]) -> dict[str, Any]:
    tenant_id = (profile.get("delegated_tenant_id") or profile.get("tenant_id") or "").strip()
    client_id = (profile.get("delegated_client_id") or _DEFAULT_CLIENT_ID).strip()
    profile_name = (profile.get("name") or "delegated").strip()

    if not tenant_id:
        raise ValueError("delegated 模式缺少 tenant_id/delegated_tenant_id")

    sink: dict[str, str] = {}
    cred = _build_device_credential(tenant_id=tenant_id, client_id=client_id, sink=sink)

    state = DelegatedAuthState(
        profile_name=profile_name,
        tenant_id=tenant_id,
        client_id=client_id,
        status="pending",
        updated_at=time.time(),
        credential=cred,
    )

    def _worker():
        try:
            # This call blocks until the user finishes auth in browser.
            cred.get_token(_ARM_SCOPE)
            with _LOCK:
                s = _STATE.get(conversation_id)
                if s:
                    s.status = "authenticated"
                    s.message = "认证成功"
                    s.updated_at = time.time()
                    s.authenticated_at = s.updated_at
        except Exception as exc:  # noqa: BLE001
            with _LOCK:
                s = _STATE.get(conversation_id)
                if s:
                    s.status = "failed"
                    s.message = str(exc)
                    s.updated_at = time.time()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

    # Give callback a short window to capture device challenge message.
    for _ in range(40):
        if sink.get("raw_message"):
            break
        time.sleep(0.05)

    raw_message = sink.get("raw_message", "")
    uri, code = _extract_uri_and_code(raw_message)
    state.verification_uri = uri
    state.user_code = code
    state.message = raw_message or "请在浏览器完成设备码登录"

    with _LOCK:
        _STATE[conversation_id] = state

    return {
        "status": state.status,
        "profile_name": state.profile_name,
        "tenant_id": state.tenant_id,
        "verification_uri": state.verification_uri,
        "user_code": state.user_code,
        "message": state.message,
    }


def get_auth_status(conversation_id: str) -> dict[str, Any]:
    with _LOCK:
        state = _STATE.get(conversation_id)
    if not state:
        return {"status": "not_started"}

    now = time.time()
    if state.status == "authenticated" and state.authenticated_at > 0 and _AUTH_TTL_MINUTES > 0:
        elapsed = now - state.authenticated_at
        if elapsed > _AUTH_TTL_SECONDS:
            with _LOCK:
                s = _STATE.get(conversation_id)
                if s and s.status == "authenticated":
                    s.status = "expired"
                    s.message = f"认证已超时（>{_AUTH_TTL_SECONDS // 60} 分钟），请重新执行 /auth login"
                    s.updated_at = now
            state = _STATE.get(conversation_id)

    return {
        "status": state.status,
        "profile_name": state.profile_name,
        "tenant_id": state.tenant_id,
        "verification_uri": state.verification_uri,
        "user_code": state.user_code,
        "message": state.message,
        "ttl_minutes": _AUTH_TTL_MINUTES,
    }


def clear_auth_state(conversation_id: str) -> None:
    with _LOCK:
        _STATE.pop(conversation_id, None)


def get_authenticated_credential(conversation_id: str) -> DeviceCodeCredential | None:
    status = get_auth_status(conversation_id)
    if status.get("status") != "authenticated":
        return None

    with _LOCK:
        state = _STATE.get(conversation_id)
    if not state or state.status != "authenticated":
        return None
    return state.credential


def require_authenticated_credential(conversation_id: str, profile: dict[str, Any]) -> DeviceCodeCredential:
    cred = get_authenticated_credential(conversation_id)
    if cred:
        return cred

    status = get_auth_status(conversation_id)
    if status.get("status") == "pending":
        raise DelegatedAuthRequiredError(
            "delegated 登录进行中，请先在浏览器完成认证，再重试。",
            verification_uri=status.get("verification_uri", ""),
            user_code=status.get("user_code", ""),
        )

    # Not started or failed: force explicit pre-auth.
    raise DelegatedAuthRequiredError(
        "当前会话 delegated 模式未认证或已超时，请先执行 /auth login。",
        verification_uri=status.get("verification_uri", ""),
        user_code=status.get("user_code", ""),
    )
