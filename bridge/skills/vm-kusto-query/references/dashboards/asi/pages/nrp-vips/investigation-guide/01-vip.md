# VIP

> Source: **NRP - NRP VIPs** dashboard, chapter **VIP** (7 queries across 7 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Offline Task (vipmanager) vs Sync (svimanager) Release

### VIP Release Offline vs Sync

_Widget purpose:_ Offline Task (vipmanager) vs Sync (svimanager) Release

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP > Offline Task (vipmanager) vs Sync (svimanager) Release`

```kusto
let allocatedIps =FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where Message startswith "Offline tasks persisted for release of VipAllocation with id "
| extend ReleaseType="Offline Task"
| summarize count() by ReleaseType
;
let reservedIps = FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where Message startswith "Released ipaddress "
| extend ReleaseType="Synchronous"
| summarize count() by ReleaseType
| union allocatedIps
;
let totalCount= toscalar(
reservedIps
| summarize sum(count_))
;
reservedIps
| extend percentTotal = count_*100/totalCount
;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `Message startswith "Offline tasks persisted for release of VipAllocation with id "` · `Message startswith "Released ipaddress "`

---

## Put/Delete Public IP +VIP Related QOS Errors

### VIP QOS Errors

_Widget purpose:_ Put/Delete Public IP +VIP Related QOS Errors

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP > Put/Delete Public IP +VIP Related QOS Errors`

```kusto
QosEtwEvent 
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where OperationName == "PutPublicIpAddressOperation"  or OperationName == "DeletePublicIpAddressOperation" 
    or ErrorDetails contains "TransferFastPathPublicIPAddresses" 
    or ErrorDetails contains "TransferVipResourceIpAndPollForCompletionAsync" 
    or ErrorDetails contains "VipAllocationToTr|ansfer" 
    or ErrorDetails contains "AllocatePublicIpAndPersistIfRequired" 
    or ErrorDetails contains "ReleasePublicIPAllocationOfflineAsync" 
   // or ErrorDetails contains "AllocateVipPrefixInRNM" 
   // or ErrorDetails contains "ReleaseVipAllocationPrefixAsync" 
    or ErrorDetails contains "ReleasePublicIpAsync"
    or ErrorDetails contains "ReservePublicIpAsync"
| where Success == false 
| where UserError == false 
| extend containsParentOperation = ParentOperationId != "" 
| where ErrorDetails !contains "FabricNotPrimaryException"  
    and ErrorCode != "TaskCanceled"  
    and ErrorCode != "PrimaryFailover"  
    and ErrorDetails !startswith "System.OperationCanceledException: "  
    and ErrorDetails !startswith "Microsoft.WindowsAzure.Networking.Nrp.Frontend.Common.NrpException: Primay role " 
    and ErrorDetails !startswith "System.Fabric.FabricTransientException: The operation failed because this replica set is currently reconfiguring."
| extend errorType = case( 
    ErrorDetails contains "There is no more VipAllocationService Uri with the current VIpClassification to try but still cannot allocate Vip address.", "Unable To Allocate", 
    ErrorDetails contains "Microsoft.Windows.Azure.Networking.Dns.Common.DnsResolver.DnsQueryException: Failed to query the DNS server at ''", "DNS Failed To Query The Server", 
    ErrorDetails contains "System.ArgumentException: vipTags must not be specified along with vipPrefixAllocationId", "VIP With Prefix Not Released In Time", 
    ErrorDetails contains "System.Net.WebException: Unable to connect to the remote server ---> System.Net.Sockets." and ErrorDetails contains "DNS Facade", "dnsSocketException", 
    ErrorDetails contains "Vip reservation already exists for specified IPAddress" and ErrorDetails contains "TransferVipReservationAsync", "Reservation Already Exists For Transfer Api", 
    ErrorDetails contains "Error in CreateOrUpdateSlbServiceAsync :", "SLB Update Error", 
    ErrorDetails contains "SlbFacade.<DeleteSlbServiceAsync>", "SLB Delete Error", 
    ErrorDetails contains "This resource reference is a stub." and ErrorDetails contains "prefixes/" and ErrorDetails contains "TransferVipResourceIpAndPollForCompletionAsync", "Transfer Api Null Ref For PublicIP Prefix", 
    ErrorDetails contains "No range found that can satisfy the allocation request." and ErrorDetails contains "AllocateVipsInternal", "Vip Allocation No Range Found Error", // why would we get this error if we have already gone to that vipManager? Race condition? 
    ErrorDetails contains "Parameter name: vipAddress ---> System.ServiceModel.FaultException`1[Microsoft.WindowsAzure.Networking.Rnm.Contracts.Faults.VipManagementFault]: Value cannot be null.", "Vip Reservation Ip Address Value Is Null", 
    "Other" 
) 
| where ClientAppId !in ("a43ddf50-441a-442c-8e60-c423ceae1595","237794b4-a7ac-4073-96c6-38f0cfddd8cf","093a0dd8-9cae-4e29-a1c4-c2dc47bd2508","f81873a0-342e-4769-a266-7159ac4e8cd4") // client app id excluded
// | project Region,ErrorCode, ErrorDetails, containsParentOperation, OperationName, SourceAssemblyFileVersion, SubscriptionId, OperationId, ClientAppId
| summarize count(), make_set(ErrorDetails), make_set(Region), ReleaseBuilds = make_set(ReleaseBuild((SourceAssemblyFileVersion))) by errorType, containsParentOperation, OperationName
| summarize by count_, errorType, OperationName, containsParentOperation, Regions = tostring(set_Region), ReleaseBuilds = tostring(ReleaseBuilds), ExampleError = substring(tostring(set_ErrorDetails[0]), 0, 500)
| sort by count_ desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `OperationName == "PutPublicIpAddressOperation"`

---

## Put/Delete Public IP Operation Health

### Put/Delete Public IP Health

_Widget purpose:_ Put/Delete Public IP Operation Health

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `VIP > Put/Delete Public IP Operation Health`

```kusto
QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where OperationName == "PutPublicIpAddressOperation" or OperationName == "DeletePublicIpAddressOperation"
| where UserError == false
| summarize SuccessRate = 100.0 * countif(Success == true) / count() by bin(PreciseTimeStamp, 1d)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `OperationName == "PutPublicIpAddressOperation"`

---

## Total VIP Allocation/Reservation Count (within region)

### VipAllocations Count

_Widget purpose:_ Total VIP Allocation/Reservation Count (within region)

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP > Total VIP Allocation/Reservation Count (within region)`

```kusto
let allocatedIps =FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where EventCode == "PublicIpAllocated"
| extend allocationType="vipManager"
| summarize count() by allocationType
;
let reservedIps = FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where Message startswith "Reserved ipaddress "
| extend allocationType="sviManager"
| summarize count() by allocationType
| union allocatedIps
;
let totalCount= toscalar(
reservedIps
| summarize sum(count_))
;
reservedIps
| extend percentTotal = count_*100/totalCount
;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`, `{querySubscription}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `EventCode == "PublicIpAllocated"` · `Message startswith "Reserved ipaddress "`

---

## VIP Allocate/Release Trends

### VIP Allocate/Release Trends

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `VIP > VIP Allocate/Release Trends`

```kusto
VipLifeCycleEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| extend TransactionType = iff(TransactionType in ("Allocation","Reservation","Alloction"), "Allocation", "Release")
| summarize count() by bin(TIMESTAMP, 1d), TransactionType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"`

---

## Vip Allocation vs Reservation Performance

### VipAllocation Perf

_Widget purpose:_ Vip Allocation vs Reservation Performance

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP > Vip Allocation vs Reservation Performance`

```kusto
let allocatedIps =FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "PutPublicIpAddressOperation" 
| where EventCode == "PublicIpAllocated"
| take 10000
| summarize make_set(OperationId);
let allocated=QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where Success == true
| where OperationName == "PutPublicIpAddressOperation"
| where OperationId in (allocatedIps)
| extend allocationType="vipManager"
| summarize dcount(OperationId), max(DurationInMilliseconds), avg(DurationInMilliseconds), percentiles(DurationInMilliseconds, 50, 75, 90, 99.9) by allocationType
;
let reservedIps = FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "PutPublicIpAddressOperation" 
| where Message startswith "Reserved ipaddress "
| take 10000
| summarize make_set(OperationId);
let reserved=QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where Success == true
| where OperationName == "PutPublicIpAddressOperation"
| where OperationId in (reservedIps)
| extend allocationType="sviManager"
| summarize dcount(OperationId), max(DurationInMilliseconds), avg(DurationInMilliseconds), percentiles(DurationInMilliseconds, 50, 75, 90, 99.9) by allocationType
| union allocated
;
reserved;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`, `{querySubscription}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `OperationName == "PutPublicIpAddressOperation"` · `EventCode == "PublicIpAllocated"` · `Message startswith "Reserved ipaddress "`

---

## VIP Transfer Count by Operation

### Transfer Count

_Widget purpose:_ VIP Transfer Count by Operation

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP > VIP Transfer Count by Operation`

```kusto
let transferredIps =FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where Message startswith "PublicIp Transfer Reservation SUCCESS for subscriptionId: "
| summarize count() by OperationName
;transferredIps
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `Message startswith "PublicIp Transfer Reservation SUCCESS for subscriptionId: "`

---
