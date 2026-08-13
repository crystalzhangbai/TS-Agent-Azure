# Detectors — Host Crash / Bugcheck

> Source: EEE RDOS Start Hub dashboard (8 queries).

Host OS bugcheck / kernel crash / power-loss signatures. Run these when the host node rebooted unexpectedly or VMs on a node all went down together.

---

### IssueDetector_SoC_Crash

_Purpose:_ Automated Detector

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`

```kusto
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;
let socID = toscalar(cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').GetSocOrNodeFromResourceId(_NodeId));
let SocName = toscalar(
    cluster('Azuredcm').database('AzureDCMDb').dcmInventoryMachines
    | where AzureNodeId =~ socID
    | project MachineName);
let socdumps=cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2
    | extend CrashTimeDt = PreciseTimeStamp
    | where PreciseTimeStamp >= _startTime and PreciseTimeStamp <= _endTime
    | where apMachine =~ SocName;
socdumps
| where socID != "00000000-0000-0000-0000-000000000000" and apMachine endswith "SOC"
| project CrashTimeDt, process
| take 1
| extend Severity = "Critical"
| extend Title = strcat("Crash found: ",process)
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/VM%20Availability?containerId=",queryContainerId,"&nodeId=",queryNodeId,"&Tenant=",queryCluster,"&tenantName=",queryTenantName,"&virtualMachineUniqueId=",queryVmId,"&roleInstanceName=",queryRoleInstanceName,"&globalFrom=",queryStart,"&globalTo=",queryEnd,"&__userData=%7B%22nodeData%22%3A%7B%22d30a6308-e96a-4b4f-8788-0848ca12e329%22%3A%223d9520f4-d3e4-4bf1-aaea-dd1f44714c31%22%2C%22e5e26ca1-7248-4667-8318-673024d48eee%22%3A%22a2bafed4-b13d-4719-b6d0-c58ddea78a39%22%7D%7D"),"'>Check VM General Availability Page-Network-SOC for details</a>")
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryNodeId}`, `{queryContainerId}`, `{queryCluster}`, `{queryRoleInstanceName}`, `{queryTenantName}`, `{queryVmId}`

**Signal filters seen in KQL:** `socID != "00000000-0000-0000-0000-000000000000"`

---

### IssueDetector_EI_node_bugcheck_0x50_netdatapath

_Purpose:_ Automated Detector

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `IssueDetector`

```kusto
let QueryFilterByNodeId = cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId =~ queryNodeId;
QueryFilterByNodeId
| summarize count()
| extend OverlakeState = iff(count_ == 0, "Not Enabled", "Enabled")
| project OverlakeState, NodeId = tolower(queryNodeId)
| join kind=leftouter (QueryFilterByNodeId) on NodeId
| project OverlakeState, QNodeId=NodeId, SocNodeId
| join kind=inner
(cluster("azcore.centralus.kusto.windows.net").database("OvlProd").OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where EventType == "versionswitch" and ServiceName == "netdatapathagent"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)
| project-rename UpdateTimestamp = StartTime) on $left.SocNodeId == $right.NodeId
| join kind=inner
(cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h)) and ContainerId == queryContainerId
| where CadPrimaryKey contains "LegacyHB"
| where RCAEngineCategory <> "CustomerInitiated"
| where RCALevel2 contains '0x00000050' or RCALevel2 contains 'WRONG_SYMBOLS'
| project-rename IssueTimestamp = PreciseTimeStamp) on $left.QNodeId == $right.NodeId
| where (IssueTimestamp - UpdateTimestamp) between (0min .. 5min)
| project UpdateTimestamp, ServiceName, EventType, detail, IssueTimestamp, NodeId, ContainerId, RCALevel1, RCALevel2, RCALevel3
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222bac6a78-fe94-4269-ac0c-482d7b6091cc%22%7D%7D"),"'>Emerging issue ode bugcheck 0x50 (PAGE_FAULT_IN_NONPAGED_AREA) in netdatapathagent_1908_app_model_5_0_5_12_v_5_0_0_441</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `EventType == "versionswitch"` · `CadPrimaryKey contains "LegacyHB"` · `RCAEngineCategory <> "CustomerInitiated"` · `RCALevel2 contains "0x00000050"`

---

### IssueDetector_EI_Node Crash_due_to_0xBC0000D6_BlobCache!BcRefere

_Purpose:_ Automated Detector

Cluster: `azurewatsoncustomer.kusto.windows.net` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. 2h)
| where nodeIdentity == queryNodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=inner(
    CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (queryFrom .. 2h) and bucketString == "0xBC0000D6_BlobCache!BcReferenceTailPfnList"
) on dumpUid
| distinct crashTime, nodeIdentity, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, dumpUid
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%220a5dc75c-6b0a-453a-bc3a-ac60eb3a3fa3%22%3A%22b1aad33d-2e5c-4e1f-9563-7216117bf363%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%223a48a195-878c-4e4e-960b-b8ef08bcd28c%22%7D%7D"),"'>Emerging issue Node Crash due to 0xBC0000D6_BlobCache!BcReferenceTailPfnList</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryNodeId}`, `{queryContainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_node bugcheck_0xd1_AV_blobcache!BcPfnReferenc

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 ==  "AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex"
| distinct  PreciseTimeStamp,NodeId, RoleInstanceName,RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%220d346752-05aa-4cf5-8756-dade446c1474%22%7D%7D"),"'>Emerging issue node bugcheck 0xd1 AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOve

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
VMA
| where PreciseTimeStamp between(queryFrom .. queryTo) and RCALevel1 =="HostOSCrash" and RCALevel2 == "AV_Barbera!HbLldCompleteIrpOverlay"
| where (isnotempty(queryvirtualMachineUniqueId) and VmUniqueId == queryvirtualMachineUniqueId) or (isempty(queryvirtualMachineUniqueId) and ContainerId == querycontainerId)
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22c72ff279-86b1-49be-9429-9b66fcc1ae4d%22%7D%7D"),"'>Emerging issue node bugcheck 0xd1 - AV_Barbera!HbLldCompleteIrpOverlay</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvirtualMachineUniqueId}`, `{querycontainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{query_NodeId}`, `{queryTenant}`

---

### IssueDetector_Sudden_Power_Loss_of_host_node

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == _nodeId
| where EventId == 41 and ProviderName == "Microsoft-Windows-Kernel-Power"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = "Sudden power loss of host node logged"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---

### IssueDetector_EI_VMA_bugcheck_0x20001_HYPERVISOR_ERROR

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
cluster("https://vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between (queryFrom .. queryTo) and RCALevel1 == "HostOSCrash" and RCALevel2 == "BugCheckCode: 0x20001"
| where (isnotempty(queryvirtualMachineUniqueId) and VmUniqueId == queryvirtualMachineUniqueId) or (isempty(queryvirtualMachineUniqueId) and ContainerId == queryContainerId) 
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222b05cdb1-caf3-4d79-b5f1-d29cd1f5507b%22%2C%22c7defa0d-c1c4-4330-81b4-1ff67c1ad342%22%3A%224a61be78-02f0-422e-aa82-62f3358fceaf%22%7D%7D"),"'>Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvirtualMachineUniqueId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryNodeId}`, `{queryTenant}`

---

### IssueDetector_EI_AW_bugcheck_0x20001_HYPERVISOR_ERROR

_Purpose:_ Automated Detector

Cluster: `azurewatsoncustomer.kusto.windows.net` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo + 10h)
| where nodeIdentity == queryNodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=inner (CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (queryFrom .. queryTo + 10h) and bucketString has "NOBLOB_HYPERVISOR_ERROR_Unhandled_PageFault") on dumpUid
| distinct PreciseTimeStamp,crashTime, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, bugLink, dumpUid
| sort by crashTime asc
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222b05cdb1-caf3-4d79-b5f1-d29cd1f5507b%22%2C%22c7defa0d-c1c4-4330-81b4-1ff67c1ad342%22%3A%22d4e88a82-7e43-45bf-a410-4d6271c7e614%22%7D%7D"),"'>Emerging issue Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryNodeId}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---
