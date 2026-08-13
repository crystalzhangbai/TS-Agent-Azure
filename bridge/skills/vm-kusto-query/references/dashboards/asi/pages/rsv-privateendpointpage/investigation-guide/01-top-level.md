# (top-level)

> Source: **Recovery Services Vaults - PrivateEndpointPage** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PEDetails

Cluster: `mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Single` · Widget: `Card`

```kusto
RegionalRPResourceAll
| where ResourceId == RSVResourceId
| where TIMESTAMP > StartTime and TIMESTAMP < EndTime
| project TIMESTAMP, PrivateEndpointConnectionsBlobUri, ResourceId
| where isempty(PrivateEndpointConnectionsBlobUri) == false and PrivateEndpointConnectionsBlobUri != "null" and PrivateEndpointConnectionsBlobUri != "[]"
| extend PrivateEndpointConnectionsJson = parse_json(PrivateEndpointConnectionsBlobUri)
| mv-expand PrivateEndpointConnectionsJson 
| parse PrivateEndpointConnectionsJson with *'/privateEndpoints/'PEName'"'*
| project TIMESTAMP, PEName, PrivateEndpointConnectionsJson, ResourceId
| summarize arg_min(TIMESTAMP, *) by PEName, ResourceId
| project TIMESTAMP, PEName , ResourceId, PrivateEndpointConnectionsJson
| extend PEARMDetails = (parse_json(PrivateEndpointConnectionsJson)).properties.privateEndpoint.id
| parse PEARMDetails with "/subscriptions/"PESubscriptionId"/resourceGroups/"PEResourceGroupName"/providers/Microsoft.Network/privateEndpoints/"PEName
```

**Params:** `{RSVDeploymentName}`, `{RSVResourceId}`, `{PENameInput}`, `{StartTime}`, `{EndTime}`

---

### PETimeline

Cluster: `mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Timeline`

```kusto
let PEUpdateDetails = OperationStatsLocalAll
| where OperationName contains "BackupManagementPrivateEndpointNetAdminUpdate"
| where CompanyId == RSVResourceId
| where ServiceName == "BMS"
| where TIMESTAMP > queryFrom and TIMESTAMP < queryTo
| where iff(isempty(RSVDeploymentName), true, DeploymentName == RSVDeploymentName)
| distinct OpTaskId = TaskId, TIMESTAMP;
let PEUpdateOPTaskIds = PEUpdateDetails | distinct  OpTaskId;
let PEUpdateOPStartTime = PEUpdateDetails | summarize min(TIMESTAMP);
let PEUpdateOPEndTime = PEUpdateDetails | summarize max(TIMESTAMP);
let NRPOperations = TraceLogMessageAll
    | where Message startswith "HttpWebHelper: ExecuteRequest"
    | where ServiceName == "BMS"
    | where Message contains "PutPrivateLinkServiceProxy"
    | where Message contains RSVResourceId
    | where TIMESTAMP > toscalar(PEUpdateOPStartTime | take 1) - 1h  and TIMESTAMP < toscalar(PEUpdateOPEndTime | take 1) + 1h
    | project Message, TIMESTAMP, TaskId
    | parse Message with *"/privateLinkServiceProxies/"PEName"."*
    | extend Members = extract_all(@'\"memberName\":\"(.*?)\"', Message)
    |  parse Message with *"NRPRequestId ="NRPRequestId"}"*
    | project PEName, OperationName = "PrivateEndpointRecreateRequest", OperationTime = TIMESTAMP,  Members, AdditionalDetails = pack('NRPRequestId', NRPRequestId), TaskId 
    | where PEName =~ RSVPEName;
let PECreateDetails = OperationStatsLocalAll
| where OperationName contains "BackupManagementPrivateEndpointNetAdminUpdate" or OperationName contains "BackupManagementPrivateEndpointNetAdminCreate"
| where CompanyId == RSVResourceId
| where ServiceName == "BMS"
| where TIMESTAMP > queryFrom and TIMESTAMP < queryTo
| where iff(isempty(RSVDeploymentName), true, DeploymentName == RSVDeploymentName)
| distinct OpTaskId = TaskId, TIMESTAMP, OperationName;
let PECreateOPTaskIdOpMap = PECreateDetails |   extend map = bag_pack(OpTaskId, OperationName) | summarize make_bag(map);
let PECreateOPTaskIds = PECreateDetails |   distinct OpTaskId;
let PECreateOPStartTime = PECreateDetails | summarize min(TIMESTAMP);
let PECreateOPEndTime = PECreateDetails | summarize max(TIMESTAMP);
let RSVOperations = TraceLogMessageAll
| where TaskId in(PECreateOPTaskIds)
| where TIMESTAMP > toscalar(PECreateOPStartTime | take 1) - 1h  and TIMESTAMP < toscalar(PECreateOPEndTime | take 1)
| where ServiceName == "rrp"
| where Message startswith "PutConnectionProxy called"
| parse Message with *"/privateLinkServiceProxies/"PEName"."*
| extend Members =  (extract_all(@'\"memberName\":\"(.*?)\"', Message))
| mv-expand Members
| summarize Members = make_set(Members) by PEName, OperationName = "BackupManagementPrivateEndpointNetAdminCreate" , OperationTime = TIMESTAMP, TaskId
| where PEName =~ RSVPEName;
NRPOperations
| union RSVOperations
| order by OperationTime asc 
| project StartTime = OperationTime, Content  = OperationName, Properties = tostring( pack("PEName", PEName, "OperationName",  OperationName, "TaskId",  TaskId, "Members",  Members, "AdditionalDetails", AdditionalDetails))
```

**Params:** `{queryFrom}`, `{queryTo}`, `{RSVResourceId}`, `{RSVPEName}`, `{RSVDeploymentName}`

**Signal filters seen in KQL:** `OperationName contains "BackupManagementPrivateEndpointNetAdminUpdate"` · `ServiceName == "BMS"` · `Message startswith "HttpWebHelper: ExecuteRequest"` · `Message contains "PutPrivateLinkServiceProxy"` · `ServiceName == "rrp"` · `Message startswith "PutConnectionProxy called"`

---
