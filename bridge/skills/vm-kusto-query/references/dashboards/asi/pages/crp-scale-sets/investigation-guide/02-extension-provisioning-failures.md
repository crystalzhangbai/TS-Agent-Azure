# Extension Provisioning Failures

> Source: **CRP — Scale Sets** dashboard, chapter **Extension Provisioning Failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ScaleSet Extension Failures

_Widget purpose:_ Extension Provisioning Failures

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Extension Provisioning Failures`

```kusto
cluster("azcrp").database("crp_allprod").VmssVMGoalSeekingActivity
| where PreciseTimeStamp between (qFrom  .. qTo) and subscriptionId == qSub
| where vMName startswith qVMSS
| where callerName == 'PollForVMExtensionsProvisioningResult' and message has_all ('Extension', "reached a terminal status 'Failed'")
| project PreciseTimeStamp, vMName, callerName, activityId, message
| summarize arg_max(PreciseTimeStamp, callerName, message), CRPOperations = make_set(activityId) by vMName
| extend OperationCount = array_length(CRPOperations)
| order by PreciseTimeStamp desc
```

**Params:** `{qFrom}`, `{qTo}`, `{qSub}`, `{qVMSS}`

**Signal filters seen in KQL:** `callerName == "PollForVMExtensionsProvisioningResult"`

---
