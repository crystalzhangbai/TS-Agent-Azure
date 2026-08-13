# AgentNfcHttpDownloadFileEtwTable

> Source: **NodeService - Peregrine_ContainerEvents** dashboard, chapter **AgentNfcHttpDownloadFileEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AgentNfcHttpDownloadFileEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `AgentNfcHttpDownloadFileEtwTable`

```kusto
let nodeId = NodeServiceEventEtwTable
| where ScopeIdentifier == containerId
| take 1
| project NodeId;
AgentNfcHttpDownloadFileEtwTable
| where PreciseTimeStamp between(queryFrom..queryTo)
| where NodeId in (nodeId)
| where Url contains "|/"
| project PreciseTimeStamp, Url, StatusCode
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

**Signal filters seen in KQL:** `Url contains "|/"`

---
