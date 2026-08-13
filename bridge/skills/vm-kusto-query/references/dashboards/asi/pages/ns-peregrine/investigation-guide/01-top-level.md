# (top-level)

> Source: **NodeService - NodeService_Peregrine** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### WillBePublishesToMadariFromAzCiM

Cluster: `https://azcim-centralus.centralus.kusto.windows.net` · Database: `AZCIM` · Type: `Timeline`

```kusto
AzCiMContainerWillBe
| where PhysicalContainerId == containerId
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| sort by PreciseTimeStamp asc
| parse WillBe with '{"revision":' Revision ',' * '"state":"' State '",' *
| project PreciseTimeStamp, Revision, State, WillBe
| serialize 
| where prev(State) != State
| project Table="WillBePublishesToMadari",
          StartTime=PreciseTimeStamp, 
          Content=case(isempty(Revision), "Deleted",
                       State),
          Tooltip=case(isempty(Revision), "Deleted",
                       strcat("Revision=", Revision)),
          WillBe
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### WillBeReceiptsFromMadari

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceMadariEventsEtwTable
| where RelativePath == strcat("/containers/", containerId)
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| where Operation == "MadariNotificationCallback"
| project Table="WillBeReceiptsFromMadari",
          StartTime=PreciseTimeStamp,
          Content=tostring(MadariVersion),
          Tooltip=strcat(Message, " MadariVersion=", MadariVersion)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

**Signal filters seen in KQL:** `Operation == "MadariNotificationCallback"`

---

### ContainerWorkflowBlocked

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceEventEtwTable
| where Message contains containerId
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| where Message contains "Overpacking" or Message contains "Container workflow blocked"
| sort by PreciseTimeStamp asc
| parse Message with * "overpackedCaseReason=" OverpackedCaseReason
| parse Message with * "Container workflow blocked: " WorkflowBlockedReason "." *
| parse Message with * "EscalateTo: " EscalateTo "." *
| project Table="OverpackingTable",
          StartTime=PreciseTimeStamp,
          Content=case(OverpackedCaseReason != "", OverpackedCaseReason,
                       WorkflowBlockedReason)
| summarize min(StartTime), max(StartTime), count() by Content
| project StartTime=min_StartTime,
          EndTime=max_StartTime,
          Content,
          Tooltip=tostring(count_),
          GroupBy=Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

**Signal filters seen in KQL:** `Message contains "Overpacking"`

---
