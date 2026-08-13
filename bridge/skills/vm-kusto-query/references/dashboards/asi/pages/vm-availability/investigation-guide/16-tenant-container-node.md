# Tenant / Container / Node

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Tenant / Container / Node** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Container Features

_Widget purpose:_ Tenant / Container / Node

Cluster: `azurecm.kusto.windows.net` · Database: `azurecm` · Type: `FeatureList` · Widget: `Card`
Source panel: `Tenant / Container / Node`

```kusto
let spotVM = (cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainer
| top 1 by PreciseTimeStamp desc
| project priority
| project features = pack("Spot VM", iif((priority == "200000"), "Enabled", "Disabled")));
union spotVM, (cluster('vmainsight.kusto.windows.net').database('Air').LmApplicableVms
| where SnapshotTime between (queryFrom .. queryTo)
| where ContainerId == queryContainer
| summarize arg_max(SnapshotTime, *) 
| project ContainerId, IsLmEligible, IsSwiftVm, IsLmDisabledTenantVm
| project features = pack(
    "Swift VM", iif(tobool(IsSwiftVm), "Enabled", "Disabled"),
    "LM Eligible", iif(tobool(IsLmEligible), "Enabled", "Disabled"), 
    "LM on Tenant", iif(tobool(IsLmDisabledTenantVm), "Disabled", "Enabled")))   
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), State = tostring(features[1])
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainer}`

---
