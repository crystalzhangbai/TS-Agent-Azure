# At-A-Glance Health

> Source: **Aztec — Tenant** dashboard, chapter **At-A-Glance Health** (8 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Tenant Upgrade Rollouts

_Widget purpose:_ At-A-Glance Health

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `At-A-Glance Health`

```kusto
LogTenantSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName == queryTenantName
| project StartTime = PreciseTimeStamp, Content = tenantUpgradeRolloutWaitReason
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case (Content contains "WaitingFor", "Degraded", 
  Content == "NoUpgradeInProgress", "Healthy",
  "Neutral")
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Tenant Container Health Faults

_Widget purpose:_ At-A-Glance Health

Cluster: `azurecm` · Database: `azurecm` · Type: `Timeline`
Source panel: `At-A-Glance Health`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between(qFrom..qTo)
| where tenantName == queryTenantName
| where isnotempty(faultInfo)
| extend faultJson = parse_json(faultInfo)
| extend reason = tostring(faultJson.Reason)
| extend correlationId = tostring(faultJson.CorrelationGuid)
| extend faultTime = tostring(faultJson.Time)
| extend ContainerLink = strcat(
    "<a href='https://azureserviceinsights.trafficmanager.net/view/services/Aztec/pages/Containers?",
    "containerId=",containerId,
    "&subscriptionId=",qSub,
    "&nodeId=",nodeId,
    "&tenantName=",tenantName,
    "&virtualMachineUniqueId=",virtualMachineUniqueId,
    "' target='_blank' rel='noopener noreferrer'>", 
    containerId, 
    "</a>"
)
| summarize arg_max(PreciseTimeStamp, *) by containerId, reason, faultTime
| extend Content = strcat(
    "Container Fault (Check the SH Faults tab)",
    "<br>Click for details of fault."
    "<br>ContainerID: ", containerId
)
| project StartTime = PreciseTimeStamp, Content, containerId, nodeId, virtualMachineUniqueId, roleInstanceName, 
    correlationId, tenantName, reason, faultTime, faultJson, ExtendedDetails = faultJson.ExtendedDetails
```

**Params:** `{queryTenantName}`, `{qSub}`, `{qFrom}`, `{qTo}`

---

### VMA

_Widget purpose:_ At-A-Glance Health

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`
Source panel: `At-A-Glance Health`

```kusto
VMA
| where PreciseTimeStamp between(queryFrom..queryTo)
| where isempty(queryTenantName) or TenantName == queryTenantName
| where isempty(queryContainerId) or ContainerId == queryContainerId
| where CadPrimaryKey !contains 'composite'
| extend ContainerLink = strcat(
    "<a href='https://azureserviceinsights.trafficmanager.net/view/services/Aztec/pages/Containers?containerId=",
    ContainerId,
    "' target='_blank' rel='noopener noreferrer'>", 
    ContainerId, 
    "</a>"
)
| extend NodeLink = strcat(
    "<a href='https://azureserviceinsights.trafficmanager.net/view/services/Aztec/pages/Nodes?nodeId=",
    NodeId,
    "' target='_blank' rel='noopener noreferrer'>", 
    NodeId, 
    "</a>"
)
| extend TenantContent = strcat(
    RCALevel2,
    "<br/>Container: ", ContainerLink,
    "<br/>Node: ", NodeLink
)
| extend DefaultContent = RCALevel2
| extend Content = iif(isempty(queryContainerId), TenantContent, DefaultContent)
| extend Tooltip = strcat(
    "RoleInstanceName: ", RoleInstanceName,
    "<br/>RCAEngineCategory: ", RCAEngineCategory,
    "<br/>RCALevel1: ", RCALevel1,
    "<br/>RCALevel2: ", RCALevel2,
    "<br/>RCALevel3: ", RCALevel3,
    "<br/>RCA: ", RCA
)
| extend FilterCategory = RCAEngineCategory
| project StartTime, Content, Tooltip, FilterCategory
```

**Params:** `{queryContainerId}`, `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### ICM Outages

_Widget purpose:_ At-A-Glance Health

Cluster: `azurecm` · Database: `azurecm` · Type: `Timeline`
Source panel: `At-A-Glance Health`

```kusto
let subList = pack_array(querySubscriptionId);
let interestingResources = dynamic([
    "virtualmachines",
    "storage",
    "azureresourcemanager",
    "virtualnetwork"
]);
cluster('icmdataro.centralus.kusto.windows.net').database('Reporting').GetJediMetricsforSubscription(queryFrom, queryTo, subList)
| where isempty(queryRegion) or AcmImpactedRegionList has "global" or AcmImpactedRegionList has queryRegion
| extend ResourceName = tostring(parse_json(AcmImpactedRegionServiceList)[0].ResourceName)
| where ResourceName in (interestingResources)
| join kind=leftouter (
    cluster("icmcluster").database("IcmDataWarehouse").Incidents
    | where Lens_IngestionTime between(queryFrom..queryTo)
    | summarize arg_max(ModifiedDate, *) by IncidentId
) on $left.OutageIncidentId == $right.IncidentId
| extend IncidentLink = strcat(
    "<a href=\"https://portal.microsofticm.com/imp/v3/outages/details/", 
    IncidentId, 
    "/home\" target=\"_blank\" rel=\"noopener noreferrer\">", 
    IncidentId, 
    "</a>")
| extend Content = strcat(
    "Title: ", Title,
    "<br/>Resource: ", ResourceName,
    "<br/>Team: ", OwningTenantName, "/", OwningTeamName,
    "<br/>ICM: ", IncidentLink
    )
| project StartTime = ImpactStartDate, EndTime = MitigateDate, Content
```

**Params:** `{querySubscriptionId}`, `{queryRegion}`, `{queryFrom}`, `{queryTo}`

---

### FC Downtime

_Widget purpose:_ At-A-Glance Health

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Timeline`
Source panel: `At-A-Glance Health`

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

_Widget purpose:_ At-A-Glance Health

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Timeline`
Source panel: `At-A-Glance Health`

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

### Tenant State

_Widget purpose:_ At-A-Glance Health

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `At-A-Glance Health`

```kusto
LogTenantSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = state //, GroupBy = strcat("Tenant State in ", Tenant)
//| order by StartTime asc, GroupBy asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case (Content in ("Stopping", "Starting"), "Degraded", Content == "Started", "Healthy", "Unhealthy")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

## Extended Error Details

### Explode LogContainerHealthSnapshot ExtendedDetails

_Widget purpose:_ Extended Error Details

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`
Source panel: `At-A-Glance Health > Extended Error Details`

```kusto
print qExtendedDetails
| mv-expand row = qExtendedDetails 
| extend Name = tostring(row.Name), Value = tostring(row.Value)
| project-away row, print_0
| order by Name asc
```

**Params:** `{qExtendedDetails}`

---
