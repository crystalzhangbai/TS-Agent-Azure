---
description: KQL queries for CRP API operations and compute capacity trends.
---

# CRP CRUD & Compute Capacity Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: CRP, Compute Capacity Trends

## CRP

### API QOS Event

```kql
let starttime = _startTime;
let endtime = _endTime;
let corrid = iff(isempty(ARMCorrelationId), "xyz", ARMCorrelationId);
cluster('azcrp').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where correlationId == corrid
| project PreciseTimeStamp , subscriptionId, region, resourceGroupName , resourceName, operationId, correlationId, operationName, httpStatusCode, resultCode, requestEntity, errorDetails  
```

### Context Activity

```kql
let starttime = _startTime;
let endtime = _endTime;
let corrid = iff(isempty(ARMCorrelationId), "xyz", ARMCorrelationId);
let OperationId = cluster('azcrp').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where correlationId == corrid
| distinct operationId;
cluster('azcrp').database('crp_allprod').ContextActivity
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where activityId  in (OperationId)
| project PreciseTimeStamp, RPTenant, activityId, traceCode, callerName, message
```

## Compute Capacity Trends

### Available Capacity Trends Per SKU

```kql
let starttime= _startTime;
let endtime = _endTime;
let ComputeRegion = CCRegion;
cluster("azureallocator.westcentralus.kusto.windows.net").database("AzureAllocator").AllocatorMonitoringLogAllocableVMCount
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Tenant has_all (ComputeRegion)
| where vmType in (ComputeSKU)
//| where vmType !has 'Promo'
| where deploymentType == "EnforcedMinusReservedAndDecom"// "EnforcedMinusReserved" for new deployment and "UpgradeMinusReserved" for upgrade
| where partitionType == "AvailabilityZone"
| summarize AvailabilityVMCount=sum(vmCount) by Cluster, PreciseTimeStamp = bin(todatetime(PreciseTimeStamp), 5m), deploymentType,partitionName
| project PreciseTimeStamp, Zone=partitionName, AvailabilityVMCount
| render timechart
```
