# AzSM Service Healing Step Result Events table

> Source: **Aztec Service Healing Investigations Guide** dashboard, chapter **AzSM Service Healing Step Result Events table** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzSM Service Healing Summary Query

_Widget purpose:_ AzSM Service Healing Step Result Events table

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `AzSM Service Healing Step Result Events table`

```kusto
let convert_to_mins = (milliSecondsVal:int) {round(todouble(milliSecondsVal / 60000.0), 2)};
let _serviceHealingTriggerId = toscalar(AzSMServiceHealingTriggerEvents
| where * has _sourceContainerIdToHeal
| extend RowType = "TriggerEvent"
| extend migrationRequestDetails = parse_json(migrationRequestDetails)
| where PreciseTimeStamp between (queryFrom .. queryTo)
| summarize arg_max(PreciseTimeStamp, *)
| union (
AzSMServiceHealingResultEvents
| where * has _sourceContainerIdToHeal
| extend RowType = "TriggerEvent"
| where PreciseTimeStamp between (queryFrom .. queryTo)
)
| summarize arg_min(PreciseTimeStamp, *)
| distinct triggerId);
AzSMServiceHealingTriggerEvents
| where triggerId == _serviceHealingTriggerId
| extend RowType = "TriggerEvent"
| extend migrationRequestDetails = parse_json(migrationRequestDetails)
| where PreciseTimeStamp between (queryFrom .. queryTo)
| union
(AzSMServiceHealingResultEvents
| where triggerId == _serviceHealingTriggerId
| where PreciseTimeStamp between (queryFrom .. queryTo)
| extend RowType = "FinalEvent"
)
| union
(AzSMServiceHealingStepResultEvents
| where triggerId == _serviceHealingTriggerId
| where PreciseTimeStamp between (queryFrom .. queryTo)
| extend RowType = "StepResultEvent"
| parse stateMachineId with 'AzSM.StateMachines.TenantContainersMigration.ContainersMigrationStateMachine:' StepResultTenantName ':' StepResultSourceContainerId
)
| take 1000
| order by PreciseTimeStamp asc
| extend SourceCid = strcat(triggerObjectId, StepResultSourceContainerId, sourceContainerId),
    TargetCid = iif(isempty( targetContainerId), '00000000-0000-0000-0000-000000000000', targetContainerId),
    StepContext = case(
        isempty( stepContext) and isnotempty( migrationRequestDetails), migrationRequestDetails,
        stepContext),
    StepType = case(
        RowType == "TriggerEvent", "TriggerEvent",
        RowType == "FinalEvent", "FinalResultEvent",
        containerMigrationStepType),
    roleInstanceNames = case (
    isempty(roleInstanceNames), prev(roleInstanceNames),
    roleInstanceNames),
   SteptMetadata =  case (
        RowType == "FinalEvent", bag_pack(
            'isContainerMigrationAttemptedOnContainerMismatch', isContainerMigrationAttemptedOnContainerMismatch,
            'isContainerMigrationCrossFc', isContainerMigrationCrossFc,
            'isContainerMigrationMiddleOfTenantUpgrade', isContainerMigrationMiddleOfTenantUpgrade,
            'isContainerMigrationUpdated', isContainerMigrationUpdated,
            'isMultipleRoleInstancesTenant', isMultipleRoleInstancesTenant),
        RowType == "TriggerEvent", bag_pack(
        "triggerType", triggerType,
        "sourceFabricName", fabricName,
        "faultCode", faultCode,
        "faultReason", faultReason,
        "isResumeopartion", isResumeOperation),
        dynamic({}))
| project PreciseTimeStamp, Cluster, StepType, result, tenantName, TriggerRoleInstanceName = roleInstanceNames,
    SourceCid, TargetCid, JobId, DurationMin = convert_to_mins(totalDurationInMilliSeconds), SteptMetadata, StepContext, triggerId//, RowType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_sourceContainerIdToHeal}`

---
