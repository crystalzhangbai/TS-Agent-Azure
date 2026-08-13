# (top-level)

> Source: **Aztec AzAllocatorAllocations Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "AzSMAllocations"

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `ResourceGet` · Widget: `Container`

```kusto
AzSMAllocationEvents
| where PreciseTimeStamp between (globalFrom..globalTo)
| where allocationId contains 'searchText'
| take 1
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_allocationId}`

**Signal filters seen in KQL:** `allocationId contains "searchText"`

---

### Query AllocatorContainerResult

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Table`

```kusto
AllocatorContainerResult
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where  allocationId == queryAllocationId
| project PreciseTimeStamp, containerRequestId, containerIndex, isSucceeded, resultType, containerId, nodeId, totalTime, comment
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---
