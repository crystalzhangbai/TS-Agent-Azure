# Eviction

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Eviction** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## LowPriorityVmPreemptionEvent 

### Query LowPriorityVmPreemptionEvent

_Widget purpose:_ LowPriorityVmPreemptionEvent 

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Eviction > LowPriorityVmPreemptionEvent `

```kusto
LowPriorityVmPreemptionEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where message contains queryContainerId or message contains queryTenantName or message contains queryRoleInstanceName
| project PreciseTimeStamp, Tenant, message, context
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryTenantName}`, `{queryRoleInstanceName}`

---
