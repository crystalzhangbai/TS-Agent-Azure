# Gateway Service

> Source: **Aztec — Clusters** dashboard, chapter **Gateway Service** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## GatewayServiceTraceEvent 

### Check GatewayServiceTraceEvent by Cluster

_Widget purpose:_ GatewayServiceTraceEvent 

Cluster: `azcpplatform.westcentralus.kusto.windows.net` · Database: `azcpplatform` · Type: `Table`
Source panel: `Gateway Service > GatewayServiceTraceEvent `

```kusto
GatewayServiceTraceEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Tenant =~ queryClusterTenantName
| where level in ("Error", "Warning") or 
  message has_any("primary replica", "replica primary information", "Not a successful response", "Primary check request was faulted ", "Could not find primary for ") 
  or componentName contains "FabricPrimaryChaserV2"
| project PreciseTimeStamp, ActivityId, level, componentName, message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryClusterTenantName}`

---
