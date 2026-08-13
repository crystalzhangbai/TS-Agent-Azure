# Detectors — Other / Uncategorized

> Source: EEE RDOS Start Hub dashboard (2 queries).

Detectors that did not match any specific group.

---

### IssueDetector_EI_EQ stuck_on_EQn_0x4

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where NodeId =~ query_NodeId
| where EventId == 20 and ProviderName == "mlnx5"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%227cd435d3-8b55-432c-a24b-8d95455f2dcd%22%7D%7D"),"'>Emerging issue EQ stuck on EQn 0x4</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_Standard_ND96isr_H100_v5_HardwareFault_pCIfata

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between (queryFrom .. 2h)
| where RoleInstanceName == queryroleInstanceName and RCA_CSS == "Unplanned.HardwareFault.pCIfatal"
| join kind=inner 
(cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogContainerSnapshot
| where containerType == "Standard_ND96isr_H100_v5") on $left.ContainerId == $right.containerId
| join kind=inner 
(cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h)
| where faultInfo has "pCIfatal") on $left.NodeId == $right.nodeId
| project PreciseTimeStamp, Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCALevel1, RCALevel2, RCALevel3, RCA_CSS, containerType, faultInfo
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22a50c26bb-f673-4f43-a409-e849e4d0f84b%22%7D%7D"),"'>Emerging issue Standard_ND96isr_H100_v5 HardwareFault.pCIfatal</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryroleInstanceName}`, `{querySubscription}`, `{querycontainerId}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `containerType == "Standard_ND96isr_H100_v5"` · `faultInfo has "pCIfatal"`

---
