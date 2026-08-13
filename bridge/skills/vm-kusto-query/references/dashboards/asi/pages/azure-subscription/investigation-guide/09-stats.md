# Stats

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Stats** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Total VMs

### Azure Host Subscription VMs Timeline

_Widget purpose:_ Total VMs

Cluster: `AzureCM` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Stats > Total VMs`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo) and subscriptionId == subId 
| summarize TotalVMs = dcount(containerId) by bin(PreciseTimeStamp, 2h)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`

---

## VM Sizes

### Azure Host Subscriptions VMs by Type

_Widget purpose:_ VM Sizes

Cluster: `AzureCM` · Database: `AzureCM` · Type: `CategoryChart`
Source panel: `Stats > VM Sizes`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo) and subscriptionId == subId
| summarize TotalVMs = dcount(containerId) by VMSize = containerType
| sort by TotalVMs desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`

---
