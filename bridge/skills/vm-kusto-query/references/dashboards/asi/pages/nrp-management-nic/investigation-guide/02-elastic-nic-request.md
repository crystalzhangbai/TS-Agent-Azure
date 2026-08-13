# Elastic Nic Request

> Source: **NRP - Management Nic** dashboard, chapter **Elastic Nic Request** (3 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Elastic Nic Usage

### Enic Change Distibution

_Widget purpose:_ Elastic Nic Usage

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Elastic Nic Request > Elastic Nic Usage`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(5d)
| where OperationName == "PutNicOperation"
| where Request contains "\"nictype\": \"Elastic\""
| summarize uc = count() by OperationName, Region, bin(TIMESTAMP, 1h)
| summarize UpdateCount = sum(uc)/1.0 by OperationName, Region, bin(TIMESTAMP, 5m)
| project TIMESTAMP, UpdateCount, Region
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## Parent Nic Usage

### Parent Nic Usage

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Elastic Nic Request > Parent Nic Usage`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(5d)
| where OperationName == "PutNicOperation"
| where Request contains "\"elasticNetworkInterfaceLinks\""
| summarize uc = count() by OperationName, Region, bin(TIMESTAMP, 1h)
| summarize UpdateCount = sum(uc)/1.0 by OperationName, Region, bin(TIMESTAMP, 1h)
| project TIMESTAMP, UpdateCount, Region
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## VMSS Enic Request

### VMSS Enic Hourly Summarize

_Widget purpose:_ VMSS Enic Request

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Elastic Nic Request > VMSS Enic Request`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(8d)
| where OperationName == "PutVMScaleSetOperation" or OperationName == "ValidateVMScaleSetOperation"
| where Request contains "\"elasticNetworkInterfaceLinkConfigurations\""
| summarize uc = count() by OperationName, Region, bin(TIMESTAMP, 1h)
| summarize UpdateCount = sum(uc)/1.0 by OperationName, Region, bin(TIMESTAMP, 5m)
| project TIMESTAMP, UpdateCount, Region
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `Request contains "\"`

---
