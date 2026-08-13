# Detectors — SoC / Overlake / FPGA

> Source: EEE RDOS Start Hub dashboard (2 queries).

Smart-NIC / Overlake host networking / FPGA-related signatures.

---

### IssueDetector_SoC_Update

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `IssueDetector`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where NodeId =~ querySocNodeId 
| where EventType == "versionswitch"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, NodeId, MachineName, Cluster
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1206867/Host-Network-Investigation_Restarts?anchor=soc-investigation"),"'>Use TSG for SoC Update</a>")
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"`

---

### IssueDetector_EI_Backplane_service_crash_on_SoC_impacts_VM

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

```kusto
VMA 
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where Subscription =~ querySubscriptionId and RoleInstanceName has queryVMName and RCALevel2 == "backplane deadlocked"
| join kind=inner(cluster("Gandalfdeepad.kusto.windows.net").database("gandalf_deepAD").GetSocCrashData()
| where PreciseTimeStamp between (queryFrom .. 2h)
| where bucketString contains "LINUX_SIGNAL_SIGABRT_CODE_0xfffffffa_e0534947_vfp.so!"
| where (faultingProcess contains 'dpdk' or faultingProcess contains "vfp" or faultingProcess contains 'netdatapath'))on $left.NodeId == $right.NodeId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS, bucketString
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscriptionId,"&query_VMName=",queryVMName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e5c1985f-06f5-4a6b-8956-574d54df8ab9%22%7D%7D"),"'>Emerging issue Backplane service crash on SoC impacts VM accessibility</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querycontainerId}`, `{querySubscriptionId}`, `{queryVMName}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `bucketString contains "LINUX_SIGNAL_SIGABRT_CODE_0xfffffffa_e0534947_vfp.so!"`

---
