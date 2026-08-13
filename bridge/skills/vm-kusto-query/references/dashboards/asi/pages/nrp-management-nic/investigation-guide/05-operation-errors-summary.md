# Operation Errors Summary

> Source: **NRP - Management Nic** dashboard, chapter **Operation Errors Summary** (3 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Elastic Nic Create/Update Error Summarize

### ElasticNic Query

_Widget purpose:_ Elastic Nic Create/Update Error Summarize

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Operation Errors Summary > Elastic Nic Create/Update Error Summarize`

```kusto
WriteOperationResponseEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationName == "PutNicOperation"
| where Request contains "\"nictype\": \"Elastic\""
| where ErrorCode != ""
| summarize count() by OperationName, Region, SubscriptionId, ErrorCode
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## Parent Nic Create/Update Error Summarize

### Parent Nic

_Widget purpose:_ Parent Nic Create/Update Error Summarize

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Operation Errors Summary > Parent Nic Create/Update Error Summarize`

```kusto
WriteOperationResponseEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationName == "PutNicOperation"
| where Request contains "\"elasticNetworkInterfaceLinks\""
| where ErrorCode != ""
| summarize count() by OperationName, Region, SubscriptionId, ErrorCode
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## VMSS with Mgmt Nic Config

### VMSS with Mgmt Nic

_Widget purpose:_ VMSS with Mgmt Nic Config

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Operation Errors Summary > VMSS with Mgmt Nic Config`

```kusto
WriteOperationResponseEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationName == "PutVMScaleSetOperation" or OperationName == "ValidateVMScaleSetOperation"
| where Request contains "\"elasticNetworkInterfaceLinkConfigurations\""
| where ErrorCode != ""
| summarize count() by OperationName, Region, SubscriptionId, ErrorCode
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `Request contains "\"`

---
