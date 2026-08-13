"""把现有的 Azure 查询能力（内网IP定位VM + VM指标）包装成 LLM 可调用的工具。

设计原则（对齐架构记忆 /memories/repo/sre-agent-architecture.md）：
- 这里先用最简单的"Python 函数 = tool"方式接入，快速跑通 MVP。
- 未来这些函数会被抽成独立 MCP server / SKILL.md，被 MAF core 动态发现。
"""
import json
import os
import re

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

from credentials import credential_for_subscription, has_customer_config, iter_environments


def _default_credential():
    """无客户配置时的回退：优先 .env 里的 SP，否则 az login。"""
    tenant = os.environ.get("AZURE_TENANT_ID") or os.environ.get("nonprod_tenantid")
    client_id = os.environ.get("AZURE_CLIENT_ID") or os.environ.get("nonprod_clientid")
    secret = os.environ.get("AZURE_CLIENT_SECRET") or os.environ.get("nonprod_clientsecret")
    if tenant and client_id and secret:
        return ClientSecretCredential(tenant, client_id, secret)
    return DefaultAzureCredential()


def _kql_literal(value: str) -> str:
    return (value or "").replace("'", "''")


def _parse_vm_resource_id(resource_id: str) -> dict:
    rid = (resource_id or "").strip()
    pattern = re.compile(
        r"^/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft\.Compute/virtualMachines/([^/]+)$",
        re.IGNORECASE,
    )
    m = pattern.match(rid)
    if not m:
        return {}
    return {
        "subscription_id": m.group(1),
        "resource_group": m.group(2),
        "vm_name": m.group(3),
        "resource_id": rid,
    }


# 按内网IP搜 VM 的 Resource Graph 查询
def _vm_by_ip_query(private_ip: str, subscriptions: list[str]) -> QueryRequest:
    return QueryRequest(
        query=f"""Resources
            | where type =~ 'microsoft.network/networkinterfaces'
            | mv-expand ipconfig = properties.ipConfigurations
            | extend privateIp = tostring(ipconfig.properties.privateIPAddress),
                     vmId = tolower(tostring(properties.virtualMachine.id))
            | where privateIp == '{private_ip}'
            | join kind=inner (
                Resources
                | where type =~ 'microsoft.compute/virtualmachines'
                | extend vmId = tolower(tostring(id))
                | project vmId, subscriptionId, vmName = name, resourceGroup,
                          vmSize = tostring(properties.hardwareProfile.vmSize)
            ) on vmId
            | project vmId, subscriptionId, vmName, resourceGroup, privateIp, vmSize""",
        subscriptions=subscriptions,
    )


def _vm_by_name_query(subscription_id: str, vm_name: str) -> QueryRequest:
    safe_sub = _kql_literal(subscription_id)
    safe_vm = _kql_literal(vm_name)
    return QueryRequest(
        query=f"""Resources
            | where type =~ 'microsoft.compute/virtualmachines'
            | where subscriptionId =~ '{safe_sub}' and name =~ '{safe_vm}'
            | project vmId = tolower(tostring(id)), resourceId = tostring(id), subscriptionId, vmName = name, resourceGroup,
                      vmSize = tostring(properties.hardwareProfile.vmSize)""",
        subscriptions=[subscription_id],
    )


def _vm_by_resource_id_query(subscription_id: str, resource_id: str) -> QueryRequest:
    safe_sub = _kql_literal(subscription_id)
    safe_id = _kql_literal(resource_id)
    return QueryRequest(
        query=f"""Resources
            | where type =~ 'microsoft.compute/virtualmachines'
            | where subscriptionId =~ '{safe_sub}' and id =~ '{safe_id}'
            | project vmId = tolower(tostring(id)), resourceId = tostring(id), subscriptionId, vmName = name, resourceGroup,
                      vmSize = tostring(properties.hardwareProfile.vmSize)""",
        subscriptions=[subscription_id],
    )


def _normalize_vm_row(row: dict, *, mode: str) -> dict:
    return {
        "match_mode": mode,
        "subscription_id": row.get("subscriptionId", ""),
        "resource_group": row.get("resourceGroup", ""),
        "vm_name": row.get("vmName", ""),
        "resource_id": row.get("resourceId") or row.get("vmId", ""),
        "private_ip": row.get("privateIp", ""),
        "vm_size": row.get("vmSize", ""),
        "environment": row.get("_environment", ""),
    }


def _query_vm_rows_for_subscription(cred, subscription_id: str, request: QueryRequest) -> list[dict]:
    resp = ResourceGraphClient(cred).resources(request)
    return list(resp.data)


# =========================================================
# Tool 1: 通过内网 IP 定位虚拟机（跨所有已注册客户订阅）
# =========================================================
def find_vm_by_private_ip(private_ip: str) -> str:
    """在所有已注册客户环境里，根据内网 IP 查到对应的 VM。

    - 配了 customers.json：逐个客户环境用其 SP 在其订阅里搜，合并结果。
    - 没配：回退到 az login/.env SP，跨该身份可见的订阅搜。
    """
    all_vms: list[dict] = []

    if has_customer_config():
        for env, cred in iter_environments():
            subs = env.get("subscriptions") or [
                s.subscription_id for s in SubscriptionClient(cred).subscriptions.list()
            ]
            try:
                resp = ResourceGraphClient(cred).resources(_vm_by_ip_query(private_ip, subs))
            except Exception as exc:  # noqa: BLE001 - 单个客户失败不影响其他
                all_vms.append({"_environment": env.get("name"), "error": str(exc)})
                continue
            for row in resp.data:
                row["_environment"] = env.get("name")
                all_vms.append(row)
    else:
        cred = _default_credential()
        subs = [s.subscription_id for s in SubscriptionClient(cred).subscriptions.list()]
        resp = ResourceGraphClient(cred).resources(_vm_by_ip_query(private_ip, subs))
        all_vms = list(resp.data)

    found = [v for v in all_vms if "error" not in v]
    if not found:
        return json.dumps(
            {"found": False, "private_ip": private_ip, "message": "在已注册订阅中未找到该内网IP对应的虚拟机", "diagnostics": all_vms},
            ensure_ascii=False,
        )
    return json.dumps({"found": True, "count": len(found), "vms": found[:5]}, ensure_ascii=False)


def resolve_vm_resource_info(
    private_ip: str = "",
    subscription_id: str = "",
    vm_name: str = "",
    resource_id: str = "",
) -> str:
    """Resolve VM identity via one unified workflow.

    Supported inputs (priority order):
    1) resource_id
    2) vm_name + subscription_id
    3) private_ip + subscription_id
    4) private_ip (cross-visible subscriptions)
    """
    private_ip = (private_ip or "").strip()
    subscription_id = (subscription_id or "").strip()
    vm_name = (vm_name or "").strip()
    resource_id = (resource_id or "").strip()

    if not any([private_ip, subscription_id, vm_name, resource_id]):
        return json.dumps(
            {
                "found": False,
                "message": "请至少提供一个输入：resource_id，或(vm_name + subscription_id)，或(private_ip + subscription_id)，或private_ip。",
            },
            ensure_ascii=False,
        )

    rows: list[dict] = []
    mode = ""

    try:
        if resource_id:
            parsed = _parse_vm_resource_id(resource_id)
            if not parsed:
                return json.dumps(
                    {
                        "found": False,
                        "message": "resource_id 不是标准 VM 资源 ID。期望格式: /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<name>",
                        "resource_id": resource_id,
                    },
                    ensure_ascii=False,
                )
            mode = "resource_id"
            sub = parsed["subscription_id"]
            cred = credential_for_subscription(sub)
            rows = _query_vm_rows_for_subscription(cred, sub, _vm_by_resource_id_query(sub, parsed["resource_id"]))

        elif vm_name and subscription_id:
            mode = "vm_name_subscription"
            cred = credential_for_subscription(subscription_id)
            rows = _query_vm_rows_for_subscription(cred, subscription_id, _vm_by_name_query(subscription_id, vm_name))

        elif private_ip and subscription_id:
            mode = "private_ip_subscription"
            cred = credential_for_subscription(subscription_id)
            rows = _query_vm_rows_for_subscription(cred, subscription_id, _vm_by_ip_query(private_ip, [subscription_id]))

        elif private_ip:
            mode = "private_ip_cross_subscription"
            result = json.loads(find_vm_by_private_ip(private_ip))
            if not result.get("found"):
                return json.dumps(result, ensure_ascii=False)
            rows = result.get("vms", [])

    except Exception as exc:  # noqa: BLE001
        return json.dumps(
            {
                "found": False,
                "message": "查询 VM 信息失败",
                "error": str(exc),
                "mode": mode,
            },
            ensure_ascii=False,
        )

    if not rows:
        return json.dumps(
            {
                "found": False,
                "mode": mode,
                "message": "未找到匹配的 VM 资源信息。",
                "inputs": {
                    "private_ip": private_ip,
                    "subscription_id": subscription_id,
                    "vm_name": vm_name,
                    "resource_id": resource_id,
                },
            },
            ensure_ascii=False,
        )

    normalized = [_normalize_vm_row(r, mode=mode) for r in rows]
    return json.dumps(
        {
            "found": True,
            "mode": mode,
            "count": len(normalized),
            "vms": normalized[:10],
        },
        ensure_ascii=False,
    )


# =========================================================
# Tool 2: 查询 VM 指标
# =========================================================
_DEFAULT_METRICS = "Percentage CPU,Available Memory Percentage,Network In Total,Network Out Total"


def get_vm_metrics(
    subscription_id: str,
    resource_group: str,
    vm_name: str,
    start_time_utc: str,
    end_time_utc: str,
    metric_names: str = _DEFAULT_METRICS,
    interval: str = "PT1M",
) -> str:
    """查询指定 VM 在时间窗内的 Azure Monitor 指标，返回压缩后的统计摘要。

    时间格式：ISO8601 UTC，例如 2026-05-19T00:50:00Z。
    """
    cred = credential_for_subscription(subscription_id)
    compute = ComputeManagementClient(cred, subscription_id)
    monitor = MonitorManagementClient(cred, subscription_id)

    vm = compute.virtual_machines.get(resource_group, vm_name)
    resource_id = vm.id
    timespan = f"{start_time_utc}/{end_time_utc}"

    result = monitor.metrics.list(
        resource_id, timespan, interval, metric_names, "average,total,maximum", None, None, None
    )

    summary = []
    for metric in result.value:
        points = []
        for ts in metric.timeseries:
            for d in ts.data:
                val = d.average if d.average is not None else d.total
                if val is not None:
                    points.append(val)
        if points:
            summary.append({
                "metric": metric.name.value,
                "unit": metric.unit,
                "samples": len(points),
                "avg": round(sum(points) / len(points), 2),
                "max": round(max(points), 2),
                "min": round(min(points), 2),
            })
        else:
            summary.append({"metric": metric.name.value, "unit": metric.unit, "samples": 0})

    return json.dumps({
        "vm": vm_name,
        "resource_group": resource_group,
        "timespan": timespan,
        "metrics": summary,
    }, ensure_ascii=False)


# =========================================================
# 工具的 JSON Schema（提供给 Azure OpenAI function calling）
# =========================================================
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "resolve_vm_resource_info",
            "description": "统一解析 VM 资源信息：支持 resource_id，或 vm_name+subscription_id，或 private_ip(+subscription_id)。返回 subscription/resource_group/vm_name/resource_id 等字段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "private_ip": {"type": "string", "description": "内网IP，如 10.83.4.46"},
                    "subscription_id": {"type": "string", "description": "订阅ID。配合 vm_name 或 private_ip 使用"},
                    "vm_name": {"type": "string", "description": "虚拟机名称。需要与 subscription_id 配合"},
                    "resource_id": {"type": "string", "description": "完整 VM 资源ID。提供后优先使用"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_vm_by_private_ip",
            "description": "根据虚拟机内网IP地址，查找对应的订阅ID、资源组、VM名称和资源ID。当用户只给了IP时先调用它。",
            "parameters": {
                "type": "object",
                "properties": {
                    "private_ip": {"type": "string", "description": "虚拟机的内网IP地址，如 10.94.109.31"}
                },
                "required": ["private_ip"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_vm_metrics",
            "description": "查询指定虚拟机在某个UTC时间窗内的 Azure Monitor 性能指标（CPU/内存/网络等）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "subscription_id": {"type": "string", "description": "订阅ID"},
                    "resource_group": {"type": "string", "description": "资源组名称"},
                    "vm_name": {"type": "string", "description": "虚拟机名称"},
                    "start_time_utc": {"type": "string", "description": "开始时间, ISO8601 UTC, 如 2026-05-19T00:50:00Z"},
                    "end_time_utc": {"type": "string", "description": "结束时间, ISO8601 UTC, 如 2026-05-19T01:20:00Z"},
                    "metric_names": {"type": "string", "description": "逗号分隔的指标名，可省略使用默认(CPU/内存/网络)"},
                    "interval": {"type": "string", "description": "抽样间隔, PT1M 或 PT1H, 默认 PT1M"},
                },
                "required": ["subscription_id", "resource_group", "vm_name", "start_time_utc", "end_time_utc"],
            },
        },
    },
]

# 名称 -> 可调用函数
TOOL_FUNCS = {
    "resolve_vm_resource_info": resolve_vm_resource_info,
    "find_vm_by_private_ip": find_vm_by_private_ip,
    "get_vm_metrics": get_vm_metrics,
}
