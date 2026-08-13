# Tenant Logs

> Source: **Aztec — Tenant** dashboard, chapter **Tenant Logs** (4 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Tenant Logs

### Query all TMMgmtNodeEventsEtwTable in the one tenant

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Table`
Source panel: `Tenant Logs > Tenant Logs > Node Events > Node Events`

```kusto
let slbNodes = MycroftContainerHealthSnapshot 
| where  PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| distinct NodeId;
cluster('azcore.centralus').database('Fc').TMMgmtNodeEventsEtwTable
| where  PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId in (slbNodes)
| project PreciseTimeStamp, Tenant, NodeId, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### TenantAuditEvents

_Widget purpose:_ Audit Events from TMMgmtTenantEventsEtwTable

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant Logs > Tenant Logs > Tenant Audit Events > Tenant Audit Events > Audit Events from TMMgmtTenantEventsEtwTable`

```kusto
TMMgmtTenantEventsEtwTable
| where PreciseTimeStamp between (global_startTime..global_endTime)
| where TenantName == tenantName
| project PreciseTimeStamp,Tenant, Message
| where Message contains "AUDIT"
```

**Params:** `{tenantName}`

**Signal filters seen in KQL:** `Message contains "AUDIT"`

---

### Query TMMgmtTenantEventsEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant Logs > Tenant Logs > Tenant Events > Tenant Events`

```kusto
TMMgmtTenantEventsEtwTable
| where  PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == queryTenantName  
| project PreciseTimeStamp, Tenant, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Tenant Logs

_Widget purpose:_ Tenant Logs from TMMgmtNodeEventsEtwTable + TMMgmtTenantEventsEtwTable

Cluster: `azcsupfollower` · Database: `azurecm` · Type: `Table`
Source panel: `Tenant Logs > Tenant Logs > Tenant Events and Node Events > Tenant Events and Node Events > Tenant Logs from TMMgmtNodeEventsEtwTable + TMMgmtTenantEventsEtwTable`

```kusto
let slbNodes = LogContainerSnapshot 
| where  PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct nodeId;
let nodeEvents = TMMgmtNodeEventsEtwTable 
| where  PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId in (slbNodes)
| project PreciseTimeStamp, SourceTable = "TMMgmtNodeEventsEtwTable", Tenant, NodeId, Message;
let slbAuditEvents = TMMgmtTenantEventsEtwTable
| where  PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == queryTenantName  
| project PreciseTimeStamp, SourceTable = "TMMgmtTenantEventsEtwTable", Tenant, NodeId = "" , Message;
union nodeEvents, slbAuditEvents 
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---
