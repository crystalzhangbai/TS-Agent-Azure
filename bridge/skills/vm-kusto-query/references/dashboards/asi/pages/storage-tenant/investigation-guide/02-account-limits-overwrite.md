# Account Limits Overwrite

> Source: **Storage Tenant Investigation Guide** dashboard, chapter **Account Limits Overwrite** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### List Account Limits Overwrite by Tenant

_Widget purpose:_ Account Limits Overwrite

Cluster: `https://xdeployment.westcentralus.kusto.windows.net` · Database: `Deployment` · Type: `Table`
Source panel: `Account Limits Overwrite`

```kusto
GetAccountThrottlingThresholdsSnapshot()
| where Tenant =~ tenant
| project Tenant, Account, Index , EgressThresholdInGbps, IngressThresholdInGbps, IOUnitsThresholdInKiops, RequestThresholdInKtps
```

**Params:** `{queryFrom}`, `{queryTo}`, `{tenant}`

---
