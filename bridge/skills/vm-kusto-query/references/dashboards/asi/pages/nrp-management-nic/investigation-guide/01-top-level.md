# (top-level)

> Source: **NRP - Management Nic** dashboard, chapter **(top-level)** (8 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### F5 Enic Error Summary

_Widget purpose:_ Error Summary

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(90d)
| where OperationName == "PutNicOperation"
| where Request contains "faf1f7e1-8522-498c-a7f9-6a7f1a17f873"
| where Request contains "\"nictype\": \"Elastic\""
| where ErrorCode != ""
| summarize count() by OperationName, Region, SubscriptionId, ErrorCode
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "faf1f7e1-8522-498c-a7f9-6a7f1a17f873"` · `Request contains "\"`

---

### NIC - Notifications fetched

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`

```kusto
BillingManagerEtwEvent
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Message contains "Fetching elastic network interface" and Message contains "from parent network interface"
| where Tenant == tenantName
| summarize count() by bin(PreciseTimeStamp, 1h)
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `Message contains "Fetching elastic network interface"`

---

### NIC- Notifications started being processed

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`

```kusto
BillingManagerEtwEvent 
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where EventCode == "NetworkInterfaceBillingEntityStartedBeingProcessed"
| where Tenant == tenantName
| summarize count() by bin(PreciseTimeStamp, 1h)
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `EventCode == "NetworkInterfaceBillingEntityStartedBeingProcessed"`

---

### NIC- Notifications Processed

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`

```kusto
BillingManagerEtwEvent 
| where PreciseTimeStamp > ago(1d)
| where EventCode == "NetworkInterfaceBillingEntityProcessed"
| where Tenant == tenantName
| summarize count() by bin(PreciseTimeStamp, 1h)
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `EventCode == "NetworkInterfaceBillingEntityProcessed"`

---

### NIC- Create or Update

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`

```kusto
BillingManagerEtwEvent
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where EventCode == "NetworkInterfaceBillingEntityCreatedOrUpdated"
| where Tenant == tenantName
| summarize count() by bin(PreciseTimeStamp, 1h)
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `EventCode == "NetworkInterfaceBillingEntityCreatedOrUpdated"`

---

### NIC - Delete

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`

```kusto
BillingManagerEtwEvent 
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where EventCode == "NetworkInterfaceBillingEntityDeleted"
| where Tenant == tenantName
| summarize count() by bin(PreciseTimeStamp, 1h)
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `EventCode == "NetworkInterfaceBillingEntityDeleted"`

---

###  NIC- Resource not exist but entry not deleted2

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
BillingManagerEtwEvent 
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Tenant == tenantName
| where Message contains "Failed to retrieve the ParentNic information for networkInterfaceRef" or Message contains "The enic id passed to generate URI in NetworkInterfaceBillingEntity is invalid "
| project PreciseTimeStamp, Message, EventCode, CorrelationRequestId, OperationId, Tenant, SourceAssemblyFileVersion
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `Message contains "Failed to retrieve the ParentNic information for networkInterfaceRef"`

---

### invalidEnic

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Tenant == tenantName
| where Message contains "The enic id passed to generate URI in TenantOperation.cs is invalid" or Message contains "The enic id passed to generate URI in DeleteNicOperation.cs is invalid" or Message contains "The enic id passed to generate URI in BillingManager.cs is invalid"
| project PreciseTimeStamp, Message, EventCode
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`

**Signal filters seen in KQL:** `Message contains "The enic id passed to generate URI in TenantOperation.cs is invalid"`

---
