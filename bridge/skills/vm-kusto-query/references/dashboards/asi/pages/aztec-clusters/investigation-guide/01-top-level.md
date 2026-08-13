# (top-level)

> Source: **Aztec — Clusters** dashboard, chapter **(top-level)** (7 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Clusters"

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogClusterSnapshot 
| where Tenant =~ local_Tenant
| top 1 by PreciseTimeStamp desc
| extend jarvisQueryStartTime = datetime_diff('millisecond', globalFrom, datetime(1970-01-01 00:00:00))
| extend jarvisQueryEndTime = datetime_diff('millisecond', globalTo, datetime(1970-01-01 00:00:00))
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_Tenant}`

---

### Cluster Hosting Env

_Widget purpose:_ Hosting Environment

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`

```kusto
LogClusterSnapshot 
| where PreciseTimeStamp > ago(28d)
| where Tenant == queryTenant
| top 1 by PreciseTimeStamp desc
| project hostingEnvironment
| extend json = parse_json(hostingEnvironment)
| mv-expand bagexpansion=array json
| project Name = tostring(json[0]), Value = tostring(json[1])
```

**Params:** `{queryTenant}`

---

### Cluster Setting Deletions

Cluster: `azurecm` · Database: `azurecm` · Type: `Timeline`

```kusto
LogSettingDeletionEvent
| where PreciseTimeStamp > ago(2d)
| where Tenant == queryCluster
| extend Tooltip = strcat(
    "Message: ", eventMessage,
    "<br/>Setting: ", settingName,
    "<br/>Value: ", settingValue
)
| project StartTime = PreciseTimeStamp, Content = settingName, Tooltip
```

**Params:** `{queryCluster}`

---

### Cluster Incarnations

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogClusterSnapshot 
| where Tenant == queryTenant 
| where PreciseTimeStamp between(global_startTime..global_endTime)
| summarize StartTime = min(PreciseTimeStamp), EndTime = max(PreciseTimeStamp) by IncarnationId, RoleInstance, buildVersion 
| extend UpTime = EndTime - StartTime
| extend Content = strcat(IncarnationId, " - ", RoleInstance)
| extend Tooltip = strcat(
    "IncarnationId: ", IncarnationId,
    "<br/>RoleInstance: ", RoleInstance,
    "<br/>Build: ", buildVersion,
    "<br/>Start: ", StartTime,
    "<br/>End: ", EndTime,
    "<br/>UpTime: ", UpTime
)
| project StartTime, EndTime, Content, Tooltip
```

**Params:** `{queryTenant}`

---

### LEGO DC Health Status

Cluster: `silverstonepcs.eastus.kusto.windows.net` · Database: `silverstonepcsdb` · Type: `Timeline`

```kusto
fDataCenterManagerHealthStatus(queryRegion, queryCluster, queryFrom, queryTo)
| extend Resource = Status
| extend Timestamp = todatetime(Timestamp)
| project Timestamp, Resource
| order by Timestamp asc
| extend PrevTime = prev(Timestamp)
| extend NextTime = next(Timestamp)
| extend PrevState = prev(Resource)
| extend NextState = next(Resource)
| where isnull(PrevTime) or isnull(NextTime) or (Resource != PrevState or Resource != NextState) 
| extend StartTime = Timestamp
| extend EndTime = next(Timestamp)
| project StartTime, EndTime, Content = Resource, Health = Resource
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryRegion}`, `{queryCluster}`, `{queryFrom}`, `{queryTo}`

---

### FC Downtime

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Timeline`

```kusto
let clusters =  (LogTenantSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct Tenant);
cluster('azurecm').database('azurecm').FabricFailoverDowtimeRawData(queryFrom, queryTo)
| where Tenant in (clusters)
| project Tenant, StartTime = DownTimeStart, EndTime = DownTimeEnd, Content = strcat(tostring(DurationInMs/1000), " secs"), DurationInMs, Health = "Unhealthy"
| order by StartTime asc
| extend GroupBy = strcat("FC Downtime - ", Tenant)
| order by GroupBy asc, StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### FC Failover

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Timeline`

```kusto
let clusters = (LogTenantSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| summarize by tenantName, tenantId, Tenant
| distinct Tenant);
cluster('azurecm').database('azurecm').LogClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName in (clusters)
| order by tenantName asc, PreciseTimeStamp asc 
| project StartTime = PreciseTimeStamp, tenantName, roleInstanceName
| extend flag = case (prev(roleInstanceName) <> roleInstanceName, "changed", "")
| where flag <> ""
| extend flag = case ((prev(tenantName) == tenantName) or (next(tenantName) == tenantName), "changed", "")
| where flag <> ""
| extend EndTime = case ((next(tenantName) == tenantName) and isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Content = roleInstanceName
| extend GroupBy = strcat("FC Failover - ", tenantName)
| order by GroupBy asc, StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
