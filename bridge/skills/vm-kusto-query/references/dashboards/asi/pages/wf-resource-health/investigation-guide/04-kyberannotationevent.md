# KyberAnnotationEvent

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberAnnotationEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents the annotations that Kyber receives from AzPubSub - by the containerid

### KyberAnnotationEvent

_Widget purpose:_ Represents the annotations that Kyber receives from AzPubSub - by the containerid

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Table`
Source panel: `KyberAnnotationEvent > Represents the annotations that Kyber receives from AzPubSub - by the containerid`

```kusto
KyberAnnotationEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where * contains containerId
| project OccurredTime, AnnotationName, AnnotationMetadata, ResourceIdentityMetadata, SourceServiceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
