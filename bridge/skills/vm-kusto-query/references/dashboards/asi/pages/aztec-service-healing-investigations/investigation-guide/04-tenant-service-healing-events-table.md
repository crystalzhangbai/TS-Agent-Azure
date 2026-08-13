# Tenant Service Healing Events Table

> Source: **Aztec Service Healing Investigations Guide** dashboard, chapter **Tenant Service Healing Events Table** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Tenant Events Service Healing Trigger Events

_Widget purpose:_ Tenant Service Healing Events Table

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant Service Healing Events Table`

```kusto
let tenantDetails = toscalar(cluster('mycroft.westcentralus.kusto.windows.net').database('Mycroft').MycroftContainerHealthSnapshot
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where ContainerId == queryContainerId
| extend p = bag_pack("TenantNameToCheck", TenantName, "FcCluster", ClusterName, "AzCluster", Cluster)
| summarize make_bag(p));
TMMgmtTenantEventsEtwTable
| where TenantName == tenantDetails["TenantNameToCheck"] 
| where PreciseTimeStamp between (queryFrom..queryTo) 
| extend MessageType = case(
    Message has "Pushing faulted container ", "PushMessage",
    Message has "Marking IsContainerMigrationPickedUpByAzSM to ", "MarkingPickedByAzSMSHMessage",
    Message has "Successfully pushed tenant migration request(s) ContainerId: ", "SuccessfullyPushedMessage",
    Message has " is already picked by AzSM for ServiceHealing", "PickedByAzSMShMessage",
    "Unknown")
| extend ContainerIdForSH = case (
    MessageType == "PushMessage", extract("Pushing faulted container ([\\w\\-]+) for Fc tenant: ", 1, Message),
    MessageType == "MarkingPickedByAzSMSHMessage", extract(
        "Marking IsContainerMigrationPickedUpByAzSM to true for containerId:([\\w\\-]+), ", 1, Message),
    MessageType == "SuccessfullyPushedMessage", extract(
        strcat("Successfully pushed tenant migration request\\(s\\) ContainerId: ([\\w\\-]+)"), 1, Message),
    MessageType == "PickedByAzSMShMessage", extract(
        strcat("container ([\\w\\-]+) is already picked by AzSM for ServiceHealing"), 1, Message),
    tostring(hash(Message)))
| where MessageType == "SuccessfullyPushedMessage"
| summarize arg_max(PreciseTimeStamp, *) by strcat(ContainerIdForSH, MessageType)
| project PreciseTimeStamp, Tenant, ContainerIdForSH, MessageType, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `MessageType == "SuccessfullyPushedMessage"`

---
