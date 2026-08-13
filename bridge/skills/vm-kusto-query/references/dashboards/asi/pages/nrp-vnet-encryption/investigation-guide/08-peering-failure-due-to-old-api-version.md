# Peering Failure Due To Old Api Version

> Source: **NRP - Vnet Encryption** dashboard, chapter **Peering Failure Due To Old Api Version** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PeeringFailureDueToOldApi

_Widget purpose:_ Peering Failure Due To Old Api Version

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `Peering Failure Due To Old Api Version`

```kusto
let EncryptedRemoteVnet = 
FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
// | where SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where OperationName == "PutVirtualNetworkPeeringOperation"
| where Message contains "has encryption status" and Message contains "with enforcenment policy"
| distinct OperationId;
WriteOperationResponseEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationName == "PutVirtualNetworkPeeringOperation"
| where Response !contains "remoteVirtualNetworkEncryption"
| where OperationId in (EncryptedRemoteVnet)
| extend failedDueToOldApiVersion = todatetime(ApiVersion) < todatetime("2020-11-01")
| project PreciseTimeStamp, failedDueToOldApiVersion, ApiVersion, OperationId
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `OperationName == "PutVirtualNetworkPeeringOperation"` · `Message contains "has encryption status"`

---
