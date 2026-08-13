# F5 Network

> Source: **NRP - Management Nic** dashboard, chapter **F5 Network** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Enic Usage

### F5 Enic Usage

_Widget purpose:_ Enic Usage

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `F5 Network > Enic Usage`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(90d)
| where OperationName == "PutNicOperation"
| where Request contains "\"nictype\": \"Elastic\""
| where Request contains "faf1f7e1-8522-498c-a7f9-6a7f1a17f873" //Lftr app id
| summarize uc = count() by ResourceName, bin(TIMESTAMP, 1d)
| summarize UpdateCount = sum(uc)/1.0 by ResourceName, bin(TIMESTAMP, 1d)
| project TIMESTAMP, UpdateCount
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"` · `Request contains "faf1f7e1-8522-498c-a7f9-6a7f1a17f873"`

---
