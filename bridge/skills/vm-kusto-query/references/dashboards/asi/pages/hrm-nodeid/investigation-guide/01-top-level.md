# (top-level)

> Source: **Host Resource Manager - NodeId** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "NodeId"

Cluster: `wdgeventstore.kusto.windows.net` · Database: `KernelAgent` · Type: `ResourceGet` · Widget: `Container`

```kusto
HostResourceManagerResourceSnapshotMetadata
| where TIMESTAMP between (globalFrom..globalTo) and NodeId == local_NodeId
| summarize arg_max(TIMESTAMP, Environment, Cluster, NodeId, Hostname, SnapshotId)
| project Environment, Cluster, NodeId, Hostname, SnapshotId
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_NodeId}`

---

### HRM snapshots

Cluster: `wdgeventstore` · Database: `KernelAgent` · Type: `Timeline`

```kusto
HostResourceManagerResourceSnapshotMetadata
| where TIMESTAMP between (queryFrom..queryTo) and NodeId == nodeId
| project Id=SnapshotId,
          Content=strcat(SnapshotId, ' (', SnapshotType, ')'),
          FilterCategory=ReasonLevel1,
          StartTime=SnapshotStartTime,
          EndTime=LastDataCaptureTime
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Entries for HRM snapshot

Cluster: `wdgeventstore` · Database: `KernelAgent` · Type: `Table`

```kusto
HostResourceManagerResourceSnapshotEntries
| where TIMESTAMP between (queryFrom..queryTo) and NodeId == nodeId and SnapshotId == snapshotId
| project NodeId, SnapshotId, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3, IdentifierAdditionalMetaData,
          CommitUsageBytes_Undelegated, CommitUsageBytes_Undelegated_Avg, CommitUsageBytes_Undelegated_Min, CommitUsageBytes_Undelegated_Max, CommitUsageBytes_Undelegated_LastObserved,
          CommitUsageBytes_Total, CommitUsageBytes_Total_Avg, CommitUsageBytes_Total_Min, CommitUsageBytes_Total_Max, CommitUsageBytes_Total_LastObserved,
          PhysicalUsageBytes_Undelegated, PhysicalUsageBytes_Undelegated_Avg, PhysicalUsageBytes_Undelegated_Min, PhysicalUsageBytes_Undelegated_Max, PhysicalUsageBytes_Undelegated_LastObserved,
          PhysicalUsageBytes_Total, PhysicalUsageBytes_Total_Avg, PhysicalUsageBytes_Total_Min, PhysicalUsageBytes_Total_Max, PhysicalUsageBytes_Total_LastObserved,
          AdditionalData
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{snapshotId}`

---
