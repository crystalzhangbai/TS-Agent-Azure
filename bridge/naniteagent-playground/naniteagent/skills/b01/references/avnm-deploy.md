---
description: KQL queries for Azure Virtual Network Manager (AVNM/ANM) deployment troubleshooting — commit failures, goal state propagation, routing/connectivity/security admin deployments, AVNM managed resource group issues, work request processing.
---

# Azure Virtual Network Manager (AVNM) Deployment Kusto Queries

> Source: AVNM backend telemetry
> Cluster: aznwsdn.kusto.windows.net / Database: nsmplus
> Coverage: Commit lifecycle, goal state propagation, work request processing, error diagnosis

## Key Tables

| Table | Purpose |
|-------|---------|
| `AnmTraceLogs` | Detailed trace logs — commit processing, work requests, NRP calls, errors |
| `AnmGoalStates` | Goal state items pushed to VNets/Subnets per commit |
| `AnmApiQos` | API-level QoS — commit API calls, HTTP codes, latency |
| `AnmAnalyticsRegionalGoalStates` | Regional deployment status per commit (Succeeded/Failed/InProgress) |
| `AnmShoeboxLogs` | Customer-facing diagnostic logs |
| `AnmEvents` | High-level ANM events |

---

## Commit Identification

### Find Commit by Network Manager Name

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmApiQos
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where uri has "{networkManagerName}" and uri has "commit"
| project PreciseTimeStamp, operation, uri, httpCode, succeed, correlationId, timeTaken, message
| order by PreciseTimeStamp desc
| take 20
```

### Find Commit by CorrelationId from TraceLogs

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where message has "{networkManagerName}" and message has "commit"
| where message has "PersistCommitActionAsync" or message has "CommitPersisted"
| project PreciseTimeStamp, level, message, correlationId
| order by PreciseTimeStamp desc
| take 10
```

### Find Commit by Subscription ID

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmApiQos
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where uri has "{SubscriptionID}" and uri has "commit"
| project PreciseTimeStamp, operation, uri, httpCode, succeed, correlationId, timeTaken, message
| order by PreciseTimeStamp desc
| take 20
```

---

## Regional Deployment Status

### Check Commit Deployment Status per Region

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmAnalyticsRegionalGoalStates
| where TIMESTAMP > ago(1d)
| where NetworkManagerId == "{NM-GUID}"
| project TIMESTAMP, CommitName, CommitType, RdfeRegion, Status, CustomerStatus, FailedMessage, CustomerFacingFailedMessage
| order by TIMESTAMP desc
| take 10
```

### Check Deployment Status for a Specific Commit Type

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmAnalyticsRegionalGoalStates
| where TIMESTAMP > ago(7d)
| where NetworkManagerId == "{NM-GUID}"
| where CommitType == "{Routing|Connectivity|SecurityAdmin}"
| project TIMESTAMP, CommitName, CommitType, RdfeRegion, Status, CustomerStatus, FailedMessage, CustomerFacingFailedMessage, activeConfigs, netGroups
| order by TIMESTAMP desc
| take 20
```

---

## Error Diagnosis

### Get All Errors for a CorrelationId

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| where level in ("Error", "Warning")
| project PreciseTimeStamp, level, message
| order by PreciseTimeStamp asc
```

### Check for Azure Policy Block (RequestDisallowedByPolicy)

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| where message has "RequestDisallowedByPolicy" or message has "Unable to create ResourceGroup" or message has "PutResourceGroupAsync"
| project PreciseTimeStamp, level, message
| order by PreciseTimeStamp asc
```

### Check Work Request Final Status

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| where message has "WorkRequestCompleted" or message has "WorkRequestStarted"
| project PreciseTimeStamp, level, message
| order by PreciseTimeStamp asc
```

### Check for AVNM Managed Resource Group Creation Failures

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where message has "AVNM_Managed_ResourceGroup"
| where level in ("Error", "Warning") or message has "Failure" or message has "Forbidden"
| project PreciseTimeStamp, level, correlationId, message
| order by PreciseTimeStamp desc
| take 30
```

---

## Goal State Propagation

### Goal States Pushed to a Specific VNet

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmGoalStates
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where vnetId has "{vnetName}" or vnetGuid == "{vnetGuid}"
| project PreciseTimeStamp, region, vnetId, vnetGuid, version, correlationId, itemType, goalState
| order by PreciseTimeStamp desc
| take 30
```

### Goal States for a Specific CorrelationId (Single Commit)

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmGoalStates
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| project PreciseTimeStamp, region, vnetId, vnetGuid, version, itemType, goalState
| order by PreciseTimeStamp desc
| take 50
```

### Check for Empty Goal States (VNet/Subnet Not Receiving Config)

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmGoalStates
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| where goalState == "[]" or array_length(goalState) == 0
| project PreciseTimeStamp, region, vnetId, itemType, goalState
| order by PreciseTimeStamp desc
```

### Compare Goal States Across VNets in Same Commit

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmGoalStates
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| summarize itemTypes=make_set(itemType), hasEmptyGS=countif(array_length(goalState) == 0), hasNonEmptyGS=countif(array_length(goalState) > 0) by vnetId
| order by hasEmptyGS desc
```

---

## Full Trace Timeline

### Complete Commit Lifecycle Trace

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| project PreciseTimeStamp, level, codePath, message
| order by PreciseTimeStamp asc
| take 200
```

### Key Sequence Events Only

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmTraceLogs
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId == "{correlationId}"
| where message has "SequenceEvent" or message has "PersistCommitActionAsync" or message has "Validation" or message has "WorkRequest" or message has "PutResourceGroupAsync" or message has "ConvertAndUploadResources"
| project PreciseTimeStamp, level, message
| order by PreciseTimeStamp asc
```

---

## Customer-Facing Diagnostic Logs

### ShoeboxLogs for a Network Manager

```kql
cluster('aznwsdn.kusto.windows.net').database('nsmplus').AnmShoeboxLogs
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where resourceId has "{networkManagerName}"
| project PreciseTimeStamp, operationName, category, resultType, correlationId, level, properties
| order by PreciseTimeStamp desc
| take 30
```

---

## NRP Operations for AVNM Managed Resources

### Route Table CRUD in AVNM Managed Resource Group

```kql
cluster('Nrp').database('mdsnrp').FrontendOperationEtwEvent
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where ResourceGroup has "AVNM_Managed_ResourceGroup"
| project PreciseTimeStamp, ResourceType, ResourceGroup, ResourceName, OperationName, Message
| order by PreciseTimeStamp desc
| take 30
```

### ARM Activity for AVNM Commit Operations

```kql
union cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests, cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests, cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId == "{SubscriptionID}"
| where targetUri has "networkManagers" and targetUri has "commit"
| extend URI = split(targetUri, "?")
| extend ResourceUri = tostring(split(URI[0], "443")[1])
| project PreciseTimeStamp, operationName, httpMethod, httpStatusCode, correlationId, ResourceUri, clientApplicationId
| order by PreciseTimeStamp desc
| take 20
```

---

## Common Error Patterns Reference

| Error Pattern | Key Search String | Root Cause | Resolution |
|---------------|-------------------|------------|------------|
| Azure Policy blocks managed RG | `RequestDisallowedByPolicy` + `AVNM_Managed_ResourceGroup` | Policy enforces tags/naming on RGs; AVNM creates RG without tags | Create Policy Exemption for `AVNM_Managed_ResourceGroup_*` or update policy exclusion |
| Managed RG creation failure | `CreateResourceGroupFailure` | Wrapper for policy/permission error on managed RG | Same as above — check full error for specific policy ID |
| Authorization failure | `AuthorizationFailed` or `httpCode == 403` | AVNM service principal lacks permissions in target subscription | Verify NM scope includes target subscription; check RBAC |
| Concurrent operation conflict | `AnotherOperationInProgress` or `Conflict` | Another deployment modifying same VNet/Subnet | Wait and re-commit; check for concurrent Terraform/ARM operations |
| Work request timeout | `OperationTimedOut` | Large scope or NRP throttling | Re-commit; consider splitting scope |
| Goal state empty array | `goalState == "[]"` | VNet/Subnet not in network group scope | Verify network group membership; check group conditions |

## Key Sequence Events Reference

| Sequence Event in `message` | Meaning |
|------------------------------|---------|
| `PolicyManagerCallRecieved` | Commit request received by ANM |
| `PersistCommitActionAsync: Validation Passed` | Commit validation OK |
| `CommitPersisted` | Commit stored in CosmosDB |
| `CommitTriggerWorkRequestCreated` | Work request queued for processing |
| `WorkRequestStarted` | Work request processing begins |
| `[Snapshot] Created routing in-memory snapshots` | Config snapshots created for deployment |
| `TryUpdateRegionGoalStateWithCommit` | Goal state map being updated |
| `ConvertAndUploadResources` | Converting config to NRP resources |
| `PutResourceGroupAsync` | Creating managed resource group (routing only) |
| `WorkRequestCompleted` | Final status — check `Status` field (Succeeded/Failed) |
