# NSG Updates

> Source: **NRP - Network Interfaces** dashboard, chapter **NSG Updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NSG Updates

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `NSG Updates`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where isnotempty(queryNSGName) and (SubscriptionId == querySubscriptionId and ResourceGroup =~ queryResourceGroupName and HttpMethod != "GET")
| where (ResourceType == "networkSecurityGroups" and ResourceName == queryNSGName) or (ResourceType == "securityRules")
| where ResourceType in ("networkSecurityGroups", "securityRules")
| extend StartTime = todatetime(StartTime)
| extend Content = case(
    ResourceType == "networkSecurityGroups", OperationName, 
    strcat(OperationName, " - ", ResourceName)
) 
| project-reorder ResourceGroup, ResourceName, HttpMethod, OperationName, ResourceType
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryNSGName}`, `{queryFrom}`, `{queryTo}`

---
