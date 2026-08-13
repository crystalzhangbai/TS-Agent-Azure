# KyberGHSAnnotationEmissionEvent

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberGHSAnnotationEmissionEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents the annotations sent from Kyber to Geneva Health

### KyberGHSAnnotationEmissionEvent

_Widget purpose:_ Represents the annotations sent from Kyber to Geneva Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Table`
Source panel: `KyberGHSAnnotationEmissionEvent > Represents the annotations sent from Kyber to Geneva Health`

```kusto
KyberGHSAnnotationEmissionEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where * contains containerid
| project OccurredTime, AnnotationName, AnnotationMetadata, SourceNamespace, SourceServiceName, Destination
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerid}`

---
