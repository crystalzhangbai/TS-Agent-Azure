# AzSM Events & Traces

> Source: **Aztec — Tenant** dashboard, chapter **AzSM Events & Traces** (8 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AzSM Events & Traces

### Query AzSMExceptionsEvents

_Widget purpose:_ AzSMExceptionsEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM Exceptions Events > AzSM Exceptions Events > AzSMExceptionsEvents`

```kusto
AzSMExceptionsEvents
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, Tenant, applicationName, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AzSMServiceTracesEvents

_Widget purpose:_ AzSMServiceTracesEvents 

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM Service Traces Events > AzSM Service Traces Events > AzSMServiceTracesEvents `

```kusto
AzSMServiceTracesEvents
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where message contains queryTenantName
| project PreciseTimeStamp, message, applicationName, Cluster, Tenant
| extend level = case(
    message has_any ("error", "fail", "exception"), "Error",
    message has_any ("InProgress", "in progress", "stuck", "timeout"), "Warning",    
    "Info"
)
| extend level = iif(message contains @"PacketId='Error'", "Info", level)
| where queryFilterValue == "All" or level != "Info"
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryFilterValue}`

**Signal filters seen in KQL:** `queryFilterValue == "All"`

---

### FilterMessages

_Widget purpose:_ AzSMServiceTracesEvents 

Cluster: `azurecm` · Database: `AzureCM` · Type: `Filter` · Widget: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM Service Traces Events > AzSM Service Traces Events > AzSMServiceTracesEvents `

```kusto
datatable (Value:string, Description:string)
[
    "Critical", "Critical Messages/Errors/Warnings/Exceptions/Failures (default)",
    "All", "All Logs/Events"
]
```

---

### Tenant AzSM State Machine Events

_Widget purpose:_ AzSMTenantStatemachineEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > AzSMTenantStatemachineEvents`

```kusto
AzSMTenantStatemachineEvents
| where PreciseTimeStamp between(queryFrom .. queryTo) 
| where tenantName == queryTenantName
| extend level = case(
    message has_any ("error", "exception", "fault"), "Error",
    message contains ("fail"), "Error",
    message contains ("not in goal state"), "Error",
    message contains ("Not received any packets for TenantUpdateState result.Returning"), "Error",
    // message has_any ("InProgress", "in progress", "stuck", "timeout"), "Warning",
    message has_any ("InProgress", "stuck", "timeout"), "Warning",    
    "Info"
)
| where queryFilterValue == "All" or level != "Info"
| project PreciseTimeStamp, Tenant, Cluster, applicationName, stateMachineId, stateMachineState, message, level
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`, `{queryFilterValue}`

**Signal filters seen in KQL:** `queryFilterValue == "All"`

---

### FilterMessages

_Widget purpose:_ AzSMTenantStatemachineEvents

Cluster: `azurecm` · Database: `AzureCM` · Type: `Filter` · Widget: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > AzSMTenantStatemachineEvents`

```kusto
datatable (Value:string, Description:string)
[
    "Critical", "Critical Messages/Errors/Warnings/Exceptions/Failures (default)",
    "All", "All Logs/Events"
]
```

---

### Tenant AzSM State Machine Events timeline

_Widget purpose:_ state machine timeline

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Timeline`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > state machine timeline`

```kusto
AzSMTenantStatemachineEvents
| where PreciseTimeStamp between(queryFrom .. queryTo) 
| where tenantName == queryTenantName
| sort by tenantName 
| sort by PreciseTimeStamp asc
| where tenantName == queryTenantName
// | extend level = case(
//     message has_any ("error", "exception", "fault"), "Error",
//     message contains ("fail"), "Error",
//     message contains ("not in goal state"), "Error",
//     message contains ("Not received any packets for TenantUpdateState result.Returning"), "Error",
//     // message has_any ("InProgress", "in progress", "stuck", "timeout"), "Warning",
//     message has_any ("InProgress", "stuck", "timeout"), "Warning",    
//     "Info"
// )
//| where queryFilterValue == "All" or level != "Info"
//| project PreciseTimeStamp, Tenant, Cluster, applicationName, stateMachineId, stateMachineState, message, level
| extend nextState = next(stateMachineState)
| extend prevState = prev(stateMachineState)
| where nextState != prevState
| where prevState == stateMachineState
| where isnotempty(prevState)
// | project PreciseTimeStamp, stateMachineState, message, applicationName, prevState, prev(PreciseTimeStamp)
| project Content = stateMachineState, StartTime = PreciseTimeStamp, EndTime = next(PreciseTimeStamp), GroupBy = stateMachineId
| sort by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

**Signal filters seen in KQL:** `queryFilterValue == "All"`

---

### Tenant AzSM Events

_Widget purpose:_ Tenant Events

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM Tenant Events > AzSM Tenant Events > Tenant Events`

```kusto
AzSMTenantEvents
| where PreciseTimeStamp between(queryFrom..queryTo)
| where tenantName == queryTenantName
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Query AzSMUpdateTenantEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `AzSM Events & Traces > AzSM Events & Traces > AzSM Update Tenant Events > AzSM Update Tenant Events`

```kusto
AzSMUpdateTenantEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName  == queryTenantName
| project PreciseTimeStamp,  Tenant, serviceInstanceId, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
