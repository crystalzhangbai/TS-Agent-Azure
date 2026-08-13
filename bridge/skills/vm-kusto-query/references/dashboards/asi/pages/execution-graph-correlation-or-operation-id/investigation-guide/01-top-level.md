# (top-level)

> Source: **Correlation or Operation Id** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Correlation or Operation Id"

Cluster: `https://egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `ResourceGet` · Widget: `Container`

```kusto
let vmOps = IaasVmOperations 
| where EgId =~ local_EgId
| summarize arg_max(PreciseTimeStamp, *) by EgId
| extend Source = "CRP";
let traceOps = TraceOperations() 
| where EgId =~ local_EgId
| summarize arg_max(PreciseTimeStamp, *) by EgId
| extend Source = "Traces";
union vmOps, traceOps
| take 1
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_PreciseTimeStamp}`, `{local_SubscriptionId}`, `{local_ResourceGroupName}`, `{local_Region}`, `{local_Result}`, `{local_FailureSignature}`, `{local_Source}`, `{local_EgId}`

---

### Lookup up EG

Cluster: `https://egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Single` · Widget: `Container`

```kusto
let crp = IaasVmOperations 
| where EgId == queryCorrelationOrOperationId
| extend SourceTable = "CRP"
| take 1;
let arm = UserOperations 
| where EgId =~ queryCorrelationOrOperationId
| extend SourceTable = "ARM"
| take 1;
union arm, crp
| take 1
```

**Params:** `{queryCorrelationOrOperationId}`

---
