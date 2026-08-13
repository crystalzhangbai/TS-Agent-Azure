"""Startup preflight checklist for SRE Bridge bot."""

import os
import shutil
import subprocess
from typing import Any

from session_environment import list_environment_profiles


_DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def _load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                key = k.strip()
                if not key:
                    continue
                if key not in os.environ:
                    os.environ[key] = v.strip().strip('"').strip("'")
    except OSError:
        return


_load_dotenv(_DOTENV_PATH)


def _mark(flag: bool) -> str:
    return "PASS" if flag else "TODO"


def _safe_tail(text: str, max_len: int = 180) -> str:
    t = (text or "").strip().replace("\r", " ").replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


def _run_cmd(cmd: list[str], timeout_sec: int = 8) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            check=False,
        )
        if proc.returncode == 0:
            out = proc.stdout.strip() or proc.stderr.strip()
            return True, _safe_tail(out)
        return False, _safe_tail(proc.stderr or proc.stdout)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _resolve_cmd(names: tuple[str, ...]) -> str:
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return ""

def build_preflight_items() -> list[dict[str, Any]]:
    az_path = _resolve_cmd(("az.cmd", "az.exe", "az.bat", "az"))
    devtunnel_path = _resolve_cmd(("devtunnel.exe", "devtunnel.cmd", "devtunnel.bat", "devtunnel"))
    az_ok = bool(az_path)
    devtunnel_ok = bool(devtunnel_path)

    app_id_ok = bool(os.environ.get("MicrosoftAppId"))
    app_pwd_ok = bool(os.environ.get("MicrosoftAppPassword"))
    aoai_ok = bool(os.environ.get("AZURE_OPENAI_ENDPOINT")) and bool(os.environ.get("AZURE_OPENAI_MODEL"))
    foundry_ok = bool(os.environ.get("FOUNDRY_TENANT_ID")) and bool(os.environ.get("FOUNDRY_CLIENT_ID")) and bool(os.environ.get("FOUNDRY_CLIENT_SECRET"))

    kusto_tenant = os.environ.get("KUSTO_AZ_TENANT_ID", "72f988bf-86f1-41af-91ab-2d7cd011db47")
    az_login_ok = False
    az_login_detail = ""
    if az_ok:
        ok, out = _run_cmd([az_path, "account", "show", "--query", "tenantId", "-o", "tsv"])
        az_login_ok = ok and bool((out or "").strip())
        if az_login_ok:
            tenant = (out or "").strip()
            if tenant.lower() == kusto_tenant.lower():
                az_login_detail = f"当前 az tenant: {tenant}"
            else:
                az_login_detail = f"当前 az tenant: {tenant}（建议切到 {kusto_tenant}）"
        else:
            az_login_detail = out or "请先执行 az login"

    devtunnel_login_ok = False
    devtunnel_login_detail = ""
    if devtunnel_ok:
        ok, out = _run_cmd([devtunnel_path, "user", "show"])
        devtunnel_login_ok = ok
        devtunnel_login_detail = out or ("已登录" if ok else "请先执行 devtunnel user login")

    profiles = list_environment_profiles()
    delegated_profiles = [p for p in profiles if (p.get("auth_mode") or "").lower() == "delegated"]
    delegated_ok = len(delegated_profiles) > 0 and any((p.get("delegated_tenant_id") or p.get("tenant_id") or "").strip() for p in delegated_profiles)
    delegated_names = ", ".join(p.get("name", "") for p in delegated_profiles) or "(none)"

    endpoint_cfg_ok = bool(os.environ.get("BOT_RESOURCE_ID")) and (
        (bool(os.environ.get("MGMT_SP_TENANT_ID")) and bool(os.environ.get("MGMT_SP_CLIENT_ID")) and bool(os.environ.get("MGMT_SP_CLIENT_SECRET")))
        or az_ok
    )

    return [
        {
            "title": "确认 Bot Framework 配置",
            "checked": app_id_ok and app_pwd_ok,
            "detail": "MicrosoftAppId / MicrosoftAppPassword 已配置",
            "fix": "若未配置：复制 .env.example 为 .env，填写 MicrosoftAppId 与 MicrosoftAppPassword。",
        },
        {
            "title": "确认 Azure OpenAI/Foundry 配置",
            "checked": aoai_ok and foundry_ok,
            "detail": "AOAI 与 Foundry 关键变量已配置",
            "fix": "补齐 AZURE_OPENAI_ENDPOINT/AZURE_OPENAI_MODEL 和 FOUNDRY_TENANT_ID/FOUNDRY_CLIENT_ID/FOUNDRY_CLIENT_SECRET。",
        },
        {
            "title": "确认 Azure CLI 可用",
            "checked": az_ok,
            "detail": "本机可执行 az（Kusto CLI token 场景必需）",
            "fix": "未安装请先安装 Azure CLI。",
        },
        {
            "title": "Kusto tenant 预登录",
            "checked": az_login_ok,
            "detail": az_login_detail or f"先执行: az login --tenant {kusto_tenant}",
            "fix": f"执行: az login --tenant {kusto_tenant}",
        },
        {
            "title": "确认 devtunnel CLI 与登录",
            "checked": devtunnel_ok and devtunnel_login_ok,
            "detail": devtunnel_login_detail or "请先执行 devtunnel user login",
            "fix": "执行: devtunnel user login",
        },
        {
            "title": "确认 delegated 环境配置",
            "checked": delegated_ok,
            "detail": f"已发现 delegated 环境: {delegated_names}",
            "fix": "在 session_environments.json 或 customers.json 中补齐 delegated_tenant_id（或 tenant_id）。",
        },
        {
            "title": "确认自动更新 Bot endpoint 条件",
            "checked": endpoint_cfg_ok,
            "detail": "BOT_RESOURCE_ID + (MGMT_SP_* 或 az 登录)",
            "fix": "补齐 BOT_RESOURCE_ID；推荐补齐 MGMT_SP_TENANT_ID/MGMT_SP_CLIENT_ID/MGMT_SP_CLIENT_SECRET。",
        },
    ]


def render_preflight_text() -> str:
    lines = ["SRE Bridge 运行前检查", ""]
    for idx, item in enumerate(build_preflight_items(), start=1):
        checked = bool(item.get("checked"))
        lines.append(f"{idx}. [{_mark(checked)}] {item.get('title')}")
        lines.append(f"   现状: {item.get('detail')}")
        if not checked:
            lines.append(f"   修复: {item.get('fix')}")
        lines.append("")
    lines.append("Teams 会话操作顺序: /env <环境> -> /auth login (delegated) -> /auth status -> 提问")
    return "\n".join(lines)


def build_preflight_report() -> dict[str, Any]:
    items = build_preflight_items()
    passed = sum(1 for x in items if bool(x.get("checked")))
    total = len(items)
    return {
        "ok": passed == total,
        "passed": passed,
        "total": total,
        "items": items,
        "next_steps": [
            "运行前先执行 preflight-check.ps1",
            "若存在 TODO，按修复建议处理后再启动 run.cmd/start-colleague.cmd",
            "delegated 场景在 Teams 会话中执行 /env <环境> 与 /auth login",
        ],
    }
