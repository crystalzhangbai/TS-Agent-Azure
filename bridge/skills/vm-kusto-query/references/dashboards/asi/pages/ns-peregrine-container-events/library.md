# NodeService — Peregrine_ContainerEvents: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:12:40.037Z.
> Total: 23 unique KQL queries across 7 panels (23 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 17

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Peregrine_ContainerEvents" | ResourceGet | azcore.centralus | AzureCP | local_containerId, globalFrom, globalTo |
| 2 | WillBePublishesToMadariFromAzCiM | Timeline | https://azcim-centralus.centralus | AZCIM | queryFrom, queryTo, containerId |
| 3 | NS Madari WillBe/Was Interactions | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId |
| 4 | NodeService Completed Operations | Timeline | azcore.centralus | Fa | queryFrom, queryTo, nodeId, containerId |
| 5 | NodeService Started Operations | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |
| 6 | ContainerTimeline | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |
| 7 | Fault Events | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |
| 8 | IsTip | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, nodeId |
| 9 | Was/WillBe publishes (Madari POV) | Timeline | aznwsdn | sdnpubsub | queryFrom, queryTo, containerId, nodeId |
| 10 | AzPubSub Publishing | Timeline | azcore.centralus | Fa | queryFrom, queryTo, vmId, nodeId |
| 11 | ContainerWorkflowBlocked | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |
| 12 | Madari Operation Failures | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId, vmUniqueId, azLogicalContainerId |
| 13 | NodeService Exits | Timeline | azcore.centralus | Fa | faultTime, nodeId |
| 14 | ApSvcMgr State | Timeline | https://hawkeyekustocluster.centralus | AzureDCMdb | queryNode, queryFrom, queryTo |
| 15 | LogNodeSnapshot - NodeState | Timeline | https://hawkeyekustocluster.centralus | AzureCM | queryNode, queryFrom, queryTo |
| 16 | Fault Information | Table | aplat.westcentralus | APlat | queryFrom, queryTo, containerId |
| 17 | EG links | Table | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |

### AgentNfcHttpDownloadFileEtwTable
Path: `AgentNfcHttpDownloadFileEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AgentNfcHttpDownloadFileEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId |

### AzCiMadariOperationEvent
Path: `AzCiMadariOperationEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzCiMMadariOperationEvent | Table | hawkeyekustocluster.centralus | AzureCM | queryFrom, queryTo, containerId |

### AzCiMContainerWas
Path: `AzCiMContainerWas`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzCiMContainerWas | Table | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |

### AzCiMContainerWillBe
Path: `AzCiMContainerWillBe`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzCiMContainerWillBe | Table | hawkeyekustocluster.centralus | AzureCM | queryFrom, queryTo, containerId |

### NodeServiceEvents
Path: `NodeServiceEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeServiceEventsEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId |

### NodeServiceMadariEvents
Path: `NodeServiceMadariEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeServiceMadariEventsEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId, vmUniqueId, azLogicalContainerId |
