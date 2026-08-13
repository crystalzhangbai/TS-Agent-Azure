# Account Limits & Usage (99% Percentile)

> Source: **Storage Account Investigation Guide** dashboard, chapter **Account Limits & Usage (99% Percentile)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Account Limit

_Widget purpose:_ Account Limits & Usage (99% Percentile)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Xstore` · Type: `Table`
Source panel: `Account Limits & Usage (99% Percentile)`

```kusto
let zero = toreal("0");
let gbpscoefficient=8/exp2(30);
let ktpscoefficient=1/1000.0;
let metrics = print metric = pack_array(
    pack("metric", "TotalEgress", "coefficient", gbpscoefficient),
    pack("metric", "InternalEgress", "coefficient", gbpscoefficient),
    pack("metric", "TotalIngress", "coefficient", gbpscoefficient),
    pack("metric", "Entities", "coefficient", ktpscoefficient)
)
| mv-expand metric
| evaluate bag_unpack(metric);
cluster('azcore.centralus.kusto.windows.net').database('Xstore').XAggAccountUsageMetric
| where TIMESTAMP between (queryFrom..queryTo)
| where AccountName == trim(@"[\s]+", accountName)
| join kind=inner (metrics) on $left.UsageCategory == $right.metric
| project TIMESTAMP, Tenant, UsageCategory, AdjustedUsagePerSec=MeasuredUsagePerSec*coefficient, AdjustedLimit=TargetUsageThreshold*coefficient, AccountName
| summarize AdjustedUsagePerSec=percentiles(AdjustedUsagePerSec, 99),
    AdjustedLimit=round(max(AdjustedLimit), 0)
    by AccountName, UsageCategory, Tenant
| extend AdjustedUsagePerSec=round(AdjustedUsagePerSec, 0)
| extend IngressUsed=iif(UsageCategory=="TotalIngress", AdjustedUsagePerSec, zero),
         IngressLimit=iif(UsageCategory=="TotalIngress", AdjustedLimit, zero),
         EgressUsed=iif(UsageCategory=="TotalEgress", AdjustedUsagePerSec, zero),
         EgressLimit=iif(UsageCategory=="TotalEgress", AdjustedLimit, zero),
         InternalEgressUsed=iif(UsageCategory=="InternalEgress", AdjustedUsagePerSec, zero),
         InternalEgressLimit=iif(UsageCategory=="InternalEgress", AdjustedLimit, zero),         
         TpsUsed=iif(UsageCategory=="Entities", AdjustedUsagePerSec, zero),
         TpsLimit=iif(UsageCategory=="Entities", AdjustedLimit, zero)
| summarize IngressUsed=max(IngressUsed),
            IngressLimit=max(IngressLimit),
            EgressUsed=max(EgressUsed),
            EgressLimit=max(EgressLimit),
            InternalEgressUsed=max(InternalEgressUsed),
            InternalEgressLimit=max(InternalEgressLimit),
            TpsUsed=max(TpsUsed),
            TpsLimit=max(TpsLimit)
            by AccountName, Tenant
| summarize IngressUsed=sum(IngressUsed),
            IngressLimit=sum(IngressLimit),
            EgressUsed=sum(EgressUsed),
            EgressLimit=sum(EgressLimit),
            //InternalEgressUsed=sum(InternalEgressUsed),
            //InternalEgressLimit=sum(InternalEgressLimit),            
            TpsUsed=sum(TpsUsed),
            TpsLimit=sum(TpsLimit),
            Tenants=sum(1)
            by AccountName
| order by AccountName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

---
