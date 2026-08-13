# Target Resource - VMSS

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **Target Resource - VMSS** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get VMSS from GatewayApiQoSEvent

_Widget purpose:_ Target Resource - VMSS

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `Target Resource - VMSS`

```kusto
GatewayApiQoSEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where operationId =~ queryOperationId
| where targetEndpoint contains "subscriptions" and targetEndpoint contains "Microsoft.Compute/virtualMachineScaleSets"
| extend targetUrl = substring(targetEndpoint, indexof(targetEndpoint, "/subscriptions"))
| extend targetARMResourceId = trim_end(@"(\?.*)", targetUrl)
| extend resourceGroupName = tolower(split(targetARMResourceId, "/")[4])
| extend resourceName = tolower(split(targetARMResourceId, "/")[8])
| project targetUrl, targetARMResourceId, subscriptionId = tolower(subscriptionId), resourceGroupName, resourceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

**Signal filters seen in KQL:** `targetEndpoint contains "subscriptions"`

---
