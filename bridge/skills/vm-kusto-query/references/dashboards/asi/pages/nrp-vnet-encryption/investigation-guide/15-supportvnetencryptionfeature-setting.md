# SupportVNetEncryptionFeature Setting

> Source: **NRP - Vnet Encryption** dashboard, chapter **SupportVNetEncryptionFeature Setting** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### SupportVNetEncryptionFeature

_Widget purpose:_ SupportVNetEncryptionFeature Setting

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `SupportVNetEncryptionFeature Setting`

```kusto
DynamicSettingsMonitor_Update(region)
| where setting_name == "SupportVNetEncryptionFeature"
| summarize by SettingName, SliceNum, Region, setting_value, last_run
```

**Params:** `{region}`

**Signal filters seen in KQL:** `setting_name == "SupportVNetEncryptionFeature"`

---
