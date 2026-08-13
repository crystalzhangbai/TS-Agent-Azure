# VM Stats

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **VM Stats** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VM Shoebox Counters Stats

### Azure Host Subscription VM Shoebox Counter Stats

_Widget purpose:_ VM Shoebox Counters Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Stats > VM Shoebox Counters Stats`

```kusto
VmShoeboxCounterTable
| where subscriptionId == subId and PreciseTimeStamp between (startTime .. endTime) 
        and MDMCounterName startswith "VM "
| summarize TotalVMs = dcount(VmId), VMs_doingMax = dcountif(VmId, MaxValueInaMinute >= 95 or MaxValueInaMinute >= 95) by MDMCounterName
| sort by VMs_doingMax desc
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---

## VMs that are doing more than 95% (in the time period selected)

### Azure Host Subscription VM Shoebox Top VMs doing Max

_Widget purpose:_ VMs that are doing more than 95% (in the time period selected)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Stats > VMs that are doing more than 95% (in the time period selected)`

```kusto
VmShoeboxCounterTable
| where subscriptionId == subId and PreciseTimeStamp between (startTime .. endTime) 
        and MDMCounterName startswith "VM "
        and (MaxValueInaMinute >= 95)
| summarize Count_of_30Min_Windows_Max = countif(MaxValueInaMinute >= 95) by MDMCounterName, ArmId, VmId, VMUniqueId
| sort by Count_of_30Min_Windows_Max desc
//| join kind=inner (
//    cluster('AzureCM').database('AzureCM').LogContainerSnapshot
//    | where PreciseTimeStamp between (startTime .. endTime) and subscriptionId == subId
//    | distinct virtualMachineUniqueId, containerType
//) on $left.VMUniqueId == $right.virtualMachineUniqueId
//| sort by Count_of_30Min_Windows_Max desc
//| project-away virtualMachineUniqueId, VMUniqueId
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---
