# AzSM Service Healing Summary

> Source: **Aztec Service Healing Investigations Guide** dashboard, chapter **AzSM Service Healing Summary** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzSM Service Healing Trigger and Result details

_Widget purpose:_ AzSM Service Healing Summary

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Single` · Widget: `Card`
Source panel: `AzSM Service Healing Summary`

```kusto
let convert_to_mins = (milliSecondsVal:int) {round(todouble(milliSecondsVal / 60000.0), 2)};
let _serviceHealingTriggerId = toscalar(AzSMServiceHealingTriggerEvents
| where * has _sourceContainerIdToHeal
| where PreciseTimeStamp between (queryFrom .. queryTo)
| summarize arg_max(PreciseTimeStamp, *)
| union (
AzSMServiceHealingResultEvents
| where * has _sourceContainerIdToHeal
| where PreciseTimeStamp between (queryFrom .. queryTo)
)
| summarize arg_min(PreciseTimeStamp, *)
| distinct triggerId)
;
AzSMServiceHealingTriggerEvents
| where triggerId == _serviceHealingTriggerId
| extend migrationRequestDetails = parse_json(migrationRequestDetails)
| where PreciseTimeStamp between (queryFrom .. queryTo)
| join kind=inner (
AzSMServiceHealingResultEvents
| where triggerId == _serviceHealingTriggerId
| where PreciseTimeStamp between (queryFrom .. queryTo)
) on triggerId
| extend migrationRequestDetails = parse_json(migrationRequestDetails)
| project PreciseTimeStamp, Cluster, SoureceFabricName = fabricName, SourceRiName = roleInstanceNames, tenantName, TriggerRoleInstanceName = roleInstanceNames,
    AzSMSourceContainerId = sourceContainerId, FinalResult=result,DurationMin = convert_to_mins(totalDurationInMilliSeconds),
    isResumeOperation,
    JobId,
    TriggerMetaData = bag_pack(
        "triggerId", triggerId,
        "triggerType", triggerType,
        "sourceFabricName", fabricName,
        "faultCode", faultCode,
        "faultReason", faultReason,
        "isResumeopartion", isResumeOperation),
    migrationRequestDetails,
    ResultMetadata = bag_pack(
            'isContainerMigrationAttemptedOnContainerMismatch', isContainerMigrationAttemptedOnContainerMismatch,
            'isContainerMigrationCrossFc', isContainerMigrationCrossFc,
            'isContainerMigrationMiddleOfTenantUpgrade', isContainerMigrationMiddleOfTenantUpgrade,
            'isContainerMigrationUpdated', isContainerMigrationUpdated,
            'isMultipleRoleInstancesTenant', isMultipleRoleInstancesTenant)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_sourceContainerIdToHeal}`

---
