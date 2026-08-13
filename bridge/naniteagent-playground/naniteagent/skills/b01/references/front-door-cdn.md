---
description: KQL queries for Azure Front Door and CDN: routing, origin health, WAF, edge node status.
---

# Azure Front Door & CDN Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: Azure Front Door, AFD Edge List

## Azure Front Door

### Azure Front Door List 

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscription = SubscriptionID;
let classicafd=cluster('azurecdn').database("azurecdnmds").FrontdoorSnapshot 
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId  == subscription
| where RequestPath != ""
| extend SKU="FrontDoor_Classic"
| extend ProfileId = FrontdoorId
| distinct Name, CName, FrontdoorId,ProfileId, Tenant, PartnerId, ResourceGroupName, RequestPath,CreatedTimeStamp,SKU, State=EnabledState;
let afdx=cluster('azurecdn').database("azurecdnmds").ProfilesSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId == subscription
| extend SKU = extract(@"Name\s*=\s*([^}]*)", 1, Sku)
| distinct Name=ProfileName, ProviderType, SKU,ProfileId, ResourceGroupName, Location, State, CreatedTimeStamp,PartnerId=strcat(ProfileId, "_", ProfileName);
union classicafd, afdx
| distinct Name,SKU,ProfileId,PartnerId, ResourceGroupName,CreatedTimeStamp

```

### Endpoint list Per specific Profile ID - <Default FQDN Only>

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscription = SubscriptionID;
let Pid=ProfileIds;
let min = datetime_diff('minute',endtime,starttime);
let classicafd=cluster('azurecdn').database("azurecdnmds").FrontdoorSnapshot 
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId  == subscription
| where RequestPath != ""
| extend SKU="FrontDoor_Classic"
| extend ProfileId=FrontdoorId
| distinct Name, CName, FrontdoorId, ProfileId, Tenant, PartnerId, ResourceGroupName, RequestPath,CreatedTimeStamp,SKU, State=EnabledState;
let afdx=cluster('azurecdn').database("azurecdnmds").ProfilesSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId == subscription
| extend SKU = extract(@"Name\s*=\s*([^}]*)", 1, Sku)
| distinct Name=ProfileName, ProviderType, SKU,ProfileId, ResourceGroupName, Location, State, CreatedTimeStamp,PartnerId=strcat(ProfileId, "_", ProfileName);
let ProfilezIDs=union classicafd, afdx
| where Name == Pid
| distinct ProfileId;
let afdxendpoint=cluster('azurecdn.kusto.windows.net').database("azurecdnmds").AfdEndpointSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp < endtime
| where ProfileId in (ProfilezIDs)
| distinct EndpointFQDN=HostName, ProvisioningState; //, ProviderUri
let afdclassicendpoint=cluster('azurecdn.kusto.windows.net').database("azurecdnmds").FrontendEndpointSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp < endtime
| where FrontdoorId in (ProfilezIDs)
| distinct EndpointFQDN=HostName, ProvisioningState=State;
union afdxendpoint,afdclassicendpoint
| where EndpointFQDN contains "azurefd.net"
```

### Azure Front Door Profile - Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscription = SubscriptionID;
let Pid=ProfileIds;
let min = datetime_diff('minute',endtime,starttime);
let classicafd=cluster('azurecdn').database("azurecdnmds").FrontdoorSnapshot 
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId  == subscription
| where RequestPath != ""
| extend SKU="FrontDoor_Classic"
| extend ProfileId=FrontdoorId
| distinct Name, CName, FrontdoorId, ProfileId, Tenant, PartnerId, ResourceGroupName, RequestPath,CreatedTimeStamp,SKU, State=EnabledState;
let afdx=cluster('azurecdn').database("azurecdnmds").ProfilesSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId == subscription
| extend SKU = extract(@"Name\s*=\s*([^}]*)", 1, Sku)
| distinct Name=ProfileName, ProviderType, SKU,ProfileId, ResourceGroupName, Location, State, CreatedTimeStamp,PartnerId=strcat(ProfileId, "_", ProfileName);
union classicafd, afdx
| where Name == Pid
| extend ResourceId = iff(isnotempty(FrontdoorId), strcat("/subscriptions/", subscription,"/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Network/frontdoors/",Name), strcat("/subscriptions/", subscription,"/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Cdn/profiles/",Name)) 
| extend PartnerDashboard=iff(isnotempty(FrontdoorId),strcat("https://jarvis-west.dc.ad.msft.net/dashboard/share/E37F9C52?overrides=[{%22query%22:%22//*[id='Partner']%22,%22key%22:%22value%22,%22replacement%22:%22",PartnerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true"),strcat("https://jarvis-west.dc.ad.msft.net/dashboard/share/E37F9C52?overrides=[{%22query%22:%22//*[id='Partner']%22,%22key%22:%22value%22,%22replacement%22:%22",ProfileId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true"))
| extend EndpointHealthDashboard = iff(isnotempty(FrontdoorId), strcat(" https://jarvis-west.dc.ad.msft.net/dashboard/share/BDCC5272?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceId, "%22},{%22query%22:%22//*[id='Partner']%22,%22key%22:%22value%22,%22replacement%22:%22",PartnerId, "%22},{%22query%22:%22//*[id='ApplicationEndpointPool']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true"),strcat(" https://jarvis-west.dc.ad.msft.net/dashboard/share/BDCC5272?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceId, "%22},{%22query%22:%22//*[id='Partner']%22,%22key%22:%22value%22,%22replacement%22:%22",ProfileId, "%22},{%22query%22:%22//*[id='ApplicationEndpointPool']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true"))
| extend WAF_DDOS = iff(isnotempty(FrontdoorId), "N/A",strcat("https://portal.microsoftgeneva.com/s/F4999735?overrides=[{%22query%22:%22//*[id='Partner']%22,%22key%22:%22value%22,%22replacement%22:%22",ProfileId ,"_",Name, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true"))
| extend  RoxyRequest=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=RoxyProd&en=RoxyHttpRequest&conditions=[[%22resource_id%22,%22contains%22,%22", ResourceId,"%22]]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend  ImpressionLogsSharedX=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=AFDProd&en=ImpressionLogShared0,ImpressionLogShared1,ImpressionLogShared2,ImpressionLogShared3,ImpressionLogShared4,ImpressionLogShared5,ImpressionLogShared6,ImpressionLogShared7,ImpressionLogShared8,ImpressionLogShared9&conditions=[[%22XResourceId%22,%22contains%22,%22", ResourceId,"%22]]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend WAFlog = strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=RoxyProd&en=WebApplicationFirewallCustomerLogs&conditions=[[%22resourceId%22,%22contains%22,%22", ResourceId,"%22]]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend afdcp = strcat("https://www.afdcp.com/admin/",ProfileId,"/")
| extend Healthprobelog = strcat("https://portal.microsoftgeneva.com/s/E08FD604")
| extend EdgeBGP = strcat("https://portal.microsoftgeneva.com/s/D16850F3")
| extend EdgeEnv = strcat("https://portal.microsoftgeneva.com/s/F5908DCE")
| extend Ocular = strcat("https://aka.ms/ocular-cdn?SubscriptionId=60181c42-6ab1-4a45-86e2-27d2a74ff8b0&ResourceGroup=ps-prod-azs-rg-qt-modernization&ResourceName=ps-prod-azs-cdn-pf-qt-modernization&globalFrom=2025-03-07T03:42:44.3057753Z&globalTo=2025-03-14T03:42:44.3057753Z")
| extend AcisApiLog = strcat("https://jarvis-west.dc.ad.msft.net/logs/dgrep?page=logs&be=DGrep&offset=-2&offsetUnit=Days&UTC=false&ep=Diagnostics%20PROD&ns=AzureCdnProd&en=ApiAnalytics,Logs&conditions=%5B%5B%22AnyField%22%2C%22contains%22%2C%22ps-prod-azs-cdn-pf-qt-modernization%22%5D%5D&chartEditorVisible=true&&chartType=Line&chartLayers=%5b%5b%22New%20Layer%22,%22%22%5d%5d%20")
| extend AFDEdgeLatencyCountry = strcat("https://aks.wan.azure.com/d/pCD7cfC4z/edge-latency-country-analysis?orgId=1&refresh=1h&var-country=France&kiosk")
| distinct CreatedTimeStamp,Name,SKU,ProfileId,PartnerId, ResourceId,PartnerDashboard, EndpointHealthDashboard,Healthprobelog,RoxyRequest,ImpressionLogsSharedX,WAFlog, afdcp,EdgeBGP,EdgeEnv,Ocular,AcisApiLog,AFDEdgeLatencyCountry //,WAF_DDOS
| evaluate narrow()
| project Key=Column, Value

//https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=2025-02-18T04:46:00.000Z&offset=-3&offsetUnit=Hours&UTC=true&ep=Diagnostics%20PROD&ns=RoxyProd,AFDProd&en=HealthProbeCustomerLogs&conditions=[["resourceId","contains","/subscriptions/0754aa07-6108-47ba-94ee-7823b5bf0bfe/resourcegroups/NP-GEN-EUS-EXT-FD-RG/providers/Microsoft.Cdn/profiles/np-gen-glbl-ext-001-fd"]]&kqlClientQuery=source%0A|%20extend%20json%20%3D%20parse_json(properties)%0A|%20extend%20healthProbeId%20%3D%20tostring(json.healthProbeId)%0A|%20extend%20pop%20%3D%20tostring(json.pop)%0A|%20extend%20pop%20%3D%20strcat(pop,tostring(json.POP))%0A|%20extend%20httpVerb%20%3D%20tostring(json.httpVerb)%0A|%20extend%20result%20%3D%20tostring(json.result)%0A|%20extend%20httpStatusCode%20%3D%20todouble(json.httpStatusCode)%0A|%20extend%20probeUrl%20%3D%20tostring(json.probeUrl)%0A|%20extend%20probeUrl%20%3D%20strcat(probeUrl,tostring(json.probeURL))%0A|%20extend%20originName%20%3D%20tostring(json.originName)%0A|%20extend%20originIP%20%3D%20tostring(json.originIP)%0A|%20extend%20totalLatencyMilliseconds%20%3D%20todouble(json.totalLatencyMilliseconds)%0A|%20extend%20connectionLatencyMilliseconds%20%3D%20todouble(json.connectionLatencyMilliseconds)%0A|%20extend%20dnsLatencyMilliseconds%20%3D%20todouble(json.dnsLatencyMilliseconds)%0A|%20project-away%20json,%20category,%20operationName,%20__SourceEvent__,%20__SourceMoniker__,%20properties%0A|%20where%20result%20%3D%3D%20"UnspecifiedError"&aggregatesVisible=true&aggregates=["Count%20by%20originName","Count%20by%20Tenant","Count%20by%20result"]&chartEditorVisible=true&chartType=line&chartLayers=[["New%20Layer",""]]%20
```

### WAF Policy list Per specific Profile ID

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscription = SubscriptionID;
let Pid=ProfileIds;
let min = datetime_diff('minute',endtime,starttime);
let classicafd=cluster('azurecdn').database("azurecdnmds").FrontdoorSnapshot 
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId  == subscription
| where RequestPath != ""
| extend SKU="FrontDoor_Classic"
| extend ProfileId=FrontdoorId
| distinct Name, CName, FrontdoorId, ProfileId, Tenant, PartnerId, ResourceGroupName, RequestPath,CreatedTimeStamp,SKU, State=EnabledState;
let afdx=cluster('azurecdn').database("azurecdnmds").ProfilesSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId == subscription
| extend SKU = extract(@"Name\s*=\s*([^}]*)", 1, Sku)
| distinct Name=ProfileName, ProviderType, SKU,ProfileId, ResourceGroupName, Location, State, CreatedTimeStamp,PartnerId=strcat(ProfileId, "_", ProfileName);
let ProfilezIDs=union classicafd, afdx
| where Name == Pid
| distinct ProfileId;
cluster('azurecdn').database("azurecdnmds").FrontdoorWafSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp < endtime + 5d
| where TenantId in (ProfilezIDs)
| distinct Name,SubscriptionId, ProtectionId, ResourceGroupName, State, Sku
```

### Substate of the Custom Domain’s Certificate deployment(CustomDomainSecureDeliverySnapshot)

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscription = SubscriptionID;
let Pid=ProfileIds;
let min = datetime_diff('minute',endtime,starttime);
let classicafd=cluster('azurecdn').database("azurecdnmds").FrontdoorSnapshot 
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId  == subscription
| where RequestPath != ""
| extend SKU="FrontDoor_Classic"
| extend ProfileId=FrontdoorId
| distinct Name, CName, FrontdoorId, ProfileId, Tenant, PartnerId, ResourceGroupName, RequestPath,CreatedTimeStamp,SKU, State=EnabledState;
let afdx=cluster('azurecdn').database("azurecdnmds").ProfilesSnapshot
| where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime 
| where SubscriptionId == subscription
| extend SKU = extract(@"Name\s*=\s*([^}]*)", 1, Sku)
| distinct Name=ProfileName, ProviderType, SKU,ProfileId, ResourceGroupName, Location, State, CreatedTimeStamp,PartnerId=strcat(ProfileId, "_", ProfileName);
let ProfilezIDx=union classicafd, afdx
| where Name == Pid
| distinct ProfileId;
let CDNxx=cluster('Azurecdn').database("azurecdnmds").CustomDomainSecureDeliverySnapshot
| where PreciseTimeStamp >= starttime - 30d and PreciseTimeStamp <= endtime 
| where ProfileId in (ProfilezIDx)
| project PreciseTimeStamp, HostName, ActivityId, Message, CertificateSourceParameters, CertificateAuthority;
let AFDxx=cluster('Azurecdn').database("azurecdnmds").AfdCustomDomainSnapshot
| where TIMESTAMP >= starttime - 30d and TIMESTAMP <= endtime 
| where ProfileId in (ProfilezIDx)
| project PreciseTimeStamp=TIMESTAMP, HostName,ActivityId, Message, DomainValidationToken, CertificateType, CertificateProviderUri, ManagedCertificateProviderUri;
union CDNxx, AFDxx


```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/afd";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/afd" | summarize count();
union pv, pvcount
```

## AFD Edge List

### AFD Edge List Per Country

```kql
let starttime= _startTime;
let endtime = _endTime;
let AFDxCountry=AFDCountry;
cluster('Afdmoi').database('afdmoi').AFD_EdgeEnvironments 
| where TimeStamp >= starttime - 5d and TimeStamp <= endtime
| where iff(isempty(AFDxCountry), ['Location.Country'] contains "", ['Location.Country'] in (AFDxCountry))
| summarize max(TimeStamp) by EdgeName,Cluster,['Location.City'],['Location.Country'],IPV4UnicastAddress,IPV6UnicastAddress,Enabled,IsOnNet,IsSupernode
| order by ['Location.Country'] desc  
```

### AFD Edge List Per Country

```kql
let starttime= _startTime;
let endtime = _endTime;
let AFDxCountry=AFDCountry;
cluster('Afdmoi').database('afdmoi').AFD_EdgeEnvironments 
| where TimeStamp >= starttime - 5d and TimeStamp <= endtime
| where iff(isempty(AFDxCountry), ['Location.Country'] contains "", ['Location.Country'] in (AFDxCountry))
| distinct ['Location.Country'], EdgeName
| summarize EdgeList=strcat_array(make_list(EdgeName), ", ") by Country=['Location.Country']
| order  by Country asc 
```

### AFD Edge Cluster List Per Country

```kql
let starttime= _startTime;
let endtime = _endTime;
let AFDxCountry=AFDCountry;
cluster('Afdmoi').database('afdmoi').AFD_EdgeEnvironments 
| where TimeStamp >= starttime - 5d and TimeStamp <= endtime
| where iff(isempty(AFDxCountry), ['Location.Country'] contains "", ['Location.Country'] in (AFDxCountry))
| distinct ['Location.Country'], Cluster
| summarize ClusterList=strcat_array(make_list(Cluster), ", ") by Country=['Location.Country']
| order by Country asc 
```

### AFD Edge List Per City

```kql
let starttime= _startTime;
let endtime = _endTime;
let AFDxCountry=AFDCountry;
cluster('Afdmoi').database('afdmoi').AFD_EdgeEnvironments 
| where TimeStamp >= starttime - 5d and TimeStamp <= endtime
| where iff(isempty(AFDxCountry), ['Location.Country'] contains "", ['Location.City'] in (AFDxCountry))
| distinct ['Location.City'], EdgeName
| summarize EdgeList=strcat_array(make_list(EdgeName), ", ") by City = ['Location.City']
| order by City asc  
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/afdedgedevice";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/afdedgedevice" | summarize count();
union pv, pvcount
```

