# Execution Graph

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **Execution Graph** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Execution Graph

### Lookup up EG

Cluster: `https://egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Single` · Widget: `Container`
Source panel: `Execution Graph > Execution Graph`

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
