"""多客户订阅凭据注册表。

场景：要排查的 VM 分布在**多个客户订阅**里，每个订阅有各自的 Service Principal，
和运行 bot 的身份（az login / Foundry）不同。

用法：
- 复制 customers.example.json 为 customers.json，填入每个客户环境的 SP 和订阅。
- 代码按目标 subscription_id 自动挑选对应的 SP 凭据。
- 未配置 customers.json 时回退到 DefaultAzureCredential(az login)。

安全：customers.json 含密钥，已在 .gitignore 排除，不要提交。生产建议改用 Azure Key Vault。
"""
import json
import os

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from delegated_auth import DelegatedAuthRequiredError, require_authenticated_credential
from runtime_context import get_conversation_id, get_session_environment

_CUSTOMERS_FILE = os.path.join(os.path.dirname(__file__), "customers.json")
_SESSION_ENV_FILE = os.path.join(os.path.dirname(__file__), "session_environments.json")


def _load_environments() -> list[dict]:
    """读取 customers.json 里的 environments 列表；文件不存在则返回空。"""
    if not os.path.exists(_CUSTOMERS_FILE):
        return []
    with open(_CUSTOMERS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("environments", [])


def _load_session_profiles() -> list[dict]:
    if not os.path.exists(_SESSION_ENV_FILE):
        return []
    with open(_SESSION_ENV_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("profiles", [])


def _credential_for_env(env: dict) -> ClientSecretCredential:
    return ClientSecretCredential(
        tenant_id=env["tenant_id"],
        client_id=env["client_id"],
        client_secret=env["client_secret"],
    )


def _find_env_by_name(name: str) -> dict | None:
    key = (name or "").strip().lower()
    if not key:
        return None
    for env in _load_environments():
        if (env.get("name") or "").strip().lower() == key:
            return env
    for env in _load_session_profiles():
        if (env.get("name") or "").strip().lower() == key:
            return env
    return None


def iter_environments() -> list[tuple[dict, ClientSecretCredential]]:
    """返回 [(环境配置, 该环境的 SP 凭据), ...]，供跨订阅搜索使用。"""
    return [(env, _credential_for_env(env)) for env in _load_environments()]


def credential_for_subscription(subscription_id: str):
    """按订阅ID返回对应客户环境的 SP 凭据；找不到则回退 az login。"""
    selected = get_session_environment() or {}
    auth_mode = (selected.get("auth_mode") or "").strip().lower()
    if auth_mode == "delegated":
        conversation_id = get_conversation_id()
        if not conversation_id:
            raise DelegatedAuthRequiredError("delegated 模式缺少会话上下文，请先在 Bot 会话中执行 /auth login。")
        selected_name = (selected.get("name") or "").strip()
        selected_env = _find_env_by_name(selected_name) or selected
        return require_authenticated_credential(conversation_id, selected_env)

    for env in _load_environments():
        if subscription_id in env.get("subscriptions", []):
            return _credential_for_env(env)
    return DefaultAzureCredential()


def has_customer_config() -> bool:
    return len(_load_environments()) > 0
