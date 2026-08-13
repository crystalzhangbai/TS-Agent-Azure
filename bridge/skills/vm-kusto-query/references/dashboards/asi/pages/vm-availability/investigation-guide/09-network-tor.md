# Network / TOR

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Network / TOR** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### TorDeviceInfo

_Widget purpose:_ Network / TOR

Cluster: `azphynet` · Database: `azdhmds` · Type: `Single` · Widget: `Card`
Source panel: `Network / TOR`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project NodeName=StartDevice, NodePort=StartPort, NodeSonicPort=StartSonicPort, TorDevice=EndDevice, EndPort, TorSonicPort=EndSonicPort, BandwidthInGbps, DataCenter
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### Unix Time Helper

_Widget purpose:_ Network / TOR

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single` · Widget: `Card`
Source panel: `Network / TOR`

```kusto
let toUnixTime = (dt:datetime) 
{ 
    (dt - datetime(1970-01-01)) / 1s 
};
print unixTimeFrom = toUnixTime(queryFrom)*1000, unixTimeTo = toUnixTime(queryTo)*1000, queryFrom = queryFrom, queryTo = queryTo
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### vfpMDM

_Widget purpose:_ Network / TOR

Cluster: `azurehn` · Database: `azurehn` · Type: `Single` · Widget: `Card`
Source panel: `Network / TOR`

```kusto
MdmVfpVnetAccountMaps
| where Cluster == queryCluster
| project VfpAccount
```

**Params:** `{queryCluster}`

---
