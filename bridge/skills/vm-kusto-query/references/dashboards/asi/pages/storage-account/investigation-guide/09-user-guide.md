# User Guide

> Source: **Storage Account Investigation Guide** dashboard, chapter **User Guide** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get_ServiceID

_Widget purpose:_ User Guide

Cluster: `azcore.centralus` · Database: `Xstore` · Type: `Single` · Widget: `Markdown`
Source panel: `User Guide`

```kusto
// Any cluster / Database can be used - using the same as to get Redis details - azcore.centralus / Xstore
print queryServiceId = queryServiceId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryServiceId}`

---
