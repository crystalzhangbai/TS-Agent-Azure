# Get Tenant Cluster Request

> Source: **NRP - Vnet Encryption** dashboard, chapter **Get Tenant Cluster Request** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### IfEncryptionRequiredInGetTenantCluster

_Widget purpose:_ Get Tenant Cluster Request

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Get Tenant Cluster Request`

```kusto
let operationName = "GetTenantClustersOperation"; 
FrontendOperationEtwEvent 
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
// | where SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where OperationName == operationName 
| where Message contains "encryptionRequired" 
| parse Message with "encryptionRequired: " ifEncryptionRequired 
| project Region, TIMESTAMP, SubscriptionId, CorrelationRequestId, ifEncryptionRequired
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `Message contains "encryptionRequired"`

---
