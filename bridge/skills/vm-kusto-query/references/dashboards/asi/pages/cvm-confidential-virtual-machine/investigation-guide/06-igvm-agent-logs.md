# IGVM Agent Logs

> Source: **Confidential Virtual Machines - Confidential Virtual Machine** dashboard, chapter **IGVM Agent Logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### IGVM Agent Logs

Cluster: `https://azcore.centralus.kusto.windows.net/` · Database: `acccvmtmgeneva` · Type: `Table`
Source panel: `IGVM Agent Logs`

```kusto
Log
| where env_time between (queryFrom .. queryTo)
| where tagId in~ (queryContainers)
| sort by seq_number asc 
| project Level, Timestamp = env_time, RoleInstance, az_node_id, vm_unique_id, ContainerId = tagId, Message = body
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainers}`

---
