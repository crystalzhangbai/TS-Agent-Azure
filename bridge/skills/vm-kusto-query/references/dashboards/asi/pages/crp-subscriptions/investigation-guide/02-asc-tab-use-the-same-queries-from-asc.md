# ASC Tab - Use the same queries from ASC

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **ASC Tab - Use the same queries from ASC** (7 queries across 7 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Current Maintenance-Control Status by Subscription

### Current Maintenance-Control Status by Subscription

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Current Maintenance-Control Status by Subscription`

```kusto
GetCurrentMaintenanceStatusBySubscription_Batching(querySub)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`

---

## Maintenance-Control Status History by Subscription

### Maintenance-Control Status History by Subscription

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Maintenance-Control Status History by Subscription`

```kusto
GetMaintenanceHistoryBySubscription_Batching(querySub, queryFrom, queryTo)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`

---

## Planned Maintenance History by Subscription

### Planned Maintenance History by Subscription

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Planned Maintenance History by Subscription`

```kusto
GetMaintenanceHistoryBySubscription_PlannedMaintenance(querySub, queryFrom, queryTo)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`

---

## Planned Maintenance Notifications/Emails

### GetCommunicationsForSupport

_Widget purpose:_ Planned Maintenance Notifications/Emails

Cluster: `icmcluster` · Database: `ACM.Publisher` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Planned Maintenance Notifications/Emails`

```kusto
GetCommunicationsForSupport(Cloud=queryCloud, Subid=querySub, queryFrom, queryTo)
| extend JSON = parse_json(list_json) | project-away list_json
| mv-expand JSON
| where JSON.Type contains "Maintenance"
| project Status = tostring(JSON.Status), Type = tostring(JSON.Type), TrackingId = tostring(JSON.TrackingId),ICMNumber = tostring(JSON.LSIID), 
MaintenanceStartDate = todatetime(JSON.StartTime), MaintenanceEndDate = todatetime(JSON.EndTime), NotificationCreationDate = todatetime(JSON.CreateDate), 
NotificationContent = tostring(JSON.CurrentDescription)
| where NotificationContent !contains "Azure SQL"
| order by MaintenanceStartDate desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`, `{queryCloud}`

**Signal filters seen in KQL:** `JSON.Type contains "Maintenance"`

---

## Planned Maintenance Phase Details

### Query Planned Maintenance Phase Details by Subscription

_Widget purpose:_ Planned Maintenance Phase Details

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Planned Maintenance Phase Details`

```kusto
GetVMMaintenanceStatus(querySubId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

## Planned Maintenance Status Summary

### Query Planned Maintenance Status Summary by Subscription

_Widget purpose:_ Planned Maintenance Status Summary

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Planned Maintenance Status Summary`

```kusto
GetCurrentMaintenanceStatusBySubscription_PlannedMaintenance(querySubId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

## Test

### Get Service Healing due to Planned Maintenance by Sub

_Widget purpose:_ Test

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `ASC Tab - Use the same queries from ASC > Test`

```kusto
let vmResources = LogContainerSnapshot
| where subscriptionId == querySub
| distinct cluster = Tenant, tenantName, roleInstanceName, containerId, creationTime;
let serviceHealingTriggers = union (ServiceHealingTriggerEtwTable 
   | project PreciseTimeStamp, triggerType = TriggerType, triggerObjectId =  TriggerObjectId, triggerId = TriggerId, tenantName = TenantName, FaultCode, faultReason = FaultReason, roleInstanceName = RoleInstanceName),
   (cluster("accp.centralus.kusto.windows.net").database("AZSM").AzSMServiceHealingTriggerEvents
   | project PreciseTimeStamp, triggerType, triggerObjectId, triggerId, tenantName, faultCode, faultReason, roleInstanceName = roleInstanceNames);
vmResources | join kind=inner serviceHealingTriggers on tenantName
| where triggerType in ("MaintenanceInitiatedMigration", "ClusterEvacuation", "TargetMachinePoolMismatch") // "CustomerInitiatedMigration" <-- Redeploy
| where roleInstanceName1 has roleInstanceName
| where containerId == iif(triggerObjectId == "00000000-0000-0000-0000-000000000000", triggerObjectId, containerId)
| extend containerCreationTime =  todatetime(creationTime)
| summarize arg_min(containerCreationTime, *) by triggerObjectId
| extend  faultCode = max_of(tolong(faultCode), FaultCode)
| project roleInstanceName, containerId, tenantName, cluster, serviceHealingTimeStamp = PreciseTimeStamp, triggerType, triggerId, faultCode, faultReason
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`

---
