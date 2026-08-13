---
description: KQL queries for IcM incident data and CSAT (customer satisfaction) analysis.
---

# IcM & CSAT Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: IcM, CSATData

## IcM

### Ongoing Severity 0 and 1 IcM

```kql
cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  '')
| where Severity in (0,1)
| where OwningTeamName != "UKMETSUPERCOMPUTER\\Testing" and OwningTeamName != "ICMALERTSERVICE\\Triage"
| where Status == "ACTIVE"
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project IncidentId, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
```

### IcM Search

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("Icmcluster").database("IcmDataWarehouse").IncidentDescriptions 
| where Date > starttime and Date < endtime
| where Text has  keywords
| project Date, IncidentId , ChangedBy, Text 
| join cluster("Icmcluster").database("IcmDataWarehouse").Incidents on IncidentId
| distinct CreateDate, tostring(IncidentId), Title, OwningTenantName, OwningTeamName,RootCauseId
| where CreateDate > starttime and CreateDate < endtime
| where OwningTenantName contains tenantname
| where OwningTeamName contains teamname
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
```

## CSATData

### Raised Case History

```kql
let starttime = _startTime;
let endtime = _endTime;
let u360id = iff(isnotempty(U360ID), U360ID, "abcdefg");
cluster('u360sec').database('KPISupportData').CSATDataVNext
| where CreatedDateTime >= starttime and CreatedDateTime <= endtime
| where SubscriptionId == u360id or IncidentId == u360id  or Customer_TPID == u360id or TenantId == u360id or AgentAlias == u360id
| extend IsOngoing=iff(isempty(ClosedDateTime), "Ongoing", "Closed")
//| project Customer,Customer_TPID,IncidentId, SupportProductName, Title,SupportCountry, CreatedDateTime, ClosedDateTime,ModifiedDateTime, TotalCustomerSATScore, SurveyVerbatims,TenantId, AgentAlias
  | project Customer,SubscriptionId, CaseId=IncidentId, Product=SupportProductName, Title, IsOngoing, SupportCountry,ContractRegion=Customer_SalesRegionName, Score=TotalCustomerSATScore, CreatedDateTime, ClosedDateTime,ModifiedDateTime, SurveyVerbatims,TenantId, ContractId,TPID=Customer_TPID


```

### Score

```kql
let starttime = _startTime;
let endtime = _endTime;
let u360id = iff(isnotempty(U360ID), U360ID, "abcdefg");
cluster('u360sec').database('KPISupportData').CSATDataVNext
| where CreatedDateTime >= starttime and CreatedDateTime <= endtime
| where SubscriptionId == u360id or IncidentId == u360id  or Customer_TPID == u360id or TenantId == u360id  or AgentAlias == u360id
| extend TotalCustomerSATScore=toint(iff(isempty(TotalCustomerSATScore), 0, TotalCustomerSATScore))
| project CreatedDateTime=bin(CreatedDateTime, 1m), Case=IncidentId, Score=TotalCustomerSATScore
| render columnchart 


```

