# Regional Account Distribution

> Source: **Storage Account Investigation Guide** dashboard, chapter **Regional Account Distribution** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Regional Accounts Distribution

_Widget purpose:_ Regional Account Distribution

Cluster: `https://xdeployment.westcentralus.kusto.windows.net` · Database: `Deployment` · Type: `Table`
Source panel: `Regional Account Distribution`

```kusto
let LatestRegionalAccountsDate = cluster('xdataanalytics.westcentralus.kusto.windows.net').database('XDataAnalytics').RegionalAccountsLimits_BW_V2 | summarize TimePeriod=max(TimePeriod);
let RALimits = cluster('xdataanalytics.westcentralus.kusto.windows.net').database('XDataAnalytics').RegionalAccountsLimits_BW_V2
    | join kind=inner (LatestRegionalAccountsDate) on TimePeriod
| where AccountName =~ accountName;
let strAccName = strcat(accountName, "\\");
let AccountConfigs = cluster('xtableserver.westcentralus.kusto.windows.net').database('ClusterResourceManager').AccountVirtualizationMetrics
| where AccountName contains strAccName 
| summarize arg_max(env_time, *) by AccountName;
let TenantConfigs = cluster('xtableserver.westcentralus.kusto.windows.net').database('ClusterResourceManager').TenantVirtualizationMetrics
| summarize arg_max(env_time, *) by GroupName, WeightedTenant;
let ThresholdsSnapshot = cluster('xdeployment.westcentralus.kusto.windows.net').database('Deployment').GetAccountThrottlingThresholdsSnapshot()
| where Account =~ accountName
| project Tenant=tolower(Tenant), InternalEgressThresholdInGbps;
let IngestionWeights = AccountConfigs
| join TenantConfigs on $left.IngestionGroupName == $right.GroupName
| project AccountName, GroupName, WeightedTenant, Weight;
let Limits = IngestionWeights
| join RALimits on $left.WeightedTenant == $right.Tenant;
Limits 
| join kind=leftouter ThresholdsSnapshot on Tenant
| project AccountName, HomeCluster, Tenant, GroupName, IngressThresholdInGbps, EgressThresholdInGbps, InternalEgressThresholdInGbps, TPSThresholdInKtps, IngestionWeight=Weight, StampDefault_IngressThresholdInGbps, StampDefault_EgressThresholdInGbps, StampDefault_TPSThresholdInKtps;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

---
