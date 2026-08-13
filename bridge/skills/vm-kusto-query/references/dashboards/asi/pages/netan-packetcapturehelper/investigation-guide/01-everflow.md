# Everflow

> Source: **Network Analyser - PacketCaptureHelper** dashboard, chapter **Everflow** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PacketCaptureHelper-VIP-To-MuxNode-FilterGenerator-MultiRow

Cluster: `azslb.kusto.windows.net` · Database: `azslbmds` · Type: `MultiRow` · Widget: `ForEach`
Source panel: `Everflow`

```kusto
let srcPort = '0';
let dstPort = '0';
let prot = '6';
let tcpFlags='0';
let dscp='0';
let timeDuration = ago(3h);
let rings=toscalar(cluster("azslb.kusto.windows.net").database("azslbmds").DSMulticastGroupEvent
| where env_time > timeDuration
| where SegmentName != "0.0.0.0_0" and SegmentName != "::_0" and Uri has "MuxPoolManager"
| extend CidrString = replace_string(SegmentName, "_", "/")
| summarize arg_max(env_time, *) by SegmentName, Uri
| project env_cloud_name, CidrString, GroupIncarnationId, MulticastGroup
| extend Ipv4Cidr = iff(CidrString has ":", "", CidrString), Ipv6Cidr = iff(CidrString has ":", CidrString, "")
| where ipv6_is_in_range(searchVip, Ipv6Cidr) or ipv4_is_in_range(searchVip, Ipv4Cidr)
| project SlbRing = parse_csv(replace_string(GroupIncarnationId, "-azr", "-az,r"))
);
let ringsList=parse_csv(rings);
let muxNodeDetails=cluster("azurecm.kusto.windows.net").database("AzureCM").LogNodeSnapshot
| where TIMESTAMP > timeDuration and dedicatedNodeGroupName startswith 'slb-'
| extend ring2 = substring(trim(" ", dedicatedNodeGroupName), 4), cluster = tolower(Tenant)
| where dedicatedNodeGroupName in~ (ringsList) or ring2 in~ (ringsList)
| distinct nodeId, ipAddress, nodeAvailabilityState, nodeState, ring=dedicatedNodeGroupName, cluster
| join hint.strategy=broadcast kind=innerunique (cluster("Azphynet.kusto.windows.net").database("azdhmds").DeviceStatic | extend Cluster = tolower(Cluster) | project Server=DeviceName, Cluster, ServerIp = StaticIP ) on $left.ipAddress == $right.ServerIp, $left.['cluster'] == $right.Cluster
| join hint.strategy=broadcast kind=inner (cluster("Azphynet.kusto.windows.net").database("azdhmds").DeviceInterfaceLinks | project Server=StartDevice,Tor=EndDevice) on Server
| join hint.strategy=broadcast kind=inner (cluster("Azphynet.kusto.windows.net").database("azdhmds").DeviceStatic | project Tor=DeviceName, TorIp=StaticIP ) on Tor
| project nodeId, nodeIp=ipAddress, nodeAvailabilityState, nodeState, ring, tor=Tor, torIp=TorIp, Cluster
| order by tor asc;
let nodeIps = muxNodeDetails
| summarize by ipAddress=nodeIp
| extend b1 = tostring(split(ipAddress, '.')[0]), b2 = tostring(split(ipAddress, '.')[1]), b3 = tostring(split(ipAddress, '.')[2])
;
let Summary32bits = nodeIps
| project SrcIpPrefix = strcat(ipAddress, '/32'), joinMe=1, bit=32 //, DstIpPrefix = dstIpPrefix, SrcPort = srcPort, DstPort=dstPort,Protocol = prot, TcpFlags =tcpFlags, Dscp = dscp
;
let Summary24bits = nodeIps
| summarize by b1, b2, b3
| project SrcIpPrefix = strcat_array(pack_array(b1,b2,b3,'0/24'),'.'), joinMe=1, bit=24 //, DstIpPrefix = dstIpPrefix, SrcPort = srcPort, DstPort=dstPort,Protocol = prot, TcpFlags =tcpFlags, Dscp = dscp
;
let Summary16bits = nodeIps
| summarize by b1, b2
| project SrcIpPrefix = strcat_array(pack_array(b1,b2,'0/16'),'.'), joinMe=1, bit=16 //, DstIpPrefix = dstIpPrefix, SrcPort = srcPort, DstPort=dstPort,Protocol = prot, TcpFlags =tcpFlags, Dscp = dscp
;
let muxNodeFilter=
Summary16bits | union Summary24bits | union Summary32bits
| extend DstIpPrefix = dstIpPrefix, SrcPort = srcPort, DstPort=dstPort,Protocol = prot, TcpFlags = tcpFlags, Dscp = dscp
| summarize EverFlowSummary=make_set(bag_pack_columns(SrcIpPrefix, DstIpPrefix, SrcPort, DstPort, Protocol, TcpFlags, Dscp)) by AggregationBits=bit
| order by AggregationBits asc
| extend dataPackDynamic=EverFlowSummary, moreData=bag_pack('count',array_length(EverFlowSummary),'aggregationBits',AggregationBits), joinMe=1, source='node', dataPackString=''
;
let muxTorList=muxNodeDetails | summarize torList=make_set(tor)
| project dataPackString = strcat_array(torList,','), joinMe=1, source='tor', dataPackDynamic=todynamic(''), moreData=todynamic('')
;
let finalData=
muxNodeFilter | union muxTorList
;
finalData
| project source, dataPackString, dataPackDynamic, moreData
```

**Params:** `{searchVip}`, `{dstIpPrefix}`

**Signal filters seen in KQL:** `SegmentName != "0.0.0.0_0"`

---
