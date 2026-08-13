# Shared — VM Identification & Universal Queries

> **Purpose**: The 8-10 queries that EVERY playbook (A through L) needs at Step 0/1/2.
> Canonical KQL lives here. Playbooks may inline filter-customized copies.
> If schema changes, update this file first, then sweep playbooks.

> **Note**: These queries also appear in `azurecm-queries.md` (by-cluster view) and `vmainsight-queries.md` for backward compatibility. This file is the single source of truth.

---

## Standard variables (paste at the top of any notebook)

```
{SubscriptionId}, {VMName}, {ResourceGroupName}, {ResourceId}
{NodeId}, {ContainerId}, {VMId} (= virtualMachineUniqueId), {TenantName}, {Cluster}
{StartTime} / {EndTime}  — format: 2026-06-01 14:30:00Z (subtract 1-2h from reported start)
{StorageAccountName}, {DiskName}, {LMSessionId}, {CorrelationId}, {IncidentId}
```

---

## Q0 — ResourceId decomposition

When only the Azure resource ID is provided, derive Sub/RG/VMName first.

```kusto
let MyResourceID = "{ResourceId}";
let SubID       = tostring(split(MyResourceID, "/")[2]);
let ResourceGrp = tostring(split(MyResourceID, "/")[4]);
let VMName      = tostring(split(MyResourceID, "/")[-1]);
```

---

## Q1 — LogContainerSnapshot — VM ↔ Node placement history

**Use case**: Locate which physical node hosted the VM during a time window. Returns `NodeId`, `ContainerId`, `Cluster`, `tenantName`, `VMId`. If `ContainerCreationTime` changes inside the window → VM moved hosts (Service Healing or LM happened).

```kusto
let sid     = "{SubscriptionId}";
let vmname  = "{VMName}";
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where subscriptionId == sid and roleInstanceName has vmname
| where PreciseTimeStamp between (datetime({StartTime})-2h .. datetime({EndTime})+2h)
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by roleInstanceName, creationTime, virtualMachineUniqueId, Tenant, containerId, nodeId, tenantName, containerType, updateDomain, availabilitySetName, subscriptionId
| project VMName=roleInstanceName, VMId=virtualMachineUniqueId, Cluster=Tenant, NodeId=nodeId, ContainerId=containerId,
    ContainerCreationTime=todatetime(creationTime), StartTimeStamp=min_PreciseTimeStamp, EndTimeStamp=max_PreciseTimeStamp,
    tenantName, containerType, updateDomain, availabilitySetName
| order by ContainerCreationTime asc
```

### Variant — VMs on a specific node (last 3 days)
```kusto
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where nodeId == "{NodeId}"
| where PreciseTimeStamp > ago(3d)
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, containerId
```

### Variant — Flexible identity resolution (use ANY identifier)
```kusto
let id = "{Identifier}";  // can be subscriptionId, VMName, containerId, nodeId, or VMId
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where subscriptionId == id or roleInstanceName has id or containerId == id or nodeId == id or virtualMachineUniqueId == id
| summarize arg_max(PreciseTimeStamp, *) by roleInstanceName, containerId, nodeId
```

---

## Q2 — LogContainerHealthSnapshot — Container health & faultInfo

**Use case**: See the container's lifecycle / OS state / fault info during the window. The single richest signal for "what was the VM doing?"

```kusto
cluster("Azcsupfollower.kusto.windows.net").database("AzureCM").LogContainerHealthSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where roleInstanceName contains "{VMName}"
| project PreciseTimeStamp, Tenant, roleInstanceName, tenantName, containerId, nodeId,
    containerState, actualOperationalState, containerLifecycleState, containerOsState,
    faultInfo, vmExpectedHealthState, virtualMachineUniqueId,
    containerIsolationState, AvailabilityZone, Region
| order by PreciseTimeStamp asc
```

**Filter tips:**
- `containerOsState == "ContainerOsStateUnresponsive"` — guest OS hung
- `containerOsState == "GuestOsStateProvisioningRecovery"` — provisioning recovery
- `faultInfo != ""` — CreateContainer failure or container fault (parse for FaultCode)

**Common `faultInfo.FaultCode` values:**
- `10005` + `0x80078000` → Blob Cache disk error (route to Playbook A § STG-2)
- `10036` + `"high memory usage"` → AN Overlake SoC OOM (route to Playbook A § HW-7)
- `60017` → DCM Hardware fault (route to Playbook A § HW-1)

---

## Q3 — LogNodeSnapshot — Node state & faultInfo

**Use case**: Per-node availability / disk config / OFR / Unallocatable state during the window.

```kusto
cluster("Azcsupfollower.kusto.windows.net").database("AzureCM").LogNodeSnapshot
| where nodeId =~ "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, nodeState, nodeAvailabilityState, containerCount, diskConfiguration,
    faultInfo, rootUpdateAllocationType, RoleInstance
| order by PreciseTimeStamp asc
```

**Filter tips:**
- `nodeState == "PoweringOn"` — node was restarted
- `nodeAvailabilityState == "Unallocatable"` — node marked unallocatable (no new VMs)
- `nodeState == "OutForRepair"` — node OFR (hardware repair)
- `diskConfiguration` value change → disk config change in window

### Variant — Check if a node is currently OFR
```kusto
cluster("AzureCM").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp >= ago(2h) and nodeId == "{NodeId}" and Tenant == "{Cluster}"
    and nodeState == "OutForRepair"
```

---

## Q4 — VMA — Platform RCA classification (RCAEngine verdict)

**Use case**: The **single most important** classification step. Gives you `RCALevel1` / `RCALevel2` which routes you to the correct deep playbook section.

```kusto
cluster("Vmainsight").database("vmadb").VMA
| where Subscription == "{SubscriptionId}" and RoleInstanceName has "{VMName}"
| where PreciseTimeStamp between (datetime({StartTime})-1h .. datetime({EndTime})+2h)
| where RCAEngineCategory !contains "Customer"
| distinct StartTime, EndTime, Cluster, NodeId, ContainerId, RoleInstanceName,
    RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, RCA_CSS,
    DCM_RCA, DcmNodeState_OFRFaultCode, DcmNodeState_OFRReason,
    Detail, Watson_dumpUidLink, Watson_BugLink, Watson_DumpType,
    E17_ClusterFailureReportUrl
| order by StartTime asc
```

### Variant — Filter by NodeId only (when no VMName)
```kusto
cluster("Vmainsight").database("vmadb").VMA
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 3h)
| where RCAEngineCategory !contains "Customer"
| distinct StartTime, EndTime, Cluster, NodeId, ContainerId, RoleInstanceName, RCALevel1, RCALevel2, RCA_CSS
```

### `RCALevel1` → Routing (used by Playbook A)
| `RCALevel1` | Go to |
|---|---|
| `HostOSCrash` | Playbook A § SW-1 (Host Bugcheck) |
| `NodeFault` | Playbook A § SW-3 / SW-4 (PowerCycle Unhealthy Node) |
| `Hardware*` | Playbook A § HW-* |
| `ServiceHealing*` | Playbook A § STG-2 (FC 10005) / § HW-7 (FC 10036) |
| `LiveMigration*` | Playbook A § STG-3 (VFP) |
| `HostUpdate*` / `DataPath*` | Playbook A § MAINT-1 |
| `IaaSxStoreOutage` | Playbook A § STG-1 (E17) |
| Empty / `Inconclusive` | Go to Q5 + Step 6 in Playbook A core |

---

## Q5 — VMALENS — 30-day recurrence for the VM

**Use case**: Strike / repeated impact check. Shows all VMA records for the VM over 30d.

```kusto
cluster("Vmainsight").database("vmadb").VMALENS
| where Subscription == "{SubscriptionId}" and RoleInstanceName has "{VMName}"
| where PreciseTimeStamp > ago(30d)
| project StartTime, EndTime, Cluster, NodeId, RoleInstanceName, RCALevel1, RCALevel2
| order by StartTime desc
```

---

## Q6 — GetArticleIdByFailureSignature — Signature → KB article

**Use case**: Once you have `RCALevel1.RCALevel2`, get the official customer-facing RCA KB article ID.

```kusto
cluster("Vmainsight").database("Air").GetArticleIdByFailureSignature("<RCALevel1.RCALevel2>")
// Examples:
//   GetArticleIdByFailureSignature("HostOSCrash.UnhealthyNode_OS Bugcheck 0x0000000a")
//   GetArticleIdByFailureSignature("NodeFault.UnhealthyNode_Inconclusive_Powercycled")
//   GetArticleIdByFailureSignature("HardwareFault.DCM FaultCode 60017")
```

Companion: convert article ID → wiki link:
```kusto
cluster("Vmainsight").database("Air").GetCssWikiLinkByArticleId(<articleId>)
```

---

## Q7 — KronoxVmOperationEvent — Platform / Customer-triggered VM operations

**Use case**: Was there a platform-issued or customer-issued operation (restart, stop, deallocate, redeploy) in the window? Rules out "unexpected restart" if a known op triggered it.

```kusto
cluster("Azcsupfollower").database("AzureCM").KronoxVmOperationEvent
| where ContainerId == "{ContainerId}" or RoleInstanceName has "{VMName}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, OperationName, OperationType, RoleInstanceName, NodeId, Status, Reason
```

**Companion — ARM-side customer ops (when KronoxVmOperationEvent has no row):**
```kusto
cluster("armprod").database("ARMProd").HttpIncomingRequests
| where targetResourceId =~ "{ResourceId}"
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where operationName has_any ("restart", "redeploy", "deallocate", "stop", "start")
| project TIMESTAMP, operationName, httpStatusCode, callerIpAddress, userAgent, identity
```

---

## Q8 — Hawkeye — Final platform verdict (4-24h lag)

**Use case**: Authoritative late-binding RCA from the Hawkeye engine. If VMA shows `Inconclusive` immediately after the incident, re-check Hawkeye 4-24h later.

```kusto
cluster("hawkeyedataexplorer.westus2.kusto.windows.net").database("HawkeyeLogs").GetLatestHawkeyeRCAEvents
| where NodeId == "{NodeId}"
| where RCATimestamp between (datetime({StartTime}) .. datetime({EndTime})+24h)
| project FaultTime, NodeId, RCALevel1, RCALevel2
```

If Hawkeye still says `Inconclusive` after 24h → truly Inconclusive → escalate to **EEE Host Node** by opening an ICM manually via ASC (Escalate ticket, CRI-HostNode).

---

## Quick "I just want to know X" recipes

| Question | Sequence |
|---|---|
| "Was this VM impacted at time X?" | Q1 → Q2 (look at faultInfo, containerOsState) |
| "Why did the VM restart?" | Q1 → Q4 → route by RCALevel1 to Playbook A deep |
| "Is this a known platform issue?" | Q4 → Q6 |
| "Was this caused by a customer action?" | Q7 |
| "Has this VM had repeated issues?" | Q5 |
| "Was the node affected node-wide (all VMs on it)?" | Q1 (VMs on node variant) + Q3 |
| "Is this node currently OFR / Unallocatable?" | Q3 (variant) |
| "What's the authoritative RCA?" | Q4 first, then Q8 after 4-24h if Inconclusive |

---

## Cluster shortcuts used in this file

| Cluster | URI | Database | Notes |
|---|---|---|---|
| AzureCM | `azurecm.kusto.windows.net` | `AzureCM` | Production data, low retention |
| Azcsupfollower | `azcsupfollower.kusto.windows.net` | `AzureCM` | Follower with higher retention — preferred for >30d back |
| Vmainsight | `vmainsight.kusto.windows.net` | `vmadb`, `Air`, `Vmadiag` | RCA Engine, Air events, Vmadiag (guest heartbeat) |
| ARMProd | `armprod.kusto.windows.net` | `ARMProd` | ARM API tracing |
| Hawkeye | `hawkeyedataexplorer.westus2.kusto.windows.net` | `HawkeyeLogs` | Authoritative platform RCA (lag) |
