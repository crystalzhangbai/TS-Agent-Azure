# (top-level)

> Source: **CRP VM Start Troubleshooter Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VM Start Troubleshooter"

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
VMApiQosEvent
| where PreciseTimeStamp between(globalFrom..globalTo)
| where vMId =~ local_vMId
| take 1
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_vMId}`

---

### Start Operations

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Row`

```kusto
VMApiQosEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where vMId =~ queryVmId and operationName in ("VirtualMachines.Start.POST")
| extend RequestStartTime = datetime_add("Millisecond", durationInMilliseconds * -1, PreciseTimeStamp)
| distinct RequestStartTime, correlationId, operationId, fabricTenantName
| extend Value = strcat(RequestStartTime, " - ", correlationId)
| extend 
    StartTime = datetime_add("Minute", -1, RequestStartTime),
    EndTime = datetime_add("Minute", 15, RequestStartTime)
| order by RequestStartTime asc
| project Value, StartTime, EndTime, correlationId, operationId, fabricTenantName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---
