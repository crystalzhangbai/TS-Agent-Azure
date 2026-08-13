---
description: KQL queries for Azure Host Networking troubleshooting from B01 dashboard: VFP MDM drop metrics (Resource/ACL/Malformed/Pending drops), VFP flow creation rate (CPS), Host NIC drop diagnostics (AccelnetSLI, BNIC, OverLake counters), and Network-Dashboard-VM with VFP/PNIC dashboard links.
---

# Host Networking Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: VM-Dash (Host Networking section)
> Use this file to diagnose **host-level networking issues**: VFP packet drops, Host NIC errors, AccelNet availability, and related data-plane problems.

## High-Level Scoping (Run Before Deep-Dive Analysis)

Before diving into VFP drops, Host NIC counters, or FPGA diagnostics, perform these scoping checks to build situational awareness of the node and workload. This context is critical for interpreting deeper metrics correctly.

### Step 1: Determine Node Type — OverLake vs Non-OverLake

OverLake nodes use a System-on-Chip (SoC) architecture that introduces additional data-plane components (SoC NIC, backplane, MANA driver). While OverLake provides hardware offload benefits, it also means:
- **More complex data path** — packets traverse SoC ↔ backplane ↔ host, adding potential failure points
- **Lower slow-path (VFP software path) capacity** — compared to non-OverLake nodes, OverLake has reduced CPU-based packet processing throughput; workloads with high slow-path PPS are more susceptible to drops on OverLake
- **Different diagnostic tables** — OverLake nodes use `NetDatapathPerfCounters` and `BackplaneMetricsCounters`; non-OverLake nodes use `GdmaBnicGlobalCounters`

```kql
// Check if the node is OverLake (SocNodeId is non-empty = OverLake)
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where containerId == 'CONTAINER_ID' or nodeId == 'NODE_ID'
| join kind=leftouter cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2 on $left.nodeId == $right.NodeId
| distinct nodeId, SocNodeId
| extend IsOverLake = iff(isempty(SocNodeId), "No", "Yes")
```

### Step 2: Check VM SKU Size and Network Capabilities

Different VM SKU sizes have significantly different networking capabilities:
- **vCPU count** directly impacts **CPS (Connections Per Second)** capacity — VFP flow creation is CPU-bound on the slow path
- **SKU tier and size** determine **maximum throughput (Gbps)** and **maximum PPS** limits
- **Some SKUs require Accelerated Networking (AccelNet)** — if AccelNet is disabled or disrupted on such SKUs, all traffic falls to the slow path, causing severe performance degradation
- **Smaller SKUs** are more vulnerable to resource exhaustion under traffic spikes

```kql
// Get VM SKU, OS type, and basic placement info for the target VM
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where containerId == 'CONTAINER_ID'
| distinct containerId, nodeId, VMSize = tostring(split(billingType, "|")[1]), OSType = tostring(split(billingType, "|")[0]), Tenant, Region, AvailabilityZone
```

### Step 3: Assess Traffic Volume — PPS, BPS, VFP Slow-Path PPS, CPS, and Flow Count

A sudden spike in Packets Per Second (PPS), Bits Per Second (BPS), VFP slow-path PPS, Connections Per Second (CPS), or active Flow Count is a common trigger for host networking component stress, leading to performance degradation or packet loss. Check the traffic profile during the incident window:

```kql
// VFP Port-level PPS (Inbound + Outbound) — per container on the node
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let ppsInQuery = strcat(
    "metricNamespace('VfpPortCounterRates').",
    "metric('InPacketsPerSecond').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
let ppsOutQuery = strcat(
    "metricNamespace('VfpPortCounterRates').",
    "metric('OutPacketsPerSecond').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
let ppsIn = evaluate geneva_metrics_request(vfpaccount, ppsInQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, InPPS = Sum;
let ppsOut = evaluate geneva_metrics_request(vfpaccount, ppsOutQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, OutPPS = Sum;
ppsIn
| join kind=inner ppsOut on TimestampUtc, NodeId, ContainerId
| project TimestampUtc, NodeId, ContainerId, InPPS, OutPPS, TotalPPS = InPPS + OutPPS
| order by TimestampUtc asc
```

```kql
// VFP Port-level BPS (Inbound + Outbound bytes) — per container on the node
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let bpsInQuery = strcat(
    "metricNamespace('VfpPortCounterRates').",
    "metric('InBytesPerSecond').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
let bpsOutQuery = strcat(
    "metricNamespace('VfpPortCounterRates').",
    "metric('OutBytesPerSecond').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
let bpsIn = evaluate geneva_metrics_request(vfpaccount, bpsInQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, InBPS = Sum;
let bpsOut = evaluate geneva_metrics_request(vfpaccount, bpsOutQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, OutBPS = Sum;
bpsIn
| join kind=inner bpsOut on TimestampUtc, NodeId, ContainerId
| project TimestampUtc, NodeId, ContainerId, InBPS, OutBPS, TotalBps = InBPS + OutBPS, TotalGbps = round((InBPS + OutBPS) * 8 / 1000000000.0, 2)
| order by TimestampUtc asc
```

```kql
// VFP Slow-Path PPS — packets processed by VFP software path (not GFT-offloaded)
// High slow-path PPS indicates traffic that cannot be hardware-offloaded, putting pressure on CPU
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let slowPathQuery = strcat(
    "metricNamespace('VfpPortCounterRates').",
    "metric('SoftwareProcessedInPacketsPerSecond').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
evaluate geneva_metrics_request(vfpaccount, slowPathQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, SlowPathInPPS = Sum
| order by TimestampUtc asc
```

```kql
// VFP CPS (Connections Per Second) — flow creation rate per container
// High CPS consumes CPU on the slow path; exceeding the node's CPS capacity causes Resource Drops
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let cpsInQuery = strcat(
    "metricNamespace('VfpPortFlowStats').",
    "metric('CreatedTotalFlowEntryInRate').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum','Max')\n",
    "| where NodeId == '", nodeId, "'"
);
let cpsOutQuery = strcat(
    "metricNamespace('VfpPortFlowStats').",
    "metric('CreatedTotalFlowEntryOutRate').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum','Max')\n",
    "| where NodeId == '", nodeId, "'"
);
let cpsIn = evaluate geneva_metrics_request(vfpaccount, cpsInQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, AvgCPSIn = Sum, MaxCPSIn = Max;
let cpsOut = evaluate geneva_metrics_request(vfpaccount, cpsOutQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, AvgCPSOut = Sum, MaxCPSOut = Max;
cpsIn
| join kind=inner cpsOut on TimestampUtc, NodeId, ContainerId
| project TimestampUtc, NodeId, ContainerId, AvgCPSIn, AvgCPSOut, TotalAvgCPS = AvgCPSIn + AvgCPSOut, MaxCPSIn, MaxCPSOut
| order by TimestampUtc asc
```

```kql
// VFP Flow Count — total active flow entries per container
// VFP has a per-port flow table limit (~2M entries); approaching this limit triggers Resource Drops
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let flowInQuery = strcat(
    "metricNamespace('VfpPortFlowStats').",
    "metric('CurrentTotalFlowEntryIn').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum','Max')\n",
    "| where NodeId == '", nodeId, "'"
);
let flowOutQuery = strcat(
    "metricNamespace('VfpPortFlowStats').",
    "metric('CurrentTotalFlowEntryOut').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum','Max')\n",
    "| where NodeId == '", nodeId, "'"
);
let flowIn = evaluate geneva_metrics_request(vfpaccount, flowInQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, AvgFlowIn = Sum, MaxFlowIn = Max;
let flowOut = evaluate geneva_metrics_request(vfpaccount, flowOutQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, AvgFlowOut = Sum, MaxFlowOut = Max;
flowIn
| join kind=inner flowOut on TimestampUtc, NodeId, ContainerId
| project TimestampUtc, NodeId, ContainerId, AvgFlowIn, AvgFlowOut, TotalAvgFlow = AvgFlowIn + AvgFlowOut, MaxFlowIn, MaxFlowOut, TotalMaxFlow = MaxFlowIn + MaxFlowOut
| order by TimestampUtc asc
```

> **Interpretation guide:**
> - Compare PPS/BPS against the VM SKU's documented network limits — if approaching limits, performance degradation is expected behavior, not a platform fault
> - A sudden spike in slow-path PPS (e.g., due to new flows, AccelNet disable, or GFT offload failure) is a strong signal for VFP Resource Drops
> - On OverLake nodes, the slow-path throughput ceiling is lower — even moderate slow-path PPS can cause drops
> - **CPS** — VFP flow creation is CPU-bound; a CPS spike (e.g., port scan, short-lived connections, SYN flood) can exhaust slow-path CPU, causing Resource Drops even when PPS/BPS are within limits
> - **Flow Count** — VFP has a per-port flow table limit (~2M entries); when flow count approaches this limit, new flows are dropped as Resource Drops; long-lived idle flows or flow leak can silently fill the table

### Step 4: Noisy Neighbor Check — Other VMs on the Same Host Node

In cloud networking, a **noisy neighbor** — a VM on the same physical host generating excessive traffic or consuming disproportionate resources — can degrade networking performance for all other VMs on that node. Before concluding the issue is isolated to the target VM, check all containers on the same host node:

```kql
// List all VMs (containers) on the same host node during the incident window
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where nodeId == 'NODE_ID'
| distinct containerId, roleInstanceName, subscriptionId, VMSize = tostring(split(billingType, "|")[1]), creationTime
| order by creationTime asc
```

```kql
// Check VFP Resource Drops across ALL containers on the node — identify noisy neighbor
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let dropQuery = strcat(
    "metricNamespace('VfpPortDropMetrics').",
    "metric('DroppedResourcesPacketInRate').",
    "dimensions('Cluster','NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
evaluate geneva_metrics_request(vfpaccount, dropQuery, starttime, endtime)
| summarize TotalDrops = sum(Sum) by ContainerId
| where TotalDrops > 0
| order by TotalDrops desc
```

```kql
// Check PPS across ALL containers on the node — identify which VM is generating the most traffic
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let ppsQuery = strcat(
    "metricNamespace('VfpPortCounterRates').",
    "metric('InPacketsPerSecond').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
evaluate geneva_metrics_request(vfpaccount, ppsQuery, starttime, endtime)
| summarize AvgPPS = avg(Sum), MaxPPS = max(Sum) by ContainerId
| order by MaxPPS desc
```

> **Noisy neighbor indicators:**
> - One container has significantly higher PPS/BPS than others on the same node
> - VFP Resource Drops appear across multiple containers simultaneously — suggesting node-level saturation rather than a single-VM issue
> - A large-SKU VM with AccelNet disabled can monopolize host CPU for slow-path processing, starving smaller VMs

### Step 5: Fault Isolation — Guest OS vs Single-VM Host Networking vs Node-Wide Issue

After completing Steps 1–4, use the collected evidence to classify the problem into one of three fault domains. This determines the next investigation path and avoids wasting effort on the wrong layer.

#### Category A: Guest OS / Application-Level Issue (Not a Host Networking Fault)

**Indicators:**
- Host node metrics are clean: Host-TOR PingMesh availability is 100%, no VFP Resource Drops on the target container, flow count and CPS are within normal range
- Other VMs on the same host node show no anomalies
- The VM may show a sudden traffic pattern change (e.g., PPS/BPS spike or drop) that aligns with the reported issue — this suggests the workload itself changed behavior
- VNET PingMesh for the VM shows no loss (if available)

**Conclusion:** The issue is internal to the guest OS or application (e.g., OS network stack misconfiguration, application crash, firewall rules inside VM, guest NIC driver issue). Host networking is not at fault.

**Next steps:** Recommend the customer investigate inside the guest OS — check `netstat`, OS firewall, NIC driver, application logs. Refer to `vm-dash.md` for guest OS version lookup.

#### Category B: Single-VM Host Networking Issue (Isolated to One Container)

**Indicators:**
- Other VMs on the same host node are healthy — no drops, normal PPS/BPS
- Host-TOR PingMesh is normal (100% availability) — the node's physical connectivity to TOR is fine
- **But** the target VM shows anomalies in one or more of:
  - VFP Resource Drops (DroppedResourcesPacketInRate/OutRate > 0) correlating with the issue window
  - VFP ACL Drops spike (NSG rule change or unexpected deny)
  - VNET PingMesh loss for this specific VM
  - CPS or Flow Count approaching limits on this container
  - AccelNet disable event (`AccelnetSLI`) affecting only this VM

**Conclusion:** The issue is in the host networking stack but scoped to this specific VM's VFP port, flow table, or AccelNet state. This is NOT a node-wide hardware failure.

**Next steps:** Proceed to **Host Networking Deep-Dive Diagnostics** below — start with VFP Resource Drop full scan (Step 4: 11-metric scan), then check AccelNet SLI, then Host NIC counters for this container.

#### Category C: Node-Wide Host Networking Issue (Affects All VMs on the Node)

**Indicators:**
- **Host-TOR PingMesh drop** — availability falls below 100%, indicating physical connectivity loss between the host node and TOR switch
- **VFP Resource Drops appear across multiple or all containers** on the same node simultaneously
- **Port timer anomalies** — VFP port create/delete timing issues affecting the node
- **Hardware fault signals:**
  - SoC/OverLake: `BackplaneMetricsCounters` showing errors (`NumOfMissedErrorsReceived`, `NumOfErrors*`)
  - Host NIC: `GdmaBnicGlobalCounters` showing `InTotalErrors > 0` or `OutTotalErrors > 0` across the node
  - FPGA: FPGA dashboard showing errors or datapath failure
  - AccelNet: `AccelnetSLI` events with `DisruptionCategory` indicating hardware-level disruption across multiple VMs
  - Mellanox FW: `Mlnx5FwIntermediary_v1` showing firmware-level events
- **Disk Read/Write congestion** appearing across multiple VMs — network-induced storage path degradation (see `vm-dash.md` → Disk Read/Write Congestion query)

**Conclusion:** The issue is at the physical host node level — potentially TOR link failure, Gemini Y-cable switchover, NIC hardware fault, FPGA failure, SoC backplane error, or other node-wide component failure.

**Next steps:** Proceed to **Host Networking Deep-Dive Diagnostics** below for VFP/NIC counters, then escalate to `vm-dash.md` physical network path queries (TOR↔T1 discard/error, link flap, MKA events) to check upstream network health. If hardware fault confirmed, consider platform incident (PG/Service Healing).

#### Quick Decision Matrix

| Evidence | Host-TOR PingMesh | VFP Drops on Target VM | VFP Drops on Other VMs | Traffic Pattern Change | → Fault Domain |
|----------|-------------------|------------------------|------------------------|------------------------|----------------|
| All clean, VM traffic changed | ✅ Normal | ✅ None | ✅ None | ⚠️ Spike/Drop | **A — Guest OS** |
| VFP drops on target only | ✅ Normal | ❌ Drops | ✅ None | Varies | **B — Single VM** |
| AccelNet disabled on target | ✅ Normal | ❌ Resource Drops | ✅ None | Slow-path PPS spike | **B — Single VM** |
| Drops on multiple VMs | ✅ Normal | ❌ Drops | ❌ Drops | Varies | **C — Node-wide** |
| PingMesh drop + multi-VM drops | ❌ Drop | ❌ Drops | ❌ Drops | Varies | **C — Node-wide** |

---

## Host Networking Deep-Dive Diagnostics

### VFP Resource Drop (MDM) — Per Node / Container

> **重要：** VFP drop 数据在 **Geneva MDM Metrics** 中，必须用 `evaluate geneva_metrics_request()` 查询。

#### Step 1: 查找 VFP MDM Account

```kql
cluster('azurehn').database('Azurehn').MdmVfpVnetAccountMaps()
| where Cluster =~ "CLUSTER_NAME"   // e.g. MNZ26PrdApp17
| project Cluster, VfpAccount, VNETAccount, HnMdmAccount
```

#### Step 2: VFP Resource Drop Rate（必查）

```kql
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let dropQuery = strcat(
    "metricNamespace('VfpPortDropMetrics').",
    "metric('DroppedResourcesPacketInRate').",
    "dimensions('Cluster','NodeId','ContainerId').",
    "samplingTypes('Sum')\n",
    "| where NodeId == '", nodeId, "'"
);
evaluate geneva_metrics_request(vfpaccount, dropQuery, starttime, endtime)
| project TimestampUtc, Cluster, NodeId, ContainerId, DroppedResourcesPacketInRate=Sum
| where DroppedResourcesPacketInRate > 0
| order by TimestampUtc asc
```

#### Step 3: VFP Flow 创建速率 (CPS)

```kql
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let cpsQuery = strcat(
    "metricNamespace('VfpPortFlowStats').",
    "metric('CreatedTotalFlowEntryInRate').",
    "dimensions('NodeId','ContainerId').",
    "samplingTypes('Sum','Max')\n",
    "| where NodeId == '", nodeId, "'"
);
evaluate geneva_metrics_request(vfpaccount, cpsQuery, starttime, endtime)
| project TimestampUtc, NodeId, ContainerId, AvgCPS=Sum, MaxCPS=Max
| order by TimestampUtc asc
| render timechart
```

#### Step 4: VFP 全类型 Drop 扫描（11 metrics 一次查完）

```kql
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let vfpaccount = 'VFP_ACCOUNT';
let nodeId = 'NODE_ID';
let makeQ = (metricName:string) {
    strcat("metricNamespace('VfpPortDropMetrics').metric('", metricName, "').dimensions('NodeId','ContainerId').samplingTypes('Sum')\n| where NodeId == '", nodeId, "'")
};
let fetch = (metricName:string) {
    evaluate geneva_metrics_request(vfpaccount, makeQ(metricName), starttime, endtime)
    | summarize Total=sum(Sum) by ContainerId
    | extend MetricName=metricName
};
union
    fetch('DroppedResourcesPacketInRate'),
    fetch('DroppedResourcesPacketOutRate'),
    fetch('DroppedAclPacketInRate'),
    fetch('DroppedAclPacketOutRate'),
    fetch('DroppedNoRuleMatchPacketInRate'),
    fetch('DroppedNoRuleMatchPacketOutRate'),
    fetch('DroppedMalformedPacketInRate'),
    fetch('DroppedMalformedPacketOutRate'),
    fetch('DroppedPendingPacketInRate'),
    fetch('DroppedPendingPacketOutRate'),
    fetch('DroppedSimulationPacketInRate')
| where Total > 0
| order by Total desc
```

#### VfpPortDropMetrics Metric 列表 & 排障速查

| Metric | 类型 | 优先级 | 典型场景 |
|--------|------|--------|----------|
| `DroppedResourcesPacketInRate` | Resource | ⭐⭐⭐ | 连接失败/Timeout/ICMP丢包 — Flow/UF/Rate limit |
| `DroppedResourcesPacketOutRate` | Resource | ⭐⭐ | 出方向 Resource drop |
| `DroppedAclPacketInRate` | ACL | ⭐⭐⭐ | NSG deny 入方向 |
| `DroppedAclPacketOutRate` | ACL | ⭐⭐⭐ | NSG deny 出方向（常见最高值，稳态=正常） |
| `DroppedNoRuleMatchPacketInRate` | Policy | ⭐⭐ | 无匹配规则 → 新部署/VFP 编程缺失 |
| `DroppedNoRuleMatchPacketOutRate` | Policy | ⭐⭐ | 同上出方向 |
| `DroppedMalformedPacketInRate` | Malformed | ⭐ | 畸形包 |
| `DroppedMalformedPacketOutRate` | Malformed | ⭐ | 同上出方向 |
| `DroppedPendingPacketInRate` | Pending | ⭐⭐ | VM 迁移/VFP mapping 未完成 |
| `DroppedPendingPacketOutRate` | Pending | ⭐⭐ | 同上出方向 |
| `DroppedSimulationPacketInRate` | Simulation | ⭐ | 测试包 |

#### 判断逻辑

| 条件 | 结论 |
|------|------|
| 所有 Drop = 0，Flow < 2M，CPS 正常 | VFP 排除 → 看 Host NIC / ToR |
| Resource Drop > 0 且吻合问题时间 | VFP 根因 → 查 Flow/CPS/Layer |
| ACL Drop 平稳无突变 | 正常 NSG deny → 非根因 |
| ACL Drop 突增吻合问题 | NSG 变更 → 查 `effective-nsg` |
| VFP 0 drop + Host NIC Log 空 + NMAgent fail | Host NIC Silent Failure → PG/迁移 |

> **误区：** ❌ Kusto 无 VfpPortCounters 表 ❌ 只看 Flow 不看 Drop ❌ 只查 Resource Drop 忽略 ACL ❌ `geneva_metrics_request()` 不支持 Host NIC (HNMDM/VNetMDM namespace 均 CE2029)

#### Host NIC Drop 查看方式（VFP 排除后下一步）

Host NIC drop **无法通过** `geneva_metrics_request()` 查询（已验证 HNMDM/VNetMDM/VfpMdm 共 13 个 namespace 全部 CE2029）。

**Azurehn 数据库 Host NIC 相关表（按适用范围）：**

| 表名 | 适用范围 | 关键字段 | 说明 |
|------|----------|----------|------|
| `GdmaBnicGlobalCounters` | 仅 **GPC** 集群 | NumOfInDiscardsNoWQE, OutTotalErrors | NIC 全局收发+丢包计数器 |
| `ManaBnicInternalCounters` | 仅 **MANA NIC** 节点 | Backpressure*, BnicHealthBit* | MANA BNIC 内部状态+背压 |
| `BackplaneMetricsCounters` | 有 **SoC** 的节点 | NumOfMissedErrorsReceived, NumOfErrors* | Backplane 层收发错误 |
| `NetDatapathPerfCounters` | 仅 **OverLake** 节点 | CounterName/CounterValue (pivot) | 数据面性能计数器 |
| `AccelnetSLI` | 发生 AccelNet 中断时 | AccelNetDisableTime, DisableDuration_Sec, RCALevel1 | ⭐ AccelNet 可用性 SLI |
| `Mlnx5FwIntermediary_v1` | Mellanox FW 事件 | EventId, Description | 固件级事件 |
| `AccelnetAgentProcessCounters` | 通用（所有集群） | CPU/内存/线程 | 仅进程健康，无 NIC drop |
| `VfpAgentProcessCounters` | 通用（所有集群） | CPU/内存/线程 | 仅进程健康，无 NIC drop |

> ⚠️ **`MlnxAdapterQosCounters` 表不存在。** 对于非 GPC、非 OverLake 的 App 集群节点，Kusto 中没有 Host NIC 丢包计数器。

**推荐查询路径：**

```kql
// Step 1: 查 AccelnetSLI — 是否发生过 AccelNet 中断（任何集群类型都可查）
cluster('azurehn').database('Azurehn').AccelnetSLI
| where IngestionTime between (datetime(START_TIME) .. datetime(END_TIME))
| where NodeId == 'NODE_ID'
| project IngestionTime, AccelNetDisableTime, ContainerId, RoleInstanceName, DisableDuration_Sec, RCALevel1, DisruptionCategory, Availability
```

```kql
// Step 2: 仅 GPC 集群 — 查 BNIC 全局丢包计数器
cluster('azurehn').database('Azurehn').GdmaBnicGlobalCounters
| where PreciseTimeStamp between (datetime(START_TIME) .. datetime(END_TIME))
| where NodeId == 'NODE_ID'
| where InTotalErrors > 0 or OutTotalErrors > 0
| project PreciseTimeStamp, NodeId, NumOfInDiscardsNoWQE, InTotalErrors, OutTotalErrors, NumOfOutGdmaErrors, NumOfOutGftErrors
```

```kql
// Step 3: 仅 OverLake 节点 — 查数据面计数器
cluster('azurehn').database('Azurehn').NetDatapathPerfCounters
| where PreciseTimeStamp between (datetime(START_TIME) .. datetime(END_TIME))
| where Tenant == 'DatapathOvl'
| where NodeId == 'NODE_ID'
| where CounterName has 'drop' or CounterName has 'error'
| summarize avg(CounterValue) by bin(PreciseTimeStamp, 5m), CounterName
```

**其他方式（当 Kusto 表无数据时）：**
1. **Geneva Portal** — 用 Network-Dashboard-VM 输出的 `PerProcessorPNICDashboard` 链接
2. **SAW** — `get-layer-counter` 或 NIC driver 统计

### Network-Dashboard-VM

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrContainerIdx = SubIdOrContainerId;
let CA=CustomerAddress;
//No permission to access fimpubameprodwestus now, so comment this on 5/29.
//let CAss=toscalar(cluster('fimpubameprodwestus.westus').database('AzureGraphMigration').LogicalNetwork_NetworkInterface 
//| where SubscriptionId == SubIdOrContainerIdx
//| where VirtualMachineArmId contains trim("_", VMName)
//| where Primary == "true"
//| distinct tostring(todynamic(PrivateIPAddress)[0])
//);
let CAss="0.0.0.0";
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| where shoeboxMdmAccountName != ""
| extend shoe = trim(" ", shoeboxMdmAccountName)
| distinct Region, shoeboxMdmAccountName=shoe);
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 2h  and PreciseTimeStamp <= endtime
| where (subscriptionId == SubIdOrContainerIdx and roleInstanceName == strcat("_", VMName)) or containerId == SubIdOrContainerIdx
//| where containerId contains ContainerId
| distinct roleInstanceName,subscriptionId, Tenant, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType=tostring(split(billingType, "|")[0]),VMSize=tostring(split(billingType, "|")[1]), Region,creationTime, DataCenterName, tenantName, availabilitySetName
| join kind=inner (cluster("vnetkusto.northcentralus").database("veritas").ContainerInformationEvent | where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime) on $left.containerId == $right.ContainerId
| join kind=leftouter cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2 on $left.nodeId == $right.NodeId
| distinct roleInstanceName, subscriptionId,Tenant, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress=tostring(split(PortId, "_")[1]), SocNodeId,DataCenterName,tenantName, availabilitySetName
//| join kind=inner (cluster('genevareference.westcentralus').database('AzureGraph').LogicalNetwork_NetworkInterface  | where SubscriptionId == SubscriptionID
// ) on $left.MACAddress == $right.MacAddress
//| distinct roleInstanceName, Tenant, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress, CA=tostring(parse_json(PrivateIPAddress)),SocNodeId,DataCenterName
| join kind=inner ShoeBoxMdm on $left.Region == $right.Region
| distinct roleInstanceName, Tenant,Tenantlower=tolower(Tenant), subscriptionId, nodeId, containerId, AvailabilityZone, virtualMachineUniqueId, OSType,VMSize, Region,creationTime, MACAddress, CA="-",SocNodeId,DataCenterName,shoeboxMdmAccountName,tenantName, availabilitySetName
//| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster //Remove this line on 10/9. 
| join kind=inner (cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() | extend Tenant=tolower(Cluster)) on $left.Tenantlower == $right.Tenant  //Add this line on 10/9. 
| extend VFPDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPDropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SupportDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend GFTDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/FpgaDashboardGft/FpgaDashboardGftv3?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FPGADashboard=strcat("https://portal.microsoftgeneva.com/s/C700B706?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend InvestigateNode=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", containerId, "&p-_ICMId=all#2f4843e6-c1e5-4564-ad27-cde71cebc7c7")
| extend NodeDash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-nodeid=v-", nodeId, "#805057f2-367d-4cb7-9986-89fbd2533f94")
| extend ASIHostNode=strcat("https://azureserviceinsights.trafficmanager.net/view/services/Azure%20Host/pages/Azure%20Host%20Node?nodeId=",nodeId,"&globalFrom=",format_datetime(starttime, 'yyyy-MM-dd'),"T",format_datetime(starttime, 'HH'), "%3A",format_datetime(starttime, 'mm'), "%3A51.000Z&globalTo=",format_datetime(endtime, 'yyyy-MM-dd'),"T",format_datetime(endtime, 'HH'), "%3A",format_datetime(endtime, 'mm'),"%3A51.000Z")
| extend NetVMA=strcat("https://aka.ms/netvma/?destValue=&pathQuery=false&sdnPath=false&showPingMesh=false&startTime=", format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "&endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH:mm:ss'), "&value=", containerId)
| extend PerVMAvailability=strcat("https://portal.microsoftgeneva.com/s/A03537E6?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VNETAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerProcessorPNICDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/PerProcessorNdisDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VMPerf=strcat("https://portal.microsoftgeneva.com/dashboard/RDOS/Shoebox/VMPerf-WithParameters?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",shoeboxMdmAccountName,"%22},{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22", virtualMachineUniqueId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPFullRule=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-rule%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend ListUnifiedFlow=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-unified-flow%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend KernaCaptureForNonOverLakeNode=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=datapath-operations&group=Kerna&operationId=Kerna&operationName=ExecuteKerna&inputMode=single&params={%22smeicmidparameter%22:%22264396857%22,%22smerunidparameter%22:%22",new_guid(), trim("_", roleInstanceName),"%22,%22smetargetsparameter%22:%22[{%5c%22TargetType%5c%22:%5c%22Node%5c%22,%5c%22TargetId%5c%22:[%5c%22",nodeId,"%5c%22],%5c%22TargetMetadata%5c%22:{%5c%22ClusterName%5c%22:%5c%22", Tenant, "%5c%22}}]%22,%22smejobspecificationparameter%22:%22[[{%5c%22type%5c%22:%5c%22host_capture%5c%22,%5c%22parameters%5c%22:{%5c%22duration_in_seconds%5c%22:60,%5c%22max_size_in_mbs%5c%22:2048,%5c%22output_name%5c%22:%5c%22host_capture_0%5c%22,%5c%22cmdline_args%5c%22:%5c%22provider%3DMicrosoft-Windows-Hyper-V-Vmswitch%20provider%3DMicrosoft-Windows-Hyper-V-Vfpext%20capture%3Dyes%20persistent%3Dyes%20report%3Ddis%20corr%3Ddis%20overwrite%3Dyes%20PacketTruncateBytes%3D300%20capturetype%3Dboth%5c%22}},{%5c%22type%5c%22:%5c%22fpga_capture%5c%22,%5c%22parameters%5c%22:{%5c%22duration_in_seconds%5c%22:60,%5c%22max_size_in_mbs%5c%22:2048,%5c%22output_name%5c%22:%5c%22fpga_capture_0%5c%22,%5c%22cmdline_args%5c%22:%5c%22-capture%20-parse%20-bytesPerPkt%20256%20-KbytesToCap%20circular%20-pcapCfg%20BOTH_NIC_TOR%20-fileName%20FPGACapture01%5c%22}},{%5c%22type%5c%22:%5c%22nvspinfo%5c%22,%5c%22parameters%5c%22:{%5c%22cmdline_args%5c%22:%5c%22-V%5c%22,%5c%22output_name%5c%22:%5c%22nvspinfo%5c%22}},{%5c%22type%5c%22:%5c%22vfpctrl%5c%22,%5c%22parameters%5c%22:{%5c%22cmdline_args%5c%22:%5c%22/list-vmswitch-port%5c%22,%5c%22output_name%5c%22:%5c%22vmswitch_ports%5c%22}},{%5c%22type%5c%22:%5c%22vfpctrl%5c%22,%5c%22parameters%5c%22:{%5c%22cmdline_args%5c%22:%5c%22/port%20External_", MACAddress, "%20/list-unified-flow%5c%22,%5c%22output_name%5c%22:%5c%22list-unified-flow%5c%22}}]]%22,%22smekernavepathparameter%22:%22orchestrationpolicy%5c%5cOaas%5c%5cVirtualEnvironments%5c%5cHostNetworking%5c%5cKerna%22}&actionEndpoint=Kerna&genevatraceguid=47e380be-c490-4ccb-ab52-8858bf881502")
| project CreationTime=creationTime,VMName=roleInstanceName, Region,NodeDash, AvailabilityZone, ClusterName=Tenant, NodeId=nodeId, ContainerID=containerId, VirtualMachineUniqueId=virtualMachineUniqueId, OSType, VMSize, CA,MACAddress,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,KernaCaptureForNonOverLakeNode, CAandMAC=strcat(CA, " ----> ", MACAddress),SocNodeId,DataCenterName,subscriptionId,tenantName, availabilitySetName
| summarize CAandMAC = replace(@"\\", "", tostring(make_list(CAandMAC))) by CreationTime, VMName, Region,AvailabilityZone, ClusterName, NodeId, ContainerID,DataCenterName,VirtualMachineUniqueId,OSType, VMSize,SocNodeId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode,NodeDash, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,KernaCaptureForNonOverLakeNode,subscriptionId,tenantName, availabilitySetName
| extend ProcessTupleOutbound=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", ClusterName, "%22,%22smenodeidparam%22:%22", NodeId, "%22,%22smecontaineridparam%22:%22", ContainerID,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22process-tuples%22,%22smevfpfilteroptionsparam%22:%22\\%226%20", CAss, "%201234%208.8.8.8%20443%20out%201\\%22%22}&actionEndpoint=Production&genevatraceguid=6138abc0-1c93-4b03-bf62-a63eaa6d9ad2")
| extend VMCRUD=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-SubscriptionID=", subscriptionId,"&p-ResourceURI=v-", trim("_", VMName), "&p-CorrelationId=v-CorrelationRequestId#d1d4e231-22ae-4d17-95f9-eecac5ed1695")
| project CreationTime,VMName, Region, AvailabilityZone, ClusterName, NodeId, SocNodeId, ContainerID, NodeDash,VirtualMachineUniqueId, OSType, VMSize,subscriptionId, CAandMAC,VFPDashBoard,VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound,KernaCaptureForNonOverLakeNode,DataCenterName,VMCRUD,tenantName, availabilitySetName
| join kind=leftouter cluster('AzureCM').database('AzureCM').LogNodeSnapshot on $left.NodeId == $right.nodeId
| summarize CAandMACs = replace(@"\\", "", tostring(make_set(CAandMAC))), availabilitySetName=tostring(make_set(availabilitySetName)),ProcessTupleOutbounds=make_set(ProcessTupleOutbound)[0], HostCaptureForNonOverLakeNode=make_set(KernaCaptureForNonOverLakeNode)[0] by CreationTime,VMName, Region, AvailabilityZone, ClusterName, NodeId, SocNodeId, ContainerID, VirtualMachineUniqueId, OSType, VMSize,VFPDashBoard,VFPDropDashBoard, DataCenterName,SupportDashBoard, DropDashBoard, GFTDashboard, FPGADashboard,InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,NodeDash,VMCRUD,subscriptionId,tenantName,NodeIP=ipAddress
| extend IsOverLake=iff(isempty(SocNodeId), "No", "Yes")
| project CreationTime,VMName, Region, AvailabilityZone,DataCenterName, ClusterName, NodeId,NodeIP, IsOverLake, SocNodeId, ContainerID, tenantName,availabilitySetName,VirtualMachineUniqueId, OSType, VMSize,subscriptionId,VMCRUD,VFPDashBoard,VFPDropDashBoard, SupportDashBoard, DropDashBoard, GFTDashboard,FPGADashboard, DriDash=InvestigateNode,NodeDash, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard, VMPerf, VFPFullRule, ListUnifiedFlow,ProcessTupleOutbounds,HostCaptureForNonOverLakeNode
| evaluate narrow()
| project Key=Column, Value
```

### VFP API Call Latency Dashboard (OverLake / SoC)

Use this dashboard to investigate **VFP API call latency, call count, and permission-level metrics** on OverLake (SoC) nodes. It surfaces per-function latency breakdowns useful for diagnosing slow VFP programming, high-latency mapping operations, or API-level bottlenecks on the SoC data path.

**Parameters to replace:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FUNCTION_NAME` | VFP API function name to filter on | `VfpUtilAddMapping` |
| `MDM_ACCOUNT` | VNetMDM MDM account for the cluster region (e.g. `VNetMDMEastUS2`) | — |
| `CLUSTER_NAME` | Cluster name (e.g. `LVL04PrdGPC08`) | — |
| `NODE_ID` | Node ID(s), comma-separated for multiple nodes | — |
| `START_TIME` / `END_TIME` | KQL datetime values for the investigation window | — |

```kql
// VFP API Call Latency Dashboard — generates a direct Geneva Portal link
// Replace FUNCTION_NAME, CLUSTER_NAME, NODE_ID, MDM_ACCOUNT, START_TIME, END_TIME
let starttime = datetime(START_TIME);
let endtime = datetime(END_TIME);
let functionName = 'FUNCTION_NAME';      // e.g. VfpUtilAddMapping
let clusterName = 'CLUSTER_NAME';        // e.g. LVL04PrdGPC08
let nodeId = 'NODE_ID';                  // comma-separated GUIDs for multiple nodes
let mdmAccount = 'MDM_ACCOUNT';          // e.g. VNetMDMEastUS2
let startunixtime = tolong(starttime - datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime - datetime(1970-01-01)) / 10000;
print VfpApiLatencyDashboard = strcat(
    "https://portal.microsoftgeneva.com/dashboard/VNetMDM/Overlake/Soc-Vfp-Api%2520Latency",
    "?overrides=[",
    "{%22query%22:%22//*[id%3D%27FunctionName%27]%22,%22key%22:%22value%22,%22replacement%22:%22", functionName, "%22},",
    "{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22", mdmAccount, "%22},",
    "{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22", clusterName, "%22},",
    "{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22", nodeId, "%22}",
    "]&globalStartTime=", startunixtime,
    "&globalEndTime=", endunixtime,
    "&pinGlobalTimeRange=true"
)
```

> **Common FunctionName values:** `VfpUtilAddMapping`, `VfpUtilDeleteMapping`, `VfpUtilUpdateMapping`, `VfpUtilLookupMapping`  
> **MDM Account lookup:** Use `cluster('azurehn').database('Azurehn').MdmVfpVnetAccountMaps() | where Cluster =~ "CLUSTER_NAME" | project VNETAccount, VfpAccount, HnMdmAccount` — `VNETAccount` = VNetMDM dashboards, `VfpAccount` = VfpMDM dashboards, `HnMdmAccount` = Host Networking MDM dashboards.

---

### 🔑 Tips: NodeId / ContainerId → Cluster → MDM Account Resolution

Use these quick-resolution queries when you only have a **NodeId** or **ContainerId** and need to find the Azure cluster name, VNetMDM account, or VfpMDM account to build dashboard URLs or run scoped queries.

> **Key gotcha:** `LogNodeSnapshot` uses `nodeId` (lowercase) — querying `NodeId` (PascalCase) returns no results. The Azure cluster name is stored in the **`Tenant`** column, **not** a `Cluster` column.

---

#### Step 1a — NodeId → Cluster (Tenant)

```kql
// Resolve NodeId to Azure cluster name (Tenant), region, and datacenter
cluster('AzureCM').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp >= ago(1d)
| where nodeId =~ "NODE_ID"                // use lowercase nodeId — PascalCase returns nothing
| project nodeId, Tenant, Region, DataCenterName, torId
| take 1
```

> **Result:** `Tenant` = Azure cluster name (e.g., `LVL04PrdGPC08`). Use this as `Cluster` in all MDM dashboard overrides.

---

#### Step 1b — ContainerId → NodeId + Cluster (Tenant)

```kql
// Resolve ContainerId to NodeId and Azure cluster name
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= ago(1d)
| where containerId =~ "CONTAINER_ID"
| project containerId, nodeId, Tenant=Cluster, Region, DataCenterName
| take 1
```

> **Note:** In `LogContainerSnapshot`, the cluster column is named `Cluster` (not `Tenant`). The value is the same Azure cluster name.

---

#### Step 2 — Cluster → VNetMDM + VfpMDM Accounts

```kql
// Resolve Azure cluster name to VNetMDM, VfpMDM, and HN MDM accounts
cluster('azurehn').database('Azurehn').MdmVfpVnetAccountMaps()
| where Cluster =~ "CLUSTER_NAME"          // e.g. LVL04PrdGPC08
| project Cluster, VNETAccount, VfpAccount, HnMdmAccount
```

| Column | Used For |
|--------|----------|
| `VNETAccount` | VNetMDM dashboards (e.g., VFP API Latency, Per-VM Availability) |
| `VfpAccount` | VfpMDM dashboards (e.g., FPGA Dashboard, PerProcessorNDIS, Drops Dashboard) |
| `HnMdmAccount` | Host Networking MDM dashboards (AccelNet, BNIC, OverLake counters) |

---

#### Combined: NodeId → Cluster → Both MDM Accounts (single query)

```kql
// One-shot: NodeId → Cluster → VNetMDM + VfpMDM accounts
cluster('AzureCM').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp >= ago(1d)
| where nodeId =~ "NODE_ID"
| take 1
| project nodeId, ClusterName=Tenant, Region, DataCenterName
| join kind=inner (
    cluster('azurehn').database('Azurehn').MdmVfpVnetAccountMaps()
) on $left.ClusterName == $right.Cluster
| project nodeId, ClusterName, Region, DataCenterName, VNETAccount, VfpAccount, HnMdmAccount
```

> **Tip:** Once you have `VNETAccount` and `VfpAccount`, you can directly use them in any `strcat()` dashboard URL builder in this file without separate lookups.
