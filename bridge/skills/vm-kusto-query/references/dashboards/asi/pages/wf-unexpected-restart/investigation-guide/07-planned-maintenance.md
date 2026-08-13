# Planned Maintenance

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Planned Maintenance** (13 queries across 11 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Control Events for VM

### Control Events for VM DS

_Widget purpose:_ GetCurrentMaintenanceStatus

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `Planned Maintenance > Control Events for VM > GetCurrentMaintenanceStatus`

```kusto
GetCurrentMaintenanceStatus_Batching(query_SubscriptionId,query_VMName, query_TenantName)
```

**Params:** `{query_SubscriptionId}`, `{query_VMName}`, `{query_TenantName}`

---

## Control History for VM

### Control History for VM DS

_Widget purpose:_ GetMaintenanceHistory

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `Planned Maintenance > Control History for VM > GetMaintenanceHistory`

```kusto
GetMaintenanceHistory_Batching(query_SubscriptionId, query_VMName, query_TenantName, query_BeginTime, query_EndTime)
```

**Params:** `{query_SubscriptionId}`, `{query_VMName}`, `{query_TenantName}`, `{query_BeginTime}`, `{query_EndTime}`

---

## Customer Notification1

### CustomerNotification1 DS

_Widget purpose:_ Customer Notification1

Cluster: `icmcluster` · Database: `ACM.Publisher` · Type: `Table`
Source panel: `Planned Maintenance > Customer Notification1 > Customer Notification1`

```kusto
let ParamSubscriptionId =  query_SubscriptionId;  
GetCommunicationsForSupport(Cloud="Public", Subid=ParamSubscriptionId, StartTime=ago(60d), EndTime=now()) 
| extend JSON = parse_json(list_json) | project-away list_json 
| mv-expand JSON 
| where JSON.Type contains "Maintenance" 
| project Status = tostring(JSON.Status), Type = tostring(JSON.Type), TrackingId = tostring(JSON.TrackingId),ICMNumber = tostring(JSON.LSIID),  
MaintenanceStartDate = todatetime(JSON.StartTime), MaintenanceEndDate = todatetime(JSON.EndTime), NotificationCreationDate = todatetime(JSON.CreateDate),  
NotificationContent = tostring(JSON.CurrentDescription) 
| where NotificationContent !contains "Azure SQL" 
| order by MaintenanceStartDate desc
```

**Params:** `{query_SubscriptionId}`

**Signal filters seen in KQL:** `JSON.Type contains "Maintenance"`

---

## Customer Notification2

### CustomerNotification2 DS

_Widget purpose:_ Customer Notification2

Cluster: `Icmcluster` · Database: `ACM.Publisher` · Type: `Table`
Source panel: `Planned Maintenance > Customer Notification2 > Customer Notification2`

```kusto
AlbnTargets 
| where Subscriptions contains query_SubscriptionId
| project CommunicationId 
| join cluster('Icmcluster').database("ACM.Backend").PublishRequest on CommunicationId 
| where CommunicationDateTime >= query_BeginTime 
| order by CommunicationDateTime desc 
| project CommunicationDateTime, CommunicationType, Title, IncidentId, RichTextMessage, CommunicationId
```

**Params:** `{query_BeginTime}`, `{query_SubscriptionId}`

---

## Events for VM

### Events for VM DS

_Widget purpose:_ GetCurrentMaintenanceStatus

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `Planned Maintenance > Events for VM > GetCurrentMaintenanceStatus`

```kusto
GetCurrentMaintenanceStatus_PlannedMaintenance(query_SubscriptionId ,query_VMName,query_TenantName)
```

**Params:** `{query_SubscriptionId}`, `{query_VMName}`, `{query_TenantName}`

---

## History for VM

### History for VM DS

_Widget purpose:_ GetMaintenanceHistory

Cluster: `Azdeployer` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `Planned Maintenance > History for VM > GetMaintenanceHistory`

```kusto
GetMaintenanceHistory_PlannedMaintenance(query_SubscriptionId, query_VMName, query_TenantName,  query_BeginTime, query_EndTime)
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_SubscriptionId}`, `{query_VMName}`, `{query_TenantName}`

---

## MaintenancePhaseDetails

### PendingMaintenanceOperationDetails DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Planned Maintenance > MaintenancePhaseDetails`

```kusto
PendingMaintenanceOperationDetails
| where PreciseTimeStamp > ago(30d)
| where subscriptionId =~ query_SubscriptionId and tenantName == query_TenantName
| project PreciseTimeStamp, Tenant, scheduledMaintenanceId, subscriptionId, tenantName, SourceNodeId
```

**Params:** `{query_SubscriptionId}`, `{query_TenantName}`

---

### MaintenancePhaseDetails DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Planned Maintenance > MaintenancePhaseDetails`

```kusto
MaintenancePhaseDetails
| where scheduledMaintenanceId == query_ScheduledMaintenanceId and SourceNodeId == query_SourceNodeId
| distinct scheduledMaintenanceId, SourceNodeId, maintenanceOperationType, startTimeUTC, endTimeUTC, phaseId
```

**Params:** `{query_ScheduledMaintenanceId}`, `{query_SourceNodeId}`

---

## PendingMaintenanceOperationDetails

### PendingMaintenanceOperationDetails DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Planned Maintenance > PendingMaintenanceOperationDetails`

```kusto
PendingMaintenanceOperationDetails
| where PreciseTimeStamp > ago(30d)
| where subscriptionId =~ query_SubscriptionId and tenantName == query_TenantName
| project PreciseTimeStamp, Tenant, scheduledMaintenanceId, subscriptionId, tenantName, SourceNodeId
```

**Params:** `{query_SubscriptionId}`, `{query_TenantName}`

---

## ScheduledEventsEnablementStatus

### ScheduledEventsEnablementStatus DS

_Widget purpose:_ ScheduledEventsEnablementStatus

Cluster: `Azpe` · Database: `azpe` · Type: `Table`
Source panel: `Planned Maintenance > ScheduledEventsEnablementStatus > ScheduledEventsEnablementStatus`

```kusto
GetScheduledEventsEnablementStatusV3(query_TenantName, Timestamp=query_BeginTime)
```

**Params:** `{query_BeginTime}`, `{query_TenantName}`

---

## ScheduledMaintenanceInformational

### PendingMaintenanceOperationDetails DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Planned Maintenance > ScheduledMaintenanceInformational`

```kusto
PendingMaintenanceOperationDetails
| where PreciseTimeStamp > ago(30d)
| where subscriptionId =~ query_SubscriptionId and tenantName == query_TenantName
| project PreciseTimeStamp, Tenant, scheduledMaintenanceId, subscriptionId, tenantName, SourceNodeId
```

**Params:** `{query_SubscriptionId}`, `{query_TenantName}`

---

### ScheduledMaintenanceInformational DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Planned Maintenance > ScheduledMaintenanceInformational`

```kusto
ScheduledMaintenanceInformational
| where SourceNodeId == query_SourceNodeId and message contains query_TenantName and TIMESTAMP >= query_BeginTime
```

**Params:** `{query_BeginTime}`, `{query_SourceNodeId}`, `{query_TenantName}`

---

## TMMgmtTenantEventsEtwTable

### TenanteEventsFilteredPM DS

_Widget purpose:_ TMMgmtTenantEventsEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Planned Maintenance > TMMgmtTenantEventsEtwTable > TMMgmtTenantEventsEtwTable`

```kusto
TMMgmtTenantEventsEtwTable 
| where TenantName == query_TenantName  
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime 
| where Message contains "ServiceHealingTriggerType: TargetMachinePoolMismatch"  // usually "Hardware decommission", TSG: VM Service Healed for Planned Maint After No Action Taken_Restarts - Overview (visualstudio.com) or Hardware Decommissioning RCA_Planned Maint - Overview (visualstudio.com) 
| project PreciseTimeStamp, TenantName, Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_TenantName}`

**Signal filters seen in KQL:** `Message contains "ServiceHealingTriggerType: TargetMachinePoolMismatch"`

---
