# Playbook D — Maintenance Deep TSGs

Companion to [`playbook-D-maintenance-core.md`](playbook-D-maintenance-core.md). All KQL bodies are verbatim from the AzureIaaSVM csswiki TSGs they cite — replace `{Placeholder}` tokens with case data before execution.

**Cluster shortcuts used below:**
- `vmainsight` — `cluster("vmainsight.kusto.windows.net").database("vmadb")`
- `azcsupfollower` — `cluster("azcsupfollower.kusto.windows.net").database("AzureCM")` (also `azcsupfollower2.centralus`)
- `azcsupfollower-icm` — `cluster("icmcluster.kusto.windows.net").database("ACM.Backend")` / `ACM.Publisher`
- `moseisley` — `cluster("moseisley.kusto.windows.net").database("AzureCM")` (LM session tables)
- `azcore` — `cluster("azcore.centralus.kusto.windows.net").database("AzureCP")` (Holmes goal state)
- `azcrp` — `cluster("azcrp.kusto.windows.net").database("crp_allprod")`
- `azcrpbifollower` — `cluster("azcrpbifollower.kusto.windows.net").database("bi_allprod")`
- `azdeployer` — `cluster("Azdeployer").database("AzDeployerKusto")`
- `armprod` — `cluster("Armprod.kusto.windows.net").database("ARMProd")`

---

## § PM — Planned-Maintenance TSGs

### PM-1: Databricks RCA (cluster-deleted-from-API)

> **TSG**: [Databricks RCA_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FDatabricks-RCA_Planned-Maint)
> **Scope**: Databricks worker VM disappeared / restarted; customer thinks it was a platform action; usually it is **Databricks control plane deleting the worker**, not Azure platform maintenance.

#### PM-1.Q1 — Find the DELETE call from the Databricks RP
```kusto
cluster("Armprod.kusto.windows.net").database("ARMProd").HttpIncomingRequests
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where targetUri has "{VMName}" or targetUri has "{VMResourceId}"
| where httpMethod == "DELETE"
| project TIMESTAMP, callerIpAddress, userAgent, identity, targetUri, httpStatusCode, correlationId, durationMs
| order by TIMESTAMP asc
```
Look for `userAgent` / `identity` containing `databricks` or coming from a Databricks-owned subscription — that confirms **Databricks-initiated DELETE**, not Azure maintenance.

#### PM-1.Q2 — Confirm via VMA that no platform RCA exists
core Step 1 (`VMA()` for the VM). If RCA column is empty / shows only customer-initiated container-destroy, the deletion was Databricks.

#### PM-1.Interpretation
Databricks dynamically scales worker pools — auto-termination / job-cluster lifecycle frequently deletes worker VMs. This is **expected Databricks behavior**, not Azure planned maintenance.

#### PM-1.Customer-facing wording
> "The VM `{VMName}` was deleted at `{TIMESTAMP}` by a `DELETE` API call originated by the Databricks control plane (caller IP `{IP}`, user agent `{UA}`). This is part of Databricks worker pool lifecycle management — the Azure platform did not initiate a maintenance event against this VM. For details on Databricks cluster lifecycle, please contact Databricks support or refer to your workspace's job/cluster configuration."

---

### PM-2: Hardware Decommissioning

> **TSG**: [Hardware Decommissioning_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FHardware-Decommissioning_Planned-Maint) — aka https://aka.ms/CCSupHDPlanM
> **Scope**: Customer's VM was rebooted/migrated as part of HW decommissioning wave; needs RCA + impacted-resource list.

> **Note**: Starting with Wave 13, HW decommissioning uses the **regular planned-maintenance experience** — affected resources appear in the VM list view of the Portal with a Maintenance Status column. Customers can self-initiate maintenance via Portal/API.

#### PM-2.Q1 — Resources that **will** be impacted (forward-looking, requires Tracking ID)
```kusto
let trackingId = '{TrackingId}'; // single TrackingID
let subscriptionIds = dynamic(['{SubId1}','{SubId2}']);
cluster("Azdeployer").database("AzDeployerKusto").GetAffectedResourcesFromTrackingIdList_DecomissionMaintenance(trackingId, subscriptionIds)
```

#### PM-2.Q2 — Resources that **were** impacted (historical)
```kusto
cluster("Azcsupfollower.kusto.windows.net").database("AzureCM").ScheduledMaintenanceInformational
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where scheduledMaintenanceId contains "{TrackingId}"
//| where message contains "{TenantName}"   // alternative if no TrackingID
| where message contains "{VMName}" and traceCode contains "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"
| project TIMESTAMP, message
```
The `message` field contains structured `ResourceMaintenanceType: 'HardwareDecommissioning'`, `MaintenanceType: 'Decommission'`, plus `ControlledMaintenancePhaseStartTimeInUTC` / `EndTimeInUTC` (self-service window) and `FabricMaintenanceOperationStartTimeInUTC` / `EndTimeInUTC` (forced fabric window).

#### PM-2.Interpretation
HW Decom is a **planned, notified** event with a customer self-service window followed by a forced fabric window. By the time notifications go out, *new* allocations are already steered to fresh hardware. Any unrelated stop/start, redeploy, resize, or service heal during the window will reallocate the VM to updated hardware and the maintenance status will show completed without explicit customer action.

#### PM-2.Customer-facing wording
> "Your VM `{VMName}` was part of an Azure planned Hardware Decommissioning event (TrackingID `{TrackingId}`). Customers were notified via Service Health Dashboard on `{NotificationTime}` (UTC). The self-service window was `{ControlledMaintenancePhaseStartTimeInUTC}` → `{ControlledMaintenancePhaseEndTimeInUTC}`; the fabric maintenance window was `{FabricMaintenanceOperationStartTimeInUTC}` → `{FabricMaintenanceOperationEndTimeInUTC}`. The maintenance moved the VM to refreshed hardware to ensure continued reliability."

#### PM-2.ICM templates
- Sev 3/4 self-service issues → [ICM Template `eG3r1Z`](https://aka.ms/CRI-ComputeManager)
- Sev 1/2 self-service issues → https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=eG3r1Z
- Postpone request / questions about HW decom → [ICM Template](https://aka.ms/CRI-HardwareDecom)

---

### PM-3: List Affected VMSS Instances Using PowerShell

> **TSG**: [List Affected VMSS Instances Using PowerShell](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FList-Affected-VMSS-Instances-Using-PowerShell)
> **Scope**: Large subscription with many VMSS; customer wants to enumerate which VMSS instances are flagged for planned maintenance + whether SSM is allowed.

#### PM-3.PS — `MaintenanceIterator` function for VMSS
```powershell
function MaintenanceIterator {
    param ( [string]$subscriptionId )
    Select-AzSubscription -SubscriptionId $subscriptionId
    $resourceGroups = Get-AzResourceGroup
    $results = @()
    foreach ($rg in $resourceGroups) {
        $vmssList = Get-AzVmss -ResourceGroupName $rg.ResourceGroupName
        foreach ($vmss in $vmssList) {
            $vmssInstances = Get-AzVmssVM -ResourceGroupName $rg.ResourceGroupName -VMScaleSetName $vmss.Name
            foreach ($i in $vmssInstances) {
                $d = Get-AzVmssVM -ResourceGroupName $rg.ResourceGroupName -VMScaleSetName $vmss.Name -InstanceId $i.InstanceId
                $results += [pscustomobject]@{
                    VMSSName                              = $vmss.Name
                    VMSSInstanceID                        = $i.InstanceId
                    PreMaintenanceWindowStartTime         = $d.MaintenanceRedeployStatus.MaintenanceWindowStartTime
                    PreMaintenanceWindowEndTime           = $d.MaintenanceRedeployStatus.PreMaintenanceWindowEndTime
                    MaintenanceWindowStartTime            = $d.MaintenanceRedeployStatus.MaintenanceWindowStartTime
                    MaintenanceWindowEndTime              = $d.MaintenanceRedeployStatus.MaintenanceWindowEndTime
                    LastOperationMessage                  = $d.MaintenanceRedeployStatus.LastOperationMessage
                    IsCustomerInitiatedMaintenanceAllowed = [bool]$d.MaintenanceRedeployStatus.IsCustomerInitiatedMaintenanceAllowed
                }
            }
        }
    }
    return $results
}
```
Run for a subscription:
```powershell
MaintenanceIterator -SubscriptionId <SubscriptionId>
```
Filter to SSM-actionable instances only:
```powershell
MaintenanceIterator -SubscriptionId <SubscriptionId> | Where-Object { $_.IsCustomerInitiatedMaintenanceAllowed -eq $true }
```

#### PM-3.Interpretation
- `IsCustomerInitiatedMaintenanceAllowed = False` + no window dates → **no action needed**.
- `IsCustomerInitiatedMaintenanceAllowed = True` + future `PreMaintenanceWindow*` → customer can self-initiate maintenance any time before `PreMaintenanceWindowEndTime`.
- `IsCustomerInitiatedMaintenanceAllowed = False` + past `PreMaintenanceWindow*` → window expired; platform will execute with isolation guarantees only. Customer can manually redeploy.
- `LastOperationMessage` shows status of last SSM attempt.

---

### PM-4: List Affected VMs Using PowerShell

> **TSG**: [List Affected VMs Using PowerShell](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FList-Affected-VMs-Using-PowerShell)
> **Scope**: Same as PM-3 but for standalone VMs (non-VMSS).

#### PM-4.PS-1 — All VMs in a subscription
```powershell
function MaintenanceIterator {
    param ( [string]$subscriptionId )
    Select-AzSubscription -SubscriptionId $subscriptionId
    $resourceGroups = Get-AzResourceGroup
    $results = @()
    foreach ($rg in $resourceGroups) {
        $vms = Get-AzVM -ResourceGroupName $rg.ResourceGroupName
        foreach ($vm in $vms) {
            $d = Get-AzVM -ResourceGroupName $rg.ResourceGroupName -Name $vm.Name -Status
            $results += [pscustomobject]@{
                VMName                                = $vm.Name
                MaintenanceRedeployStatus             = $d.MaintenanceRedeployStatus
                IsCustomerInitiatedMaintenanceAllowed = [bool]$d.MaintenanceRedeployStatus.IsCustomerInitiatedMaintenanceAllowed
                PreMaintenanceWindowStartTime         = $d.MaintenanceRedeployStatus.PreMaintenanceWindowStartTime
                PreMaintenanceWindowEndTime           = $d.MaintenanceRedeployStatus.PreMaintenanceWindowEndTime
                MaintenanceWindowStartTime            = $d.MaintenanceRedeployStatus.MaintenanceWindowStartTime
                MaintenanceWindowEndTime              = $d.MaintenanceRedeployStatus.MaintenanceWindowEndTime
                LastOperationMessage                  = $d.MaintenanceRedeployStatus.LastOperationMessage
            }
        }
    }
    return $results
}
MaintenanceIterator -SubscriptionId <SubscriptionId>
```

#### PM-4.PS-2 — Filter to SSM-actionable
```powershell
MaintenanceIterator -SubscriptionId <SubscriptionId> | Where-Object { $_.IsCustomerInitiatedMaintenanceAllowed -eq $true }
```

#### PM-4.PS-3 — Single VM
```powershell
(Get-AzVM -ResourceGroupName <RG> -Name <VMName> -Status).MaintenanceRedeployStatus
```

#### PM-4.Interpretation (same enum as PM-3)
Maintenance status fields decoded the same way as PM-3. If `LastOperationMessage` shows `MaintenanceRedeployFailed`, gather error and route to PM-15 (no-action path) or follow the SSM TSG.

---

### PM-5: Live Migration triggered by Defrag

> **TSG**: [Live Migration Defrag_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FLive-Migration-Defrag_Planned-Maint)
> **Scope**: Customer reports an unexpected LM event and the trigger turned out to be cluster defragmentation (resource balancing). Expected platform behavior — brief brownout (<5s), memory preserved, no reboot.

#### PM-5.Q1 — Confirm Defrag LM via VMA
```kusto
cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where Subscription =~ "{SubscriptionId}"
| where CadPrimaryKey contains "LegacyHB"
| where RCAEngineCategory <> "CustomerInitiated"
| where RoleInstanceName contains "{ResourceName}"
| project PreciseTimeStamp, StartTime, EndTime, RoleInstanceName, Cluster, TenantName,
          ContainerId, NodeId, VmUniqueId, RCALevel1, RCALevel2, RCALevel3,
          Storage_AccountName, Storage_AccountType, Storage_Cluster, Region, Subscription
```
Look for `"LiveMigrationSucceeded TriggerType:Defrag"` in RCALevel fields → confirms Defrag.

#### PM-5.Q2 — ASI EEE HostNode (UI alternative)
Open `ASI - EEE HostNode` from https://aka.ms/asi → StartHub view. Container view will show the Defrag LM event in the timeline.

#### PM-5.Q3 — ASC VM Availability Impact (alternative)
ASC → Health → VM Availability Impact. Failure Details for Defrag LM contain:
- `Event Type: LiveMigration`
- `Event Source: AirLiveMigrationEvents`
- `TriggerType: Defrag`
- `Impact Group: AIR-BP-subsecond`

#### PM-5.Interpretation
Defrag LM is **platform-initiated automated resource balancing**. Successful Defrag LM is **not an outage**, **not an incident**, and `RCA` terminology should be avoided when communicating with the customer (so they don't misinterpret as a degradation event). Do **not** file CRI/ICM to EEE or PG just to request an RCA for a successful Defrag LM.

If LM **failed** at that timestamp and customer wants RCA, route via [Live Migration Basic Workflow](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2173263) and PM-7. If Defrag frequency is abnormal (e.g., daily), engage Planned Maintenance SMEs via Ava channel.

#### PM-5.Customer-facing wording — single Defrag event
> "Microsoft Azure team has completed its investigation and confirmed that the cluster-level compute resource optimization operation (defragmentation) was triggered at that time.
>
> This operation is part of the platform's automated resource management process and is initiated to optimize resource allocation within the cluster. Its purpose is to efficiently balance existing workloads and maintain capacity for future compute resource deployments.
>
> The system automatically triggers this operation when needed, based on the current resource allocation state. The migration is triggered based on the Live Migration technology. For more information about Live Migration, please refer to: https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates.
>
> We sincerely apologize for the inconvenience this may have caused.
>
> Microsoft Azure Team"

#### PM-5.Customer-facing wording — VM impacted 3–9 times / month
> "Microsoft Azure team has completed its investigation and confirmed that all Live Migration events were triggered by cluster-level compute resource optimization (defragmentation). This operation is part of the platform's automated resource optimization process, initiated to optimize resource allocation within the cluster, efficiently balancing existing workloads and maintaining capacity for future compute resource deployments. The system automatically triggers this operation when needed, based on the current resource allocation state.
>
> Each optimization cycle is an independent decision made by the platform based on real-time conditions across the host infrastructure. Multiple optimizations can occur over a period of time because the platform may determine that rebalancing is needed again. While experiencing multiple events may seem unusual, it is within the expected behavior of the platform when multiple optimization cycles occur in a given timeframe.
>
> Importantly, each Live Migration event is designed for minimal disruption: a brief pause typically lasting no more than a few seconds per event, memory is fully preserved with no data loss, application state is maintained, and no reboot is required. For more information about Live Migration: https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates.
>
> For greater control over when platform maintenance occurs, you can leverage:
> - Azure Dedicated Hosts (https://learn.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts)
> - Maintenance Configurations (https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-configurations)
>
> We sincerely apologize for the inconvenience this may have caused.
>
> Microsoft Azure Team"

#### PM-5.LM Disablement
For perf-sensitive workloads that cannot tolerate brownouts, use the [Live Migration Disablement Request](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/895545) flow (HOW-2). With LM disabled, any host event becomes a **reboot** instead of brownout.

---

### PM-6: Live Migration FAQ — trigger types & session lookup

> **TSG**: [Live Migration FAQ_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FLive-Migration-FAQ_Planned-Maint)
> **Scope**: Customer asks "why was my VM live-migrated?" / "what kind of LM was this?" / "why so frequent?"

#### PM-6.TriggerType enum (filter `triggerType ==`)
| Value | Meaning |
|---|---|
| `Defrag` | Cluster resource rebalancing (PM-5) |
| `HEUpgrade` / `HostUpdate` | Host OS / firmware update (route to PM-7) |
| `UnallocatableNode` | Source node failed health checks — vacated proactively |
| `FDGroupTenantRealignment` | Fault-domain rebalancing |
| `LmGen` / `LMGen` | Internal LM regeneration |
| `Operator` | On-demand LM (HOW-1) |
| `StopMigrate` | Customer-initiated stop with migrate |
| `Unknown` | Older telemetry or trigger lost — escalate if frequent |

#### PM-6.Q1 — LM session summary for a VM
```kusto
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where roleInstanceName contains "{VMName}" or sourceContainerId == "{ContainerId}" or destinationContainerId == "{ContainerId}"
| project PreciseTimeStamp, sessionId, triggerType, migrationConstraint, result, blackoutTimeInMs, durationInMs,
          sourceNodeId, destinationNodeId, sourceContainerId, destinationContainerId, roleInstanceName, virtualMachineUniqueId
| order by PreciseTimeStamp asc
```

#### PM-6.Q2 — All LM activity on a source node (find node-wide events)
```kusto
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where sourceNodeId == "{NodeId}"
| summarize Count = count(), MinBlackoutMs = min(blackoutTimeInMs), MaxBlackoutMs = max(blackoutTimeInMs) by triggerType, result
```

#### PM-6.Q3 — LM validation errors (critical events)
```kusto
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionValidationCriticalEventLog
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where sourceNodeId == "{NodeId}" or destinationNodeId == "{NodeId}"
| project PreciseTimeStamp, sessionId, traceCode, message, sourceNodeId, destinationNodeId
```

#### PM-6.Q4 — Resolve one sessionId across all session logs
```kusto
let sid = "{SessionId}";
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationContainerDetailsEventLog
| where sessionId == sid
| project PreciseTimeStamp, sessionId, sourceContainerId, destinationContainerId
```
```kusto
let sid = "{SessionId}";
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCreatedLog
| where sessionId == sid
| project PreciseTimeStamp, sessionId, traceCode, migrationConstraint, message, subscriptionId, roleInstanceName, virtualMachineUniqueId
```
```kusto
let sid = "{SessionId}";
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCompleteLog
| where sessionId == sid
| project PreciseTimeStamp, sessionId, triggerType, result, blackoutTimeInMs, durationInMs,
          sourceNodeId, destinationNodeId, sourceContainerId, destinationContainerId
```
```kusto
let sid = "{SessionId}";
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionStatusEventLog
| where sessionId == sid
| project PreciseTimeStamp, sessionId, statusCode, traceCode, message
| order by PreciseTimeStamp asc
```

#### PM-6.Interpretation
Match `triggerType` to the right downstream playbook section:
- `Defrag` → PM-5
- `HEUpgrade` / `HostUpdate` → PM-7
- `UnallocatableNode` → cross-link to Playbook A § HW-* (source node was faulty)
- `Operator` → HOW-1 / customer-requested
- Frequency anomaly → engage SME via Ava (PM-5 wording for "3–9/month")

---

### PM-7: Live Migration with TriggerType = PlannedMaintenance

> **TSG**: [Live Migration with TriggerType PlannedMaintenance_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FLive-Migration-with-TriggerType-PlannedMaintenance_Planned-Maint)
> **Scope**: Customer Resource Health reports `"This virtual machine was paused for X seconds due to a memory-preserving Live Migration operation."` and the LM session's `triggerType == "PlannedMaintenance"`. Trigger is an IO-based maintenance / host update that vacated the node.

#### PM-7.Q1 — Resolve the LM session for the VM
```kusto
let queryFrom      = datetime({StartTime});
let queryTo        = datetime({EndTime});
let queryContainer = "{ContainerId}";
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationContainerDetailsEventLog
| where (destinationContainerId == queryContainer or sourceContainerId == queryContainer)
| where PreciseTimeStamp between (queryFrom .. queryTo)
| project sessionId
| join kind=inner (
    cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCreatedLog
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | project PreciseTimeStamp, sessionId, traceCode, migrationConstraint, message, subscriptionId, roleInstanceName, virtualMachineUniqueId
  ) on sessionId
```

#### PM-7.Q2 — Which Holmes evaluator requested the vacate (root cause for `TriggerType:PlannedMaintenance`)
```kusto
let queryFrom = datetime({StartTime});
let queryTo   = datetime({EndTime});
let queryContainerId = "{ContainerId}";
cluster("azcore.centralus.kusto.windows.net").database("AzureCP").HolmesGoalStateManagerEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainerId
| where message startswith "Triggering Holmes action"
| parse message with * "TriggerType:" triggerType:string ";" * "Deadline:" deadline:datetime
                       "called from serviceName" serviceName:string " evaluatorName" evaluatorName:string
| project PreciseTimeStamp, containerId, nodeId, actionType, triggerType, deadline, serviceName, evaluatorName, message
| extend Content = actionType, Health = "Degraded", StartTime = PreciseTimeStamp
| order by PreciseTimeStamp asc
```
The `serviceName` / `evaluatorName` identifies the maintenance subsystem (e.g., `HostUpdate`, `BiosUpdate`, `IoMaintenance`) that initiated the vacate goal-state.

#### PM-7.Q3 — Node-wide vacate goal-state confirmation
```kusto
let queryFrom = datetime({StartTime});
let queryTo   = datetime({EndTime});
let queryNodeId = "{NodeId}";
cluster("azcsupfollower.kusto.windows.net").database("AzureCM").HolmesRHMNodeVacateStatusEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where targetNodeId contains queryNodeId
| summarize max(PreciseTimeStamp) by targetNodeId, nodeMigrationGoalState
```

#### PM-7.Interpretation
`TriggerType:PlannedMaintenance` in LM session does **not** always mean a customer-visible Service Health notification — it can also be an internal IO-based maintenance (firmware, BIOS, storage stack update). The Holmes `evaluatorName` distinguishes these. If `evaluatorName` matches a customer-notified PM (PM-2/PM-12), the customer should have an ICM/Service Health record; otherwise it is internal node-level maintenance and the customer-shareable RCA is **VMA RCA Planned Maintenance NodeShutdown Live Migration** ([wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496308)).

#### PM-7.Customer-facing wording
> "Your VM `{VMName}` experienced a memory-preserving Live Migration of `{durationSec}` seconds at `{TIMESTAMP}` (UTC). The migration was initiated by an Azure platform maintenance operation (`{evaluatorName}`) on the source host node — the VM was moved to a healthy node with memory preserved. No customer action is required; data and application state were retained."

---

### PM-8: M-Series Live Migration

> **TSG**: [M-Series Live Migration_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FM-Series-Live-Migration_Planned-Maint)
> **Scope**: SAP HANA / M-series customer asks if LM is supported on their SKU and what to expect.

#### PM-8.Q1 — Is LM enabled for this SKU on this container/node
```kusto
let containerId = "{ContainerId}";
cluster("Azcsupfollower").database("AzureCM").LogContainerPolicySnapshot
| where PreciseTimeStamp > ago(7d)
| where ContainerId == containerId
| project PreciseTimeStamp, ContainerId, NodeId, vmSize, policySettings = policy
| top 1 by PreciseTimeStamp desc
| join kind=inner (
    cluster("Azcsupfollower").database("AzureCM").TMMgmtFabricSettingEtwTable
    | where PreciseTimeStamp > ago(7d)
    | where Name contains "LiveMigration" or Name contains "MSeries"
  ) on NodeId
| project PreciseTimeStamp, ContainerId, NodeId, vmSize, settingName = Name, settingValue = Value
```

#### PM-8.Q2 — Successful M-series LM events (3-way join Air ⨝ LM ⨝ CPU capping)
```kusto
let q_from = datetime({StartTime});
let q_to   = datetime({EndTime});
cluster("vmainsight.kusto.windows.net").database("vmadb").AirLiveMigrationEvents
| where PreciseTimeStamp between (q_from .. q_to)
| where vmSize startswith "Standard_M"
| project PreciseTimeStamp, sessionId, vmId, vmSize, sourceNodeId, destinationNodeId, triggerType
| join kind=inner (
    cluster("vmainsight.kusto.windows.net").database("vmadb").LiveMigrationActivities
    | where PreciseTimeStamp between (q_from .. q_to)
    | project sessionId, durationSeconds = durationInMs / 1000.0, blackoutSeconds = blackoutTimeInMs / 1000.0, result
  ) on sessionId
| join kind=leftouter (
    cluster("vmainsight.kusto.windows.net").database("vmadb").AirCpuCappingEvents
    | where PreciseTimeStamp between (q_from .. q_to)
    | project sessionId, cappingDurationMs = durationInMs
  ) on sessionId
| project PreciseTimeStamp, sessionId, vmId, vmSize, triggerType, result, durationSeconds, blackoutSeconds, cappingDurationMs
| order by PreciseTimeStamp asc
```

#### PM-8.Q3 — Failed M-series LM events with subscription context
```kusto
let q_from = datetime({StartTime});
let q_to   = datetime({EndTime});
cluster("vmainsight.kusto.windows.net").database("vmadb").LiveMigrationFailureEvents
| where PreciseTimeStamp between (q_from .. q_to)
| where vmSize startswith "Standard_M"
| project PreciseTimeStamp, sessionId, vmId, vmSize, failureReason, triggerType, sourceNodeId, destinationNodeId, subscriptionId
| join kind=leftouter (
    cluster("vmainsight.kusto.windows.net").database("vmadb").Product360CustomerSubscriptions
    | project subscriptionId, customerName, segment
  ) on subscriptionId
| order by PreciseTimeStamp asc
```

#### PM-8.Interpretation
- M-series uses an LM path with specialized large-memory pre-copy → expect blackout in single digits of seconds but pre-copy phase can run for many minutes (this is normal for multi-TB memory VMs).
- Failed LM on M-series typically falls back to a memory-preserving brownout retry or a reboot path (see Playbook A § MAINT-1).
- For SAP HANA, advise customer to validate HSR replication state after LM (replication doesn't break, but HANA needs to confirm replay).

#### PM-8.Customer-facing wording
> "Your M-series VM `{VMName}` was live-migrated on `{TIMESTAMP}`. M-series LM uses an extended pre-copy phase for multi-terabyte memory but the customer-visible blackout was `{blackoutSeconds}` seconds. No reboot occurred; memory and application state were preserved."

---

### PM-9: SGX (Confidential Compute) — host changes

> **TSG**: [SGX_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FSGX_Planned-Maint)
> **Scope**: Confidential-compute (DCsv2 / DCsv3 / DCdsv3) VM customer reports SGX enclave broken after a host update / LM / reboot. Almost always a guest-side AESM (Architectural Enclave Service Manager) issue surfaced by a platform event.

#### PM-9.Shell — Guest-side diagnostics (Linux)
```bash
# Device presence
ls -l /dev/sgx*
ls -l /dev/sgx_enclave /dev/sgx_provision

# Kernel messages
sudo dmesg | grep -i sgx

# AESM service status (Ubuntu / RHEL)
systemctl status aesmd
journalctl -u aesmd --since "{StartTime}" --until "{EndTime}"

# Reinstall guidance (Ubuntu)
sudo apt-get install -y libsgx-enclave-common libsgx-launch libsgx-urts sgx-aesm-service
sudo systemctl restart aesmd
```

#### PM-9.Interpretation
SGX enclaves are tied to **CPU microcode + platform certificate (PCK)**. A host BIOS/microcode update can require the guest AESM to refresh attestation collateral. There is **no platform-side KQL** that tells us what an SGX enclave inside the guest is doing — confirm the host event via core Step 2b, then redirect to guest-side AESM diagnostics.

#### PM-9.Customer-facing wording
> "A platform host update was applied to the underlying node of your confidential-compute VM `{VMName}` at `{TIMESTAMP}`. SGX enclave attestation collateral inside the guest may need to be refreshed by restarting the AESM service (`sudo systemctl restart aesmd`) or reinstalling the SGX runtime package. The platform side of the SGX trust chain is healthy."

---

### PM-10: Top-of-Rack (ToR) Switch Maintenance / Failure

> **TSG**: [Networking TOR_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FNetworking-TOR_Planned-Maint) — aka https://aka.ms/CCSupTORPlanM
> **Scope**: VMs on a single rack lose connectivity simultaneously; suspect ToR switch event (maintenance or failure).

#### PM-10.Q1 — Identify ToR events impacting the rack (TinsAcmEventInfo)
```kusto
cluster("Azcsupfollower").database("AzureCM").TinsAcmEventInfo
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where deviceName has "{ToRDeviceName}" or PhysicalLocation has "{ClusterName}"
| project PreciseTimeStamp, deviceName, eventType, eventCategory, eventSubCategory, PhysicalLocation, Message
| order by PreciseTimeStamp asc
```

#### PM-10.Q2 — ToR-affected node mapping (TinsNodeResourceInfo)
```kusto
cluster("Azcsupfollower").database("AzureCM").TinsNodeResourceInfo
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where deviceName has "{ToRDeviceName}"
| project PreciseTimeStamp, deviceName, NodeId, RackId, NetworkInterface, NodeAvailabilityState
| distinct deviceName, NodeId, RackId, NodeAvailabilityState
```

#### PM-10.Q3 — Customer ICM notification for the ToR event
```kusto
cluster("Icmcluster").database("ACM.Publisher").AlbnTargets
| where Subscriptions contains "{SubscriptionId}"
| project CommunicationId
| join cluster("Icmcluster").database("ACM.Backend").PublishRequest on CommunicationId
| where CommunicationDateTime between (datetime({StartTime}) .. datetime({EndTime}))
| where Title contains "Network" or Title contains "ToR" or Title contains "TOR" or RichTextMessage contains "network maintenance"
| order by CommunicationDateTime desc
| project CommunicationDateTime, CommunicationType, Title, IncidentId, RichTextMessage
```

#### PM-10.Q4 — Confirm node faultInfo points at ToR
```kusto
cluster("Azcsupfollower").database("AzureCM").LogNodeSnapshot
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where nodeId == "{NodeId}"
| project TIMESTAMP, nodeId, nodeState, faultInfo, rootUpdateAllocationType, aliveContainerCount
| where faultInfo has "ToR" or faultInfo has "network"
```

#### PM-10.Q5 — VMs running through a specific ToR (PublishRequest + Servers join)
```kusto
let starttm = datetime({StartTime});
let endtm   = datetime({EndTime});
let torDev  = "{ToRDeviceName}";
cluster("Azcsupfollower").database("AzureCM").DeviceInterfaceLinks
| where PreciseTimeStamp between (starttm .. endtm)
| where deviceName == torDev
| project NodeId, RackId, deviceName, NetworkInterface
| join kind=inner (
    cluster("Azcsupfollower").database("AzureCM").LogContainerSnapshot
    | where PreciseTimeStamp between (starttm .. endtm)
    | project NodeId, ContainerId, RoleInstanceName, SubscriptionId, TenantName
  ) on NodeId
| join kind=leftouter (
    cluster("Azcsupfollower").database("AzureCM").Servers
    | project NodeId, ServerName, RackId
  ) on NodeId
| distinct deviceName, RackId, NodeId, ServerName, ContainerId, RoleInstanceName, SubscriptionId
```

#### PM-10.Q6 — ToR `nodeAvailabilityState` timeline
```kusto
cluster("Azcsupfollower").database("AzureCM").TinsNodeResourceInfo
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where deviceName == "{ToRDeviceName}"
| summarize StateChanges = make_set(NodeAvailabilityState), Count = count() by bin(PreciseTimeStamp, 5m), deviceName
| order by PreciseTimeStamp asc
```

#### PM-10.Interpretation
- ToR maintenance is normally redundant (dual-ToR rack) — single ToR event should not impact VMs if the rack is dual-homed.
- Single-ToR rack OR concurrent dual-ToR failure → all VMs on the rack lose connectivity until ToR comes back.
- Use PM-10.Q3 to find if customer received a Service Health notification (ToR maintenance is usually announced).

#### PM-10.Customer-facing wording
> "A Top-of-Rack (ToR) network maintenance event was performed at `{TIMESTAMP}` on switch `{ToRDeviceName}` in cluster `{ClusterName}`. Customers on this rack were notified via Service Health (TrackingID `{TrackingId}`). Your VMs `{VMList}` were affected during the maintenance window. The ToR returned to healthy state at `{RecoveryTime}` and connectivity was restored."

---

### PM-11: Scheduled Events Service — enablement & verification

> **TSG**: [Scheduled Events_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FScheduled-Events_Planned-Maint)
> **Scope**: Customer claims they did **not** receive a Scheduled Event via IMDS for a maintenance that occurred; or asks how to enable Scheduled Events on their VM.

#### PM-11.Q1 — Identify tenantName + cluster for the VM
```kusto
cluster("Azcsupfollower").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp > ago(7d)
| where roleInstanceName contains "{VMName}" and subscriptionId == "{SubscriptionId}"
| top 1 by PreciseTimeStamp desc
| project PreciseTimeStamp, ContainerId, NodeId, tenantName, Cluster, RegionFriendlyName
```

#### PM-11.Q2 — Is the tenant flagged for AzPE (Azure Policy Engine / Scheduled Events) and MR (Maintenance Reschedule)?
```kusto
cluster("Azcsupfollower").database("AzureCM").LogTenantSnapshot
| where PreciseTimeStamp > ago(7d)
| where tenantName == "{TenantName}"
| top 1 by PreciseTimeStamp desc
| project PreciseTimeStamp, tenantName, isAzPE, MRTenantType, isControlledRolloutEnabled, allocationType
```

#### PM-11.Q3 — Tenant availability policy (used to compute Scheduled Events behavior)
```kusto
cluster("Azcsupfollower").database("AzureCM").AzPETenantSnapshot
| where PreciseTimeStamp > ago(7d)
| where tenantName == "{TenantName}"
| top 1 by PreciseTimeStamp desc
| project PreciseTimeStamp, tenantName, TenantAvailabilityPolicy, MRTenantType, ScheduledEventsEnablementStatus
```

#### PM-11.Q4 — Authoritative Scheduled Events enablement status (function)
```kusto
cluster("Azcsupfollower").database("AzureCM").GetScheduledEventsEnablementStatusV3(
    tenantName  = "{TenantName}",
    queryTime   = datetime({StartTime})
)
```

#### PM-11.Q5 — AzPE workflow events for the tenant (issued / scheduled / executed)
```kusto
cluster("Azcsupfollower").database("AzureCM").AzPEWorkflowEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where tenantName == "{TenantName}"
| project PreciseTimeStamp, tenantName, WorkflowName, EventType, WorkflowEventData
| order by PreciseTimeStamp asc
```

#### PM-11.Q6 — TenantManagement maintenance job correlation
```kusto
cluster("Azcsupfollower").database("AzureCM").TMMgmtTenantManagementJobInfoEtwTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where Tenant == "{TenantName}" or message contains "{TenantName}"
| project PreciseTimeStamp, Tenant, jobId, jobType, jobState, message
| order by PreciseTimeStamp asc
```

#### PM-11.Q7 — Scheduled events that were actually surfaced to IMDS
```kusto
cluster("Azcsupfollower").database("AzureCM").ScheduledEventHistoryTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where tenantName == "{TenantName}"
| project PreciseTimeStamp, tenantName, EventId, EventType, EventStatus, EventSource, NotBefore, Resources
| order by PreciseTimeStamp asc
```

#### PM-11.Interpretation
- If PM-11.Q4 shows `Disabled` → tenant/VM is **not configured** for Scheduled Events (default for some legacy SKUs / Cloud Services). Customer must enable per [Scheduled Events docs](https://learn.microsoft.com/azure/virtual-machines/linux/scheduled-events).
- If `Enabled` but PM-11.Q7 has no row → the maintenance type did not warrant a scheduled event (e.g., Defrag, sub-second LM) — this is by design.
- If `Enabled` and PM-11.Q7 has a row but customer says they didn't see it via IMDS → check customer's IMDS polling cadence (Scheduled Events are time-bounded, must be polled regularly).

#### PM-11.Customer-facing wording
> "The Scheduled Events service for tenant `{TenantName}` is `{EnablementStatus}` as of `{TIMESTAMP}`. For the maintenance event on `{EventTime}`, the platform `{did/did not}` emit a scheduled event (EventId `{EventId}`). Scheduled events for sub-second Live Migration / Defrag are not emitted by design. To consume scheduled events, please ensure your VM polls `http://169.254.169.254/metadata/scheduledevents?api-version=2020-07-01` at least once per minute."

---

### PM-12: SSM (Self-Service Maintenance) Statuses

> **TSG**: [SSM Statuses_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FSSM-Statuses_Planned-Maint)
> **Scope**: Customer sees a maintenance status string in Portal / CLI / Resource Health and asks what it means and what to do.

#### PM-12.Q1 — Per-subscription stats (clean, optimized)
```kusto
cluster("Azcompute").database("AzureCM").PlannedMaintenanceStatsForSubscriptions_CustomerView_Optimized(
    subscriptionId = "{SubscriptionId}",
    startTime      = datetime({StartTime}),
    endTime        = datetime({EndTime})
)
```

#### PM-12.Q2 — Per-subscription stats (full view — slower but more columns)
```kusto
cluster("Azcompute").database("AzureCM").PlannedMaintenanceStatsForSubscriptions_CustomerView(
    subscriptionId = "{SubscriptionId}",
    startTime      = datetime({StartTime}),
    endTime        = datetime({EndTime})
)
```

#### PM-12.Q3 — Cluster variants (use the right cluster based on region/SKU/wave)
- **Azcompute** (default) — most cases
- **AzureCMFF** — FF (fast-flush) regions
- **AzureCMBF** — BF (big-fabric) regions
- **AzcomputeMC** — MC (Maintenance Control) deployments

Replace `cluster("Azcompute")` with the appropriate one if PM-12.Q1 returns nothing.

#### PM-12.MaintenanceStatus enum (decode the result)
| Status | Meaning | Customer action |
|---|---|---|
| `MaintenanceNotPlanned` | No maintenance on this VM right now | None |
| `MaintenanceScheduled` | Maintenance pending; SSM window open | Optional: customer can self-redeploy now |
| `MaintenanceInProgress` | Fabric is executing maintenance | Wait |
| `MaintenanceCompleted` | Done successfully | None |
| `MaintenanceFailed` | Customer-initiated SSM retry failed | Retry SSM, or wait for forced window |
| `CustomerInitiatedRedeploy` | Customer triggered `Restart-AzVM -PerformMaintenance` | Wait |
| `RetryLater` | Platform busy; retry SSM later | Retry in 30 min |
| `NoActionRequired` | Maintenance is non-impactful | None |

#### PM-12.Special Situations
- **Maintenance Regressions** — Status flips back from `Completed` → `Scheduled`. Usually means a new wave covered the same VM. Treat as a new event.
- **Skipped Status** — Status was never `Scheduled` for a VM that **did** get maintained. Usually means VM was reallocated mid-window (stop/start, redeploy, service heal) and inherited a fresh host that already had the patch. No customer action.
- **Stuck in `InProgress` >24h** — Engage Planned Maintenance SMEs via Ava channel; this is abnormal.

#### PM-12.Customer-facing wording
> "Per the planned maintenance subsystem for subscription `{SubscriptionId}`, VM `{VMName}` is currently in status `{MaintenanceStatus}`. Status meaning: `{decoded above}`. {Action: …}."

---

### PM-13: Track Affected VM List (with ICM tracking ID)

> **TSG**: [Track Affected VM List_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FTrack-Affected-VM-List_Planned-Maint)
> **Scope**: Customer has an ICM Tracking ID from Service Health and wants the full impacted-VM list.

Process-only TSG (no unique KQL of its own); workflow:
1. Get the Tracking ID from the customer's Service Health alert (format `XXXX-XXX`).
2. Run **PM-2.Q1** with that Tracking ID + customer subscription list → impacted resources (forward-looking).
3. Run **PM-2.Q2** for historical confirmation if the maintenance already executed.
4. For UI verification: open https://iridias.microsoft.com/maintenance?id=`{TrackingId}` (internal Iridias) and https://portal.microsofticm.com/imp/v3/comms/trackingid/`{TrackingId}` (ICM Publisher view of the comm sent to customer).
5. Cross-link from VMs to Maintenance Status via **PM-12.Q1**.

---

### PM-14: Track Affected VM List with No ICM Tracking ID

> **TSG**: [Track Affected VM ListWithnoICM_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FTrack-Affected-VM-ListWithnoICM_Planned-Maint)
> **Scope**: Customer asks "was there any platform maintenance on my VMs?" with no Tracking ID in hand.

Process-only TSG. Workflow:
1. Run **PM-2.Q2** filtered only by `message contains "{TenantName}"` (no TrackingID) over the suspect window to discover any Decom event that touched the tenant.
2. Run **PM-10.Q3** (AlbnTargets ⨝ PublishRequest) filtered by subscription to find **any** ICM comm sent to the customer during the period — this surfaces the Tracking ID retroactively, after which you fall back to PM-13.
3. Run **PM-12.Q1** for the subscription over the window to enumerate every VM that had a non-trivial maintenance status.
4. If none of the above produces a hit, the event was either not Planned Maintenance (route via core Step 1 / VMA) or pre-dates retention (>30d).

---

### PM-15: VM Service Healed for Planned Maintenance After No Action Taken

> **TSG**: [VM Service Healed for Planned Maint After No Action Taken_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FTSGs%2FVM-Service-Healed-for-Planned-Maint-After-No-Action-Taken_Planned-Maint)
> **Scope**: VM restarted; Resource Health says "customer-initiated"; ASC `VM Availability Impacts` shows operation `VMServiceHealedAfterNoActionTaken`. The customer was notified about an HW Decom maintenance, did not act before the due date, so the fabric service-healed the VM to refreshed hardware.

#### PM-15.Q1 — VMA failure signature `CustomerInitiated.ContainerOperation.ContainerDestroyed`
```kusto
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (datetime({StartTime}) .. 10m)
| where TenantName == "{TenantName}"
| where * contains "{VMName}"
| project StartTime, EndTime, Cluster, TenantName, RCA, AnnotationType, Detail, LastEvents, ProducedBy
```
Expected RCA value: `CustomerInitiated.ContainerOperation.ContainerDestroyed DeleteTenant,True`.

#### PM-15.Q2 — Service Healing trigger events
```kusto
cluster("Azcsupfollower.kusto.windows.net").database("AzureCM").AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. 10m) and tenantName == "{TenantName}"
| project PreciseTimeStamp, tenantName, triggerId, triggerType, EventMessage
```
Expected `triggerType` values: `ClusterEvacuation` + `TargetMachinePoolMismatch`. See [Service Healing_How It Works](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1666466).

#### PM-15.Q3 — Find the scheduled maintenance ID that drove the SH
```kusto
cluster("Azcsupfollower.kusto.windows.net").database("AzureCM").ScheduledMaintenanceInformational
| where PreciseTimeStamp between (datetime({StartTime}) .. 4h) and * contains "{TenantName}" and message contains "{VMName}"
| project PreciseTimeStamp, Tenant, scheduledMaintenanceId, message
```

#### PM-15.Q4 — Resolve scheduled maintenance ID → Tracking ID (PublishRequest)
```kusto
cluster("icmcluster").database("ACM.Backend").PublishRequest
| where ExternalIncidentId == "{ScheduledMaintenanceId}"
| distinct ExternalIncidentId, IncidentId, EventStartTime, EventEndTime, RichTextMessage
```
Build the customer-visible Tracking ID URL:
- `https://iridias.microsoft.com/maintenance?id=<TRACKING-ID>` (internal)
- `https://portal.microsofticm.com/imp/v3/comms/trackingid/<TRACKING-ID>` (the comm sent to the customer)

#### PM-15.Q5 — Find the outgoing email to the customer
```kusto
cluster("Icmcluster").database("ACM.Publisher").AlbnTargets
| where Subscriptions contains "{SubscriptionIdPrefix}"
| project CommunicationId
| join cluster("Icmcluster").database("ACM.Backend").PublishRequest on CommunicationId
| where CommunicationDateTime >= datetime({StartTime})
| order by CommunicationDateTime desc
| project CommunicationDateTime, CommunicationType, Title, IncidentId, RichTextMessage
```
Customer-notification screenshots:
- Published By = `azcis@microsoft.com` → hardware decommissioning maintenance.
- Use the [Azure Communications Dashboard](https://communications.microsofticm.com/events) for tracking ID lookup.

#### PM-15.Interpretation
The Resource Health "customer-initiated" labeling is a misnomer for this scenario — it appears because the platform tears the container down (DeleteTenant=True) before redeploying on healthy hardware, which historically maps to the customer-initiated taxonomy in VMA. The actual trigger is **expired self-service window for a notified Planned Maintenance**.

#### PM-15.Customer-facing wording — RCA for Hardware Decommissioning Maintenance (post-SH-after-no-action)
> "We identified that your VM `{VMName}` became unavailable at `{StartTime}` (UTC), and availability was restored at `{EndTime}` (UTC). This expected occurrence was caused by an Azure-initiated maintenance action.
>
> Azure had previously notified impacted customers about this maintenance (TrackingID `{TrackingId}`, communication sent on `{CommunicationDateTime}`). As part of this operation, your VM experienced a reboot as it was migrated to newer hardware. RDP and SSH connections to the VM, or requests to any other services running inside the VM, could have failed during this time.
>
> We apologize for any inconvenience this may have caused. We are continuously working to improve the platform to reduce incidences of virtual machine unavailability.
>
> **Resolution**: The VMs on this node have been service-healed onto a healthy node to avoid further impact. The unhealthy node has been taken out of service for analysis and repair. Our core engineers are working to minimize such occurrences."

#### PM-15.Article / Root-Cause mapping
- GitHub Article ID: `UnexpectedVMReboot_Hardware_Decomm_Maintenance`
- Root cause path: **Windows Azure → Virtual Machines → Azure Platform → Planned Maintenance - HW Decommissioning**

---

## § LM — Live-Migration Common Reference (cross-cuts PM-5/6/7/8)

| Phase | Telemetry | Notes |
|---|---|---|
| Session creation | `LiveMigrationSessionCreatedLog` (moseisley) | `traceCode`, `migrationConstraint`, `sessionId` |
| Container/source/dest detail | `LiveMigrationContainerDetailsEventLog` (moseisley) | `sourceContainerId`, `destinationContainerId` |
| Periodic status during pre-copy | `LiveMigrationSessionStatusEventLog` (moseisley) | `statusCode`, `traceCode` |
| Session completion (final) | `LiveMigrationSessionCompleteLog` (moseisley) | `result`, `triggerType`, `blackoutTimeInMs`, `durationInMs` |
| Validation critical errors | `LiveMigrationSessionValidationCriticalEventLog` (moseisley) | Failure reasons |
| Customer-facing event surface | `AirLiveMigrationEvents` (vmainsight/vmadb) | What customer sees in ASC / Geneva |
| LM activity / duration aggregate | `LiveMigrationActivities` (vmainsight/vmadb) | Used for stats |
| LM failure aggregate | `LiveMigrationFailureEvents` (vmainsight/vmadb) | Used for stats |
| CPU capping during LM | `AirCpuCappingEvents` (vmainsight/vmadb) | Brief CPU caps applied during precopy |
| Goal-state requesting vacate | `HolmesGoalStateManagerEvent` (azcore/AzureCP) | Shows triggering subsystem |
| Node-wide vacate status | `HolmesRHMNodeVacateStatusEvent` (azcsupfollower) | All-VMs-on-node migration state |

---

## § ADH — Dedicated Host TSGs

### ADH-1: AutoManage Virtual Machines (Troubleshooting on ADH)

> **TSG**: This sub-topic is covered as part of the AutoManage stack — see ADH-4 (Automanage overview / routing) + ADH-2 (Configuration Profile deprecation errors) + ADH-3 (Forbidden error during profile creation). There is no dedicated wiki page solely for "AutoManage VMs TroubleShooting on Dedicated Host"; route to the appropriate sub-TSG.

#### ADH-1.Interpretation
For Azure VM cases that mention Automanage running on Dedicated Hosts, identify the actual symptom (config profile error → ADH-2/3, drift / status unknown → ADH-4) and follow that TSG.

#### ADH-1.Routing reminder
- Issue with **Update Management** / **Machine Configuration** / **VM Insights** / **AMA / MMA** → Azure Monitor POD.
- Issue with **Onboarding** / **Configuration Profiles** / **Result Status** → MSaaS POD Azure IaaS VM Management.
- Underlying VM agent / extension installation → Azure Arc-enabled servers (`Extensions / Extension installation or removal failed`).

---

### ADH-2: Automanage Configuration Profile Errors (Subscription state: -1)

> **TSG**: [Automanage ConfigurationProfiles Errors_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FAutomanage-ConfigurationProfiles-Errors_Dedicated-Host)
> **Scope**: Customer cannot create a new configuration profile or assign one — error `Subscription state: -1`.

#### ADH-2.Symptom
```text
An error occurred while creating the configuration profile named '<name>'.
Error details:
The operation was not allowed because the subscription is not in a state to support it. Subscription state: -1
```
Same error on assignment to a VM.

#### ADH-2.Cause
**Azure Automanage Best Practices is being retired on September 30, 2027.** Azure restricts increase in customer usage for products scheduled for deprecation. Therefore the platform blocks **new** profile creation / **new** subscription onboarding. Existing assignments continue to work until retirement.

#### ADH-2.Mitigation
- Inform customer of retirement timeline.
- Direct them to migrate to **Azure Policy** per https://learn.microsoft.com/azure/governance/policy/how-to/migrate-from-automanage-best-practices.
- No KQL required — this is a known platform behavior; no investigation needed.
- For unique customer scenarios, engage the [ADH AVA channel](https://teams.microsoft.com/l/channel/19%3A00a4d11ba47e4ef4b77877f3f09f02ac%40thread.tacv2/MGMT%20-%20Dedicated%20Host-Automanage%20(AVA)?groupId=55f6a42a-c262-4937-bf2d-d290d7037af3).

#### ADH-2.Customer-facing wording
> "The error `Subscription state: -1` when creating an Automanage configuration profile is expected behavior — Azure Automanage Best Practices is scheduled for retirement on **September 30, 2027**, and the platform no longer allows new profile creation or new subscription onboarding. To continue using the equivalent best-practices configuration, please migrate to **Azure Policy** following: https://learn.microsoft.com/azure/governance/policy/how-to/migrate-from-automanage-best-practices. Existing profile assignments remain functional until retirement."

---

### ADH-3: Automanage Forbidden Error on Log Analytics Workspace

> **TSG**: [Automanage Forbidden_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FAutomanage-Forbidden_Dedicated-Host)
> **Scope**: When creating a custom configuration profile and selecting a Log Analytics Workspace, the operation fails with `Forbidden`.

#### ADH-3.Symptom
```text
An error occurred while creating the configuration profile named '<name>'.
Error details:
An error occurred while validating the resource subscriptions/<SubId>/resourceGroups/<RG>/providers/Microsoft.OperationalInsights/workspaces/<WS>. Status code was <Forbidden>
```

#### ADH-3.Root Cause
The **Azure Automanage API Service Principal** needs **Contributor** role on the selected Log Analytics workspace. By design — PG is working on a clearer error message.

#### ADH-3.Resolution (Portal steps)
1. Log Analytics Workspace → Access Control (IAM) → Add → Add Role Assignment.
2. Select role **Contributor** (Privileged administrator role) → Next → Members.
3. Select Members → search for `Automanage API Access` service principal → Select.
4. Review and Assign.

⚠ Avoid assigning Contributor at Resource Group / Subscription level — violates least-privilege.

#### ADH-3.Customer-facing wording
> "The `Forbidden` error when selecting the Log Analytics workspace `{Workspace}` for an Automanage configuration profile is caused by missing RBAC: the `Automanage API Access` service principal requires the **Contributor** role scoped to the Log Analytics workspace. After granting that role at the workspace scope, profile creation will succeed."

---

### ADH-4: Automanage Overview / Drift Behavior / Onboarding Routing

> **TSG**: [Automanage_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FAutomanage_Dedicated-Host)
> **Scope**: Generic Automanage triage (status unknown, drift, onboarding stuck). Not really ADH-specific despite the wiki location.

#### ADH-4.Key facts
- **Drift evaluation cadence: every 6 hours.** Not trigger-based. A VM that just started may show `Unknown` for up to 6h normally.
- Automanage looks at VM instance view `vmAgent.provisioningState == Succeeded` for eligibility. A deallocated VM may still show **Eligible** because the agent state cannot be queried.
- Status `Unknown` after `>6h` usually means the **guest agent is not running / not installed**. Route to [Guest Agent Installation TSG (wiki ID 494978)](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/494978/).

#### ADH-4.Supported targets
- Azure VMs (Windows + Linux).
- Arc-enabled servers.
- **NVAs and VMSS are NOT supported.** Always confirm the target is an Azure VM.

#### ADH-4.Routing table (collab teams)
| Symptom | Owning POD |
|---|---|
| Update Management issues | Azure Monitor POD |
| Machine Configuration policies | Azure Monitor POD |
| VM Insights, Log Analytics workspace | Azure Monitor POD |
| AMA / MMA / OMS agent | Azure Monitor POD |
| Onboarding stuck / status not as expected | MSaaS POD Azure IaaS VM Management |
| Configuration Profile customization | MSaaS POD Azure IaaS VM Management |
| Arc-enabled server target issues | Azure Arc-enabled servers |
| Azure Backup integration | Azure / Azure Backup |
| Microsoft Defender for Cloud integration | Azure / MDfC / Onboarding |

#### ADH-4.ICM template
[Azure Automanage / Triage](https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=7c3P2O)

#### ADH-4.Customer-facing wording
> "Azure Automanage evaluates drift every **6 hours**, so a newly onboarded or recently restarted VM may legitimately show an `Unknown` status for up to that interval. If `Unknown` persists beyond 6 hours, the most common cause is that the Azure VM guest agent is not running or not installed — please confirm the agent's provisioning state."

---

### ADH-5: Azure Dedicated Host Unavailable / Hosts under migration

> **TSG**: [Azure Dedicated Host Unavailable_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FAzure-Dedicated-Host-Unavailable_Dedicated-Host)
> **Scope**: Customer's ADH (or VMs on it) became unavailable; ADH portal status shows `Host is under migration` / `Unavailable / Downtime / PlatformInitiated`.

#### ADH-5.Q1 — Scenario 1: Customer only has the **VM** name (not host ID) — gather fabric mapping
```kusto
cluster("azcsupfollower").database("AzureCM").LogContainerSnapshot
| where subscriptionId in ("{SubId}")
| where roleInstanceName contains "{VMNAME}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| distinct creationTime, containerId, nodeId, virtualMachineUniqueId, RegionFriendlyName, tenantName,
           dedicatedHostGroupId, dedicatedHostId
```
Use the resulting `containerId` / `nodeId` to follow [Advanced-Workflow_Restarts](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496375/Advanced-Workflow_Restarts) for the preliminary RCA on host availability.

#### ADH-5.Q2 — Scenario 2: Customer provides ADH name; look up the **host node** + lifecycle history
```kusto
cluster("azcsupfollower").database("AzureCM").LogDedicatedHostSnapshot
| where subscriptionId == "{SubId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where hostName == "{ADHName}"
| project PreciseTimeStamp, dedicatedHostId, nodeId, creationDate, hostName,
          lifecycleState, stateChangeTime, RegionFriendlyName
```
Notes:
- ASC does not directly expose the **host node ID** — only the dedicated host ID. Use this query to bridge.
- `lifecycleState` values to watch: `UnderInvestigation`, `UndergoingMigration` (problem), `Active` (healthy).
- An ADH `hostName` can map to different `nodeId`s over time (post service-healing).

#### ADH-5.Interpretation
- A single `UnderInvestigation` + `UndergoingMigration` row pair → platform is service-healing the host. Customer impact = VMs may have been restarted.
- After SH, the same `hostName` will map to a fresh healthy `nodeId`.
- Use the new `nodeId` from PM-15-style flow to chase the underlying host fault (e.g., MCE, NIC fault) via Playbook A § HW-*.

#### ADH-5.Customer-facing wording
> "Your Azure Dedicated Host `{ADHName}` became `Unavailable` at `{TIMESTAMP}` due to a platform-initiated host migration (service healing). The underlying physical node `{OldNodeId}` was taken out of service for analysis, and your dedicated host was healed onto a new healthy node `{NewNodeId}` at `{RecoveryTime}`. VMs hosted on the ADH experienced a reboot as part of the heal. The unhealthy node is being investigated and repaired."

---

### ADH-6: Dedicated HostGroup Cannot Be Deleted

> **TSG**: [Dedicated HostGroup Cannot Be Deleted_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FDedicated-HostGroup-Cannot-Be-Deleted_Dedicated-Host)
> **Scope**: Customer attempts to delete a Host Group; gets `OperationNotAllowed` because the group still contains hosts or VMs (often VMSS instances via automatic placement).

#### ADH-6.Symptom
```text
(OperationNotAllowed) Host Group '<<<Name>>>' cannot be deleted. Before deleting the host group, please ensure it does not contain any Host. Also, the host group should not contain any Virtual Machine or Virtual Machine Scale Set placed through automatic placement.
```

#### ADH-6.Q1 — Confirm the DELETE call failed with this signature
```kusto
let resuri = "/subscriptions/{SubscriptionId}/resourceGroups/{RGName}/providers/Microsoft.Compute/hostGroups/{HostGroupName}";
let sid    = replace_strings(tostring(split(resuri, "/", 2)), dynamic(['["', '"]']), dynamic(['', '']));
let rgname = replace_strings(tostring(split(resuri, "/", 4)), dynamic(['["', '"]']), dynamic(['', '']));
let dhg    = replace_strings(tostring(split(resuri, "/", 8)), dynamic(['["', '"]']), dynamic(['', '']));
let starttm = now(-2d);
let endtm   = now();
cluster("azcsupfollower2.centralus.kusto.windows.net").database("crp_allprod").ApiQosEvent_nonGet
| where PreciseTimeStamp between (starttm .. endtm) and resourceGroupName == rgname and resourceName == dhg
| where operationName == "HostGroups.ResourceOperation.DELETE" and httpStatusCode != 200
| extend json          = parse_json(errorDetails)
| extend internalerror = json["innererror"]["internalErrorCode"]
| extend code          = json["code"]
| extend msg           = json["message"]
| extend startTime     = PreciseTimeStamp - e2EDurationInMilliseconds * 1ms, completeTime = PreciseTimeStamp
| project startTime, completeTime, subscriptionId, operationName, httpStatusCode, correlationId,
          operationId, resourceGroupName, resourceName, clientRequestId, internalerror, code, Message = msg
| order by startTime desc
```
Expected `internalerror == "DedicatedHostGroupCannotBeDeleted"`, `code == "OperationNotAllowed"`, `httpStatusCode == 409`.

#### ADH-6.Q2 — Find the VMs still allocated against the Host Group
```kusto
let resuri = "/subscriptions/{SubscriptionId}/resourceGroups/{RGName}/providers/Microsoft.Compute/hostGroups/{HostGroupName}";
let sid    = replace_strings(tostring(split(resuri, "/", 2)), dynamic(['["', '"]']), dynamic(['', '']));
let rgname = replace_strings(tostring(split(resuri, "/", 4)), dynamic(['["', '"]']), dynamic(['', '']));
let dhg    = replace_strings(tostring(split(resuri, "/", 8)), dynamic(['["', '"]']), dynamic(['', '']));
let starttm = now(-2d);
let endtm   = now();
cluster("azcrpbifollower.kusto.windows.net").database("bi_allprod").VM
| where TIMESTAMP between (starttm .. endtm)
| where SubscriptionId == sid and (DedicatedHostGroupKey has rgname and DedicatedHostGroupKey has dhg)
| summarize arg_min(PreciseTimeStamp, SubscriptionId, ResourceGroupName, VMName, VMId,
                    VMTimeCreated, VMToBeDeleted, DedicatedHostGroupKey)
            by CommitSequenceNumber
```
Returns one row per VM (latest snapshot per CommitSequenceNumber). `VMToBeDeleted = False` rows are the blockers.

#### ADH-6.Interpretation
By default, deletion of dedicated hosts is **not allowed** while any VMs are allocated. Customer must reassign or move the VMs to a different ADH, **or delete the VMs first**, then re-attempt the Host Group delete.

#### ADH-6.Customer-facing wording
> "The Host Group `{HostGroupName}` cannot be deleted because it currently contains the following allocated VMs/VMSS instances:
> `{VMList}`
> Please either delete these VMs or move them to a different Dedicated Host Group before re-attempting the delete operation."

#### ADH-6.Sample ICM
- [IcM 482941534 — Unable to delete empty dedicated host group](https://portal.microsofticm.com/imp/v3/incidents/incident/482941534/summary)

---

### ADH-7: Next Forced Maintenance Date Changed to Old Date

> **TSG**: [Next forced maintenance date changed to old date_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FNext-forced-maintenance-date-changed-to-old-date_Dedicated-Host)
> **Scope**: Customer hits **Apply maintenance now** in the Dedicated Host blade and the "Next forced maintenance date" field updates to a date in the past (e.g., a year ago). Host update completes successfully — no actual customer impact, just a display anomaly during the in-progress update.

#### ADH-7.Q1 — Host update progression (BatchingRequestStatusLogETWEvent)
```kusto
cluster("Azdeployer").database("AzDeployerKusto").BatchingRequestStatusLogETWEvent
| where PreciseTimeStamp > ago(60d)
| where ResourceId == "{DedicatedHostResourceId}"  // ASC → resource explorer → DH → properties
| project PreciseTimeStamp, Region, Cluster, ResourceId, State, RequestInitiationCategory,
          EstimatedHostImpactDurationInSeconds, EstimatedHostImpact
```
Expect alternating `InProgress` → `Succeeded` rows per maintenance pass.

#### ADH-7.Q2 — Pending updates at the time of ApplyUpdates
```kusto
let _cluster   = dynamic(null);
let _startTime = datetime({StartTime});
let _endTime   = datetime({EndTime});
let _nodeid    = "{NodeId}";
cluster("Azdeployer").database("AzDeployerKusto").GetBatchNodesPendingUpdates(
    clusterStartsWith = _cluster,
    startTime         = _startTime,
    endTime           = _endTime,
    nodeId            = _nodeid
)
```
This is a Kusto function — returns per-service `PendingSince` timestamps. Old `PendingSince` for newly-added "dormant" services explains the regressed Next-Forced-Maintenance date.

#### ADH-7.Q3 — Auto-expiry recalculation events (RMOLogETWEvent)
```kusto
cluster("Azdeployer").database("AzDeployerKusto").RMOLogETWEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where Tenant == "{PMTenant}"   // e.g., "PlannedMaintenance-Prod-FRA01P"
| where RMOEventName in ("UpdateExpiryTime", "CalculatedAutoExpiryStartTimeOnNodePatrolBatchedNodes")
| where ResourceId == "{DedicatedHostResourceId}" or NodeId == "{NodeId}"
| where MonitorName == "UpdateDiscoverer"
| summarize arg_max(PreciseTimeStamp, *) by Message
| project PreciseTimeStamp, Message
```
Look for messages like `"updating expiry time to <new> (old time : <very old>)"` and `"Calculated auto-expiry start time <old date> on NodePatrol batched nodes"`.

#### ADH-7.Cause / Interpretation
The Next Forced Maintenance date is computed from the latest `ApplyUpdates` request and the earliest pending update time on the host. **A recent feature enabled tracking + updating of dormant services on the host.** Those dormant services had been staged long ago, so the calculation started using their old `PendingSince` timestamps. This **only manifests while `ApplyUpdates` is in progress** and **does not change the actual force maintenance time** — no customer impact. PG is tracking a repair item via ADO `15124080` so dormant services no longer skew the calculation.

#### ADH-7.Customer-facing wording
> "The `Next Forced Maintenance` value briefly displayed an older date for dedicated host `{HostName}` during the in-progress `Apply Updates` operation. This is a **display-only side effect** of a recently introduced feature that also tracks and updates dormant services on the host: their longer-pending timestamps were temporarily reflected in the calculation. The actual force-maintenance schedule was **not affected**, and the host update completed successfully. The engineering team is tracking a repair item to refine the calculation so dormant services no longer impact this display. No customer action is required."

#### ADH-7.Related IcM
- [IcM 323152212](https://portal.microsofticm.com/imp/v3/incidents/details/323152212/home)

---

### ADH-8: Platform Updates Caused ADH Reboot (Empty-Node Misinterpretation)

> **TSG**: [Platform Updates Caused ADH Reboot_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FPlatform-Updates-Caused-ADH-Reboot_Dedicated-Host)
> **Scope**: ADH host received a **rebootful** update (BIOS / firmware) even though customer has Maintenance Configuration attached. Known bug — the platform interpreted "VM count == 0 on the host" as an empty node and serviced it.

#### ADH-8.Symptom
Portal notification:
```text
At <Date>, the Azure monitoring system received the following information regarding your Azure Dedicated Host:
This host xxxxxx-xxx-xxxx-xxxx-xxxxxxxxxx is currently under investigation. We're working to detect and repair issues impacting the health of your host. Virtual machines may be impacted.
```

#### ADH-8.Q1 — Was the host node empty just before the update?
```kusto
cluster("azcsupfollower").database("AzureCM").LogNodeSnapshot
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where nodeId contains "{NodeId}"
| project TIMESTAMP, aliveContainerCount, alivePreemptibleContainerCount, nodeState,
          rootUpdateAllocationType, faultInfo
```
Confirm `aliveContainerCount` was momentarily `0` immediately before the update was applied.

#### ADH-8.Q2 — If customer didn't share the Node ID
Use **ADH-5.Q1** / **ADH-5.Q2** to bridge ADH name / VM name → Node ID, then run ADH-8.Q1.

#### ADH-8.Cause / Interpretation
Bug: a Dedicated Host node should **never** be interpreted as an empty node (even if VM count is zero) when an MC schedule is attached. The bug caused service healing to be triggered as if it were a regular empty node. PG tracking the fix via ADO Feature **24623603**.

#### ADH-8.Mitigation / Customer-facing wording
> "Your dedicated host `{HostName}` (node `{NodeId}`) received a platform BIOS/firmware update at `{TIMESTAMP}` that resulted in a host reboot. This update fell outside the maintenance window defined in your Maintenance Configuration. Investigation confirmed this was caused by a known platform issue (tracked under engineering work item `24623603`): when the host had `aliveContainerCount = 0` at the moment of evaluation, the system incorrectly treated it as an empty node and applied the update. Engineering is implementing a fix so that any Dedicated Host node is excluded from empty-node update handling regardless of VM count. For any follow-up RCA questions reach the [SME - Azure Dedicated Host (AVA)](https://teams.microsoft.com/l/channel/19%3a00a4d11ba47e4ef4b77877f3f09f02ac%40thread.tacv2/MGMT%2520-%2520Azure%2520Dedicated%2520Host%2520(AVA)?groupId=55f6a42a-c262-4937-bf2d-d290d7037af3&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) channel."

#### ADH-8.Reference ICMs
- [392818602](https://portal.microsofticm.com/imp/v3/incidents/details/392818602/home)
- [395456168](https://portal.microsofticm.com/imp/v3/incidents/details/395456168/home)

---

### ADH-9: ProvisioningFailedState (Dedicated Host cannot deploy VMs)

> **TSG**: [ProvisingingFailedState_DedicatedHost](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FTSGs%2FProvisingingFailedState_DedicatedHost) (note: wiki slug retains the `ProvisingingFailedState_DedicatedHost` typo)
> **Scope**: Customer cannot deploy a new VM to an Azure Dedicated Host because the host shows provisioning state `Provising Failed`.

#### ADH-9.Symptom
CRP operation signature:
```text
OperationNotAllowed/ResourceCannotBeDeployedToUnallocatedDedicatedHost
```

#### ADH-9.Scoping checklist
- When did the issue start?
- Has this ever worked the way they expect?
- Issue consistent or intermittent?
- Production or dev/test Dedicated Host?
- Issue on the Host itself, or on a VM deployment that targets the host?
- What is going on at the time of failure (specific deployment automation, backups, etc.)?

#### ADH-9.Resolution
The wiki TSG states the primary remediation is: **restart the Dedicated Host**. If the restart fails, **stop the VMs on the host first**, then restart the host.

#### ADH-9.Interpretation
The `Provising Failed` state on the host blocks new VM deployments because CRP refuses to allocate against an unallocated/failed host. A host restart re-runs the allocation/init flow and typically clears the state. If restart does not resolve, engage the [SME - Azure Dedicated Host (AVA)](https://teams.microsoft.com/l/channel/19%3ac409bf595ae5451e9d671aa74b0f4061%40thread.skype/SME%2520-%2520Azure%2520Dedicated%2520Host%2520(AVA)?groupId=90ca5c4d-946f-4250-bb79-6a51561d46e1&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) channel.

#### ADH-9.Customer-facing wording
> "The Dedicated Host `{HostName}` is in `Provisioning Failed` state, which blocks new VM deployments (CRP returns `OperationNotAllowed / ResourceCannotBeDeployedToUnallocatedDedicatedHost`). Please restart the Dedicated Host; if the restart itself fails, first stop all VMs on the host and then restart the host. The provisioning state will refresh and new VM deployments should succeed."

---

## § HOW — Operational How-Tos that appear in case work

### HOW-1: Live Migration Request

> **How-To**: [Live Migration Request_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FLive-Migration-Request_Planned-Maint)
> **Scope**: Customer wants the platform to proactively LM their VM (e.g., to drain a node before a known event).

Workflow:
1. Validate customer requirement is real (often confused with redeploy).
2. Pull `NodeId` for the VM (core Step 1).
3. File an internal request via the LM Request workflow (template in wiki).
4. Track via `LiveMigrationSessionCreatedLog` with `TriggerType == "OnDemand"` (PM-6.Q4).

### HOW-2: Live Migration Disablement Request

> **How-To**: [Live Migration Disablement Request_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FLive-Migration-Disablement-Request_Planned-Maint)
> **Scope**: Customer's workload cannot tolerate LM brownout (HPC, real-time trading) — request fabric to flag the VM as "no LM".

Workflow:
1. Set expectation: with LM disabled, **any host event becomes a reboot** instead of brownout.
2. Verify VM SKU supports the disable flag (most do; some specialized SKUs reject it).
3. File internal request; track via `KronoxVmOperationEvent` for `AllowLM = False` (see Playbook A § HW-7).

### HOW-3: VMPHU Disablement Request

> **How-To**: [VMPhu Disablement Request_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FVMPhu-Disablement-Request_Planned-Maint)
> **Scope**: Customer wants to disable VMPHU (Platform Host Update) freezes (~9s) for a specific VM.

Workflow:
1. Confirm impact tolerance: with VMPHU disabled, host-update workflow may revert to a reboot path for that node.
2. File internal request; track via `HostServiceVersionTable.Service == "VmphuSvc"` — disabled VMs should not appear in the next VMPHU wave's `AirManagedEvents` rows.

### HOW-4: Self-service Maintenance

> **How-To**: [Self service maintenance_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FSelf-service-maintenance_Planned-Maint)
> **Scope**: Customer wants to opt-in to SSM and trigger maintenance themselves within the announced window.

Workflow:
1. Confirm customer received a notification with an SSM window (PM-12 status `MaintenanceScheduled`).
2. Customer runs `Restart-AzVM -PerformMaintenance` (or `az vm perform-maintenance`).
3. Track via PM-12.Q1 → status moves to `CustomerInitiatedRedeploy` → `MaintenanceCompleted`.
4. If customer misses the window → PM-15.

### HOW-5: Maintenance Control for Platform

> **How-To**: [Maintenance Control for Platform_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FMaintenance-Control-for-Platform_Planned-Maint)
> **Scope**: Customer configures a maintenance-control configuration (`Microsoft.Maintenance/maintenanceConfigurations`) and assigns it to ADH or eligible VM SKUs.

Workflow:
1. Validate SKU eligibility — Azure Dedicated Hosts (always), Isolated VMs, VMs on DNG, plus VMs in a scale set.
2. Maintenance recurrence must be `Day`; configuration names must be unique to the resource group.
3. Confirm the `MaintenanceConfiguration` resource and assignment exist:
   ```kusto
   cluster("azcrp.kusto.windows.net").database("crp_allprod").VMApiQosEvent
   | where TIMESTAMP > ago(7d) and operationName has "MaintenanceConfiguration"
   | where subscriptionId == "{SubscriptionId}"
   ```
4. Confirm the next maintenance pass respects the configured window — track via `AzPEWorkflowEvent.WorkflowEventData.MaintenanceWindow` (PM-11.Q5).

### HOW-6: Customer Communication (ASI + standard)

> **How-To 1**: [Customer Communication_ASI_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FCustomer-Communication_ASI_Planned-Maint)
> **How-To 2**: [Customer Communication_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FCustomer-Communication_Planned-Maint)
> **Scope**: How to extract / verify the customer-facing message for a planned maintenance event (ASI = Azure Service Insights view, alternative to ICM Publisher).

Use ASI dashboard `customer-notifications` (build the link from [`../dashboards/`](../dashboards/) or open ASI manually) or the ICM query in core Step 3a (= PM-10.Q3 / PM-15.Q5). **Always** quote `JSON.Title`, `MaintenanceStartDate`, `MaintenanceEndDate` verbatim.

### HOW-7: CCOA (Critical Change Only Advisory)

> **How-To**: [Critical Change Only Advisories(CCOA)_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FCritical-Change-Only-Advisories(CCOA)_Planned-Maint)
> **Scope**: Customer received a CCOA notice (rare, used for emergency security patches) and wants to know the impact contract.

CCOA = no opt-out, no SSM window, fastest deployment cadence. Use this only to answer customer questions; do **not** suggest CCOA can be deferred — it cannot.

### HOW-8: Guest OS Enablement

> **How-To**: [Guest OS Enablement_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FGuest-OS-Enablement_Planned-Maint)
> **Scope**: PaaS Cloud Services / Worker Role / Web Role customer — Guest OS family + version + automatic update behavior.

Out of scope for IaaS VM cases unless customer mentions Cloud Services explicitly. If they do, point them to the wiki TSG verbatim.

### HOW-9: Hardware Decommissioning RCA

> **How-To**: [Hardware Decommissioning RCA_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FHardware-Decommissioning-RCA_Planned-Maint)
> **Scope**: RCA template specifically for Decom-triggered events. Use after PM-2 produces the data. Reference RCA body lives at [wiki ID 496012](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496012).

### HOW-10: RCA for DataBricks VMs

> **How-To**: [RCA for DataBricks VMs_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FRCA-for-DataBricks-VMs_Planned-Maint)
> **Scope**: RCA template specifically for Databricks workers. Use after PM-1 produces the data.

### HOW-11: List Affected VMSS instances (Planned Maint)

> **How-To**: [List Affected VMSS instances_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FHow-Tos%2FList-Affected-VMSS-instances_Planned-Maint)
> **Scope**: Same content as PM-3 but framed as a how-to script. Use PM-3 queries.

---

## § ADH-HOW — Dedicated Host operational How-Tos

### ADH-HOW-1: Deploying Dedicated Hosts
> [Deploying Dedicated Hosts_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FDeploying-Dedicated-Hosts_Dedicated-Host) — customer-facing deployment guide; quote, do not deviate.

### ADH-HOW-2: Dedicated Host SKU Retirement
> [Dedicated Host SKU Retirement_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FDedicated-Host-SKU-Retirement_Dedicated-Host) — when an ADH SKU is retired, customers must migrate to a successor SKU within the announced window; cross-link to ADH-9 if customer hits allocation failures during migration.

### ADH-HOW-3: AutoManage VMs / Migration to Azure Policy
- [AutoManage Virtual Machines_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FAutoManage-Virtual-Machines_Dedicated-Host)
- [Automange Migration to Azure Policy_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FAutomange-Migration-to-Azure-Policy_Dedicated-Host)

### ADH-HOW-4: AMA Utilization + Automanage FAQ + Troubleshooting + RG-delete
- [AMA Utilization_Automanage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FAMA-Utilization_Automanage)
- [FAQ Automanage_AGEX](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FFAQ-Automanage_AGEX)
- [Troubleshooting_Automanage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FTroubleshooting_Automanage)
- [Unable To Delete Resource Group_Automanage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FHow-Tos%2FUnable-To-Delete-Resource-Group_Automanage)

Use these as customer-facing reference; for actual investigation use ADH-1 through ADH-4.

---

## § WF — Workflow references

### WF-1: Planned Maintenance Basic Workflow
> [Basic Workflow_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FWorkflows%2FBasic-Workflow_Planned-Maint) — end-to-end PM workflow from fabric-detect → notify → execute → confirm. Quote sequence diagrams when explaining timing to customer.

### WF-2: Live Migration Basic Workflow
> [Live Migration Basic Workflow_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FWorkflows%2FLive-Migration-Basic-Workflow_Planned-Maint) — internal LM state machine (precopy → blackout → resume on dest). Use for "what does LM look like on the platform side" explanations.

### WF-3: Scheduled Events Service Workflow
> [Scheduled Events Service Workflow_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FWorkflows%2FScheduled-Events-Service-Workflow_Planned-Maint) — how AzPE workflow produces IMDS Scheduled Events. Use with PM-11.

### WF-4: ADH Basic Workflow
> [Basic Workflow_Dedicated Host](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FDedicated-Host%2FWorkflows%2FBasic-Workflow_Dedicated-Host) — ADH allocation + lifecycle workflow.

### WF-5: Planned Maintenance Messaging (RCA reference)
> [Planned Maintenance Messaging_Planned Maint](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPlanned-Maintenance%2FRCAs%2FPlanned-Maintenance-Messaging_Planned-Maint) — sample customer-facing RCA bodies. Use templates verbatim, fill placeholders from KQL.

---

## Cross-references

| Need | Reference |
|---|---|
| Core decision flow | [`playbook-D-maintenance-core.md`](playbook-D-maintenance-core.md) |
| Restart-coincident RCA | [`playbook-A-restarts-deep.md`](playbook-A-restarts-deep.md) § MAINT-1, § HW-7, § STG-3 |
| Perf-coincident RCA (freeze/brownout) | [`playbook-C-performance-deep.md`](playbook-C-performance-deep.md) § LM-Perf-1, § MAINT-Perf-1, § STG-Perf-3 |
| Cant-start/stop with maintenance lock | [`playbook-B-cant-start-stop-deep.md`](playbook-B-cant-start-stop-deep.md) § OP-Lock |
| Raw KQL — LM tables | [`azurecm-queries.md`](../catalogs/azurecm-queries.md) § Live Migration |
| Raw KQL — AzPE + GetCommunicationsForSupport | [`operations-queries.md`](../catalogs/operations-queries.md) § Maintenance & Customer Notifications, § Azure Policy Engine |
| Raw KQL — Air* tables | [`vmainsight-queries.md`](../catalogs/vmainsight-queries.md) § AirManagedEvents, § AirLiveMigrationEvents |
| Raw KQL — CRP / VMApiQosEvent / Snapshots | [`crp-queries.md`](../catalogs/crp-queries.md) |
| Raw KQL — Hardware decom | [`hardware-queries.md`](../catalogs/hardware-queries.md) |
| ADH dashboards | ASI ADH page templates under [`../dashboards/asi/pages/`](../dashboards/asi/pages/) (`adh-*`), or open ASI manually |
| Customer-facing RCA email | draft the customer RCA manually (categories: ServiceHealing, NodePause, MemoryPreserving, HardwareFault — keep internal identifiers out) |
