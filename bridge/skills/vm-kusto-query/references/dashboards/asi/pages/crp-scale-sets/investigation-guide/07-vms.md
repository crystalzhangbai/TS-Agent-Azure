# VMs

> Source: **CRP — Scale Sets** dashboard, chapter **VMs** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Instance Details

### Query VMSS Instance from BI

_Widget purpose:_ Sale Set Instances

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `VMs > Instance Details > Sale Set Instances`

```kusto
cluster("azcrpbifollower").database("bi_allprod").VMScaleSetVMInstance
| where PreciseTimeStamp between (queryFrom .. queryTo) and ResourceGroupName =~ queryResourceGroup
| where VMScaleSetName  =~ queryVmssName and SubscriptionId == querySubscriptionId
| summarize lastSeen = arg_max(PreciseTimeStamp, *) by InstanceIdString = tolong(InstanceIdString)
| order by InstanceIdString asc
| project-reorder VMScaleSetName, VMScaleSetVMInstanceId
| join kind=leftouter (
    cluster("azcrpbifollower").database("bi_allprod").VMAllocationInfo
    | where PreciseTimeStamp between (queryFrom .. queryTo) and ResourceGroupName =~ queryResourceGroup
    | where SubscriptionId == querySubscriptionId
    | parse-where kind=regex flags=i VMName with "_" VMScaleSetName "_" InstanceId:long
    | where VMScaleSetName =~ queryVmssName
    | summarize lastSeen = arg_max(PreciseTimeStamp, *) by InstanceId
) on $left.InstanceIdString == $right.InstanceId
| project-away *1
| order by InstanceId asc
| extend level = iff(State =~ 'failed' or IsGuestOSProvisioned !~ "True", 'error', '')
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroup}`, `{queryVmssName}`, `{queryFrom}`, `{queryTo}`

---

## Instance Health

### Scaleset instance health

_Widget purpose:_ Instance Health

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Timeline`
Source panel: `VMs > Instance Health > Instance Health`

```kusto
cluster("azcrpbifollower").database("bi_allprod").VMAllocationInfo
| where PreciseTimeStamp between (qFrom .. qTo)
| where ResourceGroupName =~ qRG and SubscriptionId == qSub 
| parse-where kind=regex flags=i VMName with "_" VMScaleSetName "_" InstanceId:long
| where VMScaleSetName =~ qVMSS
| project StartTime = PreciseTimeStamp, VMName, InstanceId, Content = State, IsGuestOSProvisioned
| order by InstanceId asc, StartTime asc 
| serialize 
| where (VMName != prev(VMName) 
    or VMName != next(VMName)) or (Content != prev(Content) or Content != next(Content)) 
    or (IsGuestOSProvisioned != prev(IsGuestOSProvisioned) or IsGuestOSProvisioned != next(IsGuestOSProvisioned)) 
| extend EndTime = next(StartTime)
| where VMName != prev(VMName) 
    or Content != prev(Content) 
    or IsGuestOSProvisioned != prev(IsGuestOSProvisioned)
| extend 
    GroupBy = VMName, 
    Health = iff(Content == 'Failed' or IsGuestOSProvisioned != 'True', 'error', 'healthy'),
    Tooltip = strcat("IsGuestOSProvisioned: ", IsGuestOSProvisioned)
```

**Params:** `{qFrom}`, `{qTo}`, `{qSub}`, `{qRG}`, `{qVMSS}`

---
