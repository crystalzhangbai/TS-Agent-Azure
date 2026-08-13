# VIP Prefix

> Source: **NRP - NRP VIPs** dashboard, chapter **VIP Prefix** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## All Regions with VIP Prefix Allocation 

### prefix allocated count

_Widget purpose:_ All Regions with VIP Prefix Allocation 

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP Prefix > All Regions with VIP Prefix Allocation `

```kusto
let allocatedIps =FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where SliceNum(SourceAssemblyFileVersion) < 10
| where OperationName == "PutPublicIpPrefixOperation" 
| where Message startswith "Allocating public ip prefix for"
| extend allocationType="vipManager"
| summarize count() by Region, Release=ReleaseBuild(SourceAssemblyFileVersion, IgnoreBuild=true)
;
allocatedIps
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `OperationName == "PutPublicIpPrefixOperation"` · `Message startswith "Allocating public ip prefix for"`

---

## Put/Delete PIP Prefix Qos Errors

### Put/Delete Public IP Prefix QOS Errors

_Widget purpose:_ Put/Delete PIP Prefix Qos Errors

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `VIP Prefix > Put/Delete PIP Prefix Qos Errors`

```kusto
QosEtwEvent 
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where OperationName == "PutPublicIpPrefixOperation"  or OperationName == "DeletePublicIpPrefixOperation" 
| where Success == false 
| where UserError == false 
| where ErrorDetails !contains "FabricNotPrimaryException"  
    and ErrorCode != "TaskCanceled"  
    and ErrorCode != "PrimaryFailover"  
    and ErrorDetails !startswith "System.OperationCanceledException: "  
    and ErrorDetails !startswith "Microsoft.WindowsAzure.Networking.Nrp.Frontend.Common.NrpException: Primay role " 
    and ErrorDetails !startswith "System.Fabric.FabricTransientException: The operation failed because this replica set is currently reconfiguring."
| extend errorType = case( 
    ErrorDetails contains "System.InvalidOperationException: RNM returned an error when trying to release public ip prefix with unexpected exception: System.InvalidOperationException: Reserved PublicIp Prefix release timed out for reservationId:", "Reservation Release in RNM Timed Out",
    "Other"
    )
| summarize count(), make_set(ErrorDetails), make_set(Region), ReleaseBuilds = make_set(ReleaseBuild((SourceAssemblyFileVersion))) by errorType, OperationName
| summarize by count_, errorType, OperationName, Regions = tostring(set_Region), ReleaseBuilds = tostring(ReleaseBuilds), ExampleError = substring(tostring(set_ErrorDetails[0]), 0, 500)
| sort by count_ desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `OperationName == "PutPublicIpPrefixOperation"`

---
