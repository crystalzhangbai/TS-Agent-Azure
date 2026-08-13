"""Bot 的大脑 —— Microsoft Agent Framework (MAF) 版。"""

import os
import re
from typing import Any

from azure.identity import AzureCliCredential, ClientSecretCredential
from agent_framework import Agent, AgentSession
from agent_framework.foundry import FoundryChatClient

from config import DefaultConfig

from agent_trace import format_trace, start_trace, traced
from nanite_loader import (
    build_nanite_skill_index,
    get_nanite_profile,
    load_nanite_agent_instructions,
    load_nanite_skill,
    read_nanite_skill_file,
)
from runtime_context import (
    reset_conversation_id,
    reset_session_environment,
    set_conversation_id,
    set_session_environment,
)
from skill_loader import build_skill_index, load_skill, read_skill_file
from tools.adx_link import build_adx_deeplink, build_icm_link
from tools.azure_vm import find_vm_by_private_ip, get_vm_metrics, resolve_vm_resource_info
from tools.kusto import run_kusto_query

CONFIG = DefaultConfig()
PROJECT_ENDPOINT = CONFIG.FOUNDRY_PROJECT_ENDPOINT

_BASE_INSTRUCTIONS = (
    "你是一个资深的Azure排障工程师，在Teams群聊里帮工程师排查Azure架构出现的问题。\n"
    "能力：解析VM资源身份(resource_id/vm_name/private_ip)、查询VM性能指标(CPU/内存/网络)、查内部 Kusto 遥测。\n"
    "\n## 语言/术语（重要）\n"
    "- 用与用户相同的语言回复（用户中文就中文）。\n"
    "- 但所有技术标识符必须保留英文原文，绝不翻译成中文。\n"
    "- 示例：必须写 Guest OS，不要写 来宾 OS。\n"
    "\n## 凭据/权限策略（重要）\n"
    "1. 客户配置/指标(ARM/Monitor)：用客户 SP 直接自动查(resolve_vm_resource_info/find_vm_by_private_ip/get_vm_metrics)。\n"
    "2. 内部遥测(Kusto/ICM)：只能用公司 AAD 身份，且受严格权限限制。\n"
    "- 必须先实际调用 run_kusto_query 去尝试执行查询，绝不允许在没调用它之前就直接生成深链。\n"
    "- 只有当 run_kusto_query 本次真的返回了错误(error/kusto_failed)时，才回退到 build_adx_deeplink/build_icm_link。\n"
    "- 若 run_kusto_query 成功返回数据，直接基于数据作答，不要再发深链。\n"
    "\n## 排查规则\n"
    "1. 先调用 resolve_vm_resource_info 统一解析VM身份。\n"
    "2. 时间要转成 ISO8601 UTC（用户常给北京时间，需-8小时）。\n"
    "3. 拿到数据后，用简洁中文给出结论。\n"
    "4. 缺少必要信息时，主动追问。\n"
)

_NANITE_DEEP_MODE_ENABLED = os.environ.get("NANITE_DEEP_MODE_ENABLED", "true").lower() != "false"

_QUERY_PATTERNS = [
    r"在哪个node",
    r"哪个node",
    r"哪个container",
    r"在哪个container",
    r"resource\\s*id",
    r"资源\\s*id",
    r"subscription",
    r"订阅",
    r"resource group",
    r"vm名",
    r"vm name",
    r"mapping",
    r"映射",
    r"字段",
    r"查一下.*(值|信息)",
]

_SECTION_DIVIDER = "----------------------------------------"

_agent: Agent | None = None
_nanite_agent: Agent | None = None
_router_agent: Agent | None = None
_smalltalk_agent: Agent | None = None
_sessions: dict[str, AgentSession] = {}
_nanite_sessions: dict[str, AgentSession] = {}


def _split_md_row(line: str) -> list[str]:
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return parts if any(parts) else []


def _is_md_sep_row(line: str) -> bool:
    cells = _split_md_row(line)
    if not cells:
        return False
    return all(bool(re.fullmatch(r":?-{3,}:?", c.replace(" ", ""))) for c in cells)


def _render_plain_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            if i < len(widths):
                widths[i] = max(widths[i], len(c))

    def _fmt(cells: list[str]) -> str:
        out: list[str] = []
        for i, w in enumerate(widths):
            c = cells[i] if i < len(cells) else ""
            out.append(c.ljust(w))
        return "  ".join(out).rstrip()

    lines = [_fmt(headers), _fmt(["-" * w for w in widths])]
    lines.extend(_fmt(r) for r in rows)
    return lines


def _convert_markdown_tables(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if "|" in lines[i] and i + 1 < n and _is_md_sep_row(lines[i + 1]):
            headers = _split_md_row(lines[i])
            i += 2
            rows: list[list[str]] = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_md_row(lines[i]))
                i += 1
            out.extend(_render_plain_table(headers, rows))
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def _normalize_inline_pipe_tables(text: str) -> str:
    """Turn one-line pipe tables into normal markdown table lines.

    Some model outputs compress table rows into a single line using "||".
    Example:
    | A | B ||---|---|| x | y ||
    """
    t = text or ""
    if "Dimension | Score | Justification" not in t and "||" not in t:
        return t

    # Ensure header starts as a markdown row.
    t = t.replace("Dimension | Score | Justification", "| Dimension | Score | Justification")
    # Split compressed row separators to line breaks so downstream table parser can handle it.
    t = t.replace("||", "\n|")
    # Clean occasional duplicated leading pipes caused by replacement.
    t = re.sub(r"\n\|\s*\|", "\n|", t)
    return t


def _is_section_header(line: str) -> bool:
    s = (line or "").strip()
    if not s:
        return False
    if re.fullmatch(r"【[^】]+】", s):
        return True
    if re.match(r"^(📊\s*)?confidence\s+score\b", s, flags=re.IGNORECASE):
        return True
    if re.match(r"^#{1,6}\s+\S", s):
        return True
    return False


def _add_section_dividers(text: str) -> str:
    lines = (text or "").splitlines()
    out: list[str] = []
    seen_nonempty = False

    for line in lines:
        if _is_section_header(line) and seen_nonempty:
            # Ensure: previous module content -> blank line -> divider -> blank line -> next header
            if out and out[-1].strip():
                out.append("")
            if not out or out[-1] != _SECTION_DIVIDER:
                out.append(_SECTION_DIVIDER)
            out.append("")

        out.append(line)
        if line.strip():
            seen_nonempty = True

    return "\n".join(out)


def _polish_reply_text(text: str) -> str:
    t = text or ""
    t = t.replace("【主agent基线结果】", "【基础信息】")
    t = t.replace("【nanite 深度模式】", "【深度分析】")
    t = re.sub(r"来宾\s*OS", "Guest OS", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*(【[^】]+】)", r"\n\n\1", t)
    t = _normalize_inline_pipe_tables(t)
    t = _convert_markdown_tables(t)
    t = _add_section_dividers(t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t


def _build_instructions() -> str:
    index = build_skill_index()
    return _BASE_INSTRUCTIONS + ("\n\n" + index if index else "")


def _build_foundry_credential() -> ClientSecretCredential | AzureCliCredential:
    tenant_id = (CONFIG.FOUNDRY_TENANT_ID or "").strip()
    client_id = (CONFIG.FOUNDRY_CLIENT_ID or "").strip()
    client_secret = (CONFIG.FOUNDRY_CLIENT_SECRET or "").strip()

    configured = [bool(tenant_id), bool(client_id), bool(client_secret)]
    if any(configured) and not all(configured):
        raise ValueError(
            "Foundry SP config is incomplete. Please set all of: "
            "FOUNDRY_TENANT_ID, FOUNDRY_CLIENT_ID, FOUNDRY_CLIENT_SECRET"
        )
    if not all(configured):
        raise ValueError(
            "Foundry SP config is missing. Please set FOUNDRY_TENANT_ID, "
            "FOUNDRY_CLIENT_ID, FOUNDRY_CLIENT_SECRET in bridge/.env"
        )

    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def _get_agent() -> Agent:
    global _agent
    if _agent is None:
        if not PROJECT_ENDPOINT:
            raise ValueError("FOUNDRY_PROJECT_ENDPOINT is missing. Please set it in bridge/.env")
        client = FoundryChatClient(
            project_endpoint=PROJECT_ENDPOINT,
            model=CONFIG.AOAI_MODEL,
            credential=_build_foundry_credential(),
        )
        _agent = Agent(
            client,
            instructions=_build_instructions(),
            name="SREBridge",
            tools=[
                traced(resolve_vm_resource_info),
                traced(find_vm_by_private_ip),
                traced(get_vm_metrics),
                traced(run_kusto_query),
                traced(build_adx_deeplink),
                traced(build_icm_link),
                traced(load_skill),
                traced(read_skill_file),
            ],
        )
    return _agent


def _build_nanite_instructions() -> str:
    base = load_nanite_agent_instructions()
    overlay = (
        "\n\n## SRE Bridge Integration Contract\n"
        "- You are invoked as independent deep-mode expert after main agent baseline.\n"
        "- Use load_nanite_skill/read_nanite_skill_file for nanite skills and references.\n"
        "- Keep technical identifiers in English.\n"
        "- Do NOT translate technical terms (e.g., keep Guest OS, table names, column names).\n"
        "- If data is insufficient, state missing evidence and next best action.\n"
    )
    idx = build_nanite_skill_index()
    return base + overlay + ("\n\n" + idx if idx else "")


def _get_nanite_agent() -> Agent:
    global _nanite_agent
    if _nanite_agent is None:
        client = FoundryChatClient(
            project_endpoint=PROJECT_ENDPOINT,
            model=CONFIG.AOAI_MODEL,
            credential=_build_foundry_credential(),
        )
        _nanite_agent = Agent(
            client,
            instructions=_build_nanite_instructions(),
            name="NaniteExpert",
            tools=[
                traced(resolve_vm_resource_info),
                traced(run_kusto_query),
                traced(build_adx_deeplink),
                traced(build_icm_link),
                traced(load_nanite_skill),
                traced(read_nanite_skill_file),
                traced(get_nanite_profile),
            ],
        )
    return _nanite_agent


def _get_router_agent() -> Agent:
    global _router_agent
    if _router_agent is None:
        client = FoundryChatClient(
            project_endpoint=PROJECT_ENDPOINT,
            model=CONFIG.AOAI_MODEL,
            credential=_build_foundry_credential(),
        )
        _router_agent = Agent(
            client,
            instructions=(
                "You are an intent router for a Teams SRE bot. "
                "Classify each user message into exactly one label: "
                "smalltalk or troubleshoot.\n"
                "- smalltalk: greetings, thanks, identity/capability questions, casual conversation, "
                "or messages that do not ask troubleshooting analysis.\n"
                "- troubleshoot: any message asking diagnosis/query/investigation of Azure resources, "
                "metrics, Kusto, incidents, subscriptions, auth operations, or technical actions.\n"
                "Output only one token: smalltalk or troubleshoot."
            ),
            name="SREBridgeRouter",
            tools=[],
        )
    return _router_agent


def _get_smalltalk_agent() -> Agent:
    global _smalltalk_agent
    if _smalltalk_agent is None:
        client = FoundryChatClient(
            project_endpoint=PROJECT_ENDPOINT,
            model=CONFIG.AOAI_MODEL,
            credential=_build_foundry_credential(),
        )
        _smalltalk_agent = Agent(
            client,
            instructions=(
                "You are SRE Bridge conversational assistant for Teams. "
                "Respond briefly and naturally (1-3 short sentences).\n"
                "- For greeting/casual chat: friendly short response.\n"
                "- For out-of-scope requests (e.g., weather, jokes unrelated to SRE): "
                "politely say it is out of scope and guide user to ask Azure VM troubleshooting questions.\n"
                "- Keep response in user's language.\n"
                "- Do not produce long templates or checklists in smalltalk mode."
            ),
            name="SREBridgeSmalltalk",
            tools=[],
        )
    return _smalltalk_agent


def _is_query_class(user_text: str) -> bool:
    text = (user_text or "").lower()
    return any(re.search(p, text, re.IGNORECASE) for p in _QUERY_PATTERNS)


def _main_baseline_prompt(user_text: str, session_environment: dict[str, Any] | None) -> str:
    env_block = ""
    if session_environment:
        env_block = (
            "\n\n[SESSION ENVIRONMENT]\n"
            f"name={session_environment.get('name', '')}\n"
            f"auth_mode={session_environment.get('auth_mode', '')}\n"
            f"tenant_id={session_environment.get('tenant_id', '')}\n"
            f"subscriptions={session_environment.get('subscriptions', [])}\n"
        )
    return (
        "请先完成资源定位与基础查询，不做深度根因扩展。"
        "优先返回用户直接问题所需字段（例如 node/container/resource id/subscription/RG/时间对齐）。"
        "若用户问题属于查询类，直接给出答案。"
        "\n\n用户问题:\n"
        + user_text
        + env_block
    )


def _nanite_deep_prompt(user_text: str, baseline_answer: str, session_environment: dict[str, Any] | None) -> str:
    env_block = ""
    if session_environment:
        env_block = (
            "\n\n[SESSION ENVIRONMENT]\n"
            f"name={session_environment.get('name', '')}\n"
            f"auth_mode={session_environment.get('auth_mode', '')}\n"
            f"tenant_id={session_environment.get('tenant_id', '')}\n"
            f"subscriptions={session_environment.get('subscriptions', [])}\n"
        )
    return (
        "你现在作为独立 nanite 深度专家接管分析。"
        "主agent已完成资源定位与基础结论，请在此基础上做深度诊断。"
        "\n\n用户原始问题:\n"
        + user_text
        + "\n\n主agent基线结果:\n"
        + baseline_answer
        + env_block
        + "\n\n请输出:"
        "\n1) 结论"
        "\n2) 关键证据(Kusto/字段)"
        "\n3) 下一步动作"
    )


def clear_conversation_sessions(conversation_id: str) -> None:
    _sessions.pop(conversation_id, None)
    _nanite_sessions.pop(f"{conversation_id}::nanite", None)


async def classify_user_intent(
    user_text: str,
    conversation_id: str,
    session_environment: dict[str, Any] | None = None,
) -> str:
    """Classify user text into smalltalk or troubleshoot.

    Fallback to troubleshoot on any classifier uncertainty to avoid missing real incidents.
    """
    token = set_session_environment(session_environment)
    conv_token = set_conversation_id(conversation_id)
    try:
        router = _get_router_agent()
        env_block = ""
        if session_environment:
            env_block = (
                "\n[SESSION ENVIRONMENT]\n"
                f"name={session_environment.get('name', '')}\n"
                f"auth_mode={session_environment.get('auth_mode', '')}\n"
            )
        prompt = f"[USER MESSAGE]\n{user_text}{env_block}"
        response = await router.run(prompt)
        label = ((getattr(response, "text", None) or str(response)) + "").strip().lower()
        if "smalltalk" in label:
            return "smalltalk"
        if "troubleshoot" in label:
            return "troubleshoot"
        return "troubleshoot"
    except Exception:  # noqa: BLE001
        return "troubleshoot"
    finally:
        reset_conversation_id(conv_token)
        reset_session_environment(token)


async def run_smalltalk(
    user_text: str,
    conversation_id: str,
    session_environment: dict[str, Any] | None = None,
) -> str:
    """Generate concise smalltalk reply without diagnostic tools."""
    token = set_session_environment(session_environment)
    conv_token = set_conversation_id(conversation_id)
    try:
        agent = _get_smalltalk_agent()
        env_block = ""
        if session_environment:
            env_block = (
                "\n[SESSION ENVIRONMENT]\n"
                f"name={session_environment.get('name', '')}\n"
                f"auth_mode={session_environment.get('auth_mode', '')}\n"
            )
        prompt = (
            "User message:\n"
            f"{user_text}\n"
            f"{env_block}\n"
            "Reply as SRE Bridge in concise conversational style."
        )
        response = await agent.run(prompt)
        text = (getattr(response, "text", None) or str(response) or "").strip()
        if not text:
            return "你好，我是 SRE Bridge。你可以描述 Azure VM 的排查问题，我来帮你定位。"
        return text
    except Exception:  # noqa: BLE001
        return "你好，我是 SRE Bridge。你可以描述 Azure VM 的排查问题，我来帮你定位。"
    finally:
        reset_conversation_id(conv_token)
        reset_session_environment(token)


async def run_brain(
    user_text: str,
    conversation_id: str,
    session_environment: dict[str, Any] | None = None,
) -> str:
    """按会话维持多轮上下文，跑一轮 MAF Agent，返回助手文本(附调用链)。"""
    start_trace()

    token = set_session_environment(session_environment)
    conv_token = set_conversation_id(conversation_id)
    try:
        main_agent = _get_agent()
        main_session = _sessions.get(conversation_id)
        if main_session is None:
            main_session = AgentSession()
            _sessions[conversation_id] = main_session

        query_class = _is_query_class(user_text)
        main_prompt = user_text if query_class else _main_baseline_prompt(user_text, session_environment)
        main_response = await main_agent.run(main_prompt, session=main_session)
        main_text = getattr(main_response, "text", None) or str(main_response)

        if query_class or not _NANITE_DEEP_MODE_ENABLED:
            return _polish_reply_text(main_text + format_trace())

        nanite_agent = _get_nanite_agent()
        nanite_conv = f"{conversation_id}::nanite"
        nanite_session = _nanite_sessions.get(nanite_conv)
        if nanite_session is None:
            nanite_session = AgentSession()
            _nanite_sessions[nanite_conv] = nanite_session

        deep_response = await nanite_agent.run(
            _nanite_deep_prompt(user_text, main_text, session_environment),
            session=nanite_session,
        )
        deep_text = getattr(deep_response, "text", None) or str(deep_response)

        merged = "【基础信息】\n" + main_text + "\n\n" + "【深度分析】\n" + deep_text
        return _polish_reply_text(merged + format_trace())
    finally:
        reset_conversation_id(conv_token)
        reset_session_environment(token)
