# General Tool Links

> Source: **EEE RDOS — VM Availability** dashboard, chapter **General Tool Links** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### JarvisDashTimeHelper

_Widget purpose:_ General Tool Links

Cluster: `azurecm` · Database: `azurecm` · Type: `Single` · Widget: `Card`
Source panel: `General Tool Links`

```kusto
print startTimeInMs = datetime_diff('Millisecond',queryFrom, startofyear(datetime("1970"))), endTimeInMs = datetime_diff('Millisecond',queryTo, startofyear(datetime("1970")))
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### VmssIdHelper

_Widget purpose:_ General Tool Links

Cluster: `azurecm` · Database: `azurecm` · Type: `Single` · Widget: `Card`
Source panel: `General Tool Links`

```kusto
print vmssid = parse_json(queryContainerProperties).VmssUniqueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerProperties}`

---

### Unix Time Helper

_Widget purpose:_ General Tool Links

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single` · Widget: `Card`
Source panel: `General Tool Links`

```kusto
let toUnixTime = (dt:datetime) 
{ 
    (dt - datetime(1970-01-01)) / 1s 
};
print unixTimeFrom = toUnixTime(queryFrom)*1000, unixTimeTo = toUnixTime(queryTo)*1000, queryFrom = queryFrom, queryTo = queryTo
```

**Params:** `{queryFrom}`, `{queryTo}`

---
