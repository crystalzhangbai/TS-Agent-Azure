# Outage

> Source: **ARM CoBe Control Plane Region Insights Investigation Guide** dashboard, chapter **Outage** (14 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AAD Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["azureactivedirectory", "azureactivedirectoryb2c", "azureactivedirectorydomainservices"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### ARM Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["azureresourcemanager"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### AzPolicy Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["azurepolicy"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### CosmosDB Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["azurecosmosdb"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### Virtual Machines Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["virtualmachines", "virtualmachinescalesets"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### Network Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["virtualnetwork", "networkinfrastructure", "vpngateway", "expressroute"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### AKS Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["azurekubernetesservice(aks)"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### Storage Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["storage"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### SQL Database Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["sqldatabase"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### App Services Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["appservice", "appservice(linux)"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### Container Instances Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["containerinstances"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### PostgreSQL Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["azuredatabaseforpostgresql"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### LogicApps Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["logicapps"]);
OutageTimeline(startTime,endTime,regionList,interestingResources)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### Region Outages

_Widget purpose:_ Outage

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Table`
Source panel: `Outage`

```kusto
let regionList = pack_array(tolower(replace_string(region, " ", "")));
let interestingResources = 
            dynamic(["virtualmachines", "sqldatabase",
            "azureactivedirectory", "storage", "appservice(linux)", "appservice",
            "logicapps", "applicationgateway", "azurearcenabledkubernetes",
            "azuredatabaseforpostgresql", "azureactivedirectoryb2c", "vpngateway",
            "expressroute", "azureresourcemanager", "virtualnetwork",
            "azurekubernetesservice(aks)", "containerinstances",
            "azurecosmosdb", "azureactivedirecotrydomainservices",
            "azurepolicy", "networkinfrastructure", "virtualmachinescalesets"]);
    let outages =
    database("Outage").Outages
    | where UpdatedTime between (startTime..endTime)
    | extend IncidentId=ParentId
    | order by IncidentId, UpdatedTime desc
    | extend Index=row_number(1, prev(IncidentId)!=IncidentId)
    | where Index ==1
    | project-away Index
    | where has_any_index( Json, regionList) != -1
    | extend symptoms=parse_json(Json).Symptoms
    | extend  Title=parse_json(Json)["Title"],
        Status=parse_json(Json)["CurrentStatus"],
        ImpactedService=parse_json(symptoms).ImpactedServices,
        ImpactedRegion=parse_json(symptoms).ImpactedRegions,
        ImpactedCloudNames=parse_json(symptoms).ImpactedCloudNames,
        ImpactFlag=parse_json(Json).ImpactFlag
    | where ImpactedCloudNames contains "public"
    | where has_any_index( tostring(ImpactedService), interestingResources)!=-1;
    let ids = outages | distinct IncidentId;
   Incidents
    | where ModifiedDate between (startTime..endTime)
    | where IncidentId in (ids)
    | order by IncidentId, ModifiedDate desc
    | extend Index=row_number(1, prev(IncidentId)!=IncidentId)
    | where Index == 1
    | project-away Index
    | project IncidentId, Title, Status, Severity, CreateDate, ModifiedDate
    | join kind = rightouter (
    outages
    ) on IncidentId
    | project IncidentId, Title=coalesce(Title1, Title), Status=coalesce(Status, Status1),
        ImpactedRegion, ImpactedService, Severity, ImpactFlag, CreateDate, ModifiedDate
    | where Severity <= 2
    | mv-apply ImpactedRegion,ImpactedService to typeof(dynamic) on
    (
    extend regions =parse_json(ImpactedRegion)["RegionId"], services=parse_json(ImpactedService)["ServiceId"]
    | summarize ImpactedRegion=strcat_array(make_list(regions), ", "), ImpactedService=strcat_array(make_list(services), ", ") ,take_any(CreateDate, ModifiedDate) by IncidentId)
    | extend level = iff(ImpactFlag=="High", "error", "info")
    | order by CreateDate desc
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ImpactedCloudNames contains "public"`

---
