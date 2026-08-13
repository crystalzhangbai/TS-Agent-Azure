# CRP Event Logs

> Source: **Confidential Virtual Machines - Confidential Virtual Machine** dashboard, chapter **CRP Event Logs** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### CRP VM Event Logs

_Widget purpose:_ CRP Event Logs

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP Event Logs`

```kusto
ApiQosEvent_nonGet
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionId =~ querySubscriptionId and resourceGroupName =~ queryResourceGroup and resourceName =~ queryResourceName
| project 
    PreciseTimeStamp, 
    SubscriptionId = subscriptionId, 
    ResourceGroupName = resourceGroupName,
    ResourceName = resourceName,
    OperationName = operationName, 
    OperaptionId = operationId, 
    CorrelationId = correlationId, 
    HttpStatusCode = httpStatusCode,
    ResultCode = resultCode,
    ExceptionType = exceptionType,
    ErrorDetails = errorDetails
| sort by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryResourceGroup}`, `{queryResourceName}`

---

### VMSS VM ApiQosEvent

_Widget purpose:_ CRP Event Logs

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP Event Logs`

```kusto
VmssVMApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionId =~ SubscriptionId
| where operationName == "VirtualMachineScaleSets.ResourceOperation.PUT"
| where resourceGroupName =~ ResourceGroupName
| where resourceName =~ ResourceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{SubscriptionId}`, `{ResourceGroupName}`, `{ResourceName}`

**Signal filters seen in KQL:** `operationName == "VirtualMachineScaleSets.ResourceOperation.PUT"`

---
