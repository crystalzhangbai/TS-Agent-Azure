# (top-level)

> Source: **NodeService - NodeCapabilitiesService** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### GRIP NodeCapabilitiesService Jobs

Cluster: `pubsubinfra.eastus2.kusto.windows.net` · Database: `PubSubInfraLogs` · Type: `Table`

```kusto
cluster('pubsubinfra.eastus2.kusto.windows.net').database('PubSubInfraLogs').GripProducer
| where Key == NodeId
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| where Service contains "NodeCapabilities"
| project PreciseTimeStamp, PayloadLower=tolower(Payload)
| extend CriticalServicesUp=parse_json(PayloadLower).criticalservicesup, NodeCapabilities=parse_json(PayloadLower).nodecapabilities_
| project-away PayloadLower
| sort by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{NodeId}`

**Signal filters seen in KQL:** `Service contains "NodeCapabilities"`

---
