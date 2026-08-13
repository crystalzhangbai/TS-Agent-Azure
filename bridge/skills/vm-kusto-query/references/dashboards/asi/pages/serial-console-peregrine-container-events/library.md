# Azure Serial Console — Peregrine_ContainerEvents: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:59:23.140Z.
> Total: 21 unique KQL queries across 7 panels (21 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 15

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Peregrine_ContainerEvents" | ResourceGet | hawkeyekustocluster.centralus | AzureCM | local_containerId |
| 2 | WillBePublishesToMadariFromAzCiM | Timeline | vmadiag | AzureCM | queryFrom, queryTo, containerId |
| 3 | NS Madari WillBe/Was Interactions | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId |
| 4 | NodeService Completed Operations | Timeline | azcore.centralus | Fa | queryFrom, queryTo, nodeId, containerId |
| 5 | NodeService Started Operations | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |
| 6 | ContainerTimeline | Timeline | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |
| 7 | Fault Events | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |
| 8 | IsTip | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, nodeId |
| 9 | Was/WillBe publishes (Madari POV) | Timeline | aznwsdn | sdnpubsub | queryFrom, queryTo, containerId, nodeId |
| 10 | AzPubSub Publishing | Timeline | azcore.centralus | Fa | queryFrom, queryTo, vmId, nodeId |
| 11 | lxprov | Timeline | azcore.centralus | Fa | queryFrom, queryTo, _container_id |
| 12 | ApSvcMgr State | Timeline | https://hawkeyekustocluster.centralus | AzureDCMdb | queryNode, queryFrom, queryTo |
| 13 | LogNodeSnapshot - NodeState | Timeline | https://hawkeyekustocluster.centralus | AzureCM | queryNode, queryFrom, queryTo |
| 14 | Fault Information | Table | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |
| 15 | EG links | Table | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |

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
| 1 | AzCiMContainerWas | Table | hawkeyekustocluster.centralus | AzureCM | queryFrom, queryTo, containerId |

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
| 1 | NodeServiceMadariEventsEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId |
