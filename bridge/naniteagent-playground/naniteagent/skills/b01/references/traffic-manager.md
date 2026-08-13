---
description: KQL queries for Azure Traffic Manager — profile/endpoint inventory, health state changes, DNS query analytics, probe errors, frontend logs, and performance heat maps.
---

# Traffic Manager Kusto Queries

> **Source:** Azure Traffic Manager Monitoring Cluster  
> **Cluster:** `cluster('aztmmon.kusto.windows.net')`  
> **Database:** `aztmmondb`

---

## Data Source Reference

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `Facts` | Master snapshot of all TM resource records (profiles, subscriptions, endpoints, zones) | `SubscriptionId`, `ProfileId`, `DomainName`, `RecordType`, `State`, `IsDeleted`, `PolicyData` |
| `FactsProfiles` | Normalized view of TM profile configurations | `SubscriptionId`, `DomainName`, `LoadBalancingMethod`, `TtlSeconds`, `ProbeScheme`, `ProbePort`, `ProbeMethod`, `ProbeIntervalMilliseconds`, `TrafficViewEnabled` |
| `FactsEndpoints` | Per-endpoint configuration snapshot | `SubscriptionId`, `DomainName`, `EndpointName`, `EndpointType`, `EndpointTarget`, `RunningStatus`, `Weight`, `EndpointLocation`, `TargetResourceId` |
| `FactsSubscriptions` | Per-subscription TM quota and state | `SubscriptionId`, `ProfileCount`, `DefinitionCount`, `MaxNumberProfilesAllowed`, `State`, `EnabledForRescue` |
| `FactsPerformanceProfiles` | Performance-routing profile configurations (mirrors FactsProfiles for performance method) | Same schema as `FactsProfiles` |
| `ProdHealthChanges` | Real-time health state transitions (prod) — endpoint goes Online/Degraded/Disabled | `ProfileDomainName`, `EndpointName`, `Status`, `Protocol`, `EventName`, `SubscriptionId`, `ProfileId` |
| `PrevHealthChanges` | Health state transitions for Preview environment | Same schema as `ProdHealthChanges` |
| `FFHealthChanges` | Health state transitions for FairFax (Gov) environment | Same schema as `ProdHealthChanges` |
| `MCHealthChanges` | Health state transitions for Mooncake (China) environment | Same schema as `ProdHealthChanges` |
| `DnsQuery15MinSummary` | 15-min aggregated DNS query counts by subscription/profile/response code | `SubscriptionId`, `QueryDomainName`, `ParentDomainName`, `Response`, `QueryCount`, `SourceSubnet`, `Time` |
| `DnsDailySummary` | Daily aggregated DNS queries per profile | `SubscriptionId`, `QueryDomainName`, `Response`, `QueryCount`, `SourceSubnet` |
| `HeatMap15Mins` | 15-min traffic heat map — client geo, latency, endpoint routing | `QuerySubscriptionId`, `QueryProfileName`, `EndpointResourceId`, `SourceSubnet`, `QueryCount`, `Country`, `State`, `Latency`, `StartTime` |
| `HeatMapLatency` | Reference latency per LDNS prefix to Azure region | `ldnsPrefix`, `region`, `latency` |
| `ProbeErrorReasons` | Lookup table: probe error codes → human-readable cause | `ErrorCodeOrMessage`, `Cause` |
| `ProdFrontendLogs` | ARM/frontend API request logs for TM control plane | `SubscriptionId`, `OperationName`, `DomainName`, `ProfileName`, `ProfileId`, `ClientRequestId`, `OperationId`, `Message`, `EventCode`, `ApiVersion`, `TIMESTAMP` |
| `PreProdFrontendLogs` | Control plane logs for PreProd environment | Same schema as `ProdFrontendLogs` |

---

## Queries

### 1. Look Up a Traffic Manager Profile by Domain or SubscriptionId

```kql
// Find TM profile configuration — use DomainName (e.g. myprofile.trafficmanager.net) or SubscriptionId
cluster('aztmmon.kusto.windows.net').database('aztmmondb').FactsProfiles
| where SubscriptionId == "<SubscriptionId>"                 // filter by subscription
// | where DomainName contains "<profile-name>"              // OR filter by domain name
| where IsDeleted == false
| project SubscriptionId, ResourceGroup, ProfileName, DomainName,
          LoadBalancingMethod, TtlSeconds, ProbeScheme, ProbePort,
          ProbeMethod, ProbeRequestUri, ProbeIntervalMilliseconds,
          ProbeTimeoutMilliseconds, ProbeMaxRetryTimes,
          TrafficViewEnabled, CreationTimestamp, LastChangeNumber
| order by CreationTimestamp desc
```

> **See also:** Query 9 for the full raw `RecordData`/`PolicyData` blob. Query 10 for a combined view with ARM `ResourceUri`.

---

### 2. List All Endpoints for a Profile

```kql
cluster('aztmmon.kusto.windows.net').database('aztmmondb').FactsEndpoints
| where SubscriptionId == "<SubscriptionId>"
| where DomainName contains "<profile-name>"                 // e.g. "myprofile.trafficmanager.net"
| project SubscriptionId, ResourceGroup, DomainName, EndpointName,
          EndpointType, EndpointTarget, RunningStatus,
          Weight, EndpointLocation, EndpointBillingType, TargetResourceId
| order by EndpointType asc, EndpointName asc
```

---

### 3. Endpoint Health State Changes (Production) — Key for Degraded/Offline Incidents

```kql
let starttime = datetime(<start>);
let endtime   = datetime(<end>);
cluster('aztmmon.kusto.windows.net').database('aztmmondb').ProdHealthChanges
| where TIMESTAMP between (starttime .. endtime)
| where SubscriptionId == "<SubscriptionId>"
// | where ProfileDomainName contains "<profile-name>"      // narrow to a profile
// | where EndpointName == "<endpoint>"                     // narrow to a specific endpoint
| project TIMESTAMP, ProfileDomainName, EndpointName, Status,
          Protocol, EventName, EventSource, EventCode, Message, SubscriptionId
| order by TIMESTAMP desc
```

> **Tip:** `Status` values are `Online`, `Degraded`, `Disabled`, `CheckingEndpoint`.  
> Use `PrevHealthChanges`, `FFHealthChanges`, or `MCHealthChanges` for non-Production environments.

---

### 4. DNS Query Volume and Failures — 15-Min Buckets for a Profile

```kql
let starttime = datetime(<start>);
let endtime   = datetime(<end>);
cluster('aztmmon.kusto.windows.net').database('aztmmondb').DnsQuery15MinSummary
| where Time between (starttime .. endtime)
| where SubscriptionId == "<SubscriptionId>"
| where QueryDomainName contains "<profile-name>"           // e.g. "myprofile.trafficmanager.net"
// | where Response != "NOERROR"                            // uncomment to filter failure responses only (NXDOMAIN, SERVFAIL, REFUSED, etc.)
| summarize TotalQueries = sum(QueryCount) by bin(Time, 15m), Response, QueryDomainName
| order by Time asc
```

---

### 5. Traffic Heat Map — Client Geography and Latency

```kql
let starttime = datetime(<start>);
let endtime   = datetime(<end>);
cluster('aztmmon.kusto.windows.net').database('aztmmondb').HeatMap15Mins
| where StartTime between (starttime .. endtime)
| where QuerySubscriptionId == "<SubscriptionId>"
| where QueryProfileName contains "<profile-name>"
| summarize TotalQueries = sum(QueryCount), AvgLatency = avg(Latency)
    by Country, State, EndpointResourceId, bin(StartTime, 15m)
| order by TotalQueries desc
```

---

### 6. Probe Error Reason Lookup

```kql
// Map a probe error code to a human-readable cause
cluster('aztmmon.kusto.windows.net').database('aztmmondb').ProbeErrorReasons
| where ErrorCodeOrMessage contains "<error-code-or-message>"
| project ErrorCodeOrMessage, Cause
```

---

### 7. Control Plane Operation Logs — ARM API calls against a Profile

```kql
let starttime = datetime(<start>);
let endtime   = datetime(<end>);
cluster('aztmmon.kusto.windows.net').database('aztmmondb').ProdFrontendLogs
| where TIMESTAMP between (starttime .. endtime)
| where RequestSubscriptionId == "<SubscriptionId>"
// | where ProfileName contains "<profile-name>"            // narrow to a profile
// | where OperationName contains "PUT" or OperationName contains "DELETE"
| project TIMESTAMP, OperationName, ProfileName, DomainName,
          ResourceGroupName, ApiVersion,
          ClientRequestId, OperationId,
          EventCode, Message
| order by TIMESTAMP desc
```

---

### 8. Subscription Quota and State Check

```kql
cluster('aztmmon.kusto.windows.net').database('aztmmondb').FactsSubscriptions
| where SubscriptionId == "<SubscriptionId>"
| project SubscriptionId, ResourceGroup, DomainName,
          ProfileCount, MaxNumberProfilesAllowed,
          DefinitionCount, MaxNumberDefinitionsAllowed,
          State, EnabledForRescue, AADTenantId
```

---

### 9. Raw Facts Record for a Profile (Full Policy Data)

```kql
// Use when you need the raw serialized profile or endpoint record
// See Query 1 (FactsProfiles) for a normalized config view. See Query 10 for RecordData + ARM ResourceUri combined.
cluster('aztmmon.kusto.windows.net').database('aztmmondb').Facts
| where SubscriptionId == "<SubscriptionId>"
| where DomainName contains "<profile-name>"
| where IsDeleted == false
| project Timestamp, RecordType, DomainName, ProfileId, SubscriptionId,
          ResourceGroup, State, Version, ActiveVersion,
          LastChangeNumber, RecordData, PolicyData
| order by Timestamp desc
```

---

### 10. Translate Domain Name → Combined Profile Config + ARM Resource URI

> Joins `Facts` (latest raw policy + `ChangeTimestamp`) with `FactsProfiles` (normalized config) on `DomainName`.  
> Unique value over Query 1: ARM `ResourceUri`, raw `RecordData`, and `ChangeTimestamp` from `Facts`.  
> `LoadBalancingMethod` is taken directly from `FactsProfiles` — no manual decode needed.  
> **See also:** Query 1 for a simpler normalized lookup. Query 9 for raw `PolicyData` only.

```kql
let DomainName_ = "<profile-domain>";   // e.g. myprofile.trafficmanager.net
cluster('aztmmon.kusto.windows.net').database('aztmmondb').Facts
| where DomainName =~ DomainName_
| where isnotempty(RecordData) and IsDeleted != true
| extend IngestionTime = ingestion_time()
| project-reorder IngestionTime
| project-rename ChangeTimestamp = Timestamp
| summarize arg_max(IngestionTime, *) by SubscriptionId, ResourceGroup, ProfileName, DomainName
| extend ResourceUri = strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroup, "/providers/Microsoft.Network/trafficmanagerprofiles/", ProfileName)
| join kind=leftouter (
    cluster('aztmmon.kusto.windows.net').database('aztmmondb').FactsProfiles
    | where DomainName =~ DomainName_
    | summarize arg_max(Timestamp = ingestion_time(), *) by DomainName
    | project DomainName, LoadBalancingMethod, TtlSeconds, TrafficViewEnabled,
              ProbeScheme, ProbePort, ProbeMethod, ProbeIntervalMilliseconds
) on $left.DomainName == $right.DomainName
| project
    IngestionTime,
    CreationTimestamp,
    ChangeTimestamp,
    SubscriptionId,
    ResourceGroup,
    ProfileName,
    DomainName,
    ResourceUri,
    LoadBalancingMethod,        // from FactsProfiles (already a string — no manual decode needed)
    TtlSeconds,
    TrafficViewEnabled,
    ProbeScheme,
    ProbePort,
    ProbeMethod,
    ProbeIntervalMilliseconds,
    RecordData                  // raw JSON blob — see Query 9 for full PolicyData
```

---

## Dashboard Links

### Jarvis Dashboard - ATM Customer Shoebox

> **Purpose:** End-to-end Traffic Manager monitoring dashboard — DNS query volume, endpoint health, probe results, and routing decisions for a specific profile.  
> **Host:** `portal.microsoftgeneva.com`  
> **Required parameter:** `ResourceId` — the full ARM Resource URI of the TM profile (URL-encoded)  
> **Time parameters:** `globalStartTime` / `globalEndTime` — Unix epoch **milliseconds** (not ISO 8601)

#### URL Template

```
https://portal.microsoftgeneva.com/dashboard/TrafficManager/Customer%2520Shoebox?overrides=[{%22query%22:%22//*[id=%27EndpointName%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id=%27ResourceId%27]%22,%22key%22:%22value%22,%22replacement%22:%22{ResourceId_UrlEncoded}%22}]&globalStartTime={StartTimeUnixMs}&globalEndTime={EndTimeUnixMs}&pinGlobalTimeRange=true
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `{ResourceId_UrlEncoded}` | ARM Resource URI of the TM profile, URL-encoded (`/` → `%2F`) | `%2Fsubscriptions%2F<subId>%2FresourceGroups%2F<rg>%2Fproviders%2FMicrosoft.Network%2Ftrafficmanagerprofiles%2F<profileName>` |
| `{StartTimeUnixMs}` | Start of time window in Unix epoch milliseconds | `1774768058805` |
| `{EndTimeUnixMs}` | End of time window in Unix epoch milliseconds | `1777360058805` |

#### How to Generate the Link (PowerShell)

```powershell
# Set the ARM Resource URI of the TM profile
$resourceUri = "/subscriptions/<SubscriptionId>/resourceGroups/<ResourceGroup>/providers/Microsoft.Network/trafficmanagerprofiles/<ProfileName>"

# URL-encode the resource URI
$resourceIdEncoded = [Uri]::EscapeDataString($resourceUri)

# Set time range (last 30 days by default)
$endMs   = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$startMs = [DateTimeOffset]::UtcNow.AddDays(-30).ToUnixTimeMilliseconds()

# Build the dashboard URL
$url = "https://portal.microsoftgeneva.com/dashboard/TrafficManager/Customer%2520Shoebox?overrides=[{%22query%22:%22//*[id=%27EndpointName%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id=%27ResourceId%27]%22,%22key%22:%22value%22,%22replacement%22:%22$resourceIdEncoded%22}]&globalStartTime=$startMs&globalEndTime=$endMs&pinGlobalTimeRange=true"

# Open in Edge
Start-Process "msedge.exe" -ArgumentList $url
```

> **Tips:**
> - Get `ResourceUri` from Query 10 (`Facts` + `FactsProfiles` join) — the `ResourceUri` column is already the correct ARM URI.
> - `EndpointName` override is left empty to show **all endpoints** in the dashboard.
> - To filter to a specific endpoint, replace `%22%22` in the `EndpointName` override with the URL-encoded endpoint name.
> - Use `[DateTimeOffset]::UtcNow.AddDays(-N).ToUnixTimeMilliseconds()` to adjust the lookback window.

### Geneva DGrep Log — EndpointProbeResultsEtwEvent

> **Purpose:** View raw endpoint probe results (probe status, error codes, timestamps) for a specific Traffic Manager profile.  
> **Host:** `portal.microsoftgeneva.com`  
> **Namespace:** `Watm` | **Event:** `EndpointProbeResultsEtwEvent`  
> **Required parameter:** `{fqdn}` — the Traffic Manager profile FQDN (e.g. `<profilename>.trafficmanager.net`)  
> **Time parameter:** `{EndTimeUTC}` — UTC datetime in `yyyy-MM-ddTHH:mm:ss` format; `offset=~60` means look back 60 minutes from this time

#### URL Template

```
https://portal.microsoftgeneva.com/logs/dgrep?page=logs&be=DGrep&offset=~60&time={EndTimeUTC}&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=Watm&en=EndpointProbeResultsEtwEvent&conditions=[[%22ProfileDomainName%22,%22%3D%3D%22,%22{fqdn}%22]]&clientQuery=orderby%20PreciseTimeStamp%20desc&chartEditorVisible=true&chartType=Line&chartLayers=[[%22New%20Layer%22,%22%22]]
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `{EndTimeUTC}` | End of query window in UTC, format `yyyy-MM-ddTHH:mm:ss` | `2026-04-28T07:15:41` |
| `{fqdn}` | Full TM profile FQDN (URL-encoded in the link) | `a55145055d09411db9da89f2ee1f2de6.trafficmanager.net` |

#### How to Generate the Link (PowerShell)

```powershell
$fqdn       = "<profilename>.trafficmanager.net"
$endTimeUTC = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss")
$fqdnEncoded = [Uri]::EscapeDataString($fqdn)

$url = "https://portal.microsoftgeneva.com/logs/dgrep?page=logs&be=DGrep&offset=~60&time=$endTimeUTC&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=Watm&en=EndpointProbeResultsEtwEvent&conditions=[[%22ProfileDomainName%22,%22%3D%3D%22,%22$fqdnEncoded%22]]&clientQuery=orderby%20PreciseTimeStamp%20desc&chartEditorVisible=true&chartType=Line&chartLayers=[[%22New%20Layer%22,%22%22]]"

Start-Process "msedge.exe" -ArgumentList $url
```

> **Tips:**
> - `offset=~60` shows the 60 minutes **before** `{EndTimeUTC}`. Change to `~1440` for last 24 hours.
> - Get the FQDN from `FactsProfiles.DomainName` (Query 1) or from the profile name + `.trafficmanager.net`.
> - Use alongside Query 3 / Query 6 to correlate probe errors seen in Kusto with raw Geneva log entries.

### Geneva DGrep Log — TrafficManagerDnsQueryEvent

> **Purpose:** View raw DNS query events resolved by Traffic Manager — client IPs, LDNS IPs, and response types for a specific profile FQDN.  
> **Host:** `portal.microsoftgeneva.com`  
> **Namespace:** `EdgeDns` | **Event:** `TrafficManagerDnsQueryEvent`  
> **Required parameter:** `{fqdn}` — the Traffic Manager profile FQDN (e.g. `<profilename>.trafficmanager.net`)  
> **Time parameter:** `{EndTimeUTC}` — UTC datetime in `yyyy-MM-ddTHH:mm:ss` format; `offset=-15` means look back 15 minutes from this time

#### URL Template

> Note: The `conditions`, `aggregates`, and `chartLayers` parameter values below are already URL-encoded for direct copy/paste use. Keep them URL-encoded in the final link when replacing `{fqdn}` and `{EndTimeUTC}`.

```
https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time={EndTimeUTC}&offset=-15&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=EdgeDns&en=TrafficManagerDnsQueryEvent&conditions=%5B%5B%22Query%22%2C%22contains%22%2C%22{fqdn}%22%5D%5D&kqlClientQuery=source&aggregates=%5B%22Count%20by%20ClientIp%22%2C%22Count%20by%20LdnsIp%22%2C%22Count%20by%20CompleteResponse%22%5D&chartEditorVisible=true&chartType=line&chartLayers=%5B%5B%22New%20Layer%22%2C%22%22%5D%5D
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `{EndTimeUTC}` | End of query window in UTC, format `yyyy-MM-ddTHH:mm:ss` | `2026-04-28T07:21:13` |
| `{fqdn}` | Full TM profile FQDN | `a55145055d09411db9da89f2ee1f2de6.trafficmanager.net` |

#### How to Generate the Link (PowerShell)

```powershell
$fqdn        = "<profilename>.trafficmanager.net"
$endTimeUTC  = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss")
$fqdnEncoded = [Uri]::EscapeDataString($fqdn)

$conditions   = "[[`"Query`",`"contains`",`"$fqdnEncoded`"]]"
$aggregates   = "[`"Count by ClientIp`",`"Count by LdnsIp`",`"Count by CompleteResponse`"]"
$chartLayers  = "[[`"New Layer`",`"`"]]"

$conditionsEncoded  = [Uri]::EscapeDataString($conditions)
$aggregatesEncoded  = [Uri]::EscapeDataString($aggregates)
$chartLayersEncoded = [Uri]::EscapeDataString($chartLayers)

$url = "https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=$endTimeUTC&offset=-15&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=EdgeDns&en=TrafficManagerDnsQueryEvent&conditions=$conditionsEncoded&kqlClientQuery=source&aggregates=$aggregatesEncoded&chartEditorVisible=true&chartType=line&chartLayers=$chartLayersEncoded"

Start-Process "msedge.exe" -ArgumentList $url
```

> **Tips:**
> - `offset=-15` shows the 15 minutes **before** `{EndTimeUTC}`. Change to `-1440` for last 24 hours.
> - Aggregates break down DNS queries by `ClientIp`, `LdnsIp`, and `CompleteResponse` for quick traffic distribution analysis.
> - Use alongside Query 4 (`DnsQuery15MinSummary`) to correlate DNS volume trends seen in Kusto with raw Geneva log entries.

---

## Common Investigation Scenarios

### A. Profile shows Degraded — endpoint health incident

1. Run **Query 10** to get the ARM `ResourceUri` — use it to open the **ATM Jarvis Customer Shoebox Dashboard** (see Dashboard Links section) for a visual overview.
2. Run **Query 1** to confirm profile configuration (routing method, probe settings).
3. Run **Query 2** to list all endpoints and their `RunningStatus`.
4. Run **Query 3** (`ProdHealthChanges`) scoped to the incident window to find which endpoints changed state and when.
5. Cross-reference `Protocol`, `EventCode`, and `Message` with `ProbeErrorReasons` (**Query 6**) to identify the probe failure root cause.

### B. No DNS responses / users cannot resolve profile

1. Run **Query 4** (`DnsQuery15MinSummary`) to confirm traffic drop.
2. Re-run **Query 4** with the `Response != "NOERROR"` filter uncommented to check for NXDOMAIN or SERVFAIL responses.
3. Run **Query 8** (`FactsSubscriptions`) to verify subscription `State` is not `Suspended` or `Disabled`.
4. Run **Query 1** (`FactsProfiles`) to verify `IsDeleted == false` and profile is active.

### C. Unexpected endpoint receiving traffic (performance routing)

1. Run **Query 5** (`HeatMap15Mins`) to see geo-distribution and which `EndpointResourceId` is receiving traffic by region.
2. Cross-reference with `HeatMapLatency` to verify latency-based routing decisions are expected for the client's LDNS prefix.

### D. Recent control plane change caused issue

1. Run **Query 7** (`ProdFrontendLogs`) filtered to the incident window and narrow by `PUT`/`DELETE` operations to find who changed the profile and when.
2. Correlate with `LastChangeNumber` in `FactsProfiles` (**Query 1**) and `Facts` (**Query 9**).
