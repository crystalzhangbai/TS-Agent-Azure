# Cleanup

> Source: **Aztec — Tenant** dashboard, chapter **Cleanup** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Cleanup

### Tenant AzSM Cleanup Events

_Widget purpose:_ AzSM Cleanup Events

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `Cleanup > Cleanup > AzSM Cleanup Events`

```kusto
AzSMTenantCleanupEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName == queryTenantName
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Query FRIC from RnmOperationEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `Cleanup > Cleanup > Formatted FRIC from RnmOperationEvents`

```kusto
RnmOperationEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp,message
| order by PreciseTimeStamp asc
| where message startswith "Successfully updated fabric role instances containers in RNM for tenant"
| extend UpdatedFC = extract_all(@"FabricId: (\w+), NetworkServiceInstanceId: ([-\w]+), RoleInstanceName: ([-\w]+), .*State: ([[:alpha:]]+),", message)
| mv-expand UpdatedFC
| extend jsonUpdatedFC = parse_json(tostring(UpdatedFC))
| extend FabricIds= tostring(jsonUpdatedFC[0]) 
| extend NetworkServiceInstanceId= tostring(jsonUpdatedFC[1]) 
| extend RoleInstanceName= tostring(jsonUpdatedFC[2]) 
| extend State= tostring(jsonUpdatedFC[3])
//| project-away  message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

**Signal filters seen in KQL:** `message startswith "Successfully updated fabric role instances containers in RNM for tenant"`

---

### Query LogRoleInstanceCleanupEvent by TenantName

_Widget purpose:_ LogRoleInstanceCleanupEvent

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Cleanup > Cleanup > LogRoleInstanceCleanupEvent`

```kusto
LogRoleInstanceCleanupEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, roleInstanceName, containerId, isContainerCleanupPending, isNetworkReleasePending, isLeaseReversalPending, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Rnm Operation Events

_Widget purpose:_ RnmOperationEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `Cleanup > Cleanup > RnmOperationEvents > RnmOperationEvents`

```kusto
RnmOperationEvents
| where PreciseTimeStamp between(queryFrom .. queryTo) 
| where tenantName == queryTenantName
| project PreciseTimeStamp,message
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Tenant Cleanup Events

Cluster: `azcsupfollower` · Database: `azurecm` · Type: `Table`
Source panel: `Cleanup > Cleanup > Tenant Cleanup Events`

```kusto
LogTenantCleanupEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName == queryTenantName
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---
