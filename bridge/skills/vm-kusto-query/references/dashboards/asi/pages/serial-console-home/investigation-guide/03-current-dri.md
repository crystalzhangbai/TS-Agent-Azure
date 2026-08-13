# Current DRI

> Source: **Serial Console Home** dashboard, chapter **Current DRI** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Current On-Call

_Widget purpose:_ Current DRI

Cluster: `icmcluster` · Database: `DirectoryServicePROD` · Type: `Single` · Widget: `EventDetails`
Source panel: `Current DRI`

```kusto
OnCallNow(86021)
```

**Params:** `{queryFrom}`, `{queryTo}`

---
