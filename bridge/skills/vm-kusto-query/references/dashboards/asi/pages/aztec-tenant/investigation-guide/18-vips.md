# VIPs

> Source: **Aztec — Tenant** dashboard, chapter **VIPs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Tenant VIPs

_Widget purpose:_ VIPs

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `VIPs`

```kusto
LogTenantSnapshot
| where Tenant == queryTenant and tenantName == queryTenantName
| top 1 by PreciseTimeStamp desc
| project vips
| extend IPs = split(vips, ",")
| mv-expand IPs
| project VIP = tostring(IPs)
| join kind=leftouter (
    DCMNMLBEngineClientGoalStateInfoEtwTable
    | where Tenant == queryTenant
    | where vipConfig has queryTenantName
    | summarize arg_max(PreciseTimeStamp, publicIPAddress) by publicIPAddress
    | project VIPTimeStamp = PreciseTimeStamp, publicIPAddress
) on $left.VIP == $right.publicIPAddress
| project VIPTimeStamp, VIP
| order by VIPTimeStamp desc
```

**Params:** `{queryTenantName}`, `{queryTenant}`

---
