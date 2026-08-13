# (top-level)

> Source: **EEE RDOS - Issue Detectors** dashboard, chapter **(top-level)** (4 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### IssueDetector_EI_CreateContainer Fails with 0xc3510224:VMAL_ASAP

Cluster: `azcsupfollower.kusto.windows.net` · Database: `AzureCM` · Type: `IssueDetector` · Widget: `Query`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h)
| where nodeId == querynodeid and faultInfo has "0xc3510224  VMAL_ASAPPF_NOT_RUNNING" 
| project querySubscription,PreciseTimeStamp, roleInstanceName,virtualMachineUniqueId,tenantName,Tenant, containerId,nodeId, containerState, containerOsState, containerIsolationState, containerLifecycleState, actualOperationalState, vmExpectedHealthState, faultInfo
| summarize arg_max(roleInstanceName,virtualMachineUniqueId,tenantName,Tenant, containerId,nodeId, faultInfo,containerState, containerOsState, containerIsolationState, containerLifecycleState, actualOperationalState, vmExpectedHealthState,querySubscription) by bin(PreciseTimeStamp,5m)
//| extend uri = strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",nodeId,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22903e7516-00fb-498a-8dd7-daded397a13e%22%7D%7D")
|extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",nodeId,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22903e7516-00fb-498a-8dd7-daded397a13e%22%7D%7D"),"'>Emerging issue 0xc3510224  VMAL_ASAPPF_NOT_RUNNING</a>")
|extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querynodeid}`, `{querySubscription}`

---

### IssueDetector_EI_HostAgentUpdate_to_may2024_causes_NodeFaults

Cluster: `azurecm` · Database: `AzureCM` · Type: `IssueDetector` · Widget: `Query`

```kusto
cluster('azcsupfollower').database('AzureCM').ServiceVersionSwitch 
| where NodeId == queryNodeId and PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h)) and ServiceName == "RdAgentUpdater" and CurrentVersion == "r_mar_2024_151_24_3_135" and NewVersion == "r_may_2024_151_24_5_102"
| project-rename UpdateTimestamp = PreciseTimeStamp
| join kind=inner
(cluster('azcsupfollower').database('AzureCM').TMMgmtNodeEventsEtwTable
| where TIMESTAMP between ((queryFrom - 1h) .. (queryTo + 1h)) 
| where Message has 'C351023D' and Message has 'AgentEnteredFaultedMode' and Message has 'Setting node Fault'
| project-rename NodeFaultTimestamp = PreciseTimeStamp) on NodeId
| where (NodeFaultTimestamp - UpdateTimestamp) between (0min .. 30min)
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",VMId,"&query_cluster=",queryCluster,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22789074c2-e4fb-48ab-a56e-9664e4cbe0fa%22%7D%7D"),"'>Emerging issue HostAgentUpdate to may2024 causes NodeFaults</a>")
| extend Severity = "critical"
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySubscription}`, `{roleInstanceName}`, `{containerId}`, `{tenantName}`, `{VMId}`, `{queryCluster}`

**Signal filters seen in KQL:** `Message has "C351023D"`

---

### IssueDetector_EI_Memory_Leak_caused_by_0RDN

Cluster: `gandalf.kusto.windows.net` · Database: `gandalf` · Type: `IssueDetector` · Widget: `Query`

```kusto
LeakDetection_MemoryUsageAnomaly
| where TIMESTAMP between ((queryFrom - 4h) .. (queryTo + 4h))
| where NodeId == query_NodeId and Component == "0RDN" and Severity > 1
| project TIMESTAMP, NodeId, Severity, Type, Component
| join (cluster("Gandalf").database("gandalf").LeakDetection_NodeMemoryUsageSnapshot
| where TIMESTAMP between ((queryFrom - 4h) .. (queryTo + 4h))
| where isnotnull(CommitLimit) and AvailableMemoryMB <= 6000
| extend AvailableCommitMB = (CommitLimit - CommittedBytes) / 1024 / 1024
| extend PlotSource = "AvailableCommit"
| extend MemoryDeltaMB=(AvailableMemoryMB-AvailableCommitMB)) on $left.NodeId == $right.NodeId
| project PlotTime = TIMESTAMP, AvailableMemoryMB, AvailableCommitMB, MemoryDeltaMB, PagedPoolTotalMB, NonPagedPoolTotalMB, Severity, Type, Component
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%227a5d7b50-9452-4b73-95ac-63fdcb462e78%22%7D%7D"),"'>Emerging issue Memory Leak caused by 0RDN</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_SyncPolicy_ClientFailedOrMissingSignalVmphuSvc*

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector` · Widget: `Query`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").NodeServiceEventEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == NodeID
| where Cluster == cluster
| where Message has "SyncPolicy_ClientFailedOrMissingSignalVmphuSvcPolicy_BlockCreate_OneDeploy"
| project PreciseTimeStamp, NodeId, Message
| join kind=inner (cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerHealthSnapshot
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where containerId =~ containerId 
| summarize CountContainerStart = countif(containerState == "ContainerStateStarted") by nodeId) on $left.NodeId == $right.nodeId
| where CountContainerStart == 0
| project PreciseTimeStamp, NodeId, containerId, Message, CountContainerStart
| take 1
|extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",NodeID,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",cluster,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22a6aa1140-3c31-4170-b59f-c0a980391017%22%7D%7D"),"'>Emerging issue SyncPolicy_ClientFailedOrMissingSignalVmphuSvcPolicy_BlockCreate_OneDeploy</a>")
|extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{NodeID}`, `{roleInstanceName}`, `{tenantName}`, `{virtualMachineUniqueId}`, `{cluster}`, `{querySubscription}`

**Signal filters seen in KQL:** `Message has "SyncPolicy_ClientFailedOrMissingSignalVmphuSvcPolicy_BlockCreate_OneDeploy"`

---
