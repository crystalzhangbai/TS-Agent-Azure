# (top-level)

> Source: **UX Activities** dashboard, chapter **(top-level)** (6 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Connection by OS

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`

```kusto
PortalActivity
| where TIMESTAMP > queryFrom14days
| where TIMESTAMP <= queryTo
| where message contains "PortalAction:startWSConnection"
| summarize count() by os, bin(TIMESTAMP, 1d)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFrom14days}`, `{queryTo14days}`

**Signal filters seen in KQL:** `message contains "PortalAction:startWSConnection"`

---

### Connection by resource type

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`

```kusto
PortalActivity
| where TIMESTAMP > queryFrom14days
| where TIMESTAMP <= queryTo
| where message contains "PortalAction:startWSConnection"
| summarize count() by resourceType, bin(TIMESTAMP, 1d)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFrom14days}`, `{queryTo14days}`

**Signal filters seen in KQL:** `message contains "PortalAction:startWSConnection"`

---

### Power Options

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`

```kusto
PortalActivity
| where TIMESTAMP > queryFrom14days
| where TIMESTAMP <= queryTo14days
| where message == "PortalAction:restartVM" or message contains "CommandName: reset" or message contains "CommandName: nmi" or message contains '"SysRqCommand":"b"'
| summarize Restart_VM = countif(message == "PortalAction:restartVM"),
    Reset_VM = countif(message contains "CommandName: reset"),
    Sys_Rq = countif(message contains '"SysRqCommand":"b"'),
    NMI = countif(message contains "CommandName: nmi")
    by bin(TIMESTAMP, 1d)
| render linechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFrom14days}`, `{queryTo14days}`

**Signal filters seen in KQL:** `message == "PortalAction:restartVM"`

---

### Portal Actions

_Widget purpose:_ Portal Activities

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`

```kusto
PortalActivity
| where TIMESTAMP > queryFrom14days
| where TIMESTAMP <= queryTo14days
| where message == "PortalAction:updateFontSize" or message == "PortalAction:updateFontStyle" or message == "PortalAction:helpLinkClick"
| summarize Update_FontSize = countif(message == "PortalAction:updateFontSize"),
    Update_FontStyle = countif(message == "PortalAction:updateFontStyle"),
    Click_Help_Link = countif(message == "PortalAction:helpLinkClick")
    by bin(TIMESTAMP, 1d)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFrom14days}`, `{queryTo14days}`

**Signal filters seen in KQL:** `message == "PortalAction:updateFontSize"`

---

### Top 10 Tenants by Linux

_Widget purpose:_ Daily Top 10 Tenants by Linux

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `CategoryChart`

```kusto
PortalActivity
| where TIMESTAMP > queryFrom1day
| where TIMESTAMP <= queryTo1day
| where message contains "PortalAction:startWSConnection"
| where os == "Linux"
| summarize LinuxCount = count() by RPTenant, os
| order by LinuxCount
| limit 10
| render barchart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFrom1day}`, `{queryTo1day}`

**Signal filters seen in KQL:** `message contains "PortalAction:startWSConnection"` · `os == "Linux"`

---

### Top 10 Tenants by Windows

_Widget purpose:_ Daily Top 10 Tenant by Windows

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `CategoryChart`

```kusto
PortalActivity
| where TIMESTAMP > queryFrom1day
| where TIMESTAMP <= queryTo1day
| where message contains "PortalAction:startWSConnection"
| where os == "Windows"
| summarize WindowsCount = count() by RPTenant, os
| order by WindowsCount
| limit 10
| render barchart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFrom1day}`, `{queryTo1day}`

**Signal filters seen in KQL:** `message contains "PortalAction:startWSConnection"` · `os == "Windows"`

---
