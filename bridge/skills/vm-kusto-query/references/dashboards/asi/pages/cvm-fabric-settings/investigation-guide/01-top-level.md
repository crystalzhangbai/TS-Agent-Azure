# (top-level)

> Source: **Confidential Virtual Machines - Fabric Settings** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Fabric Setting History Search

_Widget purpose:_ Please specify Clusters you want to check

Cluster: `acckusto.southcentralus.kusto.windows.net` · Database: `ACCTEST` · Type: `Table`

```kusto
cluster('azcore.centralus').database("Fc").TMMgmtFabricSettingEtwTable
| where LastModifiedTime > queryFrom and LastModifiedTime < queryTo and LastModifiedBy startswith "AME"
| where Tenant in~ (Clusters)
| serialize
| sort by PreciseTimeStamp
| where Value != prev(Value, 1)
| project PreciseTimeStamp, LastModifiedTime, Tenant, LastModifiedBy, Name, PreviousValue, Value
```

**Params:** `{queryFrom}`, `{queryTo}`, `{Clusters}`

---

### Fabric Setting History in last 7 days

_Widget purpose:_ Fabric Setting History for ACC Clusters in Last 7 days

Cluster: `acckusto.southcentralus.kusto.windows.net` · Database: `ACCTEST` · Type: `Table`

```kusto
let Clusters = cluster('acckusto.southcentralus').database("ACCTEST").getAllAccClusters 
| project Tenant=Cluster;
cluster('azcore.centralus').database("Fc").TMMgmtFabricSettingEtwTable
| where LastModifiedTime > ago(7d)  and LastModifiedBy startswith "AME"
| where Tenant in (Clusters)
| serialize
| sort by PreciseTimeStamp
| where Value != prev(Value, 1)
| project PreciseTimeStamp, LastModifiedTime, Tenant, LastModifiedBy, Name, PreviousValue, Value
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Detailed Fabric Setting History in 24 Hours

_Widget purpose:_ Fabric Setting Detail for ACC Clusters in last 24 Hours

Cluster: `acckusto.southcentralus.kusto.windows.net` · Database: `ACCTEST` · Type: `Table`

```kusto
let Clusters = cluster('acckusto.southcentralus').database("ACCTEST").getAllAccClusters 
| project Tenant=Cluster;
cluster('azcore.centralus').database("Fc").TMMgmtFabricSettingEtwTable
| where LastModifiedTime > ago(1d)  and LastModifiedBy startswith "AME"
| where Tenant in (Clusters)
| serialize
| sort by PreciseTimeStamp
| where Value != prev(Value, 1)
| project PreciseTimeStamp, LastModifiedTime, Tenant, LastModifiedBy, Name, PreviousValue, Value
```

---
