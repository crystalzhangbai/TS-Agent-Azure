# ApiQosEvent

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **ApiQosEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ApiQosEvent

### ExecutionGraph

_Widget purpose:_ ApiQosEvent - operationId {{operationId}}

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Single` · Widget: `Card`
Source panel: `ApiQosEvent > ApiQosEvent > ApiQosEvent - operationId {{operationId}}`

```kusto
union withsource=SourceTable  IaasVmOperations, UserOperations
| where EgId == queryOperationId
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---
