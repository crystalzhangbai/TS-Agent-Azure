"""ADX / ICM 深链生成 —— 人在环(human-in-the-loop)方案。

当内部遥测(Kusto/ICM)当前身份无权限自动查询时，agent 用这些工具生成"精确查询 + 可点击深链"，
让有权限的工程师本人点开运行、把结果贴回对话。这样始终合规（用工程师本人身份、本人审计）。
"""
import base64
import gzip
import json
import urllib.parse


def build_adx_deeplink(query: str, cluster_url: str, database: str) -> str:
    """为一条 KQL 生成 ADX(dataexplorer.azure.com) 可点击深链。

    当需要查内部 Kusto、但当前身份无权限自动执行时调用它：生成精确 KQL + 深链，
    交给有权限的工程师点开运行并把结果贴回。

    参数：
    - query: 完整、全限定的 KQL（应以 cluster('...').database('...').Table 开头）。
    - cluster_url: 集群地址，如 https://azurecm.kusto.windows.net 或 azurecm.kusto.windows.net。
    - database: 数据库名。
    """
    if not query or not cluster_url or not database:
        return json.dumps({"error": "需要 query + cluster_url + database"}, ensure_ascii=False)

    # ADX web 支持 gzip+base64 压缩后的 query 参数
    compressed = base64.b64encode(gzip.compress(query.encode("utf-8"))).decode("ascii")
    encoded_query = urllib.parse.quote(compressed)
    cluster = cluster_url.replace("https://", "").replace("http://", "").rstrip("/")
    link = (
        f"https://dataexplorer.azure.com/clusters/{cluster}"
        f"/databases/{urllib.parse.quote(database)}?query={encoded_query}"
    )
    return json.dumps({
        "adx_deeplink": link,
        "query": query,
        "cluster": cluster,
        "database": database,
        "hint": "无权限自动执行。请有权限的工程师点开链接在 Web ADX 中运行，并把结果贴回对话。",
    }, ensure_ascii=False)


def build_icm_link(incident_id: str) -> str:
    """为一个 IcM incident 生成门户深链。当需要看 IcM 但无权限自动查询时调用。"""
    if not incident_id or not str(incident_id).strip().isdigit():
        return json.dumps({"error": "需要数字 incident_id"}, ensure_ascii=False)
    link = f"https://portal.microsofticm.com/imp/v3/incidents/details/{incident_id}/home"
    return json.dumps({
        "icm_link": link,
        "incident_id": incident_id,
        "hint": "请有权限的工程师点开查看 IcM 详情，并把关键信息贴回对话。",
    }, ensure_ascii=False)
