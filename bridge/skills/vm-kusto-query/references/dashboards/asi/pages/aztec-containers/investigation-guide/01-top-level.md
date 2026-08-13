# (top-level)

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **(top-level)** (10 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Containers"

Cluster: `azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp  between (globalFrom .. globalTo)
| where containerId == local_containerId
| take 1
| project-reorder containerId, Tenant, nodeId, tenantName, virtualMachineUniqueId, roleInstanceName
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_containerId}`, `{local_nodeId}`, `{local_subscriptionId}`, `{local_tenantName}`, `{local_virtualMachineUniqueId}`

---

### Lookup AzCompute Shoebox Account

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
LogClusterSnapshot
| where RegionFriendlyName =~ queryRegionName
| take 1
| project shoeboxMdmAccountName
```

**Params:** `{queryRegionName}`

---

### Lookup AzNw Region Code

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
// Now we get the region code from the networking cluster
cluster("aznwnetmon").database('aznwmds').RegionNamesMap
| where RegionName == queryRegionName
| take 1
| project NetworkRegionCode = RegionCode
```

**Params:** `{queryRegionName}`

---

### VM Context

_Widget purpose:_ Host Context

Cluster: `Vmainsight` · Database: `CAD` · Type: `Single` · Widget: `Card`

```kusto
CADDAILY
| where PreciseTimeStamp  between (queryFrom - 1d .. queryTo)
| where ContainerId =~ queryContainerId
| top 1 by PreciseTimeStamp desc
| project
PreciseTimeStamp,
Storage_Cluster, 
Hardware_Model,
Hardware_Location,
Hardware_Rack,
NodeSS_NMAgentHostPlugin,
NodeSS_SLBHostPluginService,
NodeSS_SlbMonAgentHost,
Network_TOR2,
NodeSS_NodeDataCollectedOn
```

**Params:** `{queryContainerId}`, `{queryFrom}`, `{queryTo}`

---

### Node TOR Info

_Widget purpose:_ TOR

Cluster: `Vmainsight` · Database: `AzureGraph` · Type: `Single` · Widget: `Card`

```kusto
Compute_Node 
| where Id =~ queryNodeId
| top 1 by TimeStamp desc
| project NodeId = Id, ClusterId, tostring(ToRRouter), State, IPAddress, NetworkSwitchPort
```

**Params:** `{queryNodeId}`

---

### VM Impacting Events

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`

```kusto
VmImpactingEventsV1
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where ContainerId == queryContainerId and RCAEngineCategory != "CustomerInitiated"
| extend Content = strcat(RCAEngineCategory, " - ", RCALevel1)
| extend Tooltip = strcat("RCALevel2: ", RCALevel2, "<br/>RCALevel3: ", RCALevel3, "<br/>Detail: ", Detail)
| project StartTime = PreciseTimeStamp, Content, Tooltip
```

**Params:** `{queryContainerId}`

---

### VMA

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`

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

### Air Managed Events

Cluster: `vmainsight` · Database: `Air` · Type: `Timeline`

```kusto
AirManagedEvents
| where EventTime between(queryFrom..queryTo)
//| where EventCategoryLevel3 == 'HostNetworkingUpdate'
| where ObjectId == queryContainerId
| extend Content = strcat(RCALevel1, " / ", EventCategoryLevel3)
| extend Tooltip = strcat(
    "EventCategoryLevel1: ", EventCategoryLevel1,
    "<br/>EventCategoryLevel2: ", EventCategoryLevel2,
    "<br/>EventCategoryLevel3: ", EventCategoryLevel3,
    "<br/>RCALevel1: ", RCALevel1,
    "<br/>RCALevel2: ", RCALevel2
)
| project StartTime = EventTime, Content, Tooltip
```

**Params:** `{queryContainerId}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `EventCategoryLevel3 == "HostNetworkingUpdate"`

---

### Query DCMNMAgentProgrammingDurationEtwTable

_Widget purpose:_ DCM NMAgent Programming Duration

Cluster: `azurecm` · Database: `azurecm` · Type: `MultiRow` · Widget: `DynamicTab`

```kusto
DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp between (queryFrom..queryTo)
| where interfaceId contains"queryContainerId"
| project PreciseTimeStamp,message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `interfaceId contains "queryContainerId"`

---

### Container DNS Queries

Cluster: `azcore.centralus.kusto.windows.net` · Database: `PrivateDnsRr` · Type: `Table`

```kusto
// These lists aren't exhaustive but include the most common types
let qtypeStrings = datatable (QTYPE:long, QTYPESTR:string) [1, "A", 2, "NS", 5, "CNAME", 6, "SOA", 12, "PTR", 16, "TXT", 28, "AAAA", 33, "SRV", 65, "HTTPS"];
let rcodeStrings = datatable (RCODE:long, RCODESTR:string) [0, "NOERROR", 1, "FORMERROR", 2, "SERVFAIL", 3, "NXDOMAIN", 4, "NOTIMP", 5, "REFUSED"];
DnsResponseSuccessSampled
| union DnsResponseFailureSampled
| where PreciseTimeStamp between (queryFrom..queryTo)
| where EDNSCorrelationTag == queryContainerId
| lookup qtypeStrings on QTYPE
| lookup rcodeStrings on RCODE
| extend Protocol = iff(TCP==0, "UDP", "TCP")
| extend QTYPE = iff(isnotempty(QTYPESTR), strcat(QTYPESTR, " (", QTYPE, ")"), tostring(QTYPE))
| extend RCODE = iff(isnotempty(RCODESTR), strcat(RCODESTR, " (", RCODE, ")"), tostring(RCODE))
| project PreciseTimeStamp, QueryResult = KeywordName, Protocol, QTYPE, QNAME, RCODE, ElapsedTimeMs = ElapsedTime
| sort by PreciseTimeStamp desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---
