# Get Expected Nic Flag

> Source: **NRP - Vnet Encryption** dashboard, chapter **Get Expected Nic Flag** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Expected Nic Flag

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Get Expected Nic Flag`

```kusto
FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
// | where SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where OperationName == "AllocateVirtualMachinesOperation"
| where Message contains "vnet encryption enabled: " and Message contains "vm size capable of encryption: "
| parse Message with "goal nic id: " nicId ", vnet encryption enabled: " encryptionStatus ", vm size capable of encryption: " vmSizeCapability ", expected VnetEncryptionSupported flag: " nicFlag
| project TIMESTAMP, OperationId, nicId, encryptionStatus, vmSizeCapability, nicFlag
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `OperationName == "AllocateVirtualMachinesOperation"` · `Message contains "vnet encryption enabled: "`

---
