# ASI Portal (asi.azure.ms)

ASI hosts the EEE, WF, Hawkeye, and various Azure Compute monitoring dashboards. All of them are powered by **KQL queries against public Kusto clusters** (e.g. `azurecm`, `vmainsight`, `azcore.centralus`, `storageclient.eastus`, …).

## Architecture

```
Browser → ASI front-end (SPA)
            │
            ├── GET /api/services/<svc>/pages/<page>      → page widget tree (recursive)
            ├── GET /api/compoundWidgetGroups/<id>        → sub-panel definition
            └── POST /api/queries/search                  → bulk fetch full KQL bodies
                                                            by (groupId, majorVersion)
                                                              │
                                                              ▼
                                                       Kusto clusters (cross-cluster)
```

### Page metadata

Each ASI page is a JSON tree of nested widgets:

- `CompoundWidgetContainer` → nests sub-panels (referenced by `compoundWidgetId`)
- Leaf widgets carry `queries: [{ groupId, majorVersion, ... }]` or `selectedProperties[].mapping.groupId`
- Query bodies are NOT inlined — they're stored separately and fetched by groupId

### Query body retrieval

```
POST /api/queries/search
{
  "selectors": [
    { "groupId": "<guid>", "majorVersion": 1, "searchType": "ByGroupId" },
    ...
  ]
}
→ array of { id, name, cluster, database, kustoQuery, params, schema, ... }
```

The same query (groupId, majorVersion) can be referenced by many widgets; dedupe before fetching.

### Param-name quirk

ASI widgets use **30+ alias names for the same value**:

| Canonical | Aliases observed |
|-----------|------------------|
| `startTime` | `starttime`, `_starttime`, `queryFrom`, `queryStart`, `startTimeFilter`, `globalFrom` |
| `endTime` | `endtime`, `_endtime`, `queryTo`, `queryEnd`, `endTimeFilter`, `globalTo` |
| `containerId` | `containerid`, `queryContainerId`, `_containerid` |
| `nodeId` | `nodeid`, `queryNodeId`, `_nodeid` |
| `vmId` | `vmid`, `queryVmId`, `_vmid`, `VmUniqueId` |
| `cluster` | `Cluster`, `clustername`, `_cluster` |
| `tenantName` | `tenantname`, `TenantName`, `_tenantname` |
| `roleInstanceName` | `RoleInstanceName`, `roleinstancename`, `_roleinstancename` |

Each page's `meta.json` records the alias map; each `replay.py` normalizes from canonical slots before substituting into the KQL via a `let name = <literal>;` prelude.

## Authentication

- **Audience**: `api://eb092fbe-b5f4-492f-bd9a-3787232fbdeb`
- **Bearer required** — cookies alone return 401
- Token is acquired via MSAL but **not exposed as a window global** — easiest path is to grab the `Authorization` header from a recorded request in DevTools (token lifetime ~82 min)
- Underlying Kusto clusters require Azure AD auth via `az login` (tenant `72f988bf-86f1-41af-91ab-2d7cd011db47`); the replay scripts use `kusto_runner.py` which handles this

## Extracting a new page

See [`_tooling/README.md`](_tooling/README.md) for the workflow. Summary:

1. Capture an ASI Bearer token from a logged-in browser session.
2. Edit `_tooling/extract.js` constants: `SERVICE`, `PAGE`.
3. Run `node extract.js <token-file> ../pages/<slug>/raw`.
4. Run `node build-library.js ../pages/<slug>/raw ../pages/<slug>/library`.
5. Copy `pages/eee-rdos-start-hub/replay.py` to the new page folder; update `ALIASES` dict if the new page uses new param names.
6. Write a `meta.json` with the URL pattern + param descriptions.

## Pages extracted

| Slug | Service / Page | Queries | Panels | Replay |
|------|----------------|--------:|-------:|--------|
| [`eee-rdos-start-hub`](pages/eee-rdos-start-hub/library.md) | EEE RDOS / Start Hub | 166 | 31 | `python pages/eee-rdos-start-hub/replay.py --help` |

## Discovered Kusto clusters (across all ASI pages so far)

`azcore.centralus`, `storageclient.eastus`, `azurecm`, `vmainsight`, `azuredcm`, `aplat.westcentralus`, `aznwsdn`, `azurewatsoncustomer`, `icmcluster`, `accp.centralus`, `azcrpbifollower`, `sparkle.eastus`.

ASI sometimes stores cluster names without the `.kusto.windows.net` suffix — `replay.py` appends it if missing.
