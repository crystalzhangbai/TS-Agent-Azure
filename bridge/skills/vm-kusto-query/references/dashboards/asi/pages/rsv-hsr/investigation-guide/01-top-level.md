# (top-level)

> Source: **Recovery Services Vaults - HSR** dashboard, chapter **(top-level)** (16 queries).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## (no subgroup)

### Retrieve Resource "HSR"

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `ResourceGet` · Widget: `Container`

```kusto
WBEBackupStatsAll
| where LogicalContainerId == local_LogicalContainerId
| where SubscriptionId == local_SubscriptionId
|top 1 by TimeStamp desc
| project SubscriptionId,LogicalContainerId
```

**Params:** `{local_HSRNameGivenInPreRegScript}`, `{local_LogicalContainerId}`, `{local_SubscriptionId}`

---

### Backup Success Without user error

_Widget purpose:_ Backup Stats

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `DataSummary`

```kusto
let st = queryFrom;
let end = queryTo;
let prevstart = queryFrom-(end-st);
WBEBackupStatsAll
| where TIMESTAMP between (st .. end)
| where DatasourceType contains "SAPHana"
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
| where ErrorCode !contains "usererror"
| summarize CountNow = dcount(TaskId)  by ErrorCode
| as CT
| extend PercentageNow = round(100.0 * CountNow / toscalar(CT | summarize sum(CountNow)), 3)
| project ErrorCode,CountNow,PercentageNow
| join kind=leftouter 
(
 WBEBackupStatsAll
 | where TIMESTAMP between (prevstart .. st ) 
 | where DatasourceType contains "SAPHana"
 | where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
 | extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
 | where ErrorCode !contains "usererror"
 | summarize CountPrev = dcount(TaskId)  by ErrorCode
 | as PT
 | extend PercentagePrev = round(100.0 * CountPrev / toscalar(PT | summarize sum(CountPrev)), 3)
 ) on ErrorCode
 | extend PercentageChange = todouble(PercentageNow-PercentagePrev)
 | project ErrorCode,CountPrev,CountNow,PercentagePrev,PercentageNow,PercentageChange
 | where ErrorCode == "Success"
| sort by CountNow desc
| extend Value = tostring(PercentageNow) 
| extend Health = case(PercentageNow > 99 , "Healthy" , case(PercentageNow < 90, "Unhealthy" ,"Degraded" ))
| extend ValueContext = tostring(PercentageChange)
| extend Trend = case(PercentageChange > 0 , "Up", case( PercentageChange == 0 , "Neutral", "Down"))
| extend Description = "Backup stats without user error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `DatasourceType contains "SAPHana"` · `ErrorCode == "Success"`

---

### Restore stats

_Widget purpose:_ Restore Stats

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `DataSummary`

```kusto
let st = queryFrom;
let end = queryTo;
let prevstart = queryFrom-(end-st);
let dsIds = 
WBEBackupStatsAll
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where TIMESTAMP >  ago(90d)
| distinct DatasourceId;
WBERecoveryStatsAll
| where TIMESTAMP between (st .. end)
| where DatasourceType contains "SAPHana"
| where SubscriptionId == local_subscriptionId
| where DatasourceId  in (dsIds)
| extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
| where ErrorCode !contains "usererror"
| summarize CountNow = dcount(TaskId)  by ErrorCode
| as CT
| extend PercentageNow = round(100.0 * CountNow / toscalar(CT | summarize sum(CountNow)), 3)
| project ErrorCode,CountNow,PercentageNow
| join kind=leftouter 
(
 WBERecoveryStatsAll
 | where TIMESTAMP between (prevstart .. st ) 
 | where DatasourceType contains "SAPHana"
 | where SubscriptionId == local_subscriptionId
| where DatasourceId  in (dsIds)
 | extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
 | where ErrorCode !contains "usererror"
 | summarize CountPrev = dcount(TaskId)  by ErrorCode
 | as PT
 | extend PercentagePrev = round(100.0 * CountPrev / toscalar(PT | summarize sum(CountPrev)), 3)
 ) on ErrorCode
 | extend PercentageChange = todouble(PercentageNow-PercentagePrev)
 | project ErrorCode,CountPrev,CountNow,PercentagePrev,PercentageNow,PercentageChange
 | where ErrorCode == "Success"
| sort by CountNow desc
| extend Value = tostring(PercentageNow) 
| extend Health = case(PercentageNow > 99 , "Healthy" , case(PercentageNow < 90, "Unhealthy" ,"Degraded" ))
| extend ValueContext = tostring(PercentageChange)
| extend Trend = case(PercentageChange > 0 , "Up", case( PercentageChange == 0 , "Neutral", "Down"))
| extend Description = "Restore stats without user error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `DatasourceType contains "SAPHana"` · `ErrorCode == "Success"`

---

### Protection Stats

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `DataSummary`

```kusto
let st = queryFrom;
let end = queryTo;
let prevstart = queryFrom-(end-st);
let cNames = 
WBEBackupStatsAll
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where TIMESTAMP between (st .. end)
| distinct ContainerName;
WBEProtectionStatsAll
| where TIMESTAMP between (st .. end)
| where DatasourceType contains "SAPHana"
| where SubscriptionId == local_subscriptionId
| where ContainerName in (cNames)
| extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
| where ErrorCode !contains "usererror"
| summarize CountNow = dcount(TaskId)  by ErrorCode
| as CT
| extend PercentageNow = round(100.0 * CountNow / toscalar(CT | summarize sum(CountNow)), 3)
| project ErrorCode,CountNow,PercentageNow
| join kind=leftouter 
(
 WBEProtectionStatsAll
 | where TIMESTAMP between (prevstart .. st ) 
 | where DatasourceType contains "SAPHana"
 | where SubscriptionId == local_subscriptionId
| where ContainerName in (cNames)
 | extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
 | where ErrorCode !contains "usererror"
 | summarize CountPrev = dcount(TaskId)  by ErrorCode
 | as PT
 | extend PercentagePrev = round(100.0 * CountPrev / toscalar(PT | summarize sum(CountPrev)), 3)
 ) on ErrorCode
 | extend PercentageChange = todouble(PercentageNow-PercentagePrev)
 | project ErrorCode,CountPrev,CountNow,PercentagePrev,PercentageNow,PercentageChange
 | where ErrorCode == "Success"
| sort by CountNow desc
| extend Value = tostring(PercentageNow) 
| extend Health = case(PercentageNow > 99 , "Healthy" , case(PercentageNow < 90, "Unhealthy" ,"Degraded" ))
| extend ValueContext = tostring(PercentageChange)
| extend Trend = case(PercentageChange > 0 , "Up", case( PercentageChange == 0 , "Neutral", "Down"))
| extend Description = "Protection stats without user error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `DatasourceType contains "SAPHana"` · `ErrorCode == "Success"`

---

### Registration Stats

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `DataSummary`

```kusto
let st = queryFrom;
let end = queryTo;
let prevstart = queryFrom-(end-st);
let cNames = 
WBEBackupStatsAll
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where TIMESTAMP between (st .. end)
| distinct ContainerName;
FabricSvcRegistrationStatsAll
| where TIMESTAMP between (st .. end)
| where SubscriptionId == local_subscriptionId
| where ContainerName in (cNames)
| extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
| where ErrorCode !contains "usererror"
| summarize CountNow = dcount(TaskId)  by ErrorCode
| as CT
| extend PercentageNow = round(100.0 * CountNow / toscalar(CT | summarize sum(CountNow)), 3)
| project ErrorCode,CountNow,PercentageNow
| join kind=leftouter 
(
FabricSvcRegistrationStatsAll
 | where TIMESTAMP between (prevstart .. st ) 
 | where SubscriptionId == local_subscriptionId
| where ContainerName in (cNames)
 | extend ErrorCode = iff(ErrorCode contains "usererror", ErrorCode = "UserError", ErrorCode = ErrorCode)
 | where ErrorCode !contains "usererror"
 | summarize CountPrev = dcount(TaskId)  by ErrorCode
 | as PT
 | extend PercentagePrev = round(100.0 * CountPrev / toscalar(PT | summarize sum(CountPrev)), 3)
 ) on ErrorCode
 | extend PercentageChange = todouble(PercentageNow-PercentagePrev)
 | project ErrorCode,CountPrev,CountNow,PercentagePrev,PercentageNow,PercentageChange
 | where ErrorCode == "Success"
| sort by CountNow desc
| extend Value = tostring(PercentageNow) 
| extend Health = case(PercentageNow > 99 , "Healthy" , case(PercentageNow < 90, "Unhealthy" ,"Degraded" ))
| extend ValueContext = tostring(PercentageChange)
| extend Trend = case(PercentageChange > 0 or isempty( PercentageChange), "Up", case( PercentageChange == 0  , "Neutral", "Down"))
| extend Description = "Registration stats without user error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `ErrorCode == "Success"`

---

### hdbnsutil tool mode value

_Widget purpose:_ Active Node Tracking as per HDBnsutil tool

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Timeline`

```kusto
let taskids=
WBEBackupStatsAll
| where TIMESTAMP between (queryFrom..queryTo)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| distinct TaskId;
WBETraceLogAll
| where TaskId in (taskids)
| where Message == "[HANAPlugin PrBk]: hdbnsutilparsed value is "
| parse Properties with "{hsrTopology = " currentTopology "}"
| extend d = parse_json(currentTopology)
| extend mode = d.mode
| extend topology = d.currentTopology
| extend isSystemOnline = d.isSystemOnline
| extend isSystemOnline = case(isSystemOnline  == 0, "true",case(isSystemOnline == 1, "false", "unknown"))
| extend Health = case(mode contains "primary" , "Healthy", case( mode contains "sync" , "Degraded","Unhealthy" ) )
| extend EventName = "mode"
| parse ContainerName with "Compute;" * ";" Content
| extend GroupBy = Content //strcat(Content, " : ",BackupType)
| extend Content = tostring(mode)
| extend StartTime = TimeStamp
| project TimeStamp,mode,topology,isSystemOnline,TaskId,Health,Content,GroupBy,StartTime
| summarize arg_max(TimeStamp,TimeStamp,mode,topology,isSystemOnline,Health,Content,GroupBy,StartTime) by TaskId
| project-away TimeStamp1,TimeStamp
| union
(
WBETraceLogAll
| where TaskId in (alltaskids)
| where Message == "[HANAPlugin] : Successfully set the HSRTopology."
| parse Properties with "{HSRTopolgy = " currentTopology "}{key = HSRTopology}"
| extend d = parse_json(currentTopology)
| extend timeOfCreation = d.timeOfCreation
| extend activeNodeOSName = d.activeNodeOSName
| extend topology = d
| extend topologyUpdatedByNode = d.topologyUpdatedByNode
| parse ContainerName with "Compute;" * ";" Content
| extend GroupBy = "Replica View"
| extend Content = tostring(activeNodeOSName)
| extend StartTime = TimeStamp
| project TimeStamp,timeOfCreation,activeNodeOSName,topology,TaskId,topologyUpdatedByNode,GroupBy,StartTime,Content
| summarize arg_min(TimeStamp,StartTime,GroupBy,Content,topologyUpdatedByNode,topology) by TaskId
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`, `{alltaskids}`

**Signal filters seen in KQL:** `Message == "[HANAPlugin PrBk]: hdbnsutilparsed value is "` · `Message == "[HANAPlugin] : Successfully set the HSRTopology."`

---

### get all backup task id queries

_Widget purpose:_ Active Node Tracking as per HDBnsutil tool

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `MultiRow` · Widget: `Timeline`

```kusto
WBEBackupStatsAll
| where TIMESTAMP between (queryFrom..queryTo)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| distinct TaskId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

---

### active node tracking for Log Backups

_Widget purpose:_ Backup Birds Eye View

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Timeline`

```kusto
let taskids=
WBEBackupStatsAll
| where TIMESTAMP between (queryFrom..queryTo)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType != "Log"
| distinct TaskId;
WBETraceLogAll
| where TaskId in (taskids)
| summarize EndTime=max(TimeStamp) by TaskId
| join kind=inner 
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFrom..queryTo)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType != "Log"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
//| extend StartTime = case(BackupType contains "Log" , min_of(PitStartTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend StartTime = min_of(PitEndTime,CoordCreatedTime)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("Extension POV: non log Backup Health: ",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = BackupType
| parse ContainerName with "Compute;" * ";" Content
| extend GroupBy = Content//strcat(Content," : ",BackupType)
| extend Content = strcat(BackupType, " : ",ErrorCode)
| project EventId,EventName,StartTime,Health,Tooltip,Content,TaskId,GroupBy,FilterCategory
) on $left.TaskId == $right.TaskId
| project-away TaskId1
| union
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFrom..queryTo)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType == "Log"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , min_of(CoordCreatedTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend EndTime = PitEndTime//TimeStamp
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = "Extension POV: Log Backup Health"
| extend Tooltip = EventId
| extend FilterCategory = BackupType
| parse ContainerName with "Compute;" * ";" Content
| extend GroupBy = Content //strcat(Content, " : ",BackupType)
| extend Content = strcat(BackupType," : ",ErrorCode)
| project StartTime,EndTime,Health,Content,GroupBy,TaskId,FilterCategory
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `BackupType != "Log"` · `BackupType == "Log"`

---

### Backup Timelines from extension POV

_Widget purpose:_ Backup Timelines detailed view

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `CoBeTimeline`

```kusto
let taskids=
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType != "Log"
| distinct TaskId;
WBETraceLogAll
| where TaskId in (taskids)
| summarize EndTime=max(TimeStamp) by TaskId
| join kind=inner 
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType != "Log"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
//| extend StartTime = case(BackupType contains "Log" , min_of(PitStartTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend StartTime = min_of(PitEndTime,CoordCreatedTime)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("Extension POV: non log Backup Health: ",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = "Extension"
| project EventId,EventName,StartTime,Health,Tooltip,FilterCategory,TaskId
) on $left.TaskId == $right.TaskId
| project-away TaskId,TaskId1
| union
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType == "Log"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , min_of(CoordCreatedTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend EndTime = TimeStamp
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("Coordinator POV: Log Backup Health: ",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = "Extension"
| project EventId,EventName,StartTime,EndTime,Health,Tooltip,FilterCategory
)
| union
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , CoordCreatedTime, PitEndTime)
| extend EventId = strcat_delim("_",BackupType,hanaBackupId,TaskId)
| extend EndTime = PitEndTime
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("SAPHana POV: Backup Health",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = "SAPHana"
| extend ParentId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| where isnotempty( StartTime)
| project EventId,EventName,StartTime,EndTime,Health,Tooltip,FilterCategory,TaskId,ParentId
)
| union
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = todatetime(d.SubmitTime)
| extend EventId = strcat_delim("_",BackupType,hanaBackupId,TaskId,"CoordinatorWaitInQueue")
| extend EndTime = todatetime(d.FirstStartTime)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("Coordinator Queue Waiting POV: Backup Health: ",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = "Coordinator Queue Wait"
| extend ParentId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| where isnotempty( StartTime)
| project EventId,EventName,StartTime,EndTime,Health,Tooltip,FilterCategory,TaskId,ParentId
)
| union
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = todatetime(d.CreatedTime)
| extend EventId = strcat_delim("_",BackupType,hanaBackupId,TaskId,"CoordinatorWaitBetweenCreationAndSubmission")
| extend EndTime = todatetime(d.SubmitTime)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("Task creation and submission diff POV: Backup Health: ",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = "Task creation and submission time diff"
| extend ParentId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| where isnotempty( StartTime)
| project EventId,EventName,StartTime,EndTime,Health,Tooltip,FilterCategory,TaskId,ParentId
)
| union
(
WBETraceLogAll
| where TaskId in (local_taskids)
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where Message == "[HANAPlugin Bkp]: Stamping PIT metadata."
| parse Properties with "{Medatada = " PitMetadata "}{storageContainerInfo =" *
| extend PitMetadata = parse_json(PitMetadata)
| extend FileList = PitMetadata.BackupSet.Catalog.FILE_LIST
| extend HanaService = PitMetadata.BackupSet.Catalog.DB_OBJECT_ID
| extend StartTime = todatetime(PitMetadata.BackupSet.Catalog.UTC_START_TIME)
| summarize arg_max(TimeStamp,FileList,HanaService,StartTime) by TaskId
| join kind=inner 
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType == "Log"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = todatetime(d.PitEndTime)
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
//| extend StartTime = case(BackupType contains "Log" , PitStartTime, PitEndTime)
| extend EventId = strcat_delim("_",BackupType,hanaBackupId,TaskId,"Service")
| extend EndTime = PitEndTime
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = strcat("Service POV: log Backup Health",DatasourceName)
| extend Tooltip = EventId
| extend FilterCategory = "Service"
| extend ParentId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| project EventId,EventName,EndTime,Health,Tooltip,FilterCategory,TaskId,ParentId
) on $left.TaskId == $right.TaskId
| extend EventName = strcat(HanaService,EventName)
| extend Tooltip = tostring(FileList)
| project-away TaskId,TaskId1,FileList,HanaService
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`, `{queryFromC}`, `{queryToC}`, `{local_taskids}`

**Signal filters seen in KQL:** `BackupType != "Log"` · `BackupType == "Log"` · `Message == "[HANAPlugin Bkp]: Stamping PIT metadata."`

---

### get log backup Task id queries

_Widget purpose:_ Backup Timelines detailed view

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `MultiRow` · Widget: `CoBeTimeline`

```kusto
WBEBackupStatsAll
| where TIMESTAMP between (queryFrom..queryTo)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where BackupType == "Log"
| distinct TaskId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `BackupType == "Log"`

---

### Backup Chaining query

_Widget purpose:_ Backup Chaining

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Graph`

```kusto
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where ErrorCode == "Success"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| where ChildOf contains ","
| mv-expand ChildOf =split(ChildOf, ",") to typeof(string) 
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , min_of(PitStartTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend EndTime = TimeStamp
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = "Extension POV up Health"
| extend Type = "Edge"
| extend Name = ""
| extend Id = strcat(ChildOf," -> ",PitId)
| extend Category = "two childof"
| extend StartId = tostring(ChildOf)
| extend EndId = tostring(PitId)
| project Type,Name,Id,Health,Category,StartId,EndId
| union 
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where ErrorCode == "Success"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| where ChildOf !contains ","
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , min_of(PitStartTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend EndTime = TimeStamp
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = "Extension POV up Health"
| extend Type = "Edge"
| extend Name = ""
| extend Id = strcat(ChildOf," -> ",PitId)
| extend Category = "one childof"
| extend StartId = tostring(ChildOf)
| extend EndId = tostring(PitId)
| project Type,Name,Id,Health,Category,StartId,EndId
)
| union 
(
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where ErrorCode == "Success"
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| where isnotempty( ParentOf)
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , min_of(PitStartTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend EndTime = TimeStamp
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = "Extension POV up Health"
| extend Type = "Edge"
| extend Name = ""
| extend Id = strcat(PitId," -> ",ParentOf)
| extend Category = "one parentof"
| extend StartId = tostring(PitId)
| extend EndId = tostring(ParentOf)
| project Type,Name,Id,Health,Category,StartId,EndId
)
| union 
(
//node
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = todatetime(d.PitStartTime)
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| extend CoordCreatedTime= todatetime(d.CreatedTime)
| extend StartTime = case(BackupType contains "Log" , min_of(PitStartTime,CoordCreatedTime),CoordCreatedTime )
| extend EventId = strcat_delim("_",ContainerName,DatasourceName,IsAdhoc,BackupType,hanaBackupId,TaskId)
| extend EndTime = TimeStamp
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend EventName = "Extension POV up Health"
| extend Type = "Node"
| extend Name = strcat_delim("_",PitId,hanaBackupId,MachineName,DatasourceName)
| extend Id = tostring(PitId)
| extend Category = BackupType
| extend Tooltip = tostring(PitEndTime)
| project Type,Name,Id,Health,Category,Properties,TaskId,Tooltip 
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`, `{queryFromC}`, `{queryToC}`

**Signal filters seen in KQL:** `ErrorCode == "Success"` · `ChildOf contains ","`

---

### Recovery bird eye view

_Widget purpose:_ Restore Bird Eye View

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Timeline`

```kusto
let dsIds = 
WBEBackupStatsAll
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where TIMESTAMP >  ago(90d)
| distinct DatasourceId;
WBERecoveryStatsAll
| where TIMESTAMP between (queryFrom .. queryTo)
| where DatasourceType contains "SAPHana"
| where SubscriptionId == local_subscriptionId
| where DatasourceId  in (dsIds)
| extend d = parse_json(Properties)
| extend EndTime = datetime_add('millisecond',DurationInMS,StartTime)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend FilterCategory = RecoveryType
| extend GroupBy = strcat(DatasourceName, " -> ",  MachineName)
| extend Content = strcat(RecoveryType," : ",ErrorCode)
| project StartTime,EndTime,Health,Content,GroupBy,TaskId,FilterCategory,RestoreToPitId,RestoreToTime
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `DatasourceType contains "SAPHana"`

---

### Pit view for pit ids

_Widget purpose:_ Pits View w.r.t Service and Datasource

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Timeline`

```kusto
let taskids=
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| distinct TaskId;
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = d.PitStartTime
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| project TimeStamp, DatasourceId,DatasourceName, PitStartTime, PitEndTime, PitId,hanaBackupId, BackupType,ChildOf, ParentOf, IsAdhoc, ExpiryTime, ErrorCode, DatasourceType, TaskId, ContainerName, DeploymentName,ProcessVersion,Properties
| join kind=leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (datetime_add('day',-1,queryFromC)..datetime_add('day',1,queryToC))
| where TaskId  in (taskids)
| where ComponentId contains "plugin"
| where Message == "[HANAPlugin Bkp]: Stamping PIT metadata."
| parse Properties with "{Medatada = " metadata "}{storageContainerInfo =" storageContainers "}"
| extend metadata = parse_json(metadata)
| extend Service = metadata.BackupSet.Catalog.DB_OBJECT_ID
| extend hanaBackupId =  metadata.BackupSet.Catalog.BACKUP_ID
| extend UTC_START_TIME = metadata.BackupSet.Catalog.UTC_START_TIME
| extend UTC_END_TIME = metadata.BackupSet.Catalog.UTC_END_TIME
| project metadata,storageContainers,TaskId,ContainerName,Service,UTC_START_TIME,UTC_END_TIME
) on $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName
| join kind=leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (datetime_add('day',-1,queryFromC)..datetime_add('day',1,queryToC))
| where TaskId  in (taskids)
| where Message == "BackupTask : Initializing BackupTask."
| parse Properties with "{TaskRequestBody = " request "}{Parameters = " *
| extend request = parse_json(request)
| extend hanabackupid = request.BackupId
| extend isCordTriggered = request.IsCoordinatorTriggeredBackup
| summarize arg_min(TimeStamp,hanabackupid,ContainerName,isCordTriggered) by TaskId
) on $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName
//| extend hanaBackupId = case(isempty(hanaBackupId ), hanabackupid, hanaBackupId )
| join kind= leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (datetime_add('day',-1,queryFromC)..datetime_add('day',1,queryToC))
| where TaskId  in (taskids)
| where ComponentId contains "plugin"
| where Message == "[HanaPlugin Bkp]: Got catalog backup id for parent backup"
| parse Properties with "{CatalogJobId = " catalogBackupId "}{ParentBackupId = " parentBackupId "}"
| project TimeStamp,catalogBackupId,parentBackupId,TaskId,ContainerName
) on $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName 
| extend hanaBackupId = case(hanaBackupId contains "adhoc", parentBackupId,hanaBackupId)
| extend hanaBackupId = case(hanaBackupId contains "Full", parentBackupId,hanaBackupId)
| extend hanaBackupId = case(hanaBackupId contains "Incremental", parentBackupId,hanaBackupId)
| extend hanaBackupIdTime = unixtime_milliseconds_todatetime(tolong(hanaBackupId))
| where isnotempty( PitId) and isnotempty( PitEndTime)
| extend StartTime = case(BackupType contains "log", todatetime(PitStartTime),todatetime(PitEndTime))
| extend PiTRelationShip = strcat("[",ChildOf,"]->","(",PitId,")->[",ParentOf,"]")
| extend Content = tostring(PitId)
| extend EndTime = todatetime(PitEndTime)
| parse ContainerName with "Compute;" * ";" machine
| extend Tooltip = strcat(hanaBackupId,":[",UTC_START_TIME,"->",UTC_END_TIME,"] by ",machine," Task ID :",TaskId)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend FilterCategory = hanaBackupId
| extend GroupBy = DatasourceName
| project TimeStamp,StartTime,EndTime,Content,Health,Tooltip,FilterCategory,GroupBy,PiTRelationShip
| sort by TimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`, `{queryFromC}`, `{queryToC}`

**Signal filters seen in KQL:** `ComponentId contains "plugin"` · `Message == "[HANAPlugin Bkp]: Stamping PIT metadata."` · `Message == "BackupTask : Initializing BackupTask."` · `Message == "[HanaPlugin Bkp]: Got catalog backup id for parent backup"`

---

### view by service machine and ds

_Widget purpose:_ Pits View w.r.t Service and Datasource

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Timeline`

```kusto
let taskids=
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| distinct TaskId;
WBEBackupStatsAll
| where TIMESTAMP between (queryFromC..queryToC)
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| extend d = parse_json(Properties)
| extend ChildOf = d.ParentPits
| extend ParentOf = d.ChildrenPits
| extend IsAdhoc = d.IsAdhoc
| extend ExpiryTime = d.PitExpiryTime
| extend PitStartTime = d.PitStartTime
| extend PitEndTime = d.PitEndTime
| extend hanaBackupId = d.BackupId
| project TimeStamp, DatasourceId,DatasourceName, PitStartTime, PitEndTime, PitId,hanaBackupId, BackupType,ChildOf, ParentOf, IsAdhoc, ExpiryTime, ErrorCode, DatasourceType, TaskId, ContainerName, DeploymentName,ProcessVersion,Properties
| join kind=leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (datetime_add('day',-1,queryFromC)..datetime_add('day',1,queryToC))
| where TaskId  in (taskids)
| where ComponentId contains "plugin"
| where Message == "[HANAPlugin Bkp]: Stamping PIT metadata."
| parse Properties with "{Medatada = " metadata "}{storageContainerInfo =" storageContainers "}"
| extend metadata = parse_json(metadata)
| extend Service = metadata.BackupSet.Catalog.DB_OBJECT_ID
| extend hanaBackupId =  metadata.BackupSet.Catalog.BACKUP_ID
| extend UTC_START_TIME = metadata.BackupSet.Catalog.UTC_START_TIME
| extend UTC_END_TIME = metadata.BackupSet.Catalog.UTC_END_TIME
| extend FirstLsn = metadata.BackupSet.Catalog.FirstLsn
| extend LastLsn = metadata.BackupSet.Catalog.LastLsn
| project metadata,storageContainers,TaskId,ContainerName,Service,UTC_START_TIME,UTC_END_TIME,FirstLsn,LastLsn
) on $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName
| join kind=leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (datetime_add('day',-1,queryFromC)..datetime_add('day',1,queryToC))
| where TaskId  in (taskids)
| where Message == "BackupTask : Initializing BackupTask."
| parse Properties with "{TaskRequestBody = " request "}{Parameters = " *
| extend request = parse_json(request)
| extend hanabackupid = request.BackupId
| extend isCordTriggered = request.IsCoordinatorTriggeredBackup
| summarize arg_min(TimeStamp,hanabackupid,ContainerName,isCordTriggered) by TaskId
) on $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName
//| extend hanaBackupId = case(isempty(hanaBackupId ), hanabackupid, hanaBackupId )
| join kind= leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (datetime_add('day',-1,queryFromC)..datetime_add('day',1,queryToC))
| where TaskId  in (taskids)
| where ComponentId contains "plugin"
| where Message == "[HanaPlugin Bkp]: Got catalog backup id for parent backup"
| parse Properties with "{CatalogJobId = " catalogBackupId "}{ParentBackupId = " parentBackupId "}"
| project TimeStamp,catalogBackupId,parentBackupId,TaskId,ContainerName
) on $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName 
| extend hanaBackupId = case(hanaBackupId contains "adhoc", parentBackupId,hanaBackupId)
| extend hanaBackupId = case(hanaBackupId contains "Full", parentBackupId,hanaBackupId)
| extend hanaBackupId = case(hanaBackupId contains "Incremental", parentBackupId,hanaBackupId)
| extend hanaBackupIdTime = unixtime_milliseconds_todatetime(tolong(hanaBackupId))
| extend StartTime = todatetime(UTC_START_TIME)
| extend StartTime = case(isempty( StartTime), TimeStamp ,StartTime)
| extend LsnMapping = strcat("[",PitId,"]->","(",hanaBackupId,"):[",FirstLsn,"->",LastLsn ,"]")
| extend Content = tostring(PitId)
| extend EndTime = todatetime(UTC_END_TIME)
| parse ContainerName with "Compute;" * ";" machine
| extend Tooltip = strcat(PitId,":[",PitStartTime,"->",PitEndTime,"] by ",machine," Task ID :",TaskId)
| extend Health = case(ErrorCode contains "Success" , "Healthy", case( ErrorCode contains "user" , "Degraded","Unhealthy" ) )
| extend FilterCategory = hanaBackupId
| extend GroupBy = strcat(machine,"[",DatasourceName,"] : ",Service)
| project TimeStamp,StartTime,EndTime,Content,Health,Tooltip,FilterCategory,GroupBy,IsAdhoc,isCordTriggered,LsnMapping,BackupType
| sort by TimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`, `{queryFromC}`, `{queryToC}`

**Signal filters seen in KQL:** `ComponentId contains "plugin"` · `Message == "[HANAPlugin Bkp]: Stamping PIT metadata."` · `Message == "BackupTask : Initializing BackupTask."` · `Message == "[HanaPlugin Bkp]: Got catalog backup id for parent backup"`

---

### get machines where recovery is done from hsr ds

_Widget purpose:_ Restore Timelines detailed View

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `MultiRow` · Widget: `CoBeTimeline`

```kusto
let dsIds = 
WBEBackupStatsAll
| where SubscriptionId == local_subscriptionId
| where LogicalContainerId == local_logicalContainerId
| where TIMESTAMP >  ago(90d)
| distinct DatasourceId;
WBERecoveryStatsAll
| where TIMESTAMP between (queryFrom .. queryTo)
| where DatasourceType contains "SAPHana"
| where SubscriptionId == local_subscriptionId
| where DatasourceId  in (dsIds)
| distinct ContainerName;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_logicalContainerId}`

**Signal filters seen in KQL:** `DatasourceType contains "SAPHana"`

---

### get component restore timings

_Widget purpose:_ Restore Timelines detailed View

Cluster: `https://mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `CoBeTimeline`

```kusto
let restoreComponentPitMapping = 
WBETraceLogAll
| where TIMESTAMP between (queryFromC .. queryToC)
| where ContainerName in (local_containerNames)
| where ComponentId contains "plugin"
| where Message == "[HANAPlugin Res]: Restoring pit component"
| parse Properties with "{Pit id = " PitID "}{Pit end time =" * "}{Ebid requested = " EBID "}{Component to restore = " componentToRestore "}{Restore path = " restorePath "}"
| project TimeStamp,TaskId,PitID,EBID,componentToRestore,restorePath,ContainerName
| sort by TimeStamp asc ;
let restoreComponentStats =
WBETraceLogAll
| where TIMESTAMP between (queryFromC .. queryToC)
| where ContainerName in (local_containerNames)
| where ComponentId contains "plugin"| where Message == "[HANAPlugin Res]: Completed restore of component."
| parse Properties with "{component restored = " componentRestored "}{component restored destination = " componentRestoredDestination "}{restore size (bytes) = " restoreSize "}{ext backup id = " EBID "}" temp "}{RestoreSize/TotalReadTime (MBps) = " ReadMBps "}{RestoreSize/TotalWriteTime (MBps) = " WriteMBps "}"
| parse Properties with "{component restored = " componentRestored1 "}{component restored destination = " componentRestoredDestination1 "}{restore size (bytes) = " restoreSize1 "}{ext backup id = " EBID1 "}{Total read time in MS = " ReadTimeInMs "}{Total write time in MS = " WriteTimeInMS "}"
| parse WriteTimeInMS with WriteTimeInMS1 "}" *
| extend WriteTimeInMS = case( isempty( WriteTimeInMS1), WriteTimeInMS, WriteTimeInMS1)
| extend componentRestored = case(isempty( componentRestored), componentRestored1,componentRestored)
| extend  componentRestoredDestination = case(isempty( componentRestoredDestination), componentRestoredDestination1,componentRestoredDestination)
| extend restoreSizeInMb = case(isempty( restoreSize), (tolong(restoreSize1)/(1024.0*1024)), (tolong(restoreSize)/(1024.0*1024)))
| extend ReadMBps = tolong((restoreSizeInMb*1000.0)/(tolong(ReadTimeInMs)*1.0))
| extend  WriteMBps = tolong((restoreSizeInMb*1000.0)/(tolong(WriteTimeInMS)*1.0)) 
| project TimeStamp,PreciseTimeStamp,FileName,LineNumber,Message,Properties,Exception,Level,ComponentId,ContainerName,ThreadId,TaskId,restoreSizeInMb,EBID1,ReadMBps,WriteMBps,temp,componentRestored1,componentRestoredDestination1
| sort by TimeStamp asc;
restoreComponentPitMapping
| join kind=leftouter 
restoreComponentStats
on $left.TaskId == $right.TaskId and $left.componentToRestore == $right.componentRestored1 and $left.ContainerName == $right.ContainerName
| project TimeStamp,TimeStamp1,PitID,EBID1,componentToRestore,restorePath,ReadMBps,WriteMBps,restoreSizeInMb,Level,TaskId,ContainerName
| join kind=leftouter 
(
WBETraceLogAll
| where TIMESTAMP between (queryFromC .. queryToC)
| where ContainerName in (local_containerNames)
| where FileName == "PitCacheHelper.cs"
| where ComponentId contains "plugin"
| where Message contains "cache hit" or Message contains "cache miss"
| parse Properties with "{ExternalBackupId = " EBID "}{PitType = " PitType "}"
| extend cacheHit = case(Message contains "hit", "true", "false")
| project TimeStamp,EBID,PitType,cacheHit,TaskId,ContainerName
| summarize CacheHitCount=countif(cacheHit == "true"), Total=count() by EBID,TaskId,ContainerName
| extend CacheHitPercentage = CacheHitCount*100.0/Total
) on $left.EBID1 == $right.EBID and $left.TaskId == $right.TaskId and $left.ContainerName == $right.ContainerName
| project-away TaskId1,EBID,CacheHitCount,Total,ContainerName1
| project-rename PitRestoreStartTime = TimeStamp, PitRestoreEndTime = TimeStamp1,EBID= EBID1
| extend CacheHitPercentage = case(isempty( CacheHitPercentage), 0.0,CacheHitPercentage)
| extend StartTime = PitRestoreStartTime
| extend EndTime = PitRestoreEndTime
| extend Health = case(CacheHitPercentage > 90, "Healthy", "Neutral")
| parse componentToRestore with *"/backint" service
| extend Content = strcat_delim("_",PitID,EBID,service)
| extend EventName =  case(componentToRestore contains "log_backup_0_0_0_0", "Catalog Restore", " Service Component Restore" )
| extend EventId = strcat_delim("_",TaskId,EventName,componentToRestore)
| extend Tooltip = Content
| extend FilterCategory = "Component Restore"
| extend ParentId = TaskId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_subscriptionId}`, `{local_containerNames}`, `{queryFromC}`, `{queryToC}`

**Signal filters seen in KQL:** `ComponentId contains "plugin"` · `Message == "[HANAPlugin Res]: Restoring pit component"` · `Message == "[HANAPlugin Res]: Completed restore of component."` · `FileName == "PitCacheHelper.cs"` · `Message contains "cache hit"`

---
