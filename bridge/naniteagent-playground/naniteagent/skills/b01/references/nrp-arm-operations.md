---
description: KQL queries for NRP (Network Resource Provider) and ARM operations: API calls, throttling, write operations, error diagnosis.
---

# NRP & ARM Operations Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: NRP&NFVRP, ARM, Resource Graph

## NRP&NFVRP

### CRUD request based on Subscription ID and Resource URI(HttpIncomingRequests)

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId", "", CorrelationId);
//let ARMCorrelationIds=materialize(cluster('ARMProd').database('ARMProd').HttpIncomingRequests
let ARMCorrelationIds=materialize(union cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests,cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests,cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where subscriptionId == SubscriptionID
| where targetUri contains resourceid
//| where correlationId contains corrId
| extend URI=split(targetUri, "?")
| extend ResourceUri = tostring(split(URI[0], "443")[1]),RequestParameters = tostring(URI[1])
| where ResourceUri !contains "diagnosticIdentity"
| distinct PreciseTimeStamp,RoleLocation,clientApplicationId, clientIpAddress,correlationId,TaskName, operationName, httpMethod,httpStatusCode, failureCause, ResourceUri,RequestParameters,targetUri,  authorizationAction);
ARMCorrelationIds;



```

### GatewayServiceOperationEtwEvent

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let GatewayServiceOperation=materialize(cluster('Nrp').database("mdsnrp").GatewayServiceOperationEtwEvent
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where CorrelationRequestId == corrId
| project PreciseTimeStamp, RoleInstance, EventCode, Level,OperationId,CorrelationRequestId, Message
| order by PreciseTimeStamp asc);
GatewayServiceOperation;


```

### FrontendOperationEtwEvent

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let FrontendOperationEtwEvent=materialize(cluster('Nrp').database('mdsnrp').FrontendOperationEtwEvent 
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where CorrelationRequestId == corrId
| project PreciseTimeStamp, ResourceType,ResourceGroup, ResourceName, OperationName, Message);
FrontendOperationEtwEvent
```

### ReadOperationResponseEtwEvent

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let ReadOperationResponseEtwEvent=materialize(cluster('Nrp').database('mdsnrp').ReadOperationResponseEtwEvent 
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where CorrelationRequestId == corrId
| project PreciseTimeStamp, Uri,Request, Response, HttpStatusCode);
ReadOperationResponseEtwEvent


```

### WriteOperationResponseEtwEvent

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let WriteOperationResponseEtwEvent=materialize(cluster('Nrp').database('mdsnrp').WriteOperationResponseEtwEvent 
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where CorrelationRequestId == corrId
| project PreciseTimeStamp, Uri,Request, Response, HttpStatusCode);
WriteOperationResponseEtwEvent


```

### EventServiceEntries

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
union cluster('armprodsea.southeastasia').database('Requests').EventServiceEntries,cluster('armprodeus.eastus').database('Requests').EventServiceEntries,cluster('armprodweu.westeurope').database('Requests').EventServiceEntries
//cluster('ARMProd').database('ARMProd').EventServiceEntries
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where correlationId == corrId
| distinct PreciseTimeStamp,status, subStatus,operationName, resourceUri, correlationId, properties, claims



```

### NRP - FrontendOperationEtwEvent - Critical Event

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let FrontendOperationEtwEvent=materialize(cluster('Nrp').database('mdsnrp').FrontendOperationEtwEvent 
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where CorrelationRequestId == corrId
| extend  Severity = iff(Level == 2, "Critical", "Default")
| where Severity == "Critical"
//| project PreciseTimeStamp, ResourceType,ResourceGroup, ResourceName, HttpMethod, OperationName, Message,Level
| project PreciseTimeStamp,OperationName, OperationId, Message,Level);
FrontendOperationEtwEvent;



```

### NFVRP-FrontendEvent

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let NFVRPFrontend=materialize(cluster('Hybridnetworking').database('NfvRpMds').FrontendEvent
| where env_time > starttime and env_time < endtime
| where CorrelationRequestId == corrId
| project env_time, ActivityID, ErrorLevel, Message);
NFVRPFrontend
```

### NFVRP-BackendEvent

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
let NFVRPBackend=materialize(cluster('Hybridnetworking').database('NfvRpMds').BackendEvent
| where env_time > starttime and env_time < endtime
| where CorrelationRequestId == corrId
| project env_time, OperationName, ActivityID,ErrorLevel, Message);
NFVRPBackend
```

### ARM Trace Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let resourceid = ResourceURI;
let corrId = iff(CorrelationId == "CorrelationRequestId" or CorrelationId == "", "CorrelationRequestId", CorrelationId);
union cluster('armprodsea.southeastasia').database('Traces').Traces,cluster('armprodeus.eastus').database('Traces').Traces,cluster('armprodweu.westeurope').database('Traces').Traces
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where correlationId == corrId
| project PreciseTimeStamp, message, exception



```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/nrp";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/nrp" | summarize count();
union pv, pvcount
```

## ARM

### Throttles (ARM HTTPIncoming  429)

```kql
let subscription = SubscriptionID;
let startTime = ['_startTime'];
let endTime = ['_endTime'];
//cluster('armprod').database('ARMProd').HttpIncomingRequests
union cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests,cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests,cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests
| where TIMESTAMP >= startTime and TIMESTAMP <= endTime
//| where targetResourceProvider == "MICROSOFT.NETWORK"
| where httpStatusCode != -1 and httpStatusCode == 429
| where subscriptionId == subscription
| summarize ThrottleCount=count() by subscriptionId, targetResourceProvider, httpMethod, operationName, failureCause
| order by ThrottleCount desc
```

### Throttles (ARM HttpOutgoing)

```kql
//let _regionValue = region;
let subscription = SubscriptionID;
let startTime = ['_startTime'];
let endTime = ['_endTime'];
//let regionMeta = split(['_regionValue'], "|");
//let crpRegion = regionMeta[0];
//let nrpRegion = regionMeta[1];
let resourceProviders = dynamic(["MICROSOFT.NETWORK","MICROSOFT.COMPUTE"]);
//cluster('armprod').database('ARMProd').HttpOutgoingRequests
union cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests,cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests,cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests
| where PreciseTimeStamp >= startTime and PreciseTimeStamp <= endTime
| where subscriptionId == ['subscription']
| where httpStatusCode != -1
//| where hostName startswith crpRegion
//| where operationName contains "Microsoft.Network"
| summarize allcalls=count(), success=countif(httpStatusCode==200 or httpStatusCode==201 or httpStatusCode==202 or httpStatusCode==204), 429_throttle=countif(httpStatusCode==429), 404_NotFound=countif(httpStatusCode==404), 403_Forbidden=countif(httpStatusCode==403), 400_BadRequest=countif(httpStatusCode==400) by subscriptionId, hostName, operationName
| extend  percentthrottle=round((429_throttle*100.0/allcalls), 4)
| project subscriptionId, hostName, operationName, allcalls, success, 429_throttle, percentthrottle, 404_NotFound, 403_Forbidden, 400_BadRequest
| order by 429_throttle desc
```

### NRP Read / Write Throttles

```kql
let subscription = SubscriptionID;
let startTime = ['_startTime'];
let endTime = ['_endTime'];
let WriteOperation429s =
(
    cluster('nrp').database('mdsnrp').WriteOperationResponseEtwEvent
    | where PreciseTimeStamp >= startTime and PreciseTimeStamp <= endTime
    | where SubscriptionId == ['subscription']
  //  | where Region == nrpRegion
    | where HttpStatusCode == "429"
    | summarize Count=count(), TRPUT429 = countif(Response contains "RetryableErrorDueToAnotherOperation"),RTO429 = countif(Response contains "RetryableErrorDueToRequestTimedOut"),  THROT429 = countif(Response contains "RetryableErrorDueToTooManyCalls"), DATA429 = countif(Response contains "RetryableErrorDueTooHighReadDataSize"),  BQT429 = countif(Response contains "RetryableErrorDueToBatchQueueTimeout"),  RRNP429 = countif(Response contains "ReferencedResourceNotProvisioned"), min(TIMESTAMP), max(TIMESTAMP) by SubscriptionId, Region, OperationName
);
let ReadOperation429s =
(
    cluster('nrp').database('mdsnrp').ReadOperationResponseEtwEvent
    | where PreciseTimeStamp >= startTime and PreciseTimeStamp <= endTime
    | where SubscriptionId == ['subscription']
 //   | where Region == nrpRegion
    | where HttpStatusCode == "429"
    | summarize Count=count(), TRPUT429 = countif(Response contains "RetryableErrorDueToAnotherOperation"), RTO429 = countif(Response contains "RetryableErrorDueToRequestTimedOut"), THROT429 = countif(Response contains "RetryableErrorDueToTooManyCalls"), DATA429 = countif(Response contains "RetryableErrorDueTooHighReadDataSize"), BQT429 = countif(Response contains "RetryableErrorDueToBatchQueueTimeout"), RRNP429 = countif(Response contains "ReferencedResourceNotProvisioned"), min(TIMESTAMP), max(TIMESTAMP) by SubscriptionId, Region, OperationName
);
union WriteOperation429s, ReadOperation429s
| order by SubscriptionId asc, Region asc, OperationName asc;
//TRPUT429=RetryableErrorDueToAnotherOperation
//THROT429=RetryableErrorDueToTooManyCalls
//DATA429=RetryableErrorDueTooHighReadDataSize
//BQT429==RetryableErrorDueToBatchQueueTimeout
//RRNP429==ReferencedResourceNotProvisioned
//TMC429=RetryableErrorDueToTooManyCallsToThisOperation
//RTO429=RetryableErrorDueToRequestTimedOut
```

### Current NRP Limitation

```kql
let subscription = SubscriptionID;
let startTime = ['_startTime'];
let endTime = ['_endTime'];
let nrpOperations = dynamic(["PutNicOperation"]);
let OperationQoS = (
    cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
    | where TIMESTAMP >= startTime and TIMESTAMP <= endTime
   // | where Region == nrpRegion
    | where SubscriptionId in (subscription)
    | where OperationName in ("PutNicOperation")
    | where Message has "has its throttling limits to be WritePer5Min:"
    | summarize hint.strategy=shuffle arg_max(TIMESTAMP, *) by Region, SubscriptionId
    | parse Message with * ' - Sequence Number: ' sequenceNumber ' has its throttling limits to be WritePer5Min: ' maxWriteOrDeleteCallsPer5Min:int ', GetPer5Min: ' maxGetCallsPer5Min:int ', ReadSizeper5Min: ' maxReadSizeInMbPer5Min :int *
    | project Region, SubscriptionId, maxWriteOrDeleteCallsPer5Min, maxGetCallsPer5Min, maxReadSizeInMbPer5Min 
    | order by SubscriptionId
);
OperationQoS
```

### NRP Read Data Size Per 5 Minutes (MB)

```kql
let subscription = SubscriptionID;
let startTime = ['_startTime'];
let endTime = ['_endTime'];
cluster('nrp.kusto.windows.net').database('mdsnrp').KvsTransactionEtwEvent
| where PreciseTimeStamp >= startTime and PreciseTimeStamp <= endTime
| where SubscriptionId == subscription
| project PreciseTimeStamp, SubscriptionId, ReadSize, RoleInstance, Pid, Tenant, Region
| summarize TotalReadsInMb=sum(ReadSize)/1000000.0 by bin(PreciseTimeStamp, 5m), Region
| order by PreciseTimeStamp asc
| render timechart


```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/arm";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/arm" | summarize count();
union pv, pvcount
```

## Resource Graph

### Resource Graph

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime and timestamp <= endtime
//| where subscriptionId == SubscriptionID
| where id in~ (ResourceURI) or subscriptionId == ResourceURI
| project timestamp, id, type, location,properties
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/resourcegraph";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/resourcegraph" | summarize count();
union pv, pvcount
```

