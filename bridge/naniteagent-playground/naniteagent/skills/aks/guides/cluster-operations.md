# AKS Cluster Operations Troubleshooting Guide

This guide covers troubleshooting for common AKS cluster operations including AsyncQoS events, auto-upgrades, and cluster autoscaler issues.

## When to Use This Guide

Use this guide when investigating:
- **Cluster CRUD operations**: Create, update, delete, start, stop operations
- **Cluster upgrade issues**: Manual or auto-upgrade failures
- **Cluster scaling issues**: Autoscaler not scaling up/down as expected

---

## Typical AKS Cluster CRUD Issues

**Keywords**: cluster state, upgrade, start, stop, cluster unhealthy

**Step 1:** Query `AsyncQoSEvents` to get recent operations
- Database: `AKSprod`
- Variables: Use Subscription ID, Resource Group name, and Cluster name from Step 3
- Time range: Use the time range provided by the user

```kql
cluster('akshuba.centralus').database('AKSprod').AsyncQoSEvents
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where resourceGroupName == '{Resource Group name}'
  and resourceName == '{Cluster name}'
| project PreciseTimeStamp, operationID, operationName, suboperationName, 
  k8sCurrentVersion, k8sGoalVersion, 
  resultType, resultCode, resultSubCode, errorDetails
| order by PreciseTimeStamp desc
| take 50
```

**Note**: Filter early (time first, then resource) for better performance.

**Present results in a table** and ask the user which operation they want to investigate further. Have them select the `operationID`.

**Step 2:** Query detailed logs using the selected operationID
- Database: `AKSprod`

```kql
union cluster('akshuba.centralus').database('AKSprod').FrontEndContextActivity, cluster('akshuba.centralus').database('AKSprod').AsyncContextActivity
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where operationID == '{selected operationID}'
| where resourceName == '{Cluster name}'
| project PreciseTimeStamp, level, operationID, operationName, msg, fileName, lineNumber
| order by PreciseTimeStamp asc
```

**Analysis Steps:**
1. First, filter and show ERROR level logs: `| where level == 'error'`
2. Then show WARNING level logs: `| where level == 'warning'`
3. Analyze the sequence of events to identify root cause
4. Look for error patterns in `msg` field

---

## Auto-Upgrade Issues

**Keywords**: cluster autoupgrade, auto upgrade

- Database: `AKSprod`

```kql
cluster('akshuba.centralus').database('AKSprod').AutoUpgraderEvents
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where resourceName == '{Cluster name}'
| where msg has_any ('defer message', 'allowed', 'scheduled', 'cancelled')
| project PreciseTimeStamp, msg, messageType, messageID, sequenceNumber, operationID
| order by PreciseTimeStamp asc
```

**Analysis tips:** 
- "defer message": Upgrades were postponed - check reason
- "scheduled": Upgrade was scheduled
- "cancelled": Upgrade was cancelled - check why

---

## Cluster Scaling Issues

**Keywords**: autoscale, scale, CA, cluster autoscaler

- Database: `AKSccplogs`
- **Important:** Use the `ccpNamespace` variable saved in Step 4

**Basic query:**
```kql
cluster('akshuba.centralus').database('AKSccplogs').ClusterAutoscaler
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| project PreciseTimeStamp, log
| order by PreciseTimeStamp asc
| take 100
```

**Targeted queries:**
```kql
// Scale-up events
| where log contains 'Scale-up'

// Scale-down events
| where log contains 'Scale-down'

// Failures and errors
| where log has_any ('fail', 'error', 'timeout', 'unable')

// Node group analysis
| where log contains 'node group'
| summarize count() by bin(PreciseTimeStamp, 5m)
```
