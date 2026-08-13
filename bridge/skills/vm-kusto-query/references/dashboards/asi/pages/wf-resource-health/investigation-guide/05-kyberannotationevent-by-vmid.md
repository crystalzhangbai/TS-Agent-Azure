# KyberAnnotationEvent by VmId

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberAnnotationEvent by VmId** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents the annotations that Kyber receives from AzPubSub - by the vmid

### kyberannotationbyvmid

_Widget purpose:_ Represents the annotations that Kyber receives from AzPubSub - by the vmid

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `KyberAnnotationEvent by VmId > Represents the annotations that Kyber receives from AzPubSub - by the vmid`

```kusto
KyberAnnotationEvent
| where Headers contains queryvmid
| where PreciseTimeStamp between (queryFrom..queryTo) 
| project PreciseTimeStamp, Cluster, AnnotationName, Headers;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvmid}`

---
