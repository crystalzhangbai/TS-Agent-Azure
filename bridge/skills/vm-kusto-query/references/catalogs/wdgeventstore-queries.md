# WDG EventStore Queries — Host OS Version / Build

Cluster: `wdgeventstore.kusto.windows.net`
Database: `HostOSDeploy`

> **Scope**: Tiny but high-value cluster — the single table `nodes` exposes the OS build of every Azure physical host node. Lets you answer "is this host running the build that supports feature X?" without engaging the deployment team.
>
> **Already used by** the ASI unexpected-restart dashboards (`dashboards/asi/pages/wf-unexpected-restart/...`) for `HostGenId` / `SKU` enrichment in node investigation queries.

---

## nodes — Host OS version lookup by NodeId

```kusto
let queryFrom = datetime({StartTime});
let queryTo   = datetime({EndTime});
let local_nodeId = "{NodeId}";
cluster('wdgeventstore.kusto.windows.net').database('HostOSDeploy').nodes
| where nodeId == local_nodeId
| project nodeId, OSVersion, HostGenId, SKU
```

Common feature thresholds:

| OS build | Feature gate |
|---|---|
| `RS 1.65*` | Hyper-V cannot expose "Available Memory" counter from Windows guest VMs (no fix path — node must be updated). Rare: <0.3% of fleet. |
| `RS 1.86+` | "Available Memory" guest counter supported (>99.7% of fleet). |

Use case examples:
- **"Available memory" metric missing for a Windows VM** → run the query; if `OSVersion` matches `RS 1.65*` the customer-facing wording is "host OS predates the feature, no ETA on update" (see playbook `MEM-Perf-1`). Any other build → the gap is guest-side (dmvsc.sys not running, Hyper-V role enabled inside guest, CVM by design, Linux balloon driver missing).
- **HostGenId / SKU enrichment** for memory-partition or hardware-class decisions — join into other queries on `NodeId`.

References:
- TSG: [Available Memory shows 0GB_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FAvailable-Memory-shows-0GB_Perf)
- Used inline by: `references/dashboards/asi/pages/wf-unexpected-restart/investigation-guide/06-node-investigation.md`
