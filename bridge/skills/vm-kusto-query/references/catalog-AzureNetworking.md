# Kusto Catalog — AzureNetworking Wiki

Source: AzureNetworking wiki (Azure DevOps content reachable through the `csswiki` MCP; `/Tooling/Kusto/Kusto Clusters and Requirements`, `/Tooling/Kusto/Kusto Examples`, `/Tooling/Kusto/How to Determine Kusto Table Latency`, plus per-service log-source pages)
Last synced: 2025-08-02

> Use `scripts/kusto_catalog_builder.py --wiki-project AzureNetworking` to refresh this file from the Azure DevOps wiki; use `csswiki` for interactive wiki search/page reads.

---

## Natural Language Semantic Glossary (for Agent Routing)

| User natural language cues | Cluster.DB | Typical interpretation |
|----------------------------|------------|------------------------|
| ARM操作失败、资源创建失败、CRUD失败、PUT/DELETE报错 | `Armprodgbl.eastus → ARMProd` | Control plane: HttpIncomingRequests, EventServiceEntries |
| NRP错误、网络资源操作失败、VNet/NSG/PIP/UDR操作 | `Nrp.mdsnrp` | QosEtwEvent (mirrors ASC Operations), FrontendOperationEtwEvent |
| VPN断连、隧道断开、IKE协商失败、隧道抖动 | `Hybridnetworking.aznwmds` | TunnelEventsTable |
| VPN Gateway事件、GatewayId相关事件 | `Hybridnetworking.aznwmds` | GatewayTenantEventsTable |
| ExpressRoute电路、ExR连接、BGP对等、授权密钥 | `Hybridnetworking.aznwmds` | CircuitTable, GatewayManagerLogsTable, GatewayTenantLogsTable |
| ExR陈旧连接、ExR关联的VNet | `Hybridnetworking.aznwmds` | VnetConfigTable |
| ExR监控告警 | `Hybridnetworking.aznwmds` | ExpressRouteMonitoringLogsTable |
| Application Gateway操作变更、AppGW配置差异、AppGW故障状态 | `Hybridnetworking.aznwmds` | AppGwOperationHistoryLogsTable, AsyncWorkerLogsTable |
| Application Gateway AGIC、AKS Ingress Controller | `Aznw.aznwcosmos` | ApplicationGatewaysExtendedLatest |
| vWAN、Virtual Hub、vHub路由、Hub信息 | `Hybridnetworking.aznwmds` | VirtualHubTable, VirtualWanTable |
| vWAN Route Service、BGP路由传播、路由通告 | `Hybridnetworking.aznwmds` | RouteServiceTable, RouteServiceBgpLogsTable, RouteServiceRoutingLog |
| vWAN VPN Gateway子网关 | `Hybridnetworking.aznwmds` | VpnGatewayTable, VpnGatewayChildGatewayTable |
| vWAN ExR Gateway | `Hybridnetworking.aznwmds` | ExpressRouteGateway |
| 负载均衡器操作、SLB、ILB | `Azslb.azslbmds` | BasicILB (及其他) |
| DDoS攻击、流量丢弃、DDoS PCAP | `Aznwddos.centralus.cnsgeneva` | DDoSPcapFlowLogs |
| Private Link、Private Endpoint CRUD失败 | `Nrp.mdsnrp` | QosEtwEvent |
| AFD、Azure Front Door、CDN操作 | `Azurecdn.azurecdnmds` | AfdCustomDomainSnapshot, ApiAnalytics, OperationSnapshot |
| DNS流量管理、Traffic Manager | `Aztmmon` | (DNS monitoring tables) |
| DNS Private Resolver、Managed Resolver | `Managedresolver.westus2` | (Private DNS Resolver tables) |
| 自动扩缩容、Insights监控、Autoscale | `Azureinsights.Insights` | TelemetryV2 |
| VNet加密、Sirius、SmartNIC、服务节点 | `Sirius.eastus.siriusLogs` | SiriusServicingInfoTable, SiriusCriticalFailureTable |
| 计算资源、CRP、VM API | `Azcrp.crp_allprod` | ApiQosEvent, VMApiQosEvent |
| vWAN资源图谱、网络拓扑 | `Argwus2nrpone.westus2.AzureResourceGraph` | Resources |
| **网络资源拓扑、VNet/NIC/PE/PIP/LB/FrontDoor/ER 查属性与关联** | `eearg.westus2.AzureResourceGraph` | Resources（schema 已展开，原生 `resourceGuid` join）— 首选 `eagleai.execute_kusto_query` |
| **跨 region ARM 调用追踪**（资源从哪个 region 发起 CRUD） | `cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests` + `cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests` + `cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests` | ARM HttpIncomingRequests — use `kusto` / `azuremcp`; use `eagleai.execute_kusto_query` only for one-cluster raw KQL |
| **网络端到端拓扑 / 连通性诊断 / NSG 分析 / PCAP 关联** | EagleAI 高层语义入口 | `eagleai.DiscoverTopology(user_query=...)` |

### Interpretation Priority

1. 对于大多数网络CRUD问题：先查 `Nrp.mdsnrp.QosEtwEvent`（最接近ASC Operations视图），再用 `correlationId` 深入 `FrontendOperationEtwEvent`，最后追溯到 `Armprodgbl/ARM` 层。
2. VPN/ExR/AppGW 问题均在 `Hybridnetworking.aznwmds` 内，通过 `GatewayId` 或 `ServiceKey` 定位。
3. Fairfax (Government) 等效集群：`Aznwff.kusto.usgovcloudapi.net`（database: `aznwmds`）覆盖 NRP、VPN、ExR、AppGW 所有表；`Armff.kusto.usgovcloudapi.net`（database: `armff`）覆盖 ARM。

---

## ARM (Azure Resource Manager) → ARMProd / Requests

**URI (Global)**: `https://Armprodgbl.eastus.kusto.windows.net` → database: `ARMProd` (use `Unionizer` function to fan out)  
**URI (Regional)**:
- East US: `https://Armprodeus.eastus.kusto.windows.net` → database: `Requests`
- West Europe: `https://Armprodweu.westeurope.kusto.windows.net` → database: `Requests`
- Southeast Asia: `https://Armprodsea.southeastasia.kusto.windows.net` → database: `Requests`

**Access**: CoreIdentity SG `WA CTS-14817` (FTE) or `ARM Logs` (non-FTE)  
**Retention**: 45 days. **Latency**: ~5–7 min.  
**Purpose**: Azure Resource Manager control plane — all CRUD API requests, audit events, outgoing calls for any ARM-managed resource.  
**Tip**: Use the global `Armprodgbl` cluster with the fully-qualified `Unionizer` call below to discover which regional cluster holds the data, then re-query regionally for full detail.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `HttpIncomingRequests` | Incoming ARM API requests (all CRUD) | TIMESTAMP, subscriptionId, operationName, httpMethod, httpStatusCode, targetUri, correlationId, userAgent, durationInMilliseconds |
| `EventServiceEntries` | ARM audit log / event service entries | TIMESTAMP, subscriptionId, operationName, resourceUri, status, correlationId, claims |
| `HttpOutgoingRequests` | Outgoing ARM requests to downstream RP | TIMESTAMP, subscriptionId, operationName, httpStatusCode, correlationId, errorCode |

### Key KQL: ARM CRUD Lookup (Two-step: global → regional)

```kusto
// Step 1 — Find which regional cluster via global Unionizer
cluster('Armprodgbl.eastus').database('ARMProd').Unionizer('Requests', 'HttpIncomingRequests')
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where subscriptionId == '{SubscriptionId}'
| where httpMethod != "GET"
| project TIMESTAMP, TaskName, operationName, httpMethod, httpStatusCode,
    targetUri, correlationId, $cluster
| order by TIMESTAMP asc

// Step 2 — Query regional cluster directly (replace with $cluster value from above)
cluster('Armprodeus.eastus').database('Requests').HttpIncomingRequests
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where subscriptionId == '{SubscriptionId}'
| where httpMethod != "GET"
| project TIMESTAMP, operationName, httpMethod, httpStatusCode, correlationId,
    targetUri, durationInMilliseconds
```

### Key KQL: ARM regional union (all-in-one)

```kusto
// Fully-qualified regional ARM union. Add/remove regional clusters based on the global Unionizer result.
cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests
| union cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests,
        cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests
| where PreciseTimeStamp >= datetime({Start})
| where subscriptionId == '{SubscriptionId}'
| where httpMethod != "GET"
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, TaskName, correlationId, operationName, httpMethod,
    httpStatusCode, targetResourceType, targetUri, userAgent, durationInMilliseconds
```

**Fairfax**: `https://Armff.kusto.usgovcloudapi.net` → database: `armff`

---

## NRP (Network Resource Provider) → mdsnrp

**URI**: `https://Nrp.kusto.windows.net` → database: `mdsnrp`  
**Access**: Included in `WA CTS-14817`  
**Retention**: ~185 days. **Latency**: ~1–3 min.  
**Purpose**: Network Resource Provider internal operations — most detailed view of NRP-layer success/failure, error codes, and operation traces for all networking resources (VNet, NSG, PIP, LB, NIC, Private Endpoint, AppGW, etc.).

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `QosEtwEvent` | NRP operation QoS — mirrors ASC Operations view; success/fail, error codes per request | TIMESTAMP, SubscriptionId, OperationName, HttpMethod, Success, StatusCode, ErrorCode, InternalErrorCode, ResourceName, Region, DurationInMilliseconds, CorrelationRequestId, ClientOperationId, UserError, AsynchronousDurationInMilliseconds |
| `FrontendOperationEtwEvent` | Detailed NRP frontend operation trace; use for root cause deep-dive after locating correlationId in QosEtwEvent | TIMESTAMP, SubscriptionId, Region, HttpMethod, OperationId, CorrelationRequestId, Message, EventCode, ResourceGroup, ResourceType, ResourceName, ClientOperationId, Sequence |

### Key KQL: NRP Failure Investigation

```kusto
// QoS view — failure summary (mirrors ASC Operations tab)
cluster('Nrp').database('mdsnrp').QosEtwEvent
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where SubscriptionId == "{SubscriptionId}"
| where Success == false
| project TIMESTAMP, HttpMethod, OperationName, Success, StatusCode, UserError,
    ResourceName, InternalErrorCode, ErrorCode, ErrorDetails,
    DurationInMilliseconds, Region, CorrelationRequestId, OperationId
| order by TIMESTAMP asc
```

```kusto
// Non-GET operations for a resource by name
cluster('Nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (datetime({Start}) .. datetime({End}))
| where SubscriptionId == "{SubscriptionId}"
| where ResourceName == "{ResourceName}"
| where HttpMethod != "GET"
| project PreciseTimeStamp, OperationName, UserError, Success, ErrorDetails,
    OperationId, CorrelationRequestId, StartTime, AsynchronousDurationInMilliseconds
```

```kusto
// Detailed trace using correlationId from ARM or ASC
cluster('nrp.kusto.windows.net').database('mdsnrp').FrontendOperationEtwEvent
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where Region == "{Region}"
| where SubscriptionId == "{SubscriptionId}"
| where CorrelationRequestId == "{CorrelationId}"
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, CorrelationRequestId, EventCode, Message, Sequence
```

**Fairfax**: `https://Aznwff.kusto.usgovcloudapi.net` → database: `aznwmds` (QosEtwEvent + FrontendOperationEtwEvent)

---

## Hybridnetworking → aznwmds (VPN / ExpressRoute / AppGW / vWAN / Gateway Manager)

**URI**: `https://Hybridnetworking.kusto.windows.net` → database: `aznwmds`  
**Access**: Included in `WA CTS-14817`  
**Retention**: ~90 days (most tables). **Latency**: 4–20 min depending on table.  
**Purpose**: Gateway Manager, VPN Gateway, ExpressRoute, Application Gateway, vWAN (Virtual Hub, Route Service), BGP routing — operations and configuration history.

### VPN / Gateway Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `TunnelEventsTable` | VPN tunnel state changes: connect/disconnect, planned failover, DPD timeout, host maintenance | TIMESTAMP, GatewayId, RoleInstance, Message, DownTimeInMilliSeconds, IsPlannedFailover, TunnelName, TunnelStateChangeReason, NegotiatedSAs |
| `GatewayTenantEventsTable` | Generic gateway tenant events | TIMESTAMP, GatewayId, RoleInstance, Message |
| `GatewayTenantLogsTable` | BGP route ingress/egress logs for VPN/ExR child gateways | TIMESTAMP, GatewayId, Message (contains route CIDR) |
| `GatewayManagerLogsTable` | Gateway Manager internal logs; used to look up ExR authorization key and correlate NRP OperationId | TIMESTAMP, NrpUri, Message, ActivityId, CustomerSubscriptionId, ServicePrefix |

**TunnelStateChangeReason decode**:
| Value | Meaning |
|-------|---------|
| `GlobalStandby` | Planned failover / active-passive switch |
| `RemotelyTriggered` | Customer side (on-prem) triggered reset |
| `DPD timed out` | Dead Peer Detection failure — actual connectivity loss |
| `Standby changed` | Host maintenance (active-active gateway) |

### Key KQL: VPN Tunnel Disconnect Investigation

```kusto
cluster("hybridnetworking").database("aznwmds").TunnelEventsTable
| where GatewayId == "{GatewayId}"
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| project TIMESTAMP, RoleInstance, Message, DownTimeInMilliSeconds,
    IsPlannedFailover, TunnelName, TunnelStateChangeReason, NegotiatedSAs
```

```kusto
// GatewayManagerLogs — trace NRP OperationId through Gateway Manager
cluster('HybridNetworking').database('aznwmds').GatewayManagerLogsTable
| where * contains "{OperationIdFromNRP}"
| where PreciseTimeStamp >= datetime("{Start}") and PreciseTimeStamp <= datetime("{End}")
| project PreciseTimeStamp, Message, ActivityId, CustomerSubscriptionId
```

### ExpressRoute Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `CircuitTable` | ExR circuit details, service provider, port info | TIMESTAMP, AzureServiceKey, AzureSubscriptionId, Location, ServiceProviderName, PortPairId |
| `VnetConfigTable` | VNet config linked to ExR circuit — used to find stale connections or identify GatewayId | TIMESTAMP, ServiceKey, VNetId, VNetName, GatewayId |
| `ExpressRouteMonitoringLogsTable` | ExR monitoring events | TIMESTAMP, PreciseTimeStamp |
| `ExpressRouteGateway` | ExR Gateway in vWAN hub (ExR GW ARM ID, child gateway ID) | TIMESTAMP, ExpressRouteGatewayArmId, ExpressRouteGatewayName, ExRGWID |

### Key KQL: ExpressRoute Stale Connection Lookup

```kusto
cluster('hybridnetworking').database('aznwmds').VnetConfigTable
| where ServiceKey == "{ExRServiceKey}"
| where PreciseTimeStamp >= datetime("{Start}") and PreciseTimeStamp <= datetime("{End}")
| project VNetId, VNetName, GatewayId
```

```kusto
// ExR authorization key lookup via GatewayManagerLogsTable
cluster('HybridNetworking').database('aznwmds').GatewayManagerLogsTable
| where Message contains "{AuthorizationKey}"
| where PreciseTimeStamp >= datetime("{Start}") and PreciseTimeStamp <= datetime("{End}")
| project PreciseTimeStamp, Message, ActivityId, CustomerSubscriptionId
```

### Application Gateway Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `AppGwOperationHistoryLogsTable` | AppGW configuration change history — shows exactly what was added/removed (diff format) per operation; covers v1/v2/WAF. Latency ~4 min | PreciseTimeStamp, GatewayId, GatewayName, OperationType, OperationName, ActivityId, OperationId, CorrelationRequestId, ConfigDiff, ResourceDiff, NewConfig, OldConfig, Status, DurationInSecond, SequenceNumber, IsNewGateway, UpdateOperationType, FastUpdateResult |
| `AsyncWorkerLogsTable` | AppGW async worker logs — internal processing details for AppGW operations | TIMESTAMP, OperationId, OperationName, Message, CustomerSubscriptionId |

### Key KQL: Application Gateway Config Change Diff

```kusto
// What changed on an AppGW? (ConfigDiff shows +/- for added/removed config)
cluster("Hybridnetworking").database("aznwmds").AppGwOperationHistoryLogsTable
| where PreciseTimeStamp > ago(1d)
| where GatewayId =~ "{GatewayId}"
| where isnotempty(ConfigDiff)
| extend OrderNr = toint(substring(SequenceNumber, 0, indexof(SequenceNumber, "/")))
| order by StartTimeUtc asc, OrderNr asc
| project StartTimeUtc, OrderNr, ConfigDiff, CorrelationRequestId, ActivityId,
    NewConfig, OldConfig, Status
```

```kusto
// Track when a specific listener/rule was added or deleted (large time window)
let AutoscaleInstanceRefreshOp = toscalar(
    cluster("Hybridnetworking").database("aznwmds").AsyncWorkerLogsTable
    | where PreciseTimeStamp between (datetime({Start}) .. datetime({End}))
    | where OperationName == "PutVMSSApplicationGatewayWorkItem"
    | where Message contains "Updating Instance List"
    | where Message contains "{ListenerName}"
    | project "AutoscaleRefreshInstanceDetails"
);
cluster("Hybridnetworking").database("aznwmds").AppGwOperationHistoryLogsTable
| where PreciseTimeStamp between (datetime({Start}) .. datetime({End}))
| where GatewayName == "{GatewayName}"
| where OperationName == "PutVMSSApplicationGatewayWorkItem"
| where ResourceDiff contains "{ListenerName}"
| summarize ConfigDiff=make_list(ConfigDiff), ResourceDiff=make_list(ResourceDiff)
    by StartTimeUtc, Tenant, OperationType, OperationName, ActivityId, OperationId,
    Status, DurationInSecond, IsNewGateway, GatewayName, UpdateOperationType,
    FastUpdateResult, FastUpdateDurationInSecond
| project StartTimeUtc, OperationName,
    UpdateOperationType=coalesce(AutoscaleInstanceRefreshOp, UpdateOperationType),
    GatewayName, Status, DurationInSecond, ResourceDiff=strcat_array(ResourceDiff, ""),
    ConfigDiff=strcat_array(ConfigDiff, "")
```

```kusto
// AsyncWorkerLogs — trace by NRP OperationId
cluster('HybridNetworking').database('aznwmds').AsyncWorkerLogsTable
| where OperationId == "{OperationIdFromNRP}"
| where PreciseTimeStamp >= datetime("{Start}") and PreciseTimeStamp <= datetime("{End}")
| project PreciseTimeStamp, Message, OperationId, OperationName, CustomerSubscriptionId
```

### vWAN Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `VirtualHubTable` | vWAN Virtual Hub info — address space, routing preference, ARM ID | TIMESTAMP, CustomerSubscriptionId, HubName, VnetName, AddressSpace, HubRoutingPreference, ArmId, ArmGuid, VpnGatewayArmId, ExpressRouteGatewayArmId |
| `VirtualWanTable` | vWAN instance info | TIMESTAMP, CustomerSubscriptionId, ArmGuid |
| `VirtualHubVnetConnectionTable` | Spoke VNet connections to vHub | TIMESTAMP, HubArmGuid, ConnectedVnetArmId |
| `VpnGatewayTable` | VPN Gateway within vHub | TIMESTAMP, VpnGatewayArmId, Name |
| `VpnGatewayChildGatewayTable` | Maps ARM VPN GW → child GatewayId (needed to query TunnelEventsTable) | TIMESTAMP, VpnGatewayArmId, GatewayId |
| `RouteServiceTable` | vWAN Route Service configuration: ASN, BGP communities, VIPs | TIMESTAMP, RouteServiceId, EnabledFeatures, ASN, BgpCommunities, NMAgentVIP, RouteServiceVIPs, HubArmId |
| `RouteServiceLogsTable` | Route Service change-history log | TIMESTAMP, RouteServiceId, RoleInstance, Message |
| `RouteServiceBgpLogsTable` | BGP protocol log for Route Service (route advertisements/withdrawals) | TIMESTAMP, DeploymentId, VirtualNetworkId, Message |
| `RouteServiceRoutingLog` | Route updates processed by Route Service | TIMESTAMP, RouteServiceId, RoleInstance, Message |
| `RouteServicePeerConfigTable` | BGP peer configuration for Route Service | TIMESTAMP, RouteServiceId, PeerIp, PeerAsn, PeerType, PeerVipAddress, PeerWeight |

### Key KQL: vWAN Hub Lookup

```kusto
cluster("Hybridnetworking.kusto.windows.net").database("aznwmds").VirtualHubTable
| where CustomerSubscriptionId == "{SubscriptionId}"
| where TIMESTAMP >= ago(15d)
| project TIMESTAMP, CustomerSubscriptionId, HubName, AddressSpace, HubRoutingPreference,
    ArmId, ArmGuid, VpnGatewayArmId, ExpressRouteGatewayArmId
```

```kusto
// Resolve ARM VpnGateway → GatewayId (needed for TunnelEventsTable)
cluster("Hybridnetworking.kusto.windows.net").database("aznwmds").VpnGatewayChildGatewayTable
| where VpnGatewayArmId contains "{VpnGatewayArmId}"
| project TIMESTAMP, VpnGatewayArmId, GatewayId
```

### Key KQL: vWAN BGP Route Tracing

```kusto
// Track route advertisement using Route Service BGP log
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceBgpLogsTable
| where DeploymentId contains "armrg-{RouteServiceId}"
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where Message contains "{RouteCIDR}"
| where Message contains "Processing ingress route"
| parse Message with * 'Processing ingress route ' routeSource:string ':' * ') ' route:string ' ' *

// Route Service change history
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceLogsTable
| where RouteServiceId == "{RouteServiceId}"
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| project TIMESTAMP, RoleInstance, Message
```

**Fairfax equivalent**: `https://Aznwff.kusto.usgovcloudapi.net` → database: `aznwmds` (all tables above)

---

## Aznw → aznwcosmos (Application Gateway AGIC / AKS Ingress)

**URI**: `https://Aznw.kusto.windows.net` → database: `aznwcosmos`  
**Access**: `WA CTS-14817`  
**Purpose**: Application Gateway Ingress Controller (AGIC) metadata — lists AppGWs managed by Kubernetes ingress within a subscription.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `ApplicationGatewaysExtendedLatest` | Snapshot of all AppGWs in a subscription; filtered by `UserTags` to find AGIC-managed gateways | CustomerSubscriptionId, CloudCustomerName, TenantCountryCode, GatewayName, InstanceCount, GroupName, UserTags, Config |

### Key KQL: List AppGWs Controlled by AGIC

```kusto
cluster('Aznw').database('aznwcosmos').ApplicationGatewaysExtendedLatest
| where UserTags contains "managed-by-k8s-ingress"
| where CustomerSubscriptionId == "{SubscriptionId}"
| project CustomerSubscriptionId, CloudCustomerName, TenantCountryCode,
    GatewayName, UserTags
| order by CloudCustomerName asc
```

```kusto
// Count AGIC-managed AppGWs and associated AKS clusters
cluster('Aznw').database('aznwcosmos').ApplicationGatewaysExtendedLatest
| where UserTags contains "managed-by-k8s-ingress"
    or Config contains "k8s-fp"
    or Config contains "k8s-ag-ingress-fp"
| where CustomerSubscriptionId == "{SubscriptionId}"
| summarize sum(InstanceCount), count(), make_list(GatewayName),
    make_list(GroupName), make_list(UserTags)
```

---

## Azslb → azslbmds (Software Load Balancer)

**URI**: `https://Azslb.kusto.windows.net` → database: `azslbmds`  
**Access**: `WA CTS-14817`  
**Purpose**: Azure Software Load Balancer (Standard LB, Basic ILB) operations and health.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `BasicILB` | Basic Internal Load Balancer operations | (use `.getschema BasicILB` to enumerate) |

> Run `cluster('Azslb').database('azslbmds') | .show tables` to discover all available tables.

**Fairfax**: `https://Azslbff.kusto.usgovcloudapi.net`

---

## Azurecdn → azurecdnmds (Azure Front Door / CDN)

**URI**: `https://Azurecdn.kusto.windows.net` → database: `azurecdnmds`  
**Access**: `WA CTS-14817`  
**Retention**: ~90 days. **Latency**: ~1–6 min.  
**Purpose**: Azure Front Door (AFD) and CDN — domain snapshots, API analytics, operation history.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `AfdCustomDomainSnapshot` | AFD custom domain configuration snapshot | (domain, origin, status) |
| `ApiAnalytics` | API-level analytics for AFD/CDN requests | (endpoint, statusCode, requestCount) |
| `OperationSnapshot` | AFD/CDN operation history | (operationName, status, timestamp) |

> Afdmoi cluster (TA/EEE/PG restricted) contains additional AFD internal data.

---

## Azureinsights → Insights (Monitoring / Autoscale)

**URI**: `https://Azureinsights.kusto.windows.net` → database: `Insights`  
**Access**: IDWeb `Insight Kusto Users`  
**Retention**: ~30 days. **Latency**: ~8 min.  
**Purpose**: Azure Monitor / Autoscale telemetry — used for diagnosing monitor alerts, autoscale scale-in/out events.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `TelemetryV2` | Monitor/Autoscale telemetry events | (subscriptionId, resourceId, operationName, statusCode) |

---

## Aznwddos.centralus → cnsgeneva (DDoS Protection)

**URI**: `https://Aznwddos.centralus.kusto.windows.net` → database: `cnsgeneva`  
**Access**: IDWeb `Ddos Kusto access for Partners` (FTE only)  
**Purpose**: DDoS Protection PCAP flow logs — packet-level evidence of attack traffic and mitigation.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `DDoSPcapFlowLogs` | DDoS mitigation packet flow log — source/dest IP/port, protocol, mitigation action | TIMESTAMP, destPublicIpAddress, srcIpAddress, destPort, srcPort, protocolNumber, action |

### Key KQL: DDoS Flow Log Investigation

```kusto
cluster('aznwddos.centralus.kusto.windows.net').database('cnsgeneva').DDoSPcapFlowLogs
| where TIMESTAMP > ago(60d)
| where destPublicIpAddress in ("{PublicIP}")
| where protocolNumber == 17  // 17=UDP, 6=TCP, 1=ICMP
| project TIMESTAMP, destPublicIpAddress, srcIpAddress, destPort, srcPort, action
```

---

## Aztmmon (DNS Traffic Manager Monitoring)

**URI**: `https://Aztmmon.kusto.windows.net`  
**Access**: `WA CTS-14817`  
**Purpose**: Azure DNS and Traffic Manager monitoring logs.

> Table names not fully enumerated in wiki. Run `.show tables` to discover available tables.

---

## Managedresolver.westus2 (DNS Private Resolver)

**URI**: `https://Managedresolver.westus2.kusto.windows.net`  
**Access**: `WA CTS-14817`  
**Purpose**: Azure DNS Private Resolver / Managed Resolver logs.

> Table names not fully enumerated in wiki. Run `.show tables` to discover available tables.

---

## azslb → azslbmds (Software Load Balancer / VIP Health / Outbound Probes)

**URI**: `https://azslb.kusto.windows.net` → database: `azslbmds`  
**Access**: `WA CTS-14817`  
**Purpose**: SLB MUX 健康状态、VIP 探测、出站探测结果、Host Agent 操作（升级/排空/重启）。

> ⚠️ **URI 陷阱**：不可使用 `Azslb.azslbmds.windows.net`——该格式会导致 auth metadata 连接失败。正确格式：`cluster('azslb.kusto.windows.net').database('azslbmds')`

| Table | Purpose | Key Columns (verified by getschema) |
|-------|---------|--------------------------------------|
| `VipHealthProbe` | SQL/SLB VIP 健康探测结果 | `env_time` (**⚠️ 非 `PreciseTimeStamp`**), `VipAddress`, `VipPort`, `Success`, `WasHealthy`, `Reason` |
| `OutboundProbeResultHistoryEvent` | 节点出站探测结果（UP/DOWN） | `PreciseTimeStamp`, `NodeId`, `ProbeResult`（值为 `"UP"`/`"DOWN"` 大写）, `FinalProbeResult`, `FinalProbeResultReason`, `Vip` |
| `HostActionHistoryEvent` | MUX/Host 操作（升级/排空/重启） | `PreciseTimeStamp`, `NodeId`, `PFMachineName`, `Action`, `IsSucceeded`, `ErrorMessage` |
| `HealthSignalStateHistoryEvent` | SLB Health Signal 状态历史 | `PreciseTimeStamp`, `HealthSignalName`, `CurrentHealthyState`, `LastHealthyState`, `CurrentDetailedReason`, `NodeId`, `PFMachineName` |
| `SlbManagerEvent` | SLB Manager 关键事件 | `PreciseTimeStamp`, `NodeId`, `EventType`, `Message` |

### ⚠️ VipHealthProbe 字段语义说明

- `Success=false` + `WasHealthy=true`：探测本次失败，但 VIP 健康状态**未降级**（SLB 容忍偶发失败），属于噪声，不代表影响。
- `Success=false` + `WasHealthy=false`：VIP 被判定为**不健康**，SLB 可能停止向该 VIP 转发流量——这才是客户影响的关键指标。

### Query Templates (verified)

```kusto
// SQL Gateway VIP 健康探测
cluster('azslb.kusto.windows.net').database('azslbmds').VipHealthProbe
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where VipAddress == '{VipAddress}'
| where VipPort == {Port}
| project env_time, VipAddress, VipPort, Success, WasHealthy, Reason
| order by env_time asc

// 节点出站探测汇总（按 NodeId）
cluster('azslb.kusto.windows.net').database('azslbmds').OutboundProbeResultHistoryEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == '{NodeId}'
| summarize Total=count(), UP=countif(ProbeResult=='UP'), Down=countif(ProbeResult!='UP') by NodeId, bin(PreciseTimeStamp, 5m)

// MUX Host Agent 操作检查（升级/排空/重启）
cluster('azslb.kusto.windows.net').database('azslbmds').HostActionHistoryEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where PFMachineName has '{PFMachineName}' or NodeId == '{NodeId}'
| where Action has 'Upgrade' or Action has 'Drain' or Action has 'Restart'
| project PreciseTimeStamp, NodeId, PFMachineName, Action, IsSucceeded, ErrorMessage
| order by PreciseTimeStamp asc

// SLB Health Signal 状态变化
cluster('azslb.kusto.windows.net').database('azslbmds').HealthSignalStateHistoryEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == '{NodeId}'
| project PreciseTimeStamp, HealthSignalName, CurrentHealthyState, LastHealthyState, CurrentDetailedReason, PFMachineName
| order by PreciseTimeStamp asc
```

---

## Argwus2nrpone.westus2 → AzureResourceGraph (Resource Graph)

**URI**: `https://Argwus2nrpone.westus2.kusto.windows.net` → database: `AzureResourceGraph`  
**Access**: CoreIdentity `ARG Networking Stamp Users`  
**Purpose**: Azure Resource Graph — full resource topology. Used in vWAN troubleshooting to look up resource address space and ARM metadata without customer access.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `Resources` | Full ARM resource metadata for all Azure resources | id, type, name, subscriptionId, resourceGroup, location, properties |

### Key KQL: vWAN Address Space Lookup via Resource Graph

```kusto
cluster('Argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where type == "microsoft.network/virtualhubs"
| where subscriptionId == "{SubscriptionId}"
| project name, location, properties.addressPrefix, properties.virtualWan
```

---

## eearg.westus2 → AzureResourceGraph (EagleEye Network ARG — 网络专用资源图)

**URI**: `https://eearg.westus2.kusto.windows.net` → database: `AzureResourceGraph`  
**推荐入口**：`eagleai` MCP（stdio relay，启动后调 `execute_kusto_query`）；也可走 `kusto` / `azuremcp` 直连。  
**Owner**: networking-copilot 团队 / EagleEye  
**Access**: Entra ID Corp account through the `eagleai` MCP relay; if direct Kusto access fails, use the repo's normal MCP troubleshooting path.

### 与通用 ARG (`Argwus2nrpone`) 的区别

| 维度 | 通用 ARG (`Argwus2nrpone`) | **eearg （Network ARG）** |
|---|---|---|
| schema | `properties` 是 JSON blob，需 `parse_json` / `mv-expand` | **网络资源字段预先展开**，可直接 `extend addressSpace = properties.addressSpace.addressPrefixes` |
| join 键 | `id` 字符串拼 | 原生 `resourceGuid`（GUID）跨表快速 join |
| 优化资源类型 | 通用 | **VNet/Subnet/NIC/NSG/PIP/PE/PLS/LB/AppGW/FrontDoor/ER/VirtualHub** |
| 访问路径 | 需 `ARG Networking Stamp Users` 组 | 企业帐号直接（eagleai MCP 代理认证）|
| 延迟 | 分钟级，有 throttle | 平台内部使用，延迟较低 |

> **经验法则**：任何“查网络资源属性 / 一个资源以及它的拓扑邻居 / 跨资源类型关联”都应优先走 `eearg`。仅在 eagleai MCP 不可用时才回退 `Argwus2nrpone`。

### 常用资源类型（`type =~` 过滤）

| type | 含义 |
|---|---|
| `microsoft.network/virtualnetworks` | VNet |
| `microsoft.network/virtualnetworks/subnets` | Subnet |
| `microsoft.network/networkinterfaces` | NIC |
| `microsoft.network/networksecuritygroups` | NSG |
| `microsoft.network/publicipaddresses` | Public IP |
| `microsoft.network/privateendpoints` | Private Endpoint |
| `microsoft.network/privatelinkservices` | Private Link Service |
| `microsoft.network/loadbalancers` | LB |
| `microsoft.network/applicationgateways` | App Gateway |
| `microsoft.network/frontdoors` / `microsoft.cdn/profiles` | Front Door / CDN |
| `microsoft.network/expressroutecircuits` | ER Circuit |
| `microsoft.network/virtualhubs` / `virtualwans` | vWAN |

### `eagleai.execute_kusto_query` 调用示例

```jsonc
// 参数：cluster 只填主机名（不带 https://），database 是 schema 名
execute_kusto_query({
  query:    "cluster('eearg.westus2').database('AzureResourceGraph').Resources | where type =~ 'microsoft.network/virtualnetworks' | where subscriptionId =~ '<sub>' | take 5",
  cluster:  "eearg.westus2",
  database: "AzureResourceGraph"
})
```

### Key KQL 模板

**T1 — 用 SubscriptionId 批量列一个订阅下所有 VNet，含地址空间 / DNS / Peering**：
```kusto
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where type =~ 'microsoft.network/virtualnetworks'
| where subscriptionId =~ '{SubscriptionId}'
| extend addressSpace   = properties.addressSpace.addressPrefixes,
         dnsServers     = properties.dhcpOptions.dnsServers,
         peeringCount   = array_length(properties.virtualNetworkPeerings),
         subnets        = properties.subnets
| project name, location, resourceGroup, addressSpace, dnsServers, peeringCount, subnets
```

**T2 — 给定 NIC 名，反查其 Subnet → VNet 拓扑**：
```kusto
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where type =~ 'microsoft.network/networkinterfaces' and name =~ '{NicName}'
| mv-expand ipconfig = properties.ipConfigurations
| extend subnetId = tostring(ipconfig.properties.subnet.id),
         privIp   = tostring(ipconfig.properties.privateIPAddress),
         pipId    = tostring(ipconfig.properties.publicIPAddress.id)
| project name, privIp, pipId, subnetId
```

**T3 — 某 region 下所有 Private Endpoint 及其连接状态**：
```kusto
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where type =~ 'microsoft.network/privateendpoints'
| where location =~ '{Region}'
| mv-expand pls = properties.privateLinkServiceConnections
| extend targetResource = tostring(pls.properties.privateLinkServiceId),
         connState      = tostring(pls.properties.privateLinkServiceConnectionState.status)
| project name, resourceGroup, subscriptionId, targetResource, connState
```

---

## ARM 跨 Region 联合查询

**场景**：不确定资源 CRUD 发起于哪个 region（如全球性 LB / Front Door / vWAN），需一次拿多 region ARM 调用。

**模板**：
```kusto
cluster('armprodsea.southeastasia').database('Requests').HttpIncomingRequests
| union cluster('armprodeus.eastus').database('Requests').HttpIncomingRequests,
        cluster('armprodweu.westeurope').database('Requests').HttpIncomingRequests
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where subscriptionId =~ '{SubscriptionId}'
| where targetUri contains '{ResourceName}'
| project TIMESTAMP, $cluster=tostring(cluster_name()), httpMethod, httpStatusCode,
          operationName, targetUri, correlationId, userAgent, durationInMilliseconds
| order by TIMESTAMP asc
```
> 三个 MCP 都能跑这句。**注意**：`eagleai.execute_kusto_query` 的 `cluster` 参数是单个主机名，裸跨 region union 请改走 `kusto` / `azuremcp`（env 默认集群 + KQL 里 `cluster()` 函数跨连）。

---

## EagleAI 高层语义入口（`EagleAI` / `DiscoverTopology`）

除了裸 KQL，`eagleai` MCP 还有两个 **只接受自然语言** 的高层工具：

### `eagleai.EagleAI(user_query)`
总入口，server 会自动路由到 RAG TSG / Kusto / topology 三条子路径之一。
适用于**故障描述明确、但不确定走哪条查询路径**的场景。

调用示例：
```jsonc
EagleAI({
  user_query: "客户 VM /subscriptions/xxx/.../vm-foo 在 04/27 UTC 03:00–04:30 连不上 Private Endpoint 后面的 storage 账号 mystoracc，走 ER，帮我排查是哪一段报错"
})
```

### `eagleai.DiscoverTopology(user_query)`
专门调用 EagleEye Portal 后面的连通性诊断引擎，返回 **拓扑递跳 / NSG 命中 / latency 分布** 等文本报告。
适用场景：
- VM → Public IP / Private Endpoint / Storage / SQL / 另一台 VM 连通性检查
- ExpressRoute gateway 诊断、Azure Front Door edge 分析
- 跨 region latency / topology hop 检查
- NSG 规则分析、Private Link 端点检查
- vWAN/Hub / VPN sites / MSEE / NVA 配置

调用示例：
```jsonc
DiscoverTopology({
  user_query: "Check connectivity from VM /subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-foo (10.1.2.4) to mystoracc.privatelink.blob.core.windows.net at 2026-04-27T03:15Z, scenario=VM-to-PrivateEndpoint"
})
```

> **拼描述要诀**：资源 ARM resource id、IP、FQDN、UTC 时间点、场景类型勿漏。Server 越能拿到结构化错误，追踪越准。

---

## Sirius.eastus → siriusLogs (VNet Encryption / SmartNIC)

**URI**: `https://Sirius.eastus.kusto.windows.net` → database: `siriusLogs`  
**Access**: AME credentials required (TA/EEE restricted)  
**Purpose**: Sirius = Azure VNet Encryption / SmartNIC servicing. Tracks provisioning, goal state, critical failures for encrypted VNET nodes.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `SiriusServicingInfoTable` | Node servicing info for VNet Encryption | (nodeId, servicing state, timestamp) |
| `SiriusCriticalFailureTable` | Critical failures in encryption provisioning | (nodeId, failureReason, timestamp) |
| `SiriusGrpcFailureTable` | gRPC channel failures to Sirius service | (nodeId, error, timestamp) |
| `SiriusMadariNotificationTable` | Madari notification events | (nodeId, event, timestamp) |
| `SiriusMadariSubscriptionTable` | Madari subscription state | (nodeId, subscriptionState) |
| `SiriusGoalStateRecievedTable` | Goal state updates received by Sirius agent | (nodeId, goalState, timestamp) |

---

## Azcrp → crp_allprod (Compute Resource Provider)

**URI**: `https://Azcrp.kusto.windows.net` → database: `crp_allprod`  
**Access**: CoreIdentity `Azc Kusto Log RO – 20100`  
**Retention**: ~365 days. **Latency**: ~1–7 min.  
**Purpose**: Compute Resource Provider — used in networking context for VM NIC attachment, VM creation failures affecting networking.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `ApiQosEvent` | CRP API QoS events | subscriptionId, operationName, httpStatusCode, durationMs, correlationId |
| `ContextActivity` | CRP context activity for complex multi-step operations | subscriptionId, operationName, correlationId |
| `VMApiQosEvent` | VM-specific API QoS events | subscriptionId, vmName, operationName, httpStatusCode |

---

## Additional Clusters (Reference Only)

These clusters are listed in the AzureNetworking Kusto Clusters page but have limited query examples in the wiki:

| Cluster | Database | Access | Purpose |
|---------|----------|--------|---------|
| `Aznwwan.kusto.windows.net` | — | `WA CTS-14817` | WAN internal |
| `Aznwsdn.kusto.windows.net` | — | `WA CTS-14817` | SDN internal |
| `Azphynet.kusto.windows.net` | — | IDWeb `aznwkustoreader` | Physical Network |
| `Ipam.kusto.windows.net` | — | IDWeb `IPAMv2-RO-USER` | IP Address Management |
| `Netcapplan.kusto.windows.net` | — | IDWeb `NetCapPlanKustoViewers` (FTE only) | Network Datapath / capacity |
| `Afdmoi.kusto.windows.net` | — | TA/EEE/PG restricted | Azure Front Door internal |
| `Azlinux.kusto.windows.net` | — | IDWeb `AzLinux Kusto Users` | Linux platform |
| `Aznwautotriage.kusto.windows.net` | — | `WA CTS-14817` | Auto-triage |
| `Azsc.kusto.windows.net` | — | `WA CTS-14817` | Azure Support Center |
| `Vmainsight.kusto.windows.net` | `vmadb` / `Air` | IDWeb `VMA KustoDB User` | VMA RCA (see catalog-AzureIaaSVM.md) |
| `Azurecm.kusto.windows.net` | `AzureCM` | CoreIdentity FC Log Read-Only (12894) | Compute Manager (see catalog-AzureIaaSVM.md) |
| `Icmcluster.kusto.windows.net` | `ACM.Publisher` | — | ICM incident notifications |
| `Xstore.kusto.windows.net` | — | — | Azure Storage |

---

## Fairfax (Azure Government) Cluster Map

| Public Cluster | Government Equivalent | Notes |
|---------------|----------------------|-------|
| `Nrp.kusto.windows.net` (mdsnrp) | `Aznwff.kusto.usgovcloudapi.net` (aznwmds) | Same table names |
| `Hybridnetworking.kusto.windows.net` (aznwmds) | `Aznwff.kusto.usgovcloudapi.net` (aznwmds) | AppGW, VPN, ExR, vWAN all in Aznwff |
| `Armprodgbl/eus/weu/sea` (ARMProd/Requests) | `Armff.kusto.usgovcloudapi.net` (armff) | HttpIncomingRequests, HttpOutgoingRequests |
| `Azslb.kusto.windows.net` (azslbmds) | `Azslbff.kusto.usgovcloudapi.net` | — |
| `Azurecm.kusto.windows.net` (AzureCM) | `Azurecmff.kusto.usgovcloudapi.net` | — |
| `Azportal` | `Azportalff` | Azure Portal |
| Other | `Gcwsbn1ff`, `Rdfeff`, `Rdosff` | Government-only clusters |

---

## Latency / Retention Quick Reference

| Cluster | Typical Latency | Typical Retention |
|---------|----------------|-------------------|
| NRP (`Nrp.mdsnrp`) | 1–3 min | ~185 days |
| ARM (`Armprod*.Requests`) | 5–7 min | ~45 days |
| Hybridnetworking (`aznwmds`) | 4–20 min (table-dependent) | ~90 days |
| Azurecdn (`azurecdnmds`) | 1–6 min | ~90 days |
| Azureinsights (`Insights`) | ~8 min | ~30 days |
| CRP (`Azcrp.crp_allprod`) | 1–7 min | ~365 days |

---

## Access Request Summary

| Access Group | Portal | Covers |
|-------------|--------|--------|
| `WA CTS-14817` | CoreIdentity | ARM (FTE), NRP, Hybridnetworking, Azslb, Azurecdn, Aznwwan, Aznwsdn, Aztmmon, Managedresolver, Aznwautotriage |
| `ARM Logs` | CoreIdentity | ARM (non-FTE only) |
| `Azc Kusto Log RO – 20100` | CoreIdentity | CRP (`Azcrp.crp_allprod`) |
| `ARG Networking Stamp Users` | CoreIdentity | Resource Graph (`Argwus2nrpone`) |
| `Ddos Kusto access for Partners` | IDWeb | DDoS (`Aznwddos.centralus`) — FTE only |
| `IPAMv2-RO-USER` | IDWeb | IPAM |
| `NetCapPlanKustoViewers` | IDWeb | Network Datapath — FTE only |
| `aznwkustoreader` | IDWeb | Physical Network (`Azphynet`) |
| `Insight Kusto Users` | IDWeb | Azure Monitor Insights |
| `VMA KustoDB User` | IDWeb | vMAInsight (shared with IaaSVM) |
| `AzLinux Kusto Users` | IDWeb | Linux platform cluster |
| AME credentials | SAW only | Sirius (`Sirius.eastus`), AKV logs |

---

# Networking Troubleshooting SOPs

> 以下章节为 b01 dashboard 知识体系蒸馏（来源：naniteagent/b01）。  
> 性质：**方法论 + 数据面 SOP**，不是 KQL 模板堆砌；与上方 cluster catalog 配合使用。

## SOP-1: Host Networking Layer Model (架构定基)

> 触发：网络丢包、连接抖动、AccelNet 异常、VFP drop、PingMesh 异常等任何"host 节点上发生的网络问题"。  
> 用法：Phase 0 架构定基阶段查阅，作为分层查询骨架。

主机网络数据面从北到南分层：

| Layer | 组件 | 关键证据来源 | 典型故障表征 |
|---|---|---|---|
| L0 网线 | TOR ↔ Host Node 物理链路 | Azphynet 接口计数、Gemini Y-cable 状态 | Link flap、CRC、optical down |
| L1 NIC HW | Mellanox / MANA 物理网卡 | `GdmaBnicGlobalCounters`、`ManaBnicInternalCounters`、`Mlnx5FwIntermediary_v1` | BNIC drop、Firmware fault、backpressure |
| L2 SmartNIC | FPGA / SoC (OverLake) | `NetDatapathPerfCounters`、GFT 状态 | FPGA datapath fail、GFT offload miss |
| L3 AccelNet | Accelerated Networking | `AccelnetSLI` 可用性 SLI | AccelNet disrupt、SR-IOV path fail |
| L4 VFP | Virtual Filtering Platform | VFP drop reasons（Resource/ACL/NoRuleMatch/Malformed/Pending） | ACL block、规则误命中、flow 表满 |
| L5 GFT | Generic Flow Table | GFT 卸载状态、unified flow entries | 卸载失败、回落到软件路径 |
| L6 Guest | VM 内部网络栈 | Guest OS / Extension 日志 | 不在 host networking 范围 |

**调查顺序**：自上而下排除：先确认 L4 VFP 是否 drop → 再看 L1/L2 NIC HW counter → 最后才到 L0 物理链路。  
**反模式**：上来就翻 BGP / 物理链路日志 ≈ 80% 的 host 侧问题被错过。

**关键集群补充**（catalog 主表已列，此处仅汇总入口）：
- `cluster('azurehn').database('Azurehn')` — VFP/Host Networking MDM 全量指标
- `cluster('aznwnetmon').database('aznwmds').sXInterfaceTable` — 物理网设备接口 SNMP（见 SOP-2）
- `cluster('aznwcc').database('aznwmds').Servers` — Node ↔ TOR DeviceName 映射

---

## SOP-2: Cross-Region Network Jitter / Latency 调查

> 触发：跨 region VM 之间 RTT 抖动、丢包、用户报告 "ER 抖动"、"跨区延迟突刺"。  
> 关键纪律：**Path First, Data Plane First**。不要从 BGP flap 入手。

### Step 1 — 描画完整物理路径

**Layer A (VM → TOR)**：
```kusto
cluster('azurecm').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= datetime({Start})
| where containerId in (dynamic([{ContainerIds}]))
| take 1
| project containerId, Cluster, NodeId, AvailabilityZone
| join kind=inner (
    cluster('aznwcc').database('aznwmds').Servers
    | where PreciseTimeStamp > ago(1d)
    | distinct NodeId, DeviceName
) on NodeId
| project containerId, Cluster, NodeId, ToRDeviceName=DeviceName
```

**Layer B (TOR → T1/T2 → WAN Edge)**：use a schema-verified `cluster('azphynet').database('{AzPhyNetDb}').DeviceInterfaceLinks` query for uplink device/interface mapping.

**Layer C (WAN Backbone via Swan TE)**：
```kusto
cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(
    datetime({Start}), datetime({End}), '{Deployment}')
| where (Source == "owr03.{SrcSite}" or Source == "owr03.{SrcSite2}")
    and (Destination == "{DstCityCode1}" or Destination == "{DstCityCode2}")
| project Source, Destination, TrafficClass, PathPriority, RequestedMbps, RouterHopsWithPorts
```
| Region 范围 | Swan Deployment Name |
|---|---|
| North America OWR | `ProductionNAM1` |
| OneWAN | `ProductionOneNam` |
| EU | `ProductionOneEu` |

> Source 用完整设备名（如 `owr03.dub07`），Destination 用城市码（如 `IAD11`, `CO8`）。DUB/EU 设备多数仅在 RouterHops 中出现而非作为 Source。

### Step 2 — 全量数据面扫描 OutDiscards（最关键的一步）

```kusto
cluster('aznwnetmon').database('aznwmds').sXInterfaceTable
| where DeviceName matches regex "^(ibr|owr|car)\\d+"
| where PreciseTimeStamp between (datetime({Start}) .. datetime({End}))
| summarize MaxOutDiscards=max(ifOutDiscards_Counter) by DeviceName, ifName
| where MaxOutDiscards > 100
| order by MaxOutDiscards desc
```

**`sXInterfaceTable` 列名陷阱（必须背熟）**：

| 正确列名 | 含义 | 常见错写 |
|---|---|---|
| `PreciseTimeStamp` | 时间戳 | ~~vscpTimeStamp~~ |
| `ifName` | 接口名 | ~~InterfaceName~~ |
| `ifOutDiscards_Counter` | OutDiscards 每周期 **delta** | ~~OutDiscards~~ |
| `ifInDiscards_Counter` | InDiscards 每周期 delta | ~~InDiscards~~ |
| `_Raw_ifOutDiscards_Counter` | OutDiscards **累积** SNMP 值 | — |
| `ifOutErrors_Counter` / `ifInErrors_Counter` | Err 每周期 delta | ~~OutErrors~~ / ~~InErrors~~ |
| `Interval` | SNMP 采样间隔（秒） | — |
| `ifHighSpeed` | 链路速度（Mbps） | — |
| `ifHCInOctets_Counter` / `ifHCOutOctets_Counter` | 字节 delta | — |

### Step 3 — 控制面检查（顺序在后，不在前）

只对 **Step 1 路径上确认的设备** 检查 BGP flap、ISIS 邻居 down、Swan tunnel down。无路径的设备不查。

### Step 4 — 根因深挖

OutDiscards 命中后：查 Swan TE 带宽分配、流量需求趋势、Link Member 状态、TE Scheduler 调度时序。

### 常见误区（强制规避）

1. ❌ 从 BGP flap 扫描开始 — 控制面 ≠ 数据面，多数 jitter 是 queue overflow
2. ❌ 调查不在路径上的设备 — 永远先描路径再调查
3. ❌ 用 "BGP 无 flap" 推论 "WAN 干净" — 零 flap 不等于零数据面问题
4. ❌ 把 `ifOutDiscards_Counter` 当累积值用 — 它是每周期 delta，要 sum 或用 `_Raw_` 前缀
5. ❌ Swan TE 把 DUB/EU 设备当 Source 查 — 它们多数只在 RouterHops 中

---

## SOP-3: SLB / MUX 节点崩溃排错

> 触发：TOR PingMesh 到 MUX 降至 0%、NAT Gateway/LB 数据面可用性下降、VIP 不可达。  
> **架构关键**：SLB MUX 由 **Service Fabric** 管，不在 AzureCM 视野内。

### 架构差异速查

| ❌ 错误做法 | ✅ 正确做法 |
|---|---|
| 用 `LogNodeSnapshot` / `LogContainerSnapshot` 查 MUX NodeId（永远 0 行） | 查 `Azslb.azslbmds` 的 `NodeHealthEvent`、`SlbCritical`、`SlbException` |
| 用 `HealthSignalStateHistoryEvent` 查 MUX（该表只跟 compute host） | 用 `NodeHealthEvent` 看 SF 节点状态 |

### azslbmds 表 schema 差异（极易混淆）

| Table | Timestamp 列 | Role/Ring 列 | Instance 列 |
|---|---|---|---|
| `SlbCritical` | `env_time` | `env_cloud_role` | `env_cloud_roleInstance` |
| `SlbException` | `env_time` | `env_cloud_role` | `env_cloud_roleInstance` |
| `SlbHealthEvent` | `env_time` | `env_cloud_role` | `env_cloud_roleInstance` |
| `NodeHealthEvent` | `TIMESTAMP` | `Role` | `NodeName` |
| `HealthSignalStateHistoryEvent` | `TIMESTAMP` | `Cluster` | `NodeId` / `Ip` |
| `HostActionHistoryEvent` | `TIMESTAMP` | `Cluster` | `Ip` |
| `BgpPeerStateSnapshotEvent` | `env_time` | `Ring` | `Node` / `NodeNumber` |
| `RepairTaskRecord` | `env_time` | `Ring` | — |

### MUX RoleInstance 命名陷阱（同一节点 4 种写法）

| 表 | 格式 | 示例 |
|---|---|---|
| `LogContainerSnapshot` (AzureCM) | `SlbRingHostRole_IN_N` | `SlbRingHostRole_IN_3` |
| `SlbCritical` / `SlbException` | `SlbRingHostRole_N` | `SlbRingHostRole_3` |
| `SlbHealthEvent` | `SlbRingHostRole_N` | `SlbRingHostRole_2` |
| `NodeHealthEvent` | `SlbRingHostRole.N` | `SlbRingHostRole.3` |

### Step 1 — 识别 Ring 和故障 MUX

查 `slb-vip` 类查询（catalog §azslb 部分）：Ring MUX Instance Information、MUX Node TOR Pingmesh，确认掉到 0% 的 NodeId。

### Step 2 — MUX 进程崩溃证据 (`SlbCritical`)

```kusto
let RingN = "{RingName}";  // 如 "r296-bl-az"
cluster('Azslb').database('azslbmds').SlbCritical
| where env_time between (datetime({Start}) .. datetime({End}))
| where env_cloud_role == RingN
| project env_time, env_cloud_roleInstance, ServiceType, Critical, Message, CallerFilePath, CallerLine
| order by env_time asc
```

**关键 `Critical` 值**：
| 值 | 含义 |
|---|---|
| `MuxShutdownUnexpected` | 🔴 MUX 进程崩溃 — **铁证** |
| `LogDropped` | 崩溃/恢复期间遥测丢失 |
| `MuxUnifiedLwfDeviceControl` | VFP LWF 驱动重初始化（恢复阶段） |

**典型崩溃证据模式**：最后正常日志 → **完全静默**（进程 dead）→ 恢复后 `MuxUnifiedLwfDeviceControl` 重初始化 → `MuxShutdownUnexpected` 在重启时由 `Worker.cs:544` 输出。

### Step 3 — Service Fabric 视角 (`NodeHealthEvent`)

```kusto
cluster('Azslb').database('azslbmds').NodeHealthEvent
| where TIMESTAMP between (datetime({Start}) .. datetime({End}))
| where Role == "{RingName}"
| project TIMESTAMP, Role, NodeName, SourceId, Property, HealthState, Description
| order by TIMESTAMP asc
```

| SourceId | Property | HealthState | 含义 |
|---|---|---|---|
| `System.FM` | `State` | `Error` | "Fabric node is down" — SF 失联 |

### Step 4 — 数据面爆炸半径 (`SlbHealthEvent`)

按 Ring 查 `DataPathAvailabilityWarning` 和 `NoForwardingDip`，确认受影响的 VIP 和租户范围。

### Step 5 — 恢复期连接异常 (`SlbException`)

MUX 重启后需重连 SDN Gateway，查 `WebException` 检测恢复延迟：

```kusto
cluster('Azslb').database('azslbmds').SlbException
| where env_time between (datetime({Start}) .. datetime({End}))
| where env_cloud_role == "{RingName}"
| project env_time, env_cloud_roleInstance, ServiceType, Exception, Message, CallerFilePath, CallerLine
| order by env_time asc
```

| Exception | 含义 |
|---|---|
| `WebException` | SDN Gateway 拒绝连接 — 崩溃后重连中 |
| `SocketException` | 网络层连接失败 |
| `TimeoutException` | SDN Gateway 无响应 |

### Step 6 — 排除物理网络

用 catalog §azslb 的 "Discard and Error packet counter over T0 of MUX" 查询 + `physical-network` 类查询，确认 ToR/T1 链路在事件窗口内全程 UP 且零 err。

### 核心结论

**TOR PingMesh 跌零 + ToR/T1 链路 UP 且无 err → 几乎一定是 MUX 进程崩溃（VFP LWF 驱动失去控制进程），不是物理网络故障。**

