# NodeService — NodeService_NodeView: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:12:40.037Z.
> Total: 40 unique KQL queries across 8 panels (40 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 33

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "NodeService_NodeView" | ResourceGet | azcore.centralus | AzureCP | local_NodeId |
| 2 | Networking dashboard query | Single | ? | ? | queryNode, queryTime |
| 3 | NodeServiceVersion | Single | azcore.centralus | Fa | nodeId, faultTime |
| 4 | SDP Phase | Single | aplat.westcentralus | APlat | faultTime, cluster |
| 5 | SocId | Single | azurecm | AzureCM | _nodeId |
| 6 | ApSvcMgr State | Timeline | https://hawkeyekustocluster.centralus | AzureDCMdb | queryNode, faultTime |
| 7 | LogNodeSnapshot - NodeState | Timeline | https://hawkeyekustocluster.centralus | AzureCM | queryNode, faultTime |
| 8 | Madari errors | Timeline | azcore.centralus | Fa | queryNode, faultTime |
| 9 | Anvil Repair Diagnostics | Timeline | aplat.westcentralus | APlat | queryNode, faultTime |
| 10 | NodeService Exits | Timeline | azcore.centralus | Fa | faultTime, nodeId |
| 11 | Fabric incarnations | Timeline | mycroft.westcentralus | Mycroft | faultTime, fabricCluster |
| 12 | SEL Events | Timeline | sparkle.eastus | defaultdb | _faultTime, _nodeId |
| 13 | TOR Send Packet Health | Timeline | aznwsdn | aznwmds | _nodeId, _faultTime |
| 14 | TOR Recv Packet Health | Timeline | aznwsdn | aznwmds | _nodeId, _faultTime |
| 15 | TOR InMaintenance | Timeline | aznwsdn | aznwmds | _nodeId, _faultTime |
| 16 | CM WillBe Generation | Timeline | hawkeyekustocluster.centralus | AzureCM | _nodeId, _faultTime |
| 17 | TOR in Quarantine Network | Timeline | azphynet | azdhmds | hostName, faultTime |
| 18 | Soc Health | Timeline | aplat.westcentralus | APlat | faultTime, queryNode |
| 19 | SeedIncarnation query | Timeline | aznwsdn | sdnpubsub | nodeId, faultTime |
| 20 | SocHB | Timeline | azdeployer | AzDeployerKusto | _nodeId, _faultTime |
| 21 | WindowsEvents | Timeline | azcore.centralus | Fa | queryNode, faultTime |
| 22 | ContainerState and ASILink | Timeline | https://mycroft.westcentralus | Mycroft | faultTime, queryNode |
| 23 | Events Count | TimeSeries | https://azcore.centralus | Fa | queryNode, faultTime |
| 24 | Overlake Healthstore Data | TimeSeries | https://azcore.centralus | OvlProd | faultTime, nodeId |
| 25 | Cluster level node unhealthy metrics | TimeSeries | hawkeyekustocluster.centralus | AzureCM | faultTime, cluster |
| 26 | Node Snapshot | Table | aplat.westcentralus | APlat | nodeId, faultTime |
| 27 | CMWorkerNodeServiceWas | Table | https://hawkeyekustocluster.centralus | AzureCM | queryNode, faultTime |
| 28 | CMWorkerNodeServiceWillBe | Table | https://hawkeyekustocluster.centralus | AzureCM | queryNode, faultTime |
| 29 | CMWorkerNodeEvents | Table | https://hawkeyekustocluster.centralus | AzureCM | queryNode, faultTime |
| 30 | MemoryReport | Table | https://azcore.centralus | KernelAgent | queryNode, faultTime |
| 31 | CPU_Usage | Table | https://azcore.centralus | Fa | queryNode, faultTime |
| 32 | CPU Graph | TimeSeries | https://azcore.centralus | Fa | queryNode, faultTime |
| 33 | ProcessMemUsage | TimeSeries | https://azcore.centralus | AutopilotDeployment | queryNode, faultTime |

### CMWorkerNodeServiceChannel failures
Path: `CMWorkerNodeServiceChannel failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CMWorkerNodeServiceChannel failures | Table | https://hawkeyekustocluster.centralus | AzureCM | queryNode, faultTime |

### NodeService Events
Path: `NodeService Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeService Events | Table | https://azcore.centralus | Fa | queryNode, faultTime |

### NodeService Exits
Path: `NodeService Exits`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeService Exits | Table | https://azcore.centralus | Fa | queryNode, faultTime |

### NodeService SoC Logs
Path: `NodeService SoC Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Echo | Single | ? | ? | _nodeId, _timeOfFault |

### NodeService Watchdog events
Path: `NodeService Watchdog events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeServiceWatchdogEtwTable | Table | https://azcore.centralus | Fa | queryNode, faultTime |

### TMMgmtNodeEvents
Path: `TMMgmtNodeEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtNodeEventsTable | Table | https://hawkeyekustocluster.centralus | AzureCM | queryNode, faultTime |

### WindowsEvents
Path: `WindowsEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WindowsEventsTable | Table | https://azcore.centralus | Fa | queryNode, faultTime |
