# Disks from CRP BI

> Source: **CRP — VMs** dashboard, chapter **Disks from CRP BI** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query VMManagedDisksAllocationInfo

_Widget purpose:_ Disks from CRP BI

Cluster: `Azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `Disks from CRP BI`

```kusto
let crpDisks = VMManagedDisksAllocationInfo
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where VMId == queryVMId
| summarize SnapshotTime = arg_max(PreciseTimeStamp, *) by CrpDiskId = DiskId;
let crpDiskIds = crpDisks | project CrpDiskId;
let disksBi  = cluster("DisksBi").database("DisksBi").Disk
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where CrpDiskId in (crpDiskIds)
| distinct CrpDiskId, DisksId;
crpDisks | join kind= fullouter disksBi on CrpDiskId
| extend diskResoureArray = split(CsmResourceId, "/")
| extend diskCsmSubId = tolower(diskResoureArray[2])
| extend diskCsmResourceGroup = tolower(diskResoureArray[4])
| extend diskCsmResourceName = tolower(diskResoureArray[8])
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMId}`

---
