# Action categories during PutVmss operation for existing resources

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Action categories during PutVmss operation for existing resources** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssActionsPerSub

_Widget purpose:_ Action categories during PutVmss operation for existing resources

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Action categories during PutVmss operation for existing resources`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let location = region;
let subId = sub;
let q=WriteOperationResponseEtwEvent
| where PreciseTimeStamp  between (startTime .. endTime)
| where Region == location
| where OperationName == "PutVMScaleSetOperation"
| where SubscriptionId == subId
| where HttpStatusCode == "OK"
| distinct  OperationId;
FrontendOperationEtwEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region == location
| where SubscriptionId == subId
| where OperationId  in (q)
| extend isCou = iff (EventCode == "VmssOperationIsComputeOnlyUpdate", 1, 0) 
| extend isNotCou = iff (EventCode == "VmssOperationIsNotComputeOnlyUpdate", 1, 0) 
| extend isElasticVmss = iff (Message startswith "checkComputeOnlyUpdateWithoutSubLockEnabled:" and Message contains "isElasticVmss:True", 1, 0)
| extend isScaleUp = iff (Message contains "VMSS is getting scaled up", 1, 0)
| extend isScaleDown = iff (Message contains "VMSS is getting scaled down", 1, 0)
| extend instancesDiffer = iff (Message contains "Complete PutVMScaleSet operation. Existing and goal VMSS instances differ.", 1, 0)
| extend tagsChanged = iff (Message startswith "resourceTagsChanged: " and Message contains "resourceTagsChanged: True", 1, 0)
| extend tenantChanged = iff (Message startswith "Instance " and Message contains "moved from tenant",1 , 0)
| extend isMigrationOperation = iff (Message  startswith "isCompleteOperationRequired:" and Message contains "isMigrationOperation: True", 1, 0)
| extend lbUndergoingMigration = iff (Message startswith "vmssNetworkingUpdateRequired" and Message startswith "vmssNetworkingUpdateRequired" and Message contains "loadBalancersUndergoingMigrationFromNicBasedToIpBased: true", 1, 0)
| extend failedPS = iff (Message contains "existingResource.ProvisioningState: Failed", 1, 0)
| extend isMultiTenantChanged = iff (Message  startswith "isCompleteOperationRequired:" and Message contains "isMultiTenantChanged: true", 1, 0)
| extend VMUpdateGroupChange = iff (Message  startswith "shouldUpdateNetworkProfileOfVmss:" and Message contains "vmInstancesMovedAcrossUpdateGroups: True", 1, 0)
| extend EmptyUGMismatch = iff (Message contains "Update groups mismatch. VMSS resource needs to be updated.", 1, 0)
| extend newUGAdded = iff (Message startswith "New update group ", 1, 0)
| extend newFPVmss = iff (Message contains "Creating new VMSS with IsFastPathVmss flag set to True.",1, 0)
| extend UGProfileMismatch = iff (Message contains "Network profile for update group " and Message contains "mismatch", 1, 0)
| extend networkProfileUpdate = iff (Message contains "Network profile for instances ", 1, 0)
| summarize PutVmssOps = dcount(OperationId), 
    ComputeOnlyUpdates= sum(isCou),
    ScaleUpOps = sum(isScaleUp), 
    ScaleDownOps = sum(isScaleDown),
    NetworkProfileUpdateOps = sum(networkProfileUpdate),
    VmsMovedAcrossUpdateGroups = sum(VMUpdateGroupChange),
    TagsChanged = sum(tagsChanged),
    TenantsChanged = sum(tenantChanged),
    EmptyUpdateGroupCountMismatch = sum(EmptyUGMismatch),
    FailedProvisioningState = sum(failedPS)
    by bin(PreciseTimeStamp, 5m)
    | render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{sub}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `HttpStatusCode == "OK"`

---
