# Service Healing

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Service Healing** (3 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Not Triggered Reasons

### Container Service Healing Not Triggered Reasons

_Widget purpose:_ Not Triggered Reasons

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Service Healing > Not Triggered Reasons`

```kusto
ServiceHealingNotTriggeredReason(queryStart, queryNodeId, queryContainerId)
```

**Params:** `{queryNodeId}`, `{queryContainerId}`, `{queryStart}`

---

## Service Healing Result

### Service Healing Result Events

_Widget purpose:_ Service Healing Result

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > Service Healing Result`

```kusto
AzSMServiceHealingResultEvents
| where sourceContainerId == queryContainerId
| where PreciseTimeStamp between (queryFrom .. queryTo)
| extend p = bag_pack(
    'isContainerMigrationAttemptedOnContainerMismatch', isContainerMigrationAttemptedOnContainerMismatch,
    'isContainerMigrationCrossFc', isContainerMigrationCrossFc,
    'isContainerMigrationMiddleOfTenantUpgrade', isContainerMigrationMiddleOfTenantUpgrade,
    'isContainerMigrationUpdated', isContainerMigrationUpdated,
    'isMultipleRoleInstancesTenant', isMultipleRoleInstancesTenant)
| summarize arg_max(PreciseTimeStamp, *) by sourceContainerId
| project PreciseTimeStamp, Cluster, tenantName, result, totalDurationInMilliSeconds, sourceContainerId, targetContainerId, JobId, triggerId, ContainerMigrationMetadata = p
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

## Tenant Triggered Fault Reason

### Service Healing - TriggeredFaultReason

_Widget purpose:_ Tenant Triggered Fault Reason

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Service Healing > Tenant Triggered Fault Reason`

```kusto
ServiceHealingTriggeredFaultReason(queryFrom, queryTenantName)
| extend Message = FaultReason
```

**Params:** `{queryTenantName}`, `{queryFrom}`

---
