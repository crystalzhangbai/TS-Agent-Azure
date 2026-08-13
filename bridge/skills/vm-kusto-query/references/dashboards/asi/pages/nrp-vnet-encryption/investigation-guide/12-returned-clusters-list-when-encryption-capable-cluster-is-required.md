# Returned Clusters List when Encryption Capable Cluster is Required

> Source: **NRP - Vnet Encryption** dashboard, chapter **Returned Clusters List when Encryption Capable Cluster is Required** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### clustersList

_Widget purpose:_ Returned Clusters List when Encryption Capable Cluster is Required

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `Returned Clusters List when Encryption Capable Cluster is Required`

```kusto
let operationName = "GetTenantClustersOperation"; 
WriteOperationResponseEtwEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where OperationName == operationName 
| where OperationId in (
    (FrontendOperationEtwEvent 
        | where PreciseTimeStamp between (startTime .. endTime)
        | where OperationName == operationName 
        | parse Message with "encryptionRequired: " ifEncryptionRequired 
        | where ifEncryptionRequired == "True"
        | distinct OperationId)
)
| project Region, PreciseTimeStamp, SubscriptionId, OperationId, CorrelationRequestId, Response
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ifEncryptionRequired == "True"`

---
