# CRP VMSS VM Event Logs

> Source: **Confidential Virtual Machines - Confidential Virtual Machine** dashboard, chapter **CRP VMSS VM Event Logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### VMSS VM ApiQosEvent

_Widget purpose:_ CRP VMSS VM Event Logs

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP VMSS VM Event Logs`

```kusto
VmssVMApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionId =~ querySubscriptionId
| where operationName == "VirtualMachineScaleSets.ResourceOperation.PUT"
| where resourceGroupName =~ queryResourceGroupName
| where resourceName =~ queryResourceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryResourceName}`

**Signal filters seen in KQL:** `operationName == "VirtualMachineScaleSets.ResourceOperation.PUT"`

---
