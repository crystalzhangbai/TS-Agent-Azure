# XStore Performance Tables

> Source: **Azure Host — Azure Host Node** dashboard, chapter **XStore Performance Tables** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Agent Start Operation Performance (P50, 90, 99)

### Agent Start Operations Performance (P50, 90, 99)

_Widget purpose:_ Agent Start Operation Performance (P50, 90, 99)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `XStore Performance Tables > Agent Start Operation Performance (P50, 90, 99)`

```kusto
let timeRangeInMicroSecs = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
// | where TenantName == 'MS-CBN13PrdStf02C'
| where Component in ('STG','XOS', 'TST','XOSTST')
| where (FinishDate > StartDate)
| top 100 by  StartDate desc
| extend timeTaken = todecimal(FinishDate - StartDate)
| summarize median = percentile(timeTaken, 50) / 2;
let timeRange = timeRangeInMicroSecs
| extend deltaTime = median / 10000000
| extend beginTime = datetime_add('second', toint(deltaTime * -1), queryFrom)
| extend finishTime = datetime_add('second', toint(deltaTime), queryFrom)
| project beginTime, finishTime;
let beginTime = toscalar(timeRange | project beginTime);
let finishTime = toscalar(timeRange | project finishTime);
let startDateFinishDate = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
| where Component in ('STG','XOS', 'TST','XOSTST')
| where StartDate between (beginTime .. queryFrom) // find the startDate that closest aligns to the startTime
| where FinishDate > StartDate
| top 1 by StartDate desc
| project StartDate, FinishDate;
let StartDate = toscalar(startDateFinishDate | project StartDate);
let FinishDate = toscalar(startDateFinishDate | project FinishDate);
cluster('azcore.centralus').database('Fa').
AgentStartOperationsPerformanceEtwTable
| where PreciseTimeStamp between (StartDate .. FinishDate)
| where Cluster contains "Stp" or Cluster contains "str"
| where Scenario == 'Reboot'
| summarize median = percentile(DurationInMilliseconds, 50), P90 = percentile(DurationInMilliseconds, 90), P99 = percentile(DurationInMilliseconds, 99), Max = percentile(DurationInMilliseconds, 100) by Operation
| project Operation, median_s = median / 1000, P90_s = P90 / 1000, P99_s = P99 / 1000, Max_s = Max / 1000
| order by P99_s
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `TenantName == "MS-CBN13PrdStf02C"` · `Cluster contains "Stp"` · `Scenario == "Reboot"`

---

## Container Workflow Details (P50, 90, 99)

### Container Workflow Details (P50, 90, 99)

Cluster: `https://azurecm.kusto.windows.net/` · Database: `AzureCM` · Type: `Table`
Source panel: `XStore Performance Tables > Container Workflow Details (P50, 90, 99)`

```kusto
let timeRangeInMicroSecs = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
// | where TenantName == 'MS-CBN13PrdStf02C'
| where Component in ('STG','XOS', 'TST','XOSTST')
| where (FinishDate > StartDate)
| top 100 by  StartDate desc
| extend timeTaken = todecimal(FinishDate - StartDate)
| summarize median = percentile(timeTaken, 50) / 2;
let timeRange = timeRangeInMicroSecs
| extend deltaTime = median / 10000000
| extend beginTime = datetime_add('second', toint(deltaTime * -1), queryFrom)
| extend finishTime = datetime_add('second', toint(deltaTime), queryFrom)
| project beginTime, finishTime;
let beginTime = toscalar(timeRange | project beginTime);
let finishTime = toscalar(timeRange | project finishTime);
let startDateFinishDate = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
| where Component in ('STG','XOS', 'TST','XOSTST')
| where StartDate between (beginTime .. queryFrom) // find the startDate that closest aligns to the startTime
| where FinishDate > StartDate
| top 1 by StartDate desc
| project StartDate, FinishDate;
let StartDate = toscalar(startDateFinishDate | project StartDate);
let FinishDate = toscalar(startDateFinishDate | project FinishDate);
cluster('azurecm').database('AzureCM').
ContainerWorkflowDurationDetails
| where PreciseTimeStamp between (StartDate .. FinishDate)
| where Tenant contains "Stp" or Tenant contains "str"
| extend duration = todecimal(workflowDuration)
| summarize median = percentile(duration, 50), P90 = percentile(duration, 90), P99 = percentile(duration, 99), Max = percentile(duration, 100) by workflowStep
| order by P99
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `TenantName == "MS-CBN13PrdStf02C"` · `Tenant contains "Stp"`

---

## IfxOperationV2 Performance (P50, 90, 99)

### IfxOperationV2 Performance (P50, 90, 99)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `XStore Performance Tables > IfxOperationV2 Performance (P50, 90, 99)`

```kusto
let timeRangeInMicroSecs = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
// | where TenantName == 'MS-CBN13PrdStf02C'
| where Component in ('STG','XOS', 'TST','XOSTST')
| where (FinishDate > StartDate)
| top 100 by  StartDate desc
| extend timeTaken = todecimal(FinishDate - StartDate)
| summarize median = percentile(timeTaken, 50) / 2;
let timeRange = timeRangeInMicroSecs
| extend deltaTime = median / 10000000
| extend beginTime = datetime_add('second', toint(deltaTime * -1), queryFrom)
| extend finishTime = datetime_add('second', toint(deltaTime), queryFrom)
| project beginTime, finishTime;
let beginTime = toscalar(timeRange | project beginTime);
let finishTime = toscalar(timeRange | project finishTime);
let startDateFinishDate = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
| where Component in ('STG','XOS', 'TST','XOSTST')
| where StartDate between (beginTime .. queryFrom) // find the startDate that closest aligns to the startTime
| where FinishDate > StartDate
| top 1 by StartDate desc
| project StartDate, FinishDate;
let StartDate = toscalar(startDateFinishDate | project StartDate);
let FinishDate = toscalar(startDateFinishDate | project FinishDate);
cluster('azcore.centralus').database('Fa').
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (StartDate .. FinishDate)
| where Cluster contains "Stp" or Cluster contains "str"
| where OperationName == 'AgentpCreateContainerWorker' or OperationName == 'AgentpStartContainerWorker' or OperationName == 'AgentpStartRole' or OperationName == 'AgentpStartRoleWorker'
 or OperationName == 'ImageDeploy' or OperationName == 'ImageDecompress' or OperationName == 'ImageDownload' or OperationName == 'VdsInitialize'
| summarize median = percentile(DurationIn100ns, 50), P90 = percentile(DurationIn100ns, 90), P99 = percentile(DurationIn100ns, 99), Max = percentile(DurationIn100ns, 100) by OperationName
| project OperationName, median_s = median / 10000, P90_s = P90 / 10000, P99_s = P99 / 10000, Max_s = Max / 10000
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `TenantName == "MS-CBN13PrdStf02C"` · `Cluster contains "Stp"` · `OperationName == "AgentpCreateContainerWorker"`

---

## Node Workflow Details (P50, 90, 99)

### NodeWorkflow P50, P90, P99

_Widget purpose:_ Node Workflow Details (P50, 90, 99)

Cluster: `https://azurecm.kusto.windows.net/` · Database: `AzureCM` · Type: `Table`
Source panel: `XStore Performance Tables > Node Workflow Details (P50, 90, 99)`

```kusto
let timeRangeInMicroSecs = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
// | where TenantName == 'MS-CBN13PrdStf02C'
| where Component in ('STG','XOS', 'TST','XOSTST')
| where (FinishDate > StartDate)
| top 100 by  StartDate desc
| extend timeTaken = todecimal(FinishDate - StartDate)
| summarize median = percentile(timeTaken, 50) / 2;
let timeRange = timeRangeInMicroSecs
| extend deltaTime = median / 10000000
| extend beginTime = datetime_add('second', toint(deltaTime * -1), queryFrom)
| extend finishTime = datetime_add('second', toint(deltaTime), queryFrom)
| project beginTime, finishTime;
let beginTime = toscalar(timeRange | project beginTime);
let finishTime = toscalar(timeRange | project finishTime);
let startDateFinishDate = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').AllDeploymentsFromReleaseDS
| where Component in ('STG','XOS', 'TST','XOSTST')
| where StartDate between (beginTime .. queryFrom) // find the startDate that closest aligns to the startTime
| where FinishDate > StartDate
| top 1 by StartDate desc
| project StartDate, FinishDate;
let StartDate = toscalar(startDateFinishDate | project StartDate);
let FinishDate = toscalar(startDateFinishDate | project FinishDate);
NodeWorkflowDurationDetails
| where PreciseTimeStamp between (StartDate .. FinishDate)
| where Tenant contains "Stp" or Tenant contains "str"
| extend duration = todecimal(workflowDuration)
| summarize median = percentile(duration, 50), P90 = percentile(duration, 90), P99 = percentile(duration, 99), Max = percentile(duration, 100) by workflowStep
| order by P99
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `TenantName == "MS-CBN13PrdStf02C"` · `Tenant contains "Stp"`

---
