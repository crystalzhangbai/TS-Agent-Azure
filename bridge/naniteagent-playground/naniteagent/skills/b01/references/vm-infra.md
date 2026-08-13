---
description: KQL queries for Azure VM troubleshooting from B01 dashboard: VM lifecycle, host health, availability, platform events, GuestAgent, serial console. Find the guest OS Linux distribution and version for a VM.
---

# VM Dashboard Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: VM-Dash

## VM-Dash

### VM under this Subscription

```kql
//forpageview
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/vm-dash";
//forpageview
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let CA=CustomerAddress;
let CAss="x.x.x.x";
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| where shoeboxMdmAccountName != ""
| extend shoe = trim(" ", shoeboxMdmAccountName)
| distinct Region, shoeboxMdmAccountName=shoe);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 2h  and PreciseTimeStamp <= endtime
| where subscriptionId == SubIdOrContainerIdx or containerId == SubIdOrContainerIdx
| distinct roleInstanceName,subscriptionId, Tenant, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType=tostring(split(billingType, "|")[0]),VMSize=tostring(split(billingType, "|")[1]), Region,creationTime, DataCenterName
| join kind=inner (cluster("vnetkusto.northcentralus").database("veritas").ContainerInformationEvent | where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime) on $left.containerId == $right.ContainerId
| join kind=leftouter cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2 on $left.nodeId == $right.NodeId
| distinct roleInstanceName, subscriptionId,Tenant, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress=tostring(split(PortId, "_")[1]), SocNodeId,DataCenterName
//| join kind=inner (cluster('genevareference.westcentralus').database('AzureGraph').LogicalNetwork_NetworkInterface  | where SubscriptionId == SubscriptionID
// ) on $left.MACAddress == $right.MacAddress
//| distinct roleInstanceName, Tenant, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress, CA=tostring(parse_json(PrivateIPAddress)),SocNodeId,DataCenterName
| join kind=inner ShoeBoxMdm on $left.Region == $right.Region
| distinct roleInstanceName, Tenant,Tenantlower=tolower(Tenant), subscriptionId, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress, CA="-",SocNodeId,DataCenterName,shoeboxMdmAccountName
//| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster //Remove this line on 10/9. 
| join kind=inner (cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() | extend Tenant=tolower(Cluster)) on $left.Tenantlower == $right.Tenant  //Add this line on 10/9. 
| extend VFPDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPDropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SupportDashBoard=strcat("https://portal.microsoftgeneva.com/s/9FDB0A67?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend GFTDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/FpgaDashboardGft/FpgaDashboardGftv3?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FPGADashboard=strcat("https://portal.microsoftgeneva.com/s/C700B706?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend InvestigateNode=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", containerId, "&p-_ICMId=all#2f4843e6-c1e5-4564-ad27-cde71cebc7c7")
| extend NodeDash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-nodeid=v-", nodeId, "#805057f2-367d-4cb7-9986-89fbd2533f94")
| extend ASIHostNode=strcat("https://azureserviceinsights.trafficmanager.net/view/services/Azure%20Host/pages/Azure%20Host%20Node?nodeId=",nodeId,"&globalFrom=",format_datetime(starttime, 'yyyy-MM-dd'),"T",format_datetime(starttime, 'HH'), "%3A",format_datetime(starttime, 'mm'), "%3A51.000Z&globalTo=",format_datetime(endtime, 'yyyy-MM-dd'),"T",format_datetime(endtime, 'HH'), "%3A",format_datetime(endtime, 'mm'),"%3A51.000Z")
| extend NetVMA=strcat("https://aka.ms/netvma/?destValue=&pathQuery=false&sdnPath=false&showPingMesh=false&startTime=", format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "&endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH:mm:ss'), "&value=", containerId)
| extend PerVMAvailability=strcat("https://portal.microsoftgeneva.com/s/A03537E6?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VNETAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerProcessorPNICDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/PerProcessorNdisDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VMPerf=strcat("https://portal.microsoftgeneva.com/dashboard/RDOS/Shoebox/VMPerf-WithParameters?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",shoeboxMdmAccountName,"%22},{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22", virtualMachineUniqueId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPFullRule=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-rule%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend ListUnifiedFlow=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-unified-flow%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend KernaCaptureForNonOverLakeNode=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=datapath-operations&group=Kerna&operationId=Kerna&operationName=ExecuteKerna&inputMode=single&params={%22smeicmidparameter%22:%22264396857%22,%22smerunidparameter%22:%22",new_guid(), trim("_", roleInstanceName),"%22,%22smetargetsparameter%22:%22[{%5c%22TargetType%5c%22:%5c%22Node%5c%22,%5c%22TargetId%5c%22:[%5c%22",nodeId,"%5c%22],%5c%22TargetMetadata%5c%22:{%5c%22ClusterName%5c%22:%5c%22", Tenant, "%5c%22}}]%22,%22smejobspecificationparameter%22:%22[[{%5c%22type%5c%22:%5c%22host_capture%5c%22,%5c%22parameters%5c%22:{%5c%22duration_in_seconds%5c%22:60,%5c%22max_size_in_mbs%5c%22:2048,%5c%22output_name%5c%22:%5c%22host_capture_0%5c%22,%5c%22cmdline_args%5c%22:%5c%22provider%3DMicrosoft-Windows-Hyper-V-Vmswitch%20provider%3DMicrosoft-Windows-Hyper-V-Vfpext%20capture%3Dyes%20persistent%3Dyes%20report%3Ddis%20corr%3Ddis%20overwrite%3Dyes%20PacketTruncateBytes%3D300%20capturetype%3Dboth%5c%22}},{%5c%22type%5c%22:%5c%22fpga_capture%5c%22,%5c%22parameters%5c%22:{%5c%22duration_in_seconds%5c%22:60,%5c%22max_size_in_mbs%5c%22:2048,%5c%22output_name%5c%22:%5c%22fpga_capture_0%5c%22,%5c%22cmdline_args%5c%22:%5c%22-capture%20-parse%20-bytesPerPkt%20256%20-KbytesToCap%20circular%20-pcapCfg%20BOTH_NIC_TOR%20-fileName%20FPGACapture01%5c%22}},{%5c%22type%5c%22:%5c%22nvspinfo%5c%22,%5c%22parameters%5c%22:{%5c%22cmdline_args%5c%22:%5c%22-V%5c%22,%5c%22output_name%5c%22:%5c%22nvspinfo%5c%22}},{%5c%22type%5c%22:%5c%22vfpctrl%5c%22,%5c%22parameters%5c%22:{%5c%22cmdline_args%5c%22:%5c%22/list-vmswitch-port%5c%22,%5c%22output_name%5c%22:%5c%22vmswitch_ports%5c%22}},{%5c%22type%5c%22:%5c%22vfpctrl%5c%22,%5c%22parameters%5c%22:{%5c%22cmdline_args%5c%22:%5c%22/port%20External_", MACAddress, "%20/list-unified-flow%5c%22,%5c%22output_name%5c%22:%5c%22list-unified-flow%5c%22}}]]%22,%22smekernavepathparameter%22:%22orchestrationpolicy%5c%5cOaas%5c%5cVirtualEnvironments%5c%5cHostNetworking%5c%5cKerna%22}&actionEndpoint=Kerna&genevatraceguid=47e380be-c490-4ccb-ab52-8858bf881502")
| project CreationTime=creationTime,Name=roleInstanceName, Region,NodeDash, AvailabilityZone, ClusterName=Tenant, NodeId=nodeId, ContainerID=containerId, VirtualMachineUniqueId=virtualMachineUniqueId, OSType, VMSize, CA,MACAddress,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,KernaCaptureForNonOverLakeNode, CAandMAC=strcat(CA, " ----> ", MACAddress),SocNodeId,DataCenterName,subscriptionId
| summarize CAandMAC = replace(@"\\", "", tostring(make_list(CAandMAC))) by CreationTime, Name, Region,AvailabilityZone, ClusterName, NodeId, ContainerID,DataCenterName,VirtualMachineUniqueId,OSType, VMSize,SocNodeId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode,NodeDash, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,KernaCaptureForNonOverLakeNode,subscriptionId
| extend ProcessTupleOutbound=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", ClusterName, "%22,%22smenodeidparam%22:%22", NodeId, "%22,%22smecontaineridparam%22:%22", ContainerID,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22process-tuples%22,%22smevfpfilteroptionsparam%22:%22\\%226%20", CAss, "%201234%208.8.8.8%20443%20out%201\\%22%22}&actionEndpoint=Production&genevatraceguid=6138abc0-1c93-4b03-bf62-a63eaa6d9ad2")
| extend VMCRUD=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-SubscriptionID=", subscriptionId,"&p-ResourceURI=v-", trim("_", Name), "&p-CorrelationId=v-CorrelationRequestId&p-HttpMethod=all&p-taskname=v-HttpIncomingRequestStart#d1d4e231-22ae-4d17-95f9-eecac5ed1695")
| project CreationTime,Name, Region, AvailabilityZone, ClusterName, NodeId, SocNodeId, ContainerID, NodeDash,VirtualMachineUniqueId, OSType, VMSize, CAandMAC,VFPDashBoard,VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound,KernaCaptureForNonOverLakeNode,DataCenterName,VMCRUD
| summarize CAandMACs = replace(@"\\", "", tostring(make_set(CAandMAC))), ProcessTupleOutbounds=make_set(ProcessTupleOutbound)[0], HostCaptureForNonOverLakeNode=make_set(KernaCaptureForNonOverLakeNode)[0] by CreationTime,Name, Region, AvailabilityZone, ClusterName, NodeId, SocNodeId, ContainerID, VirtualMachineUniqueId, OSType, VMSize,VFPDashBoard,VFPDropDashBoard, DataCenterName,SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,NodeDash,VMCRUD
| extend IsOverLake=iff(isempty(SocNodeId), "No", "Yes")
| project CreationTime,Name=trim("_", Name), Region, AvailabilityZone,DataCenterName, ClusterName, NodeId,IsOverLake, SocNodeId, ContainerID, VirtualMachineUniqueId, OSType, VMSize,VMCRUD,VFPDashBoard,VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard,FPGADashboard, DriDash=InvestigateNode,NodeDash, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,ProcessTupleOutbounds,HostCaptureForNonOverLakeNode
```

### CA-PA Mapping Information Based on Primary CA - Data observed from NSM to PubSub in last 90 days

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let containerid=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 2h  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct containerId;
let CAss=cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId == SubIdOrContainerIdx
| where VirtualMachineArmId contains trim("_", VMName)
| where Primary == "true"
| distinct PrimaryCA=tostring(todynamic(PrivateIPAddress)[0]);
let vNetId=cluster('vnetkusto.northcentralus').database('veritas').InterfaceProgramEndFiveMinuteTable
| where TIMESTAMP >= starttime - 1h  and TIMESTAMP <= endtime
| where ContainerId in (containerid)
| distinct vNetId=tolower(extract(@"{(.*?)}", 1, VnetGuid));
cluster('Azurecm').database('AzureCM').DCMLNMPubSubTaskEventEtwTable
| where TIMESTAMP >= starttime - 90d  and TIMESTAMP <= endtime
| where VnetId in (vNetId)
| where CustomerAddress in (CAss)
| where TaskStatus == "UpdateTaskAdded"
| project PreciseTimeStamp, CustomerAddress, TaskStatus, AdditionalData, ErrorCode,ErrorMesssage
| extend PA_value = extract(@"PA\s*=\s*\[(.*?)\]", 1, AdditionalData)
| extend IPv4PA=tostring(split(PA_value, ",")[0]),IPv6PA=tostring(split(PA_value, ",")[1])
| project PreciseTimeStamp, CustomerAddress, IPv4PA,IPv6PA
| order by PreciseTimeStamp asc 
| summarize PAEntryStartTime=min(PreciseTimeStamp), PAEntryEndTime=max(PreciseTimeStamp) by CustomerAddress, IPv4PA, IPv6PA
| project PAEntryStartTime=bin(PAEntryStartTime, 1m), PAEntryEndTime=bin(PAEntryEndTime,1m), CustomerAddress, IPv4PA, IPv6PA
| order by PAEntryStartTime desc  
//| evaluate narrow()
//| project Key=Column, Value
//cluster('AzureCM').database('AzureCM').LogContainerSnapshot
//| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
//| where subscriptionId == SubscriptionID
//| where roleInstanceName contains VMName
//| distinct roleInstanceName, containerId
//| join kind=leftouter cluster("aznwsdn").database('aznwmds').CAToContainerId on $left.containerId == $right.ContainerId
//| where MIN_TIMESTAMP >= starttime - 30d and MAX_TIMESTAMP <= endtime
//| distinct VMName=roleInstanceName, ContainerId, Cluster, NodeId, CA, PA, MacAddr
//| distinct VMName, ContainerId, CA, PA, MacAddr
```

### VM DownTime Event

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let VMContainerID=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct containerId;
cluster('azurecm').database('AzureCM').TMMgmtRoleInstanceDowntimeEventEtwTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where ContainerId in (VMContainerID)
| project PreciseTimeStamp, RoleInstanceName, ActivityType, ActivityDetail

```

### Loss Ratio to the VM Cluster

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let cluster=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct Tenant
);
cluster('azphynet').database('azdhsd').PathScanHealthCheck_Cluster
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where Cluster in (cluster)
| project TIMESTAMP, LossyPathRatio, Cluster
| render timechart
```

### Loss Ratio to the VM datacenter

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let DCs=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct tostring(DataCenterName)
);
cluster('azphynet').database('azdhsd').KhiSlb
| where TIMESTAMP between (starttime .. endtime)
| where Datacenter !contains "BingEdge"
| where DC in~ (DCs)
| project TIMESTAMP, DC, netscan_loss//, slb_loss
| render timechart
```

### Region Level Latency

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let Regions=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct Region
);
cluster('azphynet').database('NetPerfKustoDB').PerfAnalyzer_NetLatencyPodSetPaths 
| where startTime >= starttime and startTime <= endtime
| where region in (Regions)
| summarize Latency=round(avg(latencyMilliseconds), 4), SuccessRate=round(avg(successRate), 2) by bin(startTime, 1m), region
| project startTime, Latency, SuccessRate, region
| render timechart
```

### VM PhyNet Path Device List

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
let AZNG=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "ah"
| distinct AZNG=EndDevice);
let RA=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RHWE)
| distinct RA=EndDevice);
let OWR=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RA)
| distinct OWR=EndDevice);
T0| union T1 | union T2 | union RHWE | union AZNG | union RA | union OWR
| summarize T0=make_set_if(T0, strlen(T0) > 0), T1=make_set_if(T1, strlen(T1) > 0),T2=make_set_if(T2, strlen(T2) > 0),RHWE=make_set_if(RHWE, strlen(RHWE) > 0),AZNG=make_set_if(AZNG, strlen(AZNG) > 0),RA=make_set_if(RA, strlen(RA) > 0),OWR=make_set_if(OWR, strlen(OWR) > 0)
| distinct  T0 = strcat_array(T0, ", "),T1 = strcat_array(T1, ", "),T2 = strcat_array(T2, ", "),RHWE = strcat_array(RHWE, ", "),AZNG = strcat_array(AZNG, ", "),RA = strcat_array(RA, ", "),OWR = strcat_array(OWR, ", ")
| evaluate narrow()
| project Type=Column, Value

```

### Node<---->TOR: This is the interface traffic of TOR connecting to the physical node

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| join kind=leftouter(cluster('azphynet').database('azdhmds'). InterfaceData) on $left.EndDevice == $right.deviceHostName and $left.EndPort == $right.ifName
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| project PreciseTimeStamp, TOR=deviceHostName, ifName, ifAlias, ifType, ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2),  AverageInPacketPerSecond=round(ifHCInUcastPktsDiff/(interval / 1e3)), AverageOutPacketPerSecond=round(ifHCOutUcastPktsDiff/(interval / 1e3)), InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| project PreciseTimeStamp,AverageInBandwidthGbps, AverageInPacketPerSecond, AverageOutBandwithGbps, AverageOutPacketPerSecond, InPacketDiscardPerFiveMinutes, InPacketErrorPerFiveMinutes, OutPacketDiscardPerFiveMinutes, OutPacketErrorPerFiveMinutes
| render timechart
```

### TOR<---->T1: Average bandwidth(Gbps) of the TOR interface connecting to the T1

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T0)
| where ifAlias contains "T1:"
| project PreciseTimeStamp, TOR=deviceHostName, ifName, T1=ifAlias, ifType, ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), T1
| render timechart
```

### TOR<---->T1: Average packet per second of the TOR interface connecting to the T1

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T0)
| where ifAlias contains "T1:"
| project PreciseTimeStamp, TOR=deviceHostName, ifName, T1=ifAlias, ifType, ifOperStatus, AverageInPacketPerSecond=round(ifHCInUcastPktsDiff/(interval / 1e3)), AverageOutPacketPerSecond=round(ifHCOutUcastPktsDiff/(interval / 1e3))
| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 2m), T1
| render timechart
```

### TOR<---->T1: Discard packets of the TOR interface connecting to the T1 in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T0)
| where ifAlias contains "T1:"
| project PreciseTimeStamp, TOR=deviceHostName, ifName, T1=ifAlias, ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T1
| render timechart
```

### TOR<---->T1: Error packets of the TOR interface connecting to the T1 in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T0)
| where ifAlias contains "T1:"
| project PreciseTimeStamp, TOR=deviceHostName, ifName, T1=ifAlias, ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T1
| render timechart
```

### T1<---->T2: Average bandwidth(Gbps) of the T1 interfaces connecting to all the T2

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T1)
| where ifAlias contains "T2:"
| project PreciseTimeStamp, T1=deviceHostName, ifName, T2=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), T1
| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, T1
| render timechart
//| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 1m), T1,T2
//| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, Path=strcat(T1, "----", T2)
//| render timechart
```

### T1<---->T2: Average packet per second of the T1 interface connecting to all the T2

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T1)
| where ifAlias contains "T2:"
| project PreciseTimeStamp, T1=deviceHostName, ifName, T2=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInPacketPerSecond=round(ifHCInUcastPktsDiff/(interval / 1e3)), AverageOutPacketPerSecond=round(ifHCOutUcastPktsDiff/(interval / 1e3))
| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 2m),T1
| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, T1
| render timechart
//| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 1m),T1, T2
//| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, Path=strcat(T1, "----", T2)
//| render timechart
```

### T1<---->T2: Discard packets of the T1 interface connecting to all the T2 in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T1)
| where ifAlias contains "T2:"
| project PreciseTimeStamp, T1=deviceHostName, ifName, T2=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T1
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, T1
| render timechart
//| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T1, T2
//| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, Path=strcat(T1, "----", T2)
//| render timechart
```

### T1<---->T2: Error packets of the T1 interface connecting to all the T2 in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T1)
| where ifAlias contains "T2:"
| project PreciseTimeStamp, T1=deviceHostName, ifName, T2=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T1
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, T1
| render timechart
//| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T1,T2
//| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, Path=strcat(T1, "----", T2)
//| render timechart
```

### T2<---->RHW&RHE: Average bandwidth(Gbps) of the T2 interface connecting to all the RHW&RHE

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "rh"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, T2
| render timechart
//| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 1m), T2,RH
//| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, Path=strcat(T2, "----", RH)
//| render timechart
```

### T2<---->RHW&RHE: Average packet per second of the T2 interface connecting to all the RHW&RHE

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "rh"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInPacketPerSecond=round(ifHCInUcastPktsDiff/(interval / 1e3)), AverageOutPacketPerSecond=round(ifHCOutUcastPktsDiff/(interval / 1e3))
| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, T2
| render timechart
//| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 1m), T2, RH
//| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, Path=strcat(T2, "----", RH)
//| render timechart


```

### T2---->RHW&RHE: Discard packets of the T2 interface connecting to all the RHW&RHE in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "rh"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, T2
| render timechart
//| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T2,RH
//| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, Path=strcat(T2, "----", RH)
//| render timechart
```

### T2---->RHW&RHE: Error packets of the T2 interface connecting to all the RHW&RHE in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "rh"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),T2
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, T2
| render timechart
```

### RHW&RHE<---->RA: Average bandwidth(Gbps) of the RHW&RHE interface connecting to all the RA

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RHWE)
| where ifAlias contains "ra" or ifAlias contains "rwa"
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), RHWE
| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, RHWE
| render timechart
//| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 1m), RHWE,RH
//| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, Path=strcat(T2, "----", RH)
//| render timechart
```

### RHW&RHE<---->RA: Average packet per second of the RHW&RHE interface connecting to all the RA

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
cluster('azphynet').database('azdhmds'). InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RHWE)
| where ifAlias contains "ra" or ifAlias contains "rwa"
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInPacketPerSecond=round(ifHCInUcastPktsDiff/(interval / 1e3)), AverageOutPacketPerSecond=round(ifHCOutUcastPktsDiff/(interval / 1e3))
| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 2m), RHWE
| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, RHWE
| render timechart
//| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 1m), T2, RH
//| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, Path=strcat(T2, "----", RH)
//| render timechart


```

### RHW&RHE---->RA: Discard packets of the RHW&RHE interface connecting to all the RA

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RHWE)
| where ifAlias contains "ra" or ifAlias contains "rwa"
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), RHWE
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, RHWE
| render timechart
//| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T2,RH
//| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, Path=strcat(T2, "----", RH)
//| render timechart
```

### RHW&RHE---->RA: Error packets of the RHW&RHE interface connecting to all the RA

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RHWE)
| where ifAlias contains "ra" or ifAlias contains "rwa"
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),RHWE
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, RHWE
| render timechart
```

### Dual-TOR status

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let T0Device=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| where DeviceName !contains "sc"
| distinct T0=EndDevice;
let T0Port=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| where DeviceName !contains "sc"
| distinct EndPort);
cluster('azphynet').database('azdhmds').MuxCableLinkStatusST
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T0Device)
| where ifName in (T0Port)
| project pollingTimeStamp, deviceHostName, IsTorMuxHardwareStateActive=iff(interfaceMuxHardwareState == "active", 6, 0),IsTorMuxOverallStateActive=iff(interfaceMuxOverallState == "active", 5, 0), IsInterfaceMuxHealth=iff(interfaceMuxHealth == "healthy", 4, 0), IslinkStatusSelfUp=iff(linkStatusSelf == "up", 3, 0), IslinkStatusPeerUp=iff(linkStatusPeer == "up", 2, 0),IslinkStatusNICUp=iff(linkStatusNic == "up", 1, 0)
| project pollingTimeStamp, deviceHostName, IsTorMuxHardwareStateActive,IsTorMuxOverallStateActive,IsInterfaceMuxHealth,IslinkStatusSelfUp,IslinkStatusPeerUp,IslinkStatusNICUp
| render timechart 
```

### T1---->T0: Discard packets of the T1 interface connecting to this T0 in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T1)
| where ifAlias contains "T0:"
| extend T0s=tostring(tolower(split(ifAlias, ":")[0]))
| where T0s in (T0)
| project PreciseTimeStamp, T1=deviceHostName, ifName, ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T1
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, T1
| render timechart
//| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T1, T2
//| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, Path=strcat(T1, "----", T2)
//| render timechart
```

### T1---->T0: Error packets of the T1 interface connecting to this T0 in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T1)
| where ifAlias contains "T0:"
| extend T0s=tostring(tolower(split(ifAlias, ":")[0]))
| where T0s in (T0)
| project PreciseTimeStamp, T1=deviceHostName, ifName, ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T1
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, T1
| render timechart
```

### T2---->T1: Discard packets of the T2 interface connecting to all the T1 of this TOR in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "T1"
| extend T1s=tostring(tolower(split(ifAlias, ":")[0]))
| where T1s in (T1)
| project PreciseTimeStamp, T2=deviceHostName, ifName, ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, T2
| render timechart
//| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T2,RH
//| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, Path=strcat(T2, "----", RH)
//| render timechart
```

### T2---->T1: Error packets of the T2 interface connecting to all the T1 of this TOR in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "T1"
| extend T1s=tostring(tolower(split(ifAlias, ":")[0]))
| where T1s in (T1)
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),T2
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, T2
| render timechart
```

### RHW&RHE---->T2: Discard packets of the RHW&RHE interface connecting to all the T2

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RHWE)
| where ifAlias contains "t2"
| extend T2s=tostring(tolower(split(ifAlias, ":")[0]))
| where T2s in (T2)
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, T2s, ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), RHWE
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, RHWE
| render timechart
```

### RHW&RHE---->T2: Error packets of the RHW&RHE interface connecting to all the T2

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RHWE)
| where ifAlias contains "t2"
| extend T2s=tostring(tolower(split(ifAlias, ":")[0]))
| where T2s in (T2)
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, T2s, ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),RHWE
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, RHWE
| render timechart
```

### RA---->RHW&RHE: Discard packets of the RA interface connecting to all the RH of this VM

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
let RA=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RHWE)
| distinct RA=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RA)
| where ifAlias contains "rh"
| extend RH=iff(deviceHostName !startswith "rwa", tolower(split(ifAlias, ":")[0]),tolower(split(ifAlias, ":")[2]))
| where RH in (RHWE)
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), RHWE
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, RHWE
| render timechart
```

### RA---->RHW&RHE: Error packets of the RA interface connecting to all the RH of this VM

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
let RA=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RHWE)
| distinct RA=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (RA)
| where ifAlias contains "rh"
| extend RH=iff(deviceHostName !startswith "rwa", tolower(split(ifAlias, ":")[0]),tolower(split(ifAlias, ":")[2]))
| where RH in (RHWE)
| project PreciseTimeStamp, RA=deviceHostName, ifName, ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),RA
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, RA
| render timechart
```

### MKA Event Count in PhyNet data path between T0 and OWR

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
let AZNG=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "ah"
| distinct AZNG=EndDevice);
let RA=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RHWE)
| distinct RA=EndDevice);
let OWR=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RA)
| distinct OWR=EndDevice);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp between (starttime .. endtime)
| where Device in (T1) or Device in (T2) or Device in (RHWE) or Device in (AZNG) or Device in (RA) or Device in (OWR) or Device in (T0)
| where EventName contains "MKA"
| where Message contains "T0" or Message contains "T1" or Message contains "T2" or Message contains "rhw" or Message contains "rhe" or Message contains "ra" or Message contains "icr" or Message contains "sw" or Message contains "owr" or Message contains "rwa"
| summarize count() by  bin(PreciseTimeStamp, 5m), Device
| render columnchart    
```

### BGP Flap Count in PhyNet data path between T0 and OWR

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
let AZNG=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "ah"
| distinct AZNG=EndDevice);
let RA=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RHWE)
| distinct RA=EndDevice);
let OWR=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RA)
| distinct OWR=EndDevice);
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP between (starttime .. endtime)
| where (SrcDevice in (T1) or SrcDevice in (T2) or SrcDevice in (RHWE) or SrcDevice in (AZNG) or SrcDevice in (RA) or SrcDevice in (OWR) or SrcDevice in (T0)) and (DstDevice in (T1) or DstDevice in (T2) or DstDevice in (RHWE) or DstDevice in (AZNG) or DstDevice in (RA) or DstDevice in (OWR) or DstDevice in (T0))
| extend SrcDc=split(SrcDevice, "-")[0]
| extend DstDc=split(DstDevice, "-")[0]
| extend Path=strcat(SrcDevice, "---->", DstDevice)
| summarize count=count() by bin(TIMESTAMP,1m), Path
| render columnchart
```

### Region Level Loss Rate

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let Regions=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct Region
);
cluster('azphynet').database('NetPerfKustoDB').PerfAnalyzer_NetScanPodSetPaths  
| where startTime >= starttime and startTime <= endtime
| where region in (Regions)
| summarize AvgLossRate=avg(lossRate) by bin(startTime, 1m), region
| render timechart
```

### T2<---->AHZ&AHY: Average bandwidth(Gbps) of the T2 interface connecting to all the AHZ&AHY

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "ah"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, T2
| render timechart
//| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 1m), T2,RH
//| project PreciseTimeStamp, AverageInBandwidthGbps, AverageOutBandwithGbps, Path=strcat(T2, "----", RH)
//| render timechart
```

### T2<---->AHZ&AHY: Average packet per second of the T2 interface connecting to all the AHZ&AHY

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "ah"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, AverageInPacketPerSecond=round(ifHCInUcastPktsDiff/(interval / 1e3)), AverageOutPacketPerSecond=round(ifHCOutUcastPktsDiff/(interval / 1e3))
| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, T2
| render timechart
//| summarize AverageInPacketPerSecond=sum(AverageInPacketPerSecond), AverageOutPacketPerSecond=sum(AverageOutPacketPerSecond) by bin(PreciseTimeStamp, 1m), T2, RH
//| project PreciseTimeStamp, AverageInPacketPerSecond, AverageOutPacketPerSecond, Path=strcat(T2, "----", RH)
//| render timechart


```

### T2---->AHZ&AHY: Discard packets of the T2 interface connecting to all the AHZ&AHY in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "ah"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), T2
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, T2
| render timechart
//| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 1m), T2,RH
//| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, Path=strcat(T2, "----", RH)
//| render timechart
```

### T2---->AHZ&AHY: Error packets of the T2 interface connecting to all the AHZ&AHY in 5 minutes interval

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (T2)
| where ifAlias contains "ah"
| project PreciseTimeStamp, T2=deviceHostName, ifName, RH=tostring(tolower(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),T2
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, T2
| render timechart
```

### AHZ&AHY---->T2: Discard packets of the AHZ&AHY interface connecting to all the T2 of this VM

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let AZNG=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "ah"
| distinct AZNG=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (AZNG)
| where ifAlias contains "t2"
| extend T2s=tostring(tolower(split(ifAlias, ":")[0]))
| where T2s in (T2)
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, T2s, ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), RHWE
| project PreciseTimeStamp, InPacketDiscardPerFiveMinutes, OutPacketDiscardPerFiveMinutes, RHWE
| render timechart
```

### AHY&AHZ---->T2: Error packets of the AHY&AHZ interface connecting to all the T2 of this VM

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let DataPathScanx=DataPathScan;
let VMNames=iff(DataPathScanx== "Yes", strcat("_",VMName), VMName);
let containerIdx=iff(DataPathScanx== "No", strcat("_",SubIdOrContainerIdx), SubIdOrContainerIdx);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == containerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let AZNG=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "ah"
| distinct AZNG=EndDevice);
cluster('azphynet').database('azdhmds').InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName in (AZNG)
| where ifAlias contains "t2"
| extend T2s=tostring(tolower(split(ifAlias, ":")[0]))
| where T2s in (T2)
| project PreciseTimeStamp, RHWE=deviceHostName, ifName, T2s, ifType, ifOperStatus, InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m),RHWE
| project PreciseTimeStamp, InPacketErrorPerFiveMinutes, OutPacketErrorPerFiveMinutes, RHWE
| render timechart
```

### Find VM ARM ResourceURI by Resource Name

> 💡 **Tip:** If you only need the ARM ResourceURI (not NIC details), use `azcrp` as a fallback:
> ```kql
> cluster('azcrp').database('crp_allprod').ApiQosEvent
> | where PreciseTimeStamp >= ago(30d)
> | where subscriptionId == '<subscriptionId>'
> | where resourceName contains '<vmNameOrGuid>'
> | project PreciseTimeStamp, subscriptionId, region, resourceGroupName, resourceName, operationName,
>     ResourceURI = strcat('/subscriptions/', subscriptionId, '/resourceGroups/', resourceGroupName, '/providers/Microsoft.Compute/virtualMachines/', resourceName)
> | top 5 by PreciseTimeStamp desc
> ```

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let subscriptionidxyz=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 2h  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == strcat("_", VMName)) or containerId == SubIdOrContainerIdx
| distinct subscriptionId;
let vmnamexyz=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 2h  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == strcat("_", VMName)) or containerId == SubIdOrContainerIdx
| distinct trim("_",roleInstanceName));
cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId in~ (subscriptionidxyz)
| where  VirtualMachineArmId contains vmnamexyz
| extend RoleInstanceName=tostring(split(VirtualMachineArmId, "virtualMachines/")[1])
| extend NetworkInterface=tostring(split(tolower(ArmId), "networkinterfaces/")[1])
| extend Subnet=tostring(split(tolower(VirtualSubnetArmId),"/")[10])
| extend vNet=tostring(split(tolower(VirtualSubnetArmId),"/")[8])
| project NetworkInterface, PrivateIPAddress,MacAddress,IsprimaryNIC=Primary, AcceleratedNetworkingEnabled, MultiCA, IsIPv6, IpConfigurationsCount,vNet, Subnet, VirtualMachineResourceURI=VirtualMachineArmId,NICResourceURI=tolower(ArmId),SubnetUri=tolower(VirtualSubnetArmId)
| project NetworkInterface, PrivateIPAddress,MacAddress,IsprimaryNIC,vNet,Subnet, AcceleratedNetworkEnabled=AcceleratedNetworkingEnabled, MultiCA, IsIPv6, NICIPCount=IpConfigurationsCount
//| summarize PrivateIPAddress=strcat_array(make_list(PrivateIPAddress), ", ") by RoleInstanceName, Cloud, Region,MacAddress,IsprimaryNIC, AcceleratedNetworkingEnabled, MultiCA, IsIPv6, IpConfigurationsCount, VirtualMachineResourceURI,NICResourceURI,Subnet
//| project RoleInstanceName, PrivateIPAddress, Cloud, Region,MacAddress,IsprimaryNIC, AcceleratedNetworkingEnabled, MultiCA, IsIPv6, IpConfigurationsCount, VirtualMachineResourceURI,NICResourceURI,Subnet
//| extend ExternalInforamtion=strcat("PrivateIPAddress: ", PrivateIPAddress,";   MacAddress: ", MacAddress,";    IsprimaryNIC: ", IsprimaryNIC, ";   AcceleratedNetworkingEnabled: ",AcceleratedNetworkingEnabled, ";    MultiCA: ",MultiCA, ";    Subnet: ",Subnet, ";   NICURI: ", NICResourceURI)
//| project RoleInstanceName, ExternalInforamtion,VirtualMachineResourceURI
//| summarize make_set(ExternalInforamtion) by RoleInstanceName, VirtualMachineResourceURI
//| evaluate narrow()
//| project Column, Value



```

### LinkFlap Count in PhyNet data path between T0 and OWR

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let T0=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct NodeId=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| distinct T0=EndDevice);
let T1=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T0)
| distinct T1=EndDevice);
let T2=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T1)
| distinct T2=EndDevice);
let RHWE=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "rhe" or EndDevice contains "rhw"
| distinct RHWE=EndDevice);
let AZNG=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (T2)
| where EndDevice contains "ah"
| distinct AZNG=EndDevice);
let RA=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RHWE)
| distinct RA=EndDevice);
let OWR=materialize(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where LinkType == "DeviceInterfaceLink"
| where StartDevice in (RA)
| distinct OWR=EndDevice);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp between (starttime .. endtime)
| where Device in (T1) or Device in (T2) or Device in (RHWE) or Device in (AZNG) or Device in (RA) or Device in (OWR) or Device in (T0)
| where EventName == "LINEPROTO-5-UPDOWN"
| where Message contains "changed state to down"
| where Message contains "T0" or Message contains "T1" or Message contains "T2" or Message contains "rhw" or Message contains "rhe" or Message contains "ra" or Message contains "icr" or Message contains "sw" or Message contains "owr" or Message contains "rwa"
| extend ToDevice = tolower(extract(@"\((.*?)\)", 1, Message))
| project PreciseTimeStamp, Device, ToDevice=tostring(split(ToDevice, ":")[0]), Message
| extend Path=strcat(Device, "---->", ToDevice)
| where ToDevice in (T1) or ToDevice in (T2) or ToDevice in (RHWE) or ToDevice in (AZNG) or ToDevice in (RA) or ToDevice in (OWR) or ToDevice in (T0) 
| summarize FlapCount=count() by bin(PreciseTimeStamp, 5m), Path
| render columnchart
```

### Host-TOR PingMesh

```kql
let starttime = _startTime;
let endtime = _endTime;
let VMNames=strcat("_",VMName);
let SubIdOrContainerIdx = SubIdOrContainerId;
let nodeId=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct nodeId;
cluster('vnetkusto.northcentralus').database('veritas').TorPingSendAggreEvent
| where TIMESTAMP between (starttime .. endtime)
| where NodeId in~ (nodeId)
| summarize SendCount = max(SendCount) by TIMESTAMP, NodeId, TorName
| join kind = leftouter
(
cluster('vnetkusto.northcentralus').database('veritas').TorPingRecvAggreEvent
| where TIMESTAMP between (starttime .. endtime)
| where NodeId in~ (nodeId)
| summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
)
on TIMESTAMP, NodeId
| extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
| project TIMESTAMP, Availability = todouble(RecvCount) / todouble(SendCount) * 100
| render timechart 
```

### Disk Read/Write Congestion - Network issue in data path will result disk read/write congestion

```kql
let starttime = _startTime;
let endtime = _endTime;
let VMNames=strcat("_",VMName);
let SubIdOrContainerIdx = SubIdOrContainerId;
let nodeId=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct nodeId;
let cx3p = cluster("Netperf").database("NetPerfKustoDB").MlnxAdapterQosCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where NodeId in~ (nodeId) 
| summarize ECN_Received = sum(Responder_ECN_Handled_Successfully_Rate), CNP_Sent = sum(Responder_CNP_Sent_Successfully_Rate) 
by bin(PreciseTimeStamp,1m);
let cx4 = cluster("Netperf").database("NetPerfKustoDB").Mlx5CongestionControlCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where NodeId in~ (nodeId) 
| summarize ECN_Received = sum(Notification_Point_RoCEv2_ECN_Marked_Packets), CNP_Sent = sum(Notification_Point_CNPs_Sent_Successfully) 
by bin(PreciseTimeStamp,1m);
cx3p | union cx4
```

### VFP Flow State Per Container ID(Cid)

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let vfpaccount=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 2h  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct Tenantlower=tolower(Tenant)
| join kind=inner (cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() | extend Tenant=tolower(Cluster)) on $left.Tenantlower == $right.Tenant 
| distinct VfpAccount);
let ContainerL=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct containerId
| summarize containerlist=make_list(containerId)
| extend ContainerLists=strcat('("', array_strcat(containerlist, '","'), '")')
| distinct ContainerLists);
let CurrentTotalFlowEntryIn = strcat(@"metricNamespace('VfpPortFlowStats').metric('CurrentTotalFlowEntryIn').dimensions('ContainerId').samplingTypes('Sum') | where ContainerId in ", ContainerL);
let CurrentTotalFlowEntryOut = strcat(@"metricNamespace('VfpPortFlowStats').metric('CurrentTotalFlowEntryOut').dimensions('ContainerId').samplingTypes('Sum') | where ContainerId in ", ContainerL);
let CreatedTotalFlowEntryInRate = strcat(@"metricNamespace('VfpPortFlowStats').metric('CreatedTotalFlowEntryInRate').dimensions('ContainerId').samplingTypes('Sum') | where ContainerId in ", ContainerL);
let CreatedTotalFlowEntryOutRate = strcat(@"metricNamespace('VfpPortFlowStats').metric('CreatedTotalFlowEntryOutRate').dimensions('ContainerId').samplingTypes('Sum') | where ContainerId in ", ContainerL);
let ctfei = evaluate geneva_metrics_request(vfpaccount, CurrentTotalFlowEntryIn, starttime, endtime)
| project TimestampUtc, Cid=tostring(strcat(split(ContainerId, "-")[0],"-x")), CurrentTotalFlowEntryIn=Sum
| where Cid != ""
| render timechart;
let ctfeo = evaluate geneva_metrics_request(vfpaccount, CurrentTotalFlowEntryOut, starttime, endtime)
| project TimestampUtc, Cid=tostring(strcat(split(ContainerId, "-")[0],"-x")), CurrentTotalFlowEntryOut=Sum
| where Cid != ""
| render timechart;
union ctfei, ctfeo
//let ctfeir = evaluate geneva_metrics_request(vfpaccount, CreatedTotalFlowEntryInRate, starttime, endtime)
//| project TimestampUtc, Cid=tostring(strcat(split(ContainerId, "-")[0],"-x")), CreatedTotalFlowEntryInRate=Sum
//| where Cid != ""
//| render timechart;
//let ctfeor = evaluate geneva_metrics_request(vfpaccount, CreatedTotalFlowEntryOutRate, starttime, endtime)
//| project TimestampUtc, Cid=tostring(strcat(split(ContainerId, "-")[0],"-x")), CreatedTotalFlowEntryOutRate=Sum
//| where Cid != ""
//| render timechart;
//union ctfei, ctfeo,ctfeir,ctfeor
```

### Live Migration Event

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let VMContainerID=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct containerId;
cluster('vmainsight').database('Air').AirLiveMigrationEvents
| where EventTime >= starttime - 3h and EventTime <= endtime + 3h
| where ObjectId  in (VMContainerID)
| extend BlackoutInSec = round(Duration/1s, 2)
| extend LMStartTime = todatetime(Diagnostics.LiveMigrationStartTime)
| project EventTime, LMStartTime, RCALevel1, RCALevel2,RCALevel3, BlackoutInSec, ComputeBlackoutInSec, NetworkReadyBlackoutInSec, faultInfo_Time, faultInfo_Reason

```

### Service Healing Event

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let VMNames=strcat("_",VMName);
let VMContainerID=cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == VMNames) or containerId == SubIdOrContainerIdx
| distinct containerId;
cluster('accp.centralus').database('AZSM').AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp >= starttime   and PreciseTimeStamp <= endtime
| where triggerObjectId in (VMContainerID)
| project PreciseTimeStamp, clientType, roleInstanceNames, JobId, triggerType, faultCode, faultReason, EventMessage, migrationRequestDetails

```
### Guest OS / Image Version Lookup

**Goal:** Find the guest OS Linux distribution and version for a VM.
**Why not AzureCM?** `LogContainerSnapshot` only provides `OSType` (e.g. `Linux_IaaS`) via `split(billingType, "|")[0]` — it does not include the distro name or version.
**Solution:** Use `VMApiQosEvent` on the `azcrp` cluster. The `galleryImage` column contains the full shared image gallery path (including image definition and version), and `platformImage` contains marketplace image references when applicable.

**Key columns:**
| Column | Description |
|---|---|
| `subscriptionId` | VM subscription GUID |
| `resourceName` | VM name (case-insensitive match with `=~`) |
| `platformImage` | Marketplace image reference (publisher/offer/sku) |
| `galleryImage` | Shared Image Gallery reference (gallery/image/version) |
| `userVMImage` | Custom VHD image URI |
| `oSType` | Linux or Windows |
| `vMSize` | VM SKU size |

**Notes:**
- Extend time range (e.g. `ago(90d)`) if the VM hasn't had recent API activity.
- `galleryImage` example: `.../galleries/osimage_us/images/pke-rockyos-v6/versions/0.0.3` → Rocky Linux v6, version 0.0.3
- `platformImage` is populated for marketplace images (e.g. `Canonical/UbuntuServer/18.04-LTS`); `galleryImage` is populated for shared gallery images. Check whichever is non-empty.

```kql
cluster('azcrp').database('crp_allprod').VMApiQosEvent
| where TIMESTAMP > ago(90d)
| where subscriptionId == '<SubscriptionID>'
| where resourceName =~ '<VMName>'
| project TIMESTAMP, resourceName, platformImage, galleryImage, userVMImage, oSType, vMSize
| top 5 by TIMESTAMP desc
```


### MAC Address to ContainerID / VM Info (No Region Filter)

**Goal:** Given a MAC address, find all VMs that have used it — across all regions — with their ContainerID, SubscriptionId, NodeId, and VM name.

**Why this pattern:**
- MAC is stored in `ContainerInformationEvent.PortId` as `External_<MAC>` (uppercase, no dashes)
- Starting from `LogContainerSnapshot` (AzureCM) without a filter causes OOM on cross-cluster join — the table is too large globally
- **Correct pattern:** Enter from `vnetkusto.northcentralus` cluster (`veritas` database), `materialize()` the MAC-filtered ContainerIDs first (~few rows), then use `in` + `lookup` against `LogContainerSnapshot`

**Entry cluster:** `cluster("vnetkusto.northcentralus").database("veritas")`

```kql
let macAddress = "000D3A07F14B";  // Replace: uppercase, no dashes
let startTime = ago(7d);          // Adjust as needed; extend to 30d+ for older VMs
let MacContainers = materialize(
    cluster("vnetkusto.northcentralus").database("veritas").ContainerInformationEvent
    | where PreciseTimeStamp >= startTime
    | where PortId == strcat("External_", macAddress)
    | distinct ContainerId, PortId
);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= startTime
| where containerId in (MacContainers | project ContainerId)
| lookup MacContainers on $left.containerId == $right.ContainerId
| summarize arg_max(PreciseTimeStamp, *) by containerId
| project PreciseTimeStamp, containerId, subscriptionId, nodeId,
          virtualMachineUniqueId, roleInstanceName, Region,
          DataCenterName, AvailabilityZone,
          MACAddress=tostring(split(PortId, "_")[1])
| order by PreciseTimeStamp desc
```

**Notes:**
- MAC input format: uppercase, no dashes (e.g. `000D3A07F14B` from `00-0D-3A-07-F1-4B`)
- One VM can appear multiple times with different ContainerIDs (each live migration creates a new ContainerID); `arg_max` returns the latest snapshot per ContainerID
- A single physical MAC can be reused across VMs over time — review `roleInstanceName` and `subscriptionId` to identify the specific VM
- `Region` in results uses internal Kusto naming (e.g. `asiasoutheast` = `southeastasia`)

---

## Node-Dash

### Node Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let nid = tolower(nodeid);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| where shoeboxMdmAccountName != ""
| extend shoe = trim(" ", shoeboxMdmAccountName)
| distinct Region, shoeboxMdmAccountName=shoe);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where nodeId == nid
| distinct roleInstanceName, Tenant, nodeId, AvailabilityZone, virtualMachineUniqueId, VMSize=tostring(split(billingType, "|")[1]), Region,creationTime, DataCenterName
| join kind=leftouter cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2 on $left.nodeId == $right.NodeId
| distinct roleInstanceName, Tenant, nodeId, AvailabilityZone, Region,creationTime, SocNodeId,DataCenterName
| join kind=inner ShoeBoxMdm on $left.Region == $right.Region
| distinct Tenant, nodeId, AvailabilityZone, Region, CA="-",SocNodeId,DataCenterName,shoeboxMdmAccountName
//| join kind=inner cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps on $left.Tenant == $right.Cluster
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend VFPDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPDropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SupportDashBoard=strcat("https://portal.microsoftgeneva.com/s/9FDB0A67?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend GFTDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/FpgaDashboardGft/FpgaDashboardGftv3?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FPGADashboard=strcat("https://portal.microsoftgeneva.com/s/C700B706?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend InvestigateNode=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", "&p-_ICMId=all#2f4843e6-c1e5-4564-ad27-cde71cebc7c7")
| extend ASIHostNode=strcat("https://azureserviceinsights.trafficmanager.net/view/services/Azure%20Host/pages/Azure%20Host%20Node?nodeId=",nodeId,"&globalFrom=",format_datetime(starttime, 'yyyy-MM-dd'),"T",format_datetime(starttime, 'HH'), "%3A",format_datetime(starttime, 'mm'), "%3A51.000Z&globalTo=",format_datetime(endtime, 'yyyy-MM-dd'),"T",format_datetime(endtime, 'HH'), "%3A",format_datetime(endtime, 'mm'),"%3A51.000Z")
| extend NetVMA=strcat("https://aka.ms/netvma/?destValue=&pathQuery=false&sdnPath=false&showPingMesh=false&startTime=", format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "&endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH:mm:ss'), "&value=", nodeId)
| extend PerProcessorPNICDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/PerProcessorNdisDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| project Region, AvailabilityZone,DataCenterName, ClusterName=Tenant, NodeId=nodeId,SocNodeId,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,DriDash=InvestigateNode, ASIHostNode, NetVMA, PerProcessorPNICDashboard
| evaluate narrow()
| project Column, Value
```

### VMs under this node

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let nid = tolower(nodeid);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| where shoeboxMdmAccountName != ""
| extend shoe = trim(" ", shoeboxMdmAccountName)
| distinct Region, shoeboxMdmAccountName=shoe);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1h  and PreciseTimeStamp <= endtime
| where nodeId == nid
| distinct roleInstanceName, containerId, virtualMachineUniqueId, subscriptionId
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")

```

### SOC Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let nid = tolower(nodeid);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| where shoeboxMdmAccountName != ""
| extend shoe = trim(" ", shoeboxMdmAccountName)
| distinct Region, shoeboxMdmAccountName=shoe);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where nodeId == nid
| distinct roleInstanceName, Tenant, nodeId, AvailabilityZone, virtualMachineUniqueId, VMSize=tostring(split(billingType, "|")[1]), Region,creationTime, DataCenterName
| join kind=leftouter cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2 on $left.nodeId == $right.NodeId
| extend SOCHostName = tolower(strcat(HostName,"SOC"))
| distinct roleInstanceName, Tenant, nodeId, AvailabilityZone, Region,creationTime, SocNodeId,DataCenterName, SOCHostName
| join kind=inner ShoeBoxMdm on $left.Region == $right.Region
| distinct SOCHostName,SocNodeId,DataCenterName,shoeboxMdmAccountName, Tenant, nodeId
//| join kind=inner cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps on $left.Tenant == $right.Cluster
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend BackplaneMemoryMetrics=strcat("https://portal.microsoftgeneva.com/s/FB5CA093?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend BackplaneMetrics=strcat("https://portal.microsoftgeneva.com/s/A6871590?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SOCDashboard=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", "&p-_ICMId=all#adfd51d7-0db6-4c80-a9d1-700c2b1c5b80")
| extend IsOverLake=iff(SOCHostName == "soc", "No", "Yes")
| extend SOCHostName=iff(IsOverLake == "No", "-", SOCHostName)
| project IsOverLake, SOCHostName, SocNodeId, BackplaneMetrics, BackplaneMemoryMetrics,SOCDashboard
| evaluate narrow()
| project Column, Value
```

### SOC Crash Event

```kql
let nid = nodeid;
let starttime = _startTime;
let endtime = _endTime;
cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2
| where NodeId == nid
| extend _HostNameSoC = tolower(strcat(HostName,"SOC"))
| distinct _HostNameSoC,NodeId,Region,_cluster = DataCenterName
| join kind=inner (cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
| where PreciseTimeStamp > starttime - 1h and PreciseTimeStamp < endtime + 1h ) on $left._HostNameSoC==$right.apMachine
| project PreciseTimeStamp,faultingModule,faultingProcess,bucketString,_HostNameSoC, NodeId,Region,_cluster, dumpUid, bugLink
| join (cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2 | where PreciseTimeStamp > starttime - 1h and PreciseTimeStamp < endtime + 1h)  on dumpUid
| project PreciseTimeStamp=PreciseTimeStamp1, NodeId, crashProcessFullPath,  faultingModule, faultingProcess, bucketString, osBuildInfo, dumpURL=strcat("https://portal.watson.azure.com/dump?dumpUID=", dumpUid), bugLink
//cluster('Gandalfdeepad').database('gandalf_deepAD').GetSocCrashData()
//| where PreciseTimeStamp >= starttime - 1h and PreciseTimeStamp < endtime + 1h
//| where NodeId == nid
//| join cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2 on dumpUid
//| project PreciseTimeStamp=PreciseTimeStamp1, SocNodeId, NodeId, crashProcessFullPath,  faultingModule, faultingProcess, bucketString,Generation, osBuildInfo, dumpURL=strcat("https://portal.watson.azure.com/dump?dumpUID=", dumpUid)

```

### LogNodeSnapshot

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let nid = tolower(nodeid);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| where shoeboxMdmAccountName != ""
| extend shoe = trim(" ", shoeboxMdmAccountName)
| distinct Region, shoeboxMdmAccountName=shoe);
cluster('AzureCM').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where nodeId == nid
| project PreciseTimeStamp, nodeState, nodeAvailabilityState, containerCount, hostingEnvironment, faultDomain, nfcContainerWorkflowsEnabled, ipAddress,isIsolated, isOffline,vlanId, healthSignals
| summarize StatusStartTime=min(PreciseTimeStamp), StatusEndTime=max(PreciseTimeStamp) by nodeState, nodeAvailabilityState, containerCount, hostingEnvironment, faultDomain, nfcContainerWorkflowsEnabled, ipAddress,isIsolated, isOffline,vlanId, healthSignals
| project StatusStartTime, StatusEndTime, nodeState, nodeAvailabilityState, containerCount, hostingEnvironment, faultDomain, nfcContainerWorkflowsEnabled, ipAddress,isIsolated, isOffline,vlanId, healthSignals
```

### Host NIC Discard Counter

```kql
let starttime = _startTime;
let endtime = _endTime;
let nid = tolower(nodeid);
union cluster('netperf').database('NetPerfKustoDB').HostNetNicCx4Stats(nid, starttime, endtime),cluster('netperf').database('NetPerfKustoDB').HostNetNicCx3Stats(nid, starttime, endtime) 
| project RowTimeStamp,Packets_Received_Errors,Packets_Received_Discarded_No_Recv_WQEs,Packets_Received_Frame_Length_Error,Packets_Received_Bad_CRC_Error,Packets_Received_Symbol_Error,Packets_Outbound_Errors,Packets_Outbound_Discarded,Rdma_Bytes_Received,Rdma_Bytes_Sent,Rdma_Packets_Received,Rdma_Packets_Sent,Link_State_Change_Down_Events,Link_State_Change_Events,VfPort_Packets_Outbound_Errors,VfPort_Packets_Outbound_Discarded,VfPort_Packets_Received_Errors,VfPort_Packets_Received_Discarded
| render timechart 

```


### Anvil Repair Service Request

```kql
let starttime = _startTime;
let endtime = _endTime;
let nid = tolower(nodeid);
cluster('aplat.westcentralus').database('APlat').AnvilRepairServiceRequestSnapshot 
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where ResourceId == nid
| project PreciseTimeStamp, ResourceId, RequestAuthor, Status, SubStatus,CorrelationIdentifier, Request
```

---

## CAs-To-VMs

### Src VMs

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ContainerId = ContainerID;
let CAs = pack_array(split(SrcVMs, ","))[0];
let subid = pack_array(split(SubscriptionID, ","))[0];
let rin=cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId in~ (subid)
| where PrivateIPAddress  has_any (CAs)
| extend RoleInstanceName=tostring(strcat("_",split(VirtualMachineArmId, "virtualMachines/")[1]))
| distinct RoleInstanceName;
let VMCAs=materialize(cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId in~ (subid)
| where PrivateIPAddress  has_any (CAs)
| extend RoleInstanceName=tostring(strcat("_",split(VirtualMachineArmId, "virtualMachines/")[1]))
| summarize CAs=make_list(PrivateIPAddress) by RoleInstanceName
| extend CAs = strcat_array(CAs, ", ")
| distinct RoleInstanceName, CAs);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where subscriptionId in~ (subid)
| where roleInstanceName in (rin)
| distinct roleInstanceName, Tenant, NodeId=toupper(nodeId), containerId, AvailabilityZone, virtualMachineUniqueId, OSType=tostring(split(billingType, "|")[0]),VMSize=tostring(split(billingType, "|")[1]), Region,creationTime, DataCenterName,subscriptionId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| summarize T0=tostring(make_list(EndDevice)) by roleInstanceName, Tenant, NodeId, nodeId=tolower(NodeId), containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, DataCenterName,subscriptionId,EndPort
| join VMCAs on $left.roleInstanceName == $right.RoleInstanceName
| join kind=leftouter cluster('AzureCM').database('AzureCM').LogNodeSnapshot on nodeId
| distinct creationTime,roleInstanceName, CAs,Region, DataCenterName, AvailabilityZone, Tenant, NodeId,NodeIP=ipAddress, containerId, OSType,VMSize, T0,EndPort,subscriptionId
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| extend PhyNet=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-Regionn=v-", Region,"#a7c46df8-e9c6-407a-b161-a267e1cf4ab8")

```

### Dst VMs

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ContainerId = ContainerID;
let CAs = pack_array(split(DstVMs, ","))[0];
let subid = pack_array(split(SubscriptionID, ","))[0];
let rin=cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId in~ (subid)
| where PrivateIPAddress  has_any (CAs)
| extend RoleInstanceName=tostring(strcat("_",split(VirtualMachineArmId, "virtualMachines/")[1]))
| distinct RoleInstanceName;
let VMCAs=materialize(cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId in~ (subid)
| where PrivateIPAddress  has_any (CAs)
| extend RoleInstanceName=tostring(strcat("_",split(VirtualMachineArmId, "virtualMachines/")[1]))
| summarize CAs=make_list(PrivateIPAddress) by RoleInstanceName
| extend CAs = strcat_array(CAs, ", ")
| distinct RoleInstanceName, CAs);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where subscriptionId in~ (subid)
| where roleInstanceName in (rin)
| distinct roleInstanceName, Tenant, NodeId=toupper(nodeId), containerId, AvailabilityZone, virtualMachineUniqueId, OSType=tostring(split(billingType, "|")[0]),VMSize=tostring(split(billingType, "|")[1]), Region,creationTime, DataCenterName,subscriptionId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| summarize T0=tostring(make_list(EndDevice)) by roleInstanceName, Tenant, NodeId, nodeId=tolower(NodeId), containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, DataCenterName,subscriptionId,EndPort
| join VMCAs on $left.roleInstanceName == $right.RoleInstanceName
| join kind=leftouter cluster('AzureCM').database('AzureCM').LogNodeSnapshot on nodeId
| distinct creationTime,roleInstanceName, CAs,Region, DataCenterName, AvailabilityZone, Tenant, NodeId,NodeIP=ipAddress, containerId, OSType,VMSize, T0,EndPort,subscriptionId
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| extend PhyNet=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-Regionn=v-", Region,"#a7c46df8-e9c6-407a-b161-a267e1cf4ab8")

```

### WAN

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ContainerId = ContainerID;
let SrcCAs = pack_array(split(SrcVMs, ","))[0];
let DstCAs = pack_array(split(DstVMs, ","))[0];
let RegionMap = datatable(CMTMRegion: string, SSRegion: string)
[
"canadacentral", "canadacentral",
"northeurope", "europenorth",
"uaecentral", "uaec",
"southafricawest", "southafricaw",
"koreasouth", "koreasouth",
"westus3", "uswest3",
"japaneast", "japaneast",
"gcp", "gcp",
"australiaeast", "australiaeast",
"australiacentral2", "australiac",
"northcentralus", "usnorth",
"australiasoutheast", "australiasoutheast",
"norwayeast", "norwaye",
"australiacentral", "australiac",
"koreacentral", "koreacentral",
"francecentral", "francec",
"germanynorth", "",
"switzerlandnorth", "germanyn",
"qatarcentral", "qatarc",
"ukwest", "ukwest",
"westus", "uswest",
"norwaywest", "norwayw",
"centralus", "uscentral",
"westus2", "uswest2",
"francesouth", "frances",
"germanywestcentral", "germanywc",
"southeastasia", "asiasoutheast",
"westeurope", "europewest",
"westcentralus", "uswestcentral",
"japanwest", "japanwest",
"uaenorth", "uaen",
"italynorth", "italyn",
"southindia", "indiasouth",
"canadaeast", "canadaeast",
"eastasia", "asiaeast",
"uksouth", "uksouth",
"eastus2", "useast2",
"southafricanorth", "southafrican",
"southcentralus", "southcentralus",
"centralindia", "indiacentral",
"eastus", "useast",
"brazilsouth", "brazilsouth",
"switzerlandwest", "switzerlandw",
"israelcentral", "israelc",
"westindia", "indiawest",
"polandcentral", "polandc",
"aws", "aws",
"swedencentral", "swedenc"
];
let SrcIN=cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId == SubscriptionID
| where PrivateIPAddress  has_any (SrcCAs)
| extend RoleInstanceName=tostring(strcat("_",split(VirtualMachineArmId, "virtualMachines/")[1]))
| distinct RoleInstanceName;
let DstIN=cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
| where SubscriptionId == SubscriptionID
| where PrivateIPAddress  has_any (DstCAs)
| extend RoleInstanceName=tostring(strcat("_",split(VirtualMachineArmId, "virtualMachines/")[1]))
| distinct RoleInstanceName;
let SrcRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where subscriptionId == SubscriptionID
| where roleInstanceName in (SrcIN)
| distinct SrcR=Region
| join RegionMap on $left.SrcR == $right.SSRegion
| distinct CMTMRegion);
let DstRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where subscriptionId == SubscriptionID
| where roleInstanceName in (DstIN)
| distinct DstR=Region
| join RegionMap on $left.DstR == $right.SSRegion
| distinct CMTMRegion);
print SrcRegion=SrcRegion,DstRegion=DstRegion
| extend WAN=iff(SrcRegion == DstRegion, "Not Cross-Region Traffic, No WAN", strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SourceRegion=v-", SrcRegion,"&p-DestinationRegion=v-",DstRegion, "&p-RouteHop=all#00ec7e66-85fb-450e-a82e-898ef66ecdff"))
| evaluate narrow()
| project Key=Column, Value
```


## CAs-To-VMs-Temu

### Src VMs

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let CAs = pack_array(split(SrcVMs, ","))[0];
let _vnetid = dynamic(['9b20a390-8c10-4a0e-9257-eee34ffdcb02','8dcd538f-fcfb-4085-b448-0777e5ca7bd5','a9cf29fd-692d-47fe-a882-f36e2c82be9e','b2932e8e-5d18-4682-a325-79d702a0feb3','123f177b-a4c9-4a3d-be99-42d46b3d545b','7016ee85-2af4-4152-a9ab-065edb0a1f49','38748766-b72d-4110-84bb-967121961daf','df6350ad-7575-4efe-a1b7-e138ef0b1a00','5be9a5c7-c053-47bf-887d-8912c8b808da','e0292405-e3f7-4c7b-b3f3-ec07718439df','fa4905cf-3bae-4799-9d7b-a591e6a114d0','4869b656-11a8-4d27-b2e5-02121d6ababd','0c8cf26a-7629-4dce-a2aa-69e4cd22327d','dd98d4f9-c3bd-40c9-b374-9097c41f3756','9362f794-0fa8-4669-9cb2-769c0208bdc4','63e016a5-e6ab-4e92-85d5-e0d35f7123f7','c5054212-d2bf-42dc-a2c9-976ff72f9674','dc71d728-65e2-4ff4-98cb-b8083e8942aa','8d59369e-be4c-49c1-83be-066242c3140a','dfaf25dc-a887-411d-9424-a35e503af052','1fa4ea7c-e4d1-4408-b79d-813f02030a4d','0c308091-3c8f-44c4-8a4e-97e8ab7362a5','43f90b10-27af-4da9-9c14-6295bafb9084','e9ec03c2-e893-403a-9ffb-22faaefc8b13','be9e6cbb-1bf9-461c-9b47-2a106002ff16','3b28f358-f02e-4d20-8f40-40ca58513224','bd37dadf-aab1-41be-a1d0-bf00ff24effc','45a9ce26-98c3-4378-ad53-0de5d22d312b','885c54bf-8a43-4e65-9a0c-0018d27f386f','73f3bb54-c142-4778-b58a-abf8058d1309','6fbd6580-e33f-499e-916b-5cf79c8279d9','901e6274-e007-4ee4-a440-715461b2667b','01bb47bb-e42c-456d-945f-0761bc93eef1','92eb5ad0-1435-475a-8132-445515abfa4b','ad7f4c51-f91e-4198-becc-d6e0e49043d3','07f9a0f3-bf67-4447-bb41-8b9dc30e245c','467d67e2-a3f7-4e5f-8ec2-a390bc4ffab1','9b9da58e-6788-4664-b273-b26095854f44']);
let _subscriptionId = dynamic(['17158733-19f8-40df-b516-8303d1a10eea', '3c4f0f9b-40a2-43aa-8d7b-e1d2f0d52bad', '3ee645ef-8d96-454d-ae2f-a7512eccbd70', '5e4e755b-4b9c-4c5c-8f7a-0ba28ebdc533', '6b089ca3-c5f8-4e30-a21d-fb33da0bb6aa', '75958559-220a-4a78-84e0-feb487f25b27', '80d97b89-688a-4bb3-b6ea-71baf87b097c', '9644e9ef-8999-4a16-9319-5cb434dfc9a8', 'b6de5243-ef68-47f5-8f6d-6f48103d7c09', 'f2143dfe-bd27-4d71-b370-2a24e340fbf4', 'fe1cf735-1dd8-4121-b1fa-1abf61733e7b']);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot
| distinct Region, shoeboxMdmAccountName);
cluster('azurecm').database('AzureCM').DCMLNMPubSubTaskEventEtwTable
| where VnetId in~ (_vnetid)
| where TIMESTAMP >= ago(30d)
| where CustomerAddress in~ (CAs)
| where CAMappingData contains 'ContainerId'
| summarize arg_max(TIMESTAMP, *) by CustomerAddress 
| extend ContainerId = extract(@"ContainerId:([0-9a-fA-F-]+)", 1, CAMappingData)
| project TIMESTAMP, Region, VnetId, CustomerAddress,SourceNodeId,ContainerId 
| join kind=inner (cluster('AzureCM').database('AzureCM').LogContainerSnapshot | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where subscriptionId in~ (_subscriptionId)) on $left.ContainerId == $right.containerId
| distinct roleInstanceName, Tenant, SourceNodeId,nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType=tostring(split(billingType, "|")[0]),VMSize=tostring(split(billingType, "|")[1]), Region,creationTime,tenantName,containerType, DataCenterName,  subscriptionId,availabilitySetName,VnetId, CustomerAddress,TIMESTAMP
| join kind=inner cluster("vnetkusto.northcentralus").database("veritas").ContainerInformationEvent on $left.containerId == $right.ContainerId
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| distinct roleInstanceName, Tenant, nodeId, containerId, DataCenterName,AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress=tostring(split(PortId, "_")[1]),tenantName,containerType,subscriptionId,availabilitySetName,VnetId, CustomerAddress,TIMESTAMP
| join kind=inner ShoeBoxMdm on $left.Region == $right.Region
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend NodeIdUpper=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on $left.NodeIdUpper == $right.NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceStatic) on DeviceName
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceIpInterface| where AddressesV4 !="" ) on DeviceName
| join kind=leftouter(cluster('vnetkusto.northcentralus').database('veritas').ContainerInformationEvent| where OSVersion !=""| distinct ContainerId, PortId, OS, OSVersion) on $left.containerId == $right.ContainerId
| join kind=leftouter(cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps | project Cluster,VNETAccount,VfpAccount) on $left.Cluster == $right.Cluster
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| extend PhyNet=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-Regionn=v-", Region,"#a7c46df8-e9c6-407a-b161-a267e1cf4ab8")
| distinct roleInstanceName,creationTime, CustomerAddress,subscriptionId,Region,AvailabilityZone,DataCenterName,Cluster=Tenant,nodeId,containerId,HostV4address = AddressesV4,EndDevice, TorHostPort = EndPort, PortId ,HostV6address = AddressesV6, VnetId,tenantName, MACAddress,OSType, OSVersion1, containerType,virtualMachineUniqueId,availabilitySetName,VMdash,PhyNet
| summarize TOR=strcat_array(make_set(EndDevice), ", "), TORHostPort=strcat_array(make_set(TorHostPort), ", "),VMPortId=strcat_array(make_set(PortId), ", ") by roleInstanceName,creationTime, CustomerAddress,subscriptionId,Region,AvailabilityZone,DataCenterName,Cluster,nodeId,containerId,HostV4address,HostV6address, VnetId,tenantName, MACAddress,OSType, OSVersion1, containerType,virtualMachineUniqueId,availabilitySetName,VMdash,PhyNet
| project roleInstanceName,creationTime, CustomerAddress,containerId, Cluster,VMdash,PhyNet, subscriptionId,Region,AvailabilityZone,DataCenterName,nodeId,HostV4address,HostV6address, VnetId,tenantName, MACAddress,OSType, OSVersion1, containerType,virtualMachineUniqueId,availabilitySetName



```

### Dst VMs

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let CAs = pack_array(split(DstVMs, ","))[0];
let _vnetid = dynamic(['9b20a390-8c10-4a0e-9257-eee34ffdcb02','8dcd538f-fcfb-4085-b448-0777e5ca7bd5','a9cf29fd-692d-47fe-a882-f36e2c82be9e','b2932e8e-5d18-4682-a325-79d702a0feb3','123f177b-a4c9-4a3d-be99-42d46b3d545b','7016ee85-2af4-4152-a9ab-065edb0a1f49','38748766-b72d-4110-84bb-967121961daf','df6350ad-7575-4efe-a1b7-e138ef0b1a00','5be9a5c7-c053-47bf-887d-8912c8b808da','e0292405-e3f7-4c7b-b3f3-ec07718439df','fa4905cf-3bae-4799-9d7b-a591e6a114d0','4869b656-11a8-4d27-b2e5-02121d6ababd','0c8cf26a-7629-4dce-a2aa-69e4cd22327d','dd98d4f9-c3bd-40c9-b374-9097c41f3756','9362f794-0fa8-4669-9cb2-769c0208bdc4','63e016a5-e6ab-4e92-85d5-e0d35f7123f7','c5054212-d2bf-42dc-a2c9-976ff72f9674','dc71d728-65e2-4ff4-98cb-b8083e8942aa','8d59369e-be4c-49c1-83be-066242c3140a','dfaf25dc-a887-411d-9424-a35e503af052','1fa4ea7c-e4d1-4408-b79d-813f02030a4d','0c308091-3c8f-44c4-8a4e-97e8ab7362a5','43f90b10-27af-4da9-9c14-6295bafb9084','e9ec03c2-e893-403a-9ffb-22faaefc8b13','be9e6cbb-1bf9-461c-9b47-2a106002ff16','3b28f358-f02e-4d20-8f40-40ca58513224','bd37dadf-aab1-41be-a1d0-bf00ff24effc','45a9ce26-98c3-4378-ad53-0de5d22d312b','885c54bf-8a43-4e65-9a0c-0018d27f386f','73f3bb54-c142-4778-b58a-abf8058d1309','6fbd6580-e33f-499e-916b-5cf79c8279d9','901e6274-e007-4ee4-a440-715461b2667b','01bb47bb-e42c-456d-945f-0761bc93eef1','92eb5ad0-1435-475a-8132-445515abfa4b','ad7f4c51-f91e-4198-becc-d6e0e49043d3','07f9a0f3-bf67-4447-bb41-8b9dc30e245c','467d67e2-a3f7-4e5f-8ec2-a390bc4ffab1','9b9da58e-6788-4664-b273-b26095854f44']);
let _subscriptionId = dynamic(['17158733-19f8-40df-b516-8303d1a10eea', '3c4f0f9b-40a2-43aa-8d7b-e1d2f0d52bad', '3ee645ef-8d96-454d-ae2f-a7512eccbd70', '5e4e755b-4b9c-4c5c-8f7a-0ba28ebdc533', '6b089ca3-c5f8-4e30-a21d-fb33da0bb6aa', '75958559-220a-4a78-84e0-feb487f25b27', '80d97b89-688a-4bb3-b6ea-71baf87b097c', '9644e9ef-8999-4a16-9319-5cb434dfc9a8', 'b6de5243-ef68-47f5-8f6d-6f48103d7c09', 'f2143dfe-bd27-4d71-b370-2a24e340fbf4', 'fe1cf735-1dd8-4121-b1fa-1abf61733e7b']);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot
| distinct Region, shoeboxMdmAccountName);
cluster('azurecm').database('AzureCM').DCMLNMPubSubTaskEventEtwTable
| where VnetId in~ (_vnetid)
| where TIMESTAMP >= ago(90d)
| where CustomerAddress in~ (CAs)
| where CAMappingData contains 'ContainerId'
| summarize arg_max(TIMESTAMP, *) by CustomerAddress 
| extend ContainerId = extract(@"ContainerId:([0-9a-fA-F-]+)", 1, CAMappingData)
| project TIMESTAMP, Region, VnetId, CustomerAddress,SourceNodeId,ContainerId 
| join kind=inner (cluster('AzureCM').database('AzureCM').LogContainerSnapshot | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where subscriptionId in~ (_subscriptionId)) on $left.ContainerId == $right.containerId
| distinct roleInstanceName, Tenant, SourceNodeId,nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType=tostring(split(billingType, "|")[0]),VMSize=tostring(split(billingType, "|")[1]), Region,creationTime,tenantName,containerType, DataCenterName,  subscriptionId,availabilitySetName,VnetId, CustomerAddress,TIMESTAMP
| join kind=inner cluster("vnetkusto.northcentralus").database("veritas").ContainerInformationEvent on $left.containerId == $right.ContainerId
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| distinct roleInstanceName, Tenant, nodeId, containerId, DataCenterName,AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress=tostring(split(PortId, "_")[1]),tenantName,containerType,subscriptionId,availabilitySetName,VnetId, CustomerAddress,TIMESTAMP
| join kind=inner ShoeBoxMdm on $left.Region == $right.Region
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend NodeIdUpper=toupper(nodeId)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on $left.NodeIdUpper == $right.NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceStatic) on DeviceName
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceIpInterface| where AddressesV4 !="" ) on DeviceName
| join kind=leftouter(cluster('vnetkusto.northcentralus').database('veritas').ContainerInformationEvent| where OSVersion !=""| distinct ContainerId, PortId, OS, OSVersion) on $left.containerId == $right.ContainerId
| join kind=leftouter(cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps | project Cluster,VNETAccount,VfpAccount) on $left.Cluster == $right.Cluster
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| extend PhyNet=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-Regionn=v-", Region,"#a7c46df8-e9c6-407a-b161-a267e1cf4ab8")
| distinct roleInstanceName,creationTime, CustomerAddress,subscriptionId,Region,AvailabilityZone,DataCenterName,Cluster=Tenant,nodeId,containerId,HostV4address = AddressesV4,EndDevice, TorHostPort = EndPort, PortId ,HostV6address = AddressesV6, VnetId,tenantName, MACAddress,OSType, OSVersion1, containerType,virtualMachineUniqueId,availabilitySetName,VMdash,PhyNet
| summarize TOR=strcat_array(make_set(EndDevice), ", "), TORHostPort=strcat_array(make_set(TorHostPort), ", "),VMPortId=strcat_array(make_set(PortId), ", ") by roleInstanceName,creationTime, CustomerAddress,subscriptionId,Region,AvailabilityZone,DataCenterName,Cluster,nodeId,containerId,HostV4address,HostV6address, VnetId,tenantName, MACAddress,OSType, OSVersion1, containerType,virtualMachineUniqueId,availabilitySetName,VMdash,PhyNet
| project roleInstanceName,creationTime, CustomerAddress,containerId, Cluster,VMdash,PhyNet, subscriptionId,Region,AvailabilityZone,DataCenterName,nodeId,HostV4address,HostV6address, VnetId,tenantName, MACAddress,OSType, OSVersion1, containerType,virtualMachineUniqueId,availabilitySetName
```

