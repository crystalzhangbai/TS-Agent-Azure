# Allocation Info (Goal Seek State)

> Source: **CRP — VMs** dashboard, chapter **Allocation Info (Goal Seek State)** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### GoalState

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Timeline`
Source panel: `Allocation Info (Goal Seek State)`

```kusto
cluster("azcrpbifollower").database("bi_allprod").VMAllocationInfo
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SubscriptionId =~ querySubId
| where ResourceGroupName =~ queryResourceGroupName
| where VMName =~ queryResourceName
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = State
| extend flag  = case(Content <> prev(Content), "changed", "")
| where flag != ""
| extend EndTime = iif(isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Converged", "Healthy", Content == "Failed", "Error", "Neutral")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroupName}`, `{queryResourceName}`

---

### Error from AllocationInfo

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Timeline`
Source panel: `Allocation Info (Goal Seek State)`

```kusto
VMAllocationInfo
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SubscriptionId =~ querySubId
| where ResourceGroupName =~ queryResourceGroupName
| where VMName =~ queryResourceName
| extend Error = parse_json(iif(Error startswith "H4sIAAAAAAA", gzip_decompress_from_base64_string(Error), Error))
| extend errorCode = Error.Code, errorCategory = Error.Category, interalDetail = Error.InternalDetail, resourceType = Error.Message.resourceType, resourceCode = Error.Message.ResourceCode, Error
| extend StartTime = PreciseTimeStamp
| extend Content = tostring(errorCode)
| extend Health = iif(isempty(Error), "Healthy", "Error")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroupName}`, `{queryResourceName}`

---

## Allocation Info

### VMAllocationInfo Details

_Widget purpose:_ Allocation Info

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `Allocation Info (Goal Seek State) > Allocation Info`

```kusto
cluster("azcrpbifollower").database("bi_allprod").VMAllocationInfo
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SubscriptionId =~ querySubId
| where ResourceGroupName =~ queryResourceGroupName
| where VMName =~ queryResourceName
| extend Error = parse_json(iif(Error startswith "H4sIAAAAAAA", gzip_decompress_from_base64_string(Error), Error))
| extend errorCode = Error.Code, errorCategory = Error.Category
| extend opStartTime = LastGoalSeekingCompletionTime - 1d
| extend opEndTime = LastGoalSeekingCompletionTime + 1m 
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroupName}`, `{queryResourceName}`

---
