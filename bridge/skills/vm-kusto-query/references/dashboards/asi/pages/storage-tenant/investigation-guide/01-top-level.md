# (top-level)

> Source: **Storage Tenant Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Storage Tenant"

_Widget purpose:_ {{Tenant}}

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `ResourceGet` · Widget: `Container`

```kusto
GetTenantCatalogLatest()
| where Tenant == trim(@"[\s]+", local_Tenant)
| extend TenantMsg=""
// if Tenant not found, retuns empty line instead of ASI resource was found error and cat image
| union (       
    print TenantMsg=strcat("<span style='color:red'>Tenant <b>",trim(@"[\s]+", local_Tenant),"</b> not found</span>")
)
| sort by ClusterName nulls last
| limit 1
```

**Params:** `{local_Tenant}`, `{globalFrom}`, `{globalTo}`

---
