# Detectors — Live Migration / Service Healing

> Source: EEE RDOS Start Hub dashboard (8 queries).

Live Migration and Service Healing failure signatures. Run when LM or SH was attempted around the incident time and did not complete cleanly.

---

### IssueDetector_AzSMServiceHealing

_Purpose:_ Automated Detector

Cluster: `accp.centralus` · Database: `AZSM` · Type: `IssueDetector`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName =~ queryTenantName
| where triggerObjectId == queryContainerId
| order by PreciseTimeStamp asc
| summarize StartTime = min(PreciseTimeStamp), arg_max(PreciseTimeStamp, triggerType, faultCode, faultReason, faultCode) by triggerId
| join kind=leftouter (AzSMServiceHealingStepResultEvents
    | where PreciseTimeStamp between(queryFrom .. queryTo)
    | where tenantName == queryTenantName
    | where targetContainerId <> '00000000-0000-0000-0000-000000000000'
    | summarize EndTime = max(PreciseTimeStamp), arg_max(PreciseTimeStamp, result) by triggerId, failureReason, targetContainerId 
) on triggerId
| project StartTime, EndTime, triggerType, triggerId, faultReason, targetContainerId, result
| extend Description = strcat("VM was service healed due to ", triggerType)
| extend Severity = 'critical'
//| extend Health = iif (result != "Succeeded", "Error", "Degraded")
//| extend Content = triggerType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryContainerId}`

**Signal filters seen in KQL:** `targetContainerId <> "00000000-0000-0000-0000-000000000000"`

---

### IssueDetector_EI_NetAssistMonitorTriggers_LM

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h)
| where nodeId =~ query_NodeId and faultInfo has "Reason\":\"UnhealthyLinkWithLowSeverity" and faultInfo has "Value\":\"NetAssist" and nodeAvailabilityState == "Unallocatable"
| project PreciseTimeStamp,containerCount,nodeState,nodeAvailabilityState,faultInfo,cmNodeChannelAggregatedHealthStatus, isIsolated
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22094d0304-b537-42c7-8bc5-237aa74002a6%22%7D%7D"),"'>Emerging issue NetAssist Monitor triggers LM</a>")
| extend Severity = "Warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{query_NodeId}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LM_failure_VFPRestoreFailure_NmAgentEventDelay

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "LiveMigrationFailed Reason:VFPRestoreFailure_NmAgentEventDelay"
| join kind=inner (cluster("azcore.centralus.kusto.windows.net").database("Fc").LiveMigrationContainerDetailsEventLog
| where PreciseTimeStamp > queryFrom
| where PreciseTimeStamp < queryTo) on $left.ContainerId == $right.sourceContainerId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1, RCALevel2, sessionId
| join kind=inner (cluster("vmainsight.kusto.windows.net").database("Air").LiveMigrationActivities
| where ActivitySource in (
"ActivityStream_LiveMigration_HyperVBlackoutStartEventDelay",
"ActivityStream_LiveMigration_NmAgentVfpDeserializationTime",
"ActivityStream_LiveMigration_NMAgentVfpRestoreEventDelay",
"ActivityStream_LiveMigration_NMAgentVfpSerializationStartDelay",
"ActivityStream_LiveMigration_NMAgentVfpSerializeTransferTime",
"ActivityStream_LiveMigration_VfpPollingDelay")
| where ActivityStart >= queryFrom and ActivityEnd <= queryTo
| extend Durationinsec = Duration / 1s
| project SessionId, ActivityStart, ActivityEnd, ActivityName, ActivityImpact, Durationinsec
| where Durationinsec > 5) on $left.sessionId == $right.SessionId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1, RCALevel2, sessionId, ActivityStart, ActivityEnd, ActivityName, ActivityImpact, Durationinsec
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22491dfd95-3271-4e2e-971f-e658b6d36d12%22%7D%7D"),"'>Emerging issue LM failure due to VFPRestoreFailure_NmAgentEventDelay</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenant}`, `{queryvirtualMachineUniqueId}`, `{query_NodeId}`, `{querytenantName}`, `{querycontainerId}`, `{queryroleInstanceName}`, `{querySubscription}`

---

### IssueDetector_EI_LM_VFPRestoreFailure_Deserialization_Issue_Port

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `IssueDetector`

```kusto
LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo) and NodeId == queryNodeId and RoleInstanceName == queryVMName and RCALevel2 == "VFPRestoreFailure_Deserialization_Issue_Port_0x51a"
| project EventTime, Cluster, RCALevel1, ObjectId, NodeId, RCALevel2, RoleInstanceName, Customer, EscalateTo
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryVMName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e8a73279-3d11-4bea-a464-d5791d6a77be%22%7D%7D"),"'>Emerging issue LM:VFPRestoreFailure_Deserialization_Issue_Port_0x51a</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryVMName}`, `{querycontainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LM_SH_due_to_NVMe_Device_End_of_Life

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 4h) and nodeId == queryNodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "0030 Generic NVMe SSD End of Life Rule" and faultInfo has "32038"
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2205754247-c1c2-457d-b283-cc3c04ba6275%22%7D%7D"),"'>Emerging issue LM / SH due to NVMe Device End of Life</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LMFailed_FlexibleIODeviceRestore

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "Flexible IO Device Restore Failure"
| distinct  PreciseTimeStamp,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e546ce07-6b37-411e-b9a2-07c7a458c9bd%22%7D%7D"),"'>Emerging issue LiveMigrationFailed due to Flexible IO Device Restore Failure</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "VFPRestoreFailure_Serialization_Issue_0x5aa"
| distinct  PreciseTimeStamp,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2259fa4d3a-d620-4990-a50d-1e5cc8a7374f%22%2C%2207ff4c83-42c2-4b33-8bcf-26d9a4766ae5%22%3A%220f0ed074-9310-4bc7-a852-769018b665e3%22%7D%7D"),"'>Emerging issue LM failure VFPRestoreFailure SerializationIssue 0x5aa</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa_2

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `IssueDetector`

```kusto
LiveMigrationFailureEvents
| where EventTime >=queryFrom and EventTime < queryTo
| where (ObjectId == queryContainerId or VirtualMachineUniqueId == queryvirtualMachineUniqueId) and RCALevel2 =="VFPRestoreFailure_Serialization_Issue_0x5aa"
| project SessionId = tostring(Diagnostics.SessionId),LMStartTime=todatetime(Diagnostics.LiveMigrationStartTime),LMEndTime = EventTime, IsLMSuccessful = false,RoleInstanceName, FailureReason=RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2259fa4d3a-d620-4990-a50d-1e5cc8a7374f%22%2C%2207ff4c83-42c2-4b33-8bcf-26d9a4766ae5%22%3A%224592b02e-7455-4354-a445-3ec3b10f6d1e%22%7D%7D"),"'>Emerging issue LM failure VFPRestoreFailure SerializationIssue 0x5aa</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryvirtualMachineUniqueId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryNodeId}`, `{queryTenant}`

---
