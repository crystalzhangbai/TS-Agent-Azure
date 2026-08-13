"""Kusto (ADX) 查询工具 —— AZ CLI access token 方案（供 kusto-query skill 使用）。

用于查询 Azure 底层内部遥测集群（host 故障、热迁移、磁盘生命周期、ping 可用性等）。

⚠️ 凭据模型（重要）：
- 内部遥测(Kusto/DFM/ICM) 只能用公司 AAD 身份。
- 本实现显式通过 Azure CLI 获取 Kusto 资源的 access token，避免 DAC 凭据链歧义。
- 需要在 bot 运行账号的同一会话已完成 `az login`。

默认集群/库：可用 .env 的 KUSTO_CLUSTER_URL / KUSTO_DATABASE 设默认值。
"""
import json
import os
import shutil
import subprocess
import base64
import gzip
import time
import urllib.parse

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from runtime_event_logger import log_event

_DEFAULT_CLUSTER = os.environ.get("KUSTO_CLUSTER_URL", "")
_DEFAULT_DATABASE = os.environ.get("KUSTO_DATABASE", "")
_KUSTO_AZ_TENANT_ID = os.environ.get("KUSTO_AZ_TENANT_ID", "").strip()
_MAX_ROWS = 50

# Kusto AAD （Audience）set to be Kusto。
_KUSTO_RESOURCE = "https://kusto.kusto.windows.net"


class AzCliTokenError(RuntimeError):
    """Preserve az cli failure details so caller can echo near-raw error text."""

    def __init__(self, message: str, *, returncode: int, stderr: str, stdout: str):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout


# az 在不同 Windows 环境的可执行名：.cmd 是安装器默认形态，.exe 是 pip 装的，Linux/macOS 无扩展名。
_AZ_CANDIDATE_NAMES = ("az", "az.cmd", "az.bat", "az.exe")
# 安装器默认落地路径——用于 PATH 被裁剪（服务/计划任务/精简 shell）时的兵底探测。
_AZ_WELL_KNOWN_PATHS = (
    r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
    r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
)


def _resolve_az_executable() -> str:
    """解析 Azure CLI 可执行文件的完整路径（多环境兵底）。

    Windows 上 az 实际是 az.cmd（批处理脚本），且不同环境 PATH/PATHEXT 差异很大。
    直接把 "az" 交给 subprocess 会走 CreateProcess、不查 PATHEXT，报 FileNotFoundError
    ([WinError 2] 系统找不到指定的文件)。这里逐级兵底解析：

    1) 环境变量 AZ_CLI_PATH 显式指定（给运维一个逃生口）；
    2) 按候选名走 shutil.which（遵循 PATHEXT，能命中 az.cmd；Linux/macOS 命中无扩展名 az）；
    3) 探测安装器默认落地路径（应对 PATH 被裁剪的服务/计划任务环境）。
    """
    tried = []

    explicit = os.environ.get("AZ_CLI_PATH", "").strip().strip('"')
    if explicit:
        tried.append("AZ_CLI_PATH={0!r}".format(explicit))
        if os.path.isfile(explicit):
            return explicit

    for name in _AZ_CANDIDATE_NAMES:
        found = shutil.which(name)
        tried.append("which({0})->{1}".format(name, found))
        if found:
            return found

    for path in _AZ_WELL_KNOWN_PATHS:
        tried.append("probe({0})".format(path))
        if os.path.isfile(path):
            return path

    raise AzCliTokenError(
        "找不到 Azure CLI (az)。请安装 Azure CLI 后 `az login`；"
        "若已安装但不在 PATH，可用环境变量 AZ_CLI_PATH 指定 az 的完整路径。",
        returncode=-1,
        stderr="az executable not resolvable. tried: " + "; ".join(tried),
        stdout="",
    )


def _windows_no_window_flag() -> int:
    """在 Windows 上避免调用 az.cmd 时弹出黑色控制台窗口（pythonw/服务/GUI 宿主场景）。

    CREATE_NO_WINDOW 仅 Windows 存在；其它平台返回 0（无副作用）。
    """
    if os.name == "nt":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return 0


def _acquire_kusto_token_from_az_cli() -> str:
    cmd = [
        _resolve_az_executable(),
        "account",
        "get-access-token",
        "--resource",
        _KUSTO_RESOURCE,
        "--query",
        "accessToken",
        "-o",
        "tsv",
    ]
    if _KUSTO_AZ_TENANT_ID:
        cmd.extend(["--tenant", _KUSTO_AZ_TENANT_ID])
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            # 中文/非英文 Windows 默认用 GBK 解码 az 输出，遇非 ASCII 会报 UnicodeDecodeError，
            # 把真正的错误信息掩盖掉。显式 UTF-8 + replace 兵底：token 是纯 ASCII，绝不受影响。
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            creationflags=_windows_no_window_flag(),
        )
    except subprocess.TimeoutExpired as exc:
        raise AzCliTokenError(
            "az account get-access-token 超时（>30s）。可能是首次登录/网络受限，"
            "请手动跑一次 `az account get-access-token` 确认。",
            returncode=-1,
            stderr=str(exc),
            stdout="",
        ) from exc
    except OSError as exc:
        # 即使解析到了路径，执行 .cmd 仍可能因权限/句柄等失败——归一成可诊断错误。
        raise AzCliTokenError(
            "启动 az 进程失败：{0}".format(exc),
            returncode=-1,
            stderr=str(exc),
            stdout="",
        ) from exc

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        raise AzCliTokenError(
            "az account get-access-token failed: {0}".format(stderr),
            returncode=proc.returncode,
            stderr=stderr,
            stdout=stdout,
        )

    token = (proc.stdout or "").strip()
    if not token:
        raise RuntimeError("az account get-access-token returned empty token")

    return token


def _acquire_kusto_token_from_sp() -> str:
    """用专用 Kusto Service Principal 取 token（无人值守/服务器环境的兵底，不依赖 az login）。

    仅当 .env 同时配了 KUSTO_TENANT_ID / KUSTO_CLIENT_ID / KUSTO_CLIENT_SECRET 时启用；
    否则返回空串，交回上层继续走 az CLI。身份显式、明确，不引入 DefaultAzureCredential 的凭据链歧义。
    """
    tenant = os.environ.get("KUSTO_TENANT_ID", "").strip()
    client_id = os.environ.get("KUSTO_CLIENT_ID", "").strip()
    client_secret = os.environ.get("KUSTO_CLIENT_SECRET", "").strip()
    if not (tenant and client_id and client_secret):
        return ""

    from azure.identity import ClientSecretCredential

    credential = ClientSecretCredential(tenant, client_id, client_secret)
    # Kusto 通用 audience（v2 scope 形式），与 az CLI 的 --resource 保持一致。
    token = credential.get_token(_KUSTO_RESOURCE + "/.default")
    return token.token


def _acquire_kusto_token() -> str:
    """Kusto token 获取主入口：SP（显式配置优先）→ az CLI 依次降级。

    两条路径身份都明确，任一成功即返回；全部失败时汇总原因，便于定位。
    """
    sp_error = None
    try:
        sp_token = _acquire_kusto_token_from_sp()
        if sp_token:
            return sp_token
    except Exception as exc:  # noqa: BLE001 - SP 失败不应阻断 az 兵底
        sp_error = exc

    try:
        return _acquire_kusto_token_from_az_cli()
    except AzCliTokenError as exc:
        if sp_error is not None:
            exc.args = ("{0} | 另外 SP 兵底也失败: {1}".format(exc.args[0], sp_error),)
        raise


def _build_client(cluster_url: str) -> KustoClient:
    # 通过 token_provider 显式喂给 Kusto SDK，避免被环境变量/SP 抢占。
    kcsb = KustoConnectionStringBuilder.with_token_provider(
        cluster_url,
        _acquire_kusto_token,
    )
    return KustoClient(kcsb)


def _build_adx_deeplink(query: str, cluster_url: str, database: str) -> str:
    compressed = base64.b64encode(gzip.compress(query.encode("utf-8"))).decode("ascii")
    encoded_query = urllib.parse.quote(compressed)
    cluster = cluster_url.replace("https://", "").replace("http://", "").rstrip("/")
    return (
        f"https://dataexplorer.azure.com/clusters/{cluster}"
        f"/databases/{urllib.parse.quote(database)}?query={encoded_query}"
    )


def _try_build_adx_deeplink(query: str, cluster: str, database: str) -> str:
    if not query or not cluster or not database:
        return ""
    try:
        return _build_adx_deeplink(query=query, cluster_url=cluster, database=database)
    except Exception:
        return ""


def run_kusto_query(query: str, cluster_url: str = "", database: str = "") -> str:
    """对 Azure 底层遥测 Kusto(ADX) 集群执行 KQL 查询，返回前若干行结果(JSON)。

    参数：
    - query: 完整的 KQL 查询语句。
    - cluster_url: Kusto 集群地址(https://xxx.kusto.windows.net)；不传则用环境默认。
    - database: 数据库名；不传则用环境默认。

    用途：查 host 故障、热迁移(live migration)、磁盘生命周期、ping 可用性等平台级遥测。
    """
    started = time.perf_counter()
    cluster = cluster_url or _DEFAULT_CLUSTER
    db = database or _DEFAULT_DATABASE
    if not cluster or not db:
        payload = json.dumps(
            {
                "error": "未配置 Kusto 集群/库。请在调用时传 cluster_url+database，或在 .env 设 KUSTO_CLUSTER_URL/KUSTO_DATABASE。"
            },
            ensure_ascii=False,
        )
        log_event(
            "kusto_query",
            status="error",
            inputs={"query": query, "cluster_url": cluster_url, "database": database},
            outputs=payload,
            metadata={"cluster": cluster, "database": db, "duration_ms": int((time.perf_counter() - started) * 1000)},
        )
        return payload

    try:
        client = _build_client(cluster)
        response = client.execute(db, query)
        table = response.primary_results[0]
        cols = [c.column_name for c in table.columns]
        rows = []
        for i, row in enumerate(table):
            if i >= _MAX_ROWS:
                break
            rows.append({c: (row[c].isoformat() if hasattr(row[c], "isoformat") else row[c]) for c in cols})
        payload = json.dumps(
            {
                "cluster": cluster,
                "database": db,
                "columns": cols,
                "row_count": len(rows),
                "truncated": len(table) > _MAX_ROWS,
                "rows": rows,
            },
            ensure_ascii=False,
            default=str,
        )
        log_event(
            "kusto_query",
            status="ok",
            inputs={"query": query, "cluster_url": cluster_url, "database": database},
            outputs=payload,
            metadata={
                "cluster": cluster,
                "database": db,
                "row_count": len(rows),
                "duration_ms": int((time.perf_counter() - started) * 1000),
            },
        )
        return payload
    except Exception as exc:  # noqa: BLE001 - 错误回传给模型
        adx_deeplink = _try_build_adx_deeplink(query=query, cluster=cluster, database=db)
        payload = {
            "error": str(exc),
            "raw_error": str(exc),
            "error_type": type(exc).__name__,
            "hint": "Kusto uses Azure CLI token. Run az login (same OS user/session); if tenant is required, set KUSTO_AZ_TENANT_ID or run az login --tenant <tenant-id>.",
            "cluster": cluster,
            "database": db,
            "kusto_failed": True,
            "next_action": "share_error_and_open_adx_deeplink",
        }

        if isinstance(exc, AzCliTokenError):
            payload["az_cli_returncode"] = exc.returncode
            payload["az_cli_stderr"] = exc.stderr
            payload["az_cli_stdout"] = exc.stdout

        if adx_deeplink:
            payload["adx_deeplink"] = adx_deeplink

        payload["customer_visible_error"] = (
            "Kusto query failed. "
            "Please review raw_error/az_cli_stderr for root cause. "
            "If adx_deeplink exists, open it with a permitted account and run the same query."
        )
        payload_text = json.dumps(payload, ensure_ascii=False)
        log_event(
            "kusto_query",
            status="error",
            inputs={"query": query, "cluster_url": cluster_url, "database": database},
            outputs=payload_text,
            error=str(exc),
            metadata={"cluster": cluster, "database": db, "duration_ms": int((time.perf_counter() - started) * 1000)},
        )

        return payload_text
