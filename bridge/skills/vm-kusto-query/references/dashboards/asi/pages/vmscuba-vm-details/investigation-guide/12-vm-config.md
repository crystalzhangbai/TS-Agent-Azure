# VM Config

> Source: **VM Scuba - VM Details** dashboard, chapter **VM Config** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-VMSummary

_Widget purpose:_ VM Config

Cluster: `azcrpbifollower.kusto.windows.net` · Database: `bi_allprod` · Type: `Table`
Source panel: `VM Config`

```kusto
VM
 | where VMId == virtualMachineUniqueId
 | distinct Region,VMName,VMTimeCreated,DesiredPowerState,VMSize,OSState,OSDiskOSType,ProvisionVMAgent
```

**Params:** `{queryFrom}`, `{queryTo}`, `{virtualMachineUniqueId}`

---
