# Profiles

> Source: **NRP - AzureProfiles** dashboard, chapter **Profiles** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### azureprofiles

_Widget purpose:_ Profiles

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Profiles`

```kusto
let regionToTenant = (QosEtwEvent
| where PreciseTimeStamp > ago(1h)
| where Region == region
| parse Tenant with tenant "." *
| summarize by tenant);
let subtoRoleInstance = (QosEtwEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region == region
| where SubscriptionId == subscription
| summarize by RoleInstance
| extend roleModified = replace_string(RoleInstance, ".", "_IN_")
| summarize by roleModified
);
cluster('azureprofilerfollower.westus2.kusto.windows.net').database('azureprofiler').
Identifiers | where Timestamp between (startTime .. endTime)
| where RoleInstance contains "NRP"
| parse Tenant with tenant1 "." *
| extend tenant = tolower(iff(tenant1 == "", Tenant, tenant1))
| where tenant in (regionToTenant)
| where RoleInstance in (subtoRoleInstance)
| extend Link = strcat("<a href='", ViewerUrl, "'>AzureProfileLink</a>")
| extend NRPRoleIntance = replace_string(RoleInstance, "_IN_", ".")
| extend ProfileTrigger = iff(Topic contains "fabric__Monitoring", "DailyProfile", iff (isempty(Fuse), "UnknownTrigger", Fuse))
| project TraceStartTime, TraceEndTime,ProfileTrigger,Status,NRPRoleIntance, Link
| order by TraceStartTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{region}`, `{subscription}`

**Signal filters seen in KQL:** `RoleInstance contains "NRP"`

---
