# VmssVMApiQosEvent

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **VmssVMApiQosEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VmssVMApiQosEvent

### OperationId VmssVMApiQosEvent GET

_Widget purpose:_ VmssVMApiQosEvent - operationId {{operationId}}

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `VmssVMApiQosEvent > VmssVMApiQosEvent > VmssVMApiQosEvent - operationId {{operationId}}`

```kusto
let adjustedStart = datetime_add('hour', -6, local_startDate);
let adjustedEnd = datetime_add('hour', 6, local_endDate);
VmssVMApiQosEvent
| where PreciseTimeStamp between (adjustedStart .. adjustedEnd)
| where operationId =~ local_operationId
| project 
    availabilitySet,
    extensionStates,
    fabricCluster,
    fabricTenantName,
    oSIsoGeneratingComponent,
    oSProvisionDurationInSeconds,
    reliableProvisioningState,
    resourceName,
    vMScaleSetName
```

**Params:** `{local_operationId}`, `{local_endDate}`, `{local_startDate}`

---
