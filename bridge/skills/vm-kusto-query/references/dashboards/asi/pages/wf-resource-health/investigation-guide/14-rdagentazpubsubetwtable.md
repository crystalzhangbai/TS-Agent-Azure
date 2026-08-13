# RdAgentAzPubSubEtwTable

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **RdAgentAzPubSubEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents annotations emitted from HostAgent to AzPubSub

### RdAgentAzPubSubEtwTable

_Widget purpose:_ Represents annotations emitted from HostAgent to AzPubSub

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `RdAgentAzPubSubEtwTable > Represents annotations emitted from HostAgent to AzPubSub`

```kusto
RdAgentAzPubSubEtwTable
| where PreciseTimeStamp between (queryFrom..queryTo)
| where NodeId == nodeId
| where Message contains containerId
| project PreciseTimeStamp, Message, Level
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---
