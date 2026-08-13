# QoS - By Operation

> Source: **CRP Home Investigation Guide** dashboard, chapter **QoS - By Operation** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### QoS By Operation

_Widget purpose:_ QoS - By Operation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `TimeSeries`
Source panel: `QoS - By Operation`

```kusto
let qOperations = dynamic([
    'AvailabilitySets.StartTenantUpdate.POST',
    'KvsData.Get.GET',
    'Subscriptions.Put.PUT',
    'VirtualMachines.Capture.POST',
    'VirtualMachines.Deallocate.POST',
    'VirtualMachines.GetVMs.GET',
    'VirtualMachines.instanceView.GET',
    'VirtualMachines.Restart.POST',
    'VirtualMachines.ResourceOperation.DELETE',
    'VirtualMachines.ResourceOperation.GET',
    'VirtualMachines.ResourceOperation.PUT',
    'VirtualMachines.Start.POST',
    'VirtualMachines.Stop.POST',
    'VirtualMachineScaleSets.Deallocate.POST',
    'VirtualMachineScaleSets.ResourceOperation.DELETE',
    'VirtualMachineScaleSets.ResourceOperation.PUT',
    'VMExtensions.VMExtensionOperation.PUT',
    'VMExtensions.VMExtensionOperation.DELETE',
    'VMScaleSetVMExtensions.VMScaleSetVMExtensionOperation.PUT'
]);
ApiQosEvent
| where PreciseTimeStamp between (qFrom .. qTo)
| where operationName in~ (qOperations)
| project PreciseTimeStamp, operationName, operationId, resultType, RPTenant, region
| summarize 
    Requests = dcount(operationId),
    UnexpectedFailures = dcountif(operationId, resultType == 2) 
    by Operation = operationName, bin(PreciseTimeStamp, 5m)
| extend QoS = (100 - round((toreal(UnexpectedFailures) / Requests) * 100, 4))
| project PreciseTimeStamp, Operation, QoS
| order by Operation asc, PreciseTimeStamp asc
```

**Params:** `{qFrom}`, `{qTo}`

---
