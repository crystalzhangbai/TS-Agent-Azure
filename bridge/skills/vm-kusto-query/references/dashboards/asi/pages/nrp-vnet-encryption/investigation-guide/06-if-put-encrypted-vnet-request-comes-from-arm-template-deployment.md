# If Put Encrypted Vnet Request Comes from ARM Template Deployment

> Source: **NRP - Vnet Encryption** dashboard, chapter **If Put Encrypted Vnet Request Comes from ARM Template Deployment** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ifFromARM

_Widget purpose:_ If Put Encrypted Vnet Request Comes from ARM Template Deployment

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`
Source panel: `If Put Encrypted Vnet Request Comes from ARM Template Deployment`

```kusto
let opidLst=WriteOperationResponseEtwEvent
| where (PreciseTimeStamp between (startTime .. endTime))
| where OperationName == "PutVirtualNetworkOperation"
| where Request contains ```"encryption":{"enabled":true,```
| distinct OperationId;
let rgname = QosEtwEvent
| where TIMESTAMP between (startTime .. endTime)
| where OperationName contains "preflight"
| distinct ResourceGroup;
QosEtwEvent
| where (PreciseTimeStamp between (startTime .. endTime))
| where OperationId in (opidLst)
| extend ifRequestFromARMTemplate = ResourceGroup in (rgname)
| project Region, PreciseTimeStamp, SubscriptionId, ifRequestFromARMTemplate, ResourceGroup, CorrelationRequestId, OperationId, Success, ErrorCode
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutVirtualNetworkOperation"` · `OperationName contains "preflight"`

---
