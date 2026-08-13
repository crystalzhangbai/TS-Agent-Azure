---
description: KQL queries for Azure Private Link troubleshooting - Private Endpoint and Private Link Service health checks, CRUD operations, and connectivity diagnostics.
---

# Azure Private Link Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01), Private Link TSG Wiki  
> Coverage: Private Endpoint and Private Link Service diagnostics

## Private Endpoint Health Checks

### Private Endpoint Health Check (QosEtwEvent)

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let PEName = PEName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == PEName
| where OperationName contains "PrivateEndpoint"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

### Private Endpoint NIC Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let PENICName = PENICName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == PENICName
| where OperationName contains "NetworkInterface"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

### Private Endpoint VNet Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let VNetName = VNetName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == VNetName
| where OperationName contains "VirtualNetwork"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

## Private Link Service Health Checks

### Private Link Service Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let PLSName = PLSName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == PLSName
| where OperationName contains "PrivateLinkService"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

### Private Link Service NIC Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let PLSNICName = PLSNICName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == PLSNICName
| where OperationName contains "NetworkInterface"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

### Private Link Service VNet Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let VNetName = VNetName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == VNetName
| where OperationName contains "VirtualNetwork"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

### Private Link Service Internal Load Balancer Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ILBName = ILBName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == ILBName
| where OperationName contains "LoadBalancer"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

### Private Link Service Backend VM Health Check

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let VMName = VMName;
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == subscriptionid
| where ResourceName == VMName
| where OperationName contains "VirtualMachine"
| project PreciseTimeStamp, Tenant, Success, ResourceType, ResourceName, OperationName, CorrelationRequestId, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

## CRUD Operation Troubleshooting

### Check Azure Policy Blocked Private Endpoint Creation

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
union cluster('armprodsea.southeastasia').database('Requests').EventServiceEntries,
      cluster('armprodeus.eastus').database('Requests').EventServiceEntries,
      cluster('armprodweu.westeurope').database('Requests').EventServiceEntries
| where PreciseTimeStamp between (starttime .. endtime)
| where subscriptionId == subscriptionid
| where operationName contains "privateEndpoints"
| where properties contains "\"resourceLocation\":null"
| distinct PreciseTimeStamp, status, subStatus, operationName, resourceUri, correlationId, properties, claims
| order by PreciseTimeStamp desc
```

## Common Query Patterns

### Dashboard Parameters
- `SubscriptionID` — Azure subscription GUID
- `_startTime` / `_endTime` — Time range (datetime)
- `PEName` — Private Endpoint name
- `PLSName` — Private Link Service name
- `PENICName` / `PLSNICName` — Network Interface name
- `VNetName` — Virtual Network name
- `ILBName` — Internal Load Balancer name
- `VMName` — Virtual Machine name
- `CorrelationId` — ARM correlation request ID

### Resource Type Filters
For QosEtwEvent queries, common OperationName patterns:
- Private Endpoint: `PrivateEndpoint*`
- Private Link Service: `PrivateLinkService*`
- Associated resources: `NetworkInterface`, `VirtualNetwork`, `LoadBalancer`, `VirtualMachine`

### NRP CRUD Operations
For Private Link CRUD troubleshooting, use queries from [nrp-arm-operations.md](nrp-arm-operations.md):
- **ARM HTTPIncomingRequests** — API calls by subscription and resource URI
- **GatewayServiceOperationEtwEvent** — NRP Gateway service operations
- **FrontendOperationEtwEvent** — NRP Frontend operations
- **WriteOperationResponseEtwEvent** / **ReadOperationResponseEtwEvent** — NRP operation responses

These generic NRP queries apply to Private Link resources by filtering on:
- `ResourceURI` containing `/privateEndpoints/` or `/privateLinkServices/`
- `OperationName` containing `PrivateEndpoint` or `PrivateLinkService`
