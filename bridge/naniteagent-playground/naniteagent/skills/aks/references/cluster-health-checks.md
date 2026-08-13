# Cluster Health Checks

> Run these queries when investigating cluster-wide health issues, operation failures, or performance degradation.

## 5.1 Recent Cluster Operations

Check for recent failed or in-progress operations that may be causing issues.

**Database**: `AKSprod`

> **Default time range**: `ago(24h)` — operations may take time. Expand for upgrade/scaling history.

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(24h);
let qTo = now();

cluster('akshuba.centralus').database('AKSprod').AsyncQoSEvents
| where PreciseTimeStamp between(qFrom .. qTo)
| where namespace == qCCP
| summarize 
    Count = count(),
    FirstSeen = min(PreciseTimeStamp),
    LastSeen = max(PreciseTimeStamp)
    by operationName, resultCode, tostring(resultType)
| order by LastSeen desc
| take 50
```

### Operation Failure Investigation

When operations fail, get detailed error messages:

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(24h);
let qTo = now();

cluster('akshuba.centralus').database('AKSprod').AsyncQoSEvents
| where PreciseTimeStamp between(qFrom .. qTo)
| where namespace == qCCP
| where isnotempty(errorDetails) or resultCode != 'Succeeded'
| project 
    PreciseTimeStamp,
    operationName,
    resultCode,
    tostring(resultType),
    errorDetails,
    operationID
| order by PreciseTimeStamp desc
| take 50
```

### NRP/ARM Operation Tracking

Track Azure Resource Manager operations on the cluster:

**Database**: `AKSprod`

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(24h);
let qTo = now();

cluster('akshuba.centralus').database('AKSprod').AsyncQoSEvents
| where PreciseTimeStamp between(qFrom .. qTo)
| where namespace == qCCP
| project 
    PreciseTimeStamp,
    operationType = operationName,
    status = resultCode,
    errorCode = errorDetails,
    correlationId = operationID
| order by PreciseTimeStamp desc
| take 50
```

---

## 5.2 API Server Health & Latency

Check API server responsiveness and identify slow requests.

**Database**: `AKSccplogs`

> **Default time range**: `ago(2h)` — use shorter ranges for performance investigations.

### API Server Request Latency Distribution

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where isnotempty(stageTimestamp) and isnotempty(requestReceivedTimestamp)
| extend latencyMs = datetime_diff('millisecond', todatetime(stageTimestamp), todatetime(requestReceivedTimestamp))
| where latencyMs > 0
| summarize 
    p50 = percentile(latencyMs, 50),
    p90 = percentile(latencyMs, 90),
    p99 = percentile(latencyMs, 99),
    max_latency = max(latencyMs),
    total_requests = count()
    by bin(PreciseTimeStamp, 5m), verb
| order by PreciseTimeStamp desc
```

### Slow API Requests (> 5 seconds)

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where isnotempty(stageTimestamp) and isnotempty(requestReceivedTimestamp)
| extend latencyMs = datetime_diff('millisecond', todatetime(stageTimestamp), todatetime(requestReceivedTimestamp))
| where latencyMs > 5000
| project 
    PreciseTimeStamp,
    verb,
    resource = tostring(objectRef.resource),
    subresource = tostring(objectRef.subresource),
    namespace = tostring(objectRef.namespace),
    name = tostring(objectRef.name),
    latencyMs,
    user = tostring(user.username),
    userAgent = tostring(userAgent),
    responseCode = responseStatus.code
| order by latencyMs desc
| take 50
```

### API Server Error Rate

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where responseStatus.code >= 400
| summarize 
    ErrorCount = count(),
    UniqueResources = dcount(tostring(objectRef.resource))
    by 
    StatusCode = toint(responseStatus.code), 
    Reason = tostring(responseStatus.reason),
    Verb = verb,
    bin(PreciseTimeStamp, 5m)
| order by PreciseTimeStamp desc, ErrorCount desc
```

### API Server Throttling (429 responses)

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where responseStatus.code == 429
| project 
    PreciseTimeStamp,
    verb,
    resource = tostring(objectRef.resource),
    user = tostring(user.username),
    userAgent = tostring(userAgent),
    retryAfter = tostring(responseStatus.metadata.retryAfterSeconds)
| summarize 
    ThrottleCount = count(),
    FirstSeen = min(PreciseTimeStamp),
    LastSeen = max(PreciseTimeStamp)
    by user, resource, verb
| order by ThrottleCount desc
```

---

## 5.3 etcd Health

Check etcd database size and compaction status.

**Database**: `AKSccplogs`

> **Default time range**: `ago(6h)` — etcd metrics are periodic.

### etcd Database Size

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(6h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeControllerManager
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where log has "etcd" and log has "size"
| project PreciseTimeStamp, log
| order by PreciseTimeStamp desc
| take 20
```

### etcd Slow Requests

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(6h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').Etcd
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where log has "slow" or log has "took too long"
| project 
    PreciseTimeStamp,
    log,
    level
| order by PreciseTimeStamp desc
| take 50
```

### etcd Leader Election Changes

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(24h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').Etcd
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| where log has "leader" or log has "election"
| project 
    PreciseTimeStamp,
    log,
    level
| order by PreciseTimeStamp desc
| take 50
```

---

## Health Check Summary Table

| Check | Database | Key Indicator | Alert Threshold |
|-------|----------|---------------|-----------------|
| **API Latency** | AKSccplogs | p99 latency | > 5 seconds |
| **API Errors** | AKSccplogs | 5xx error rate | > 1% of requests |
| **Throttling** | AKSccplogs | 429 responses | Any sustained throttling |
| **etcd Size** | AKSccplogs | DB size in bytes | > 6GB (warning), > 8GB (critical) |
| **etcd Slow** | AKSccplogs | Slow request count | Any slow requests |
| **Operations** | AKSprod | Failed operations | Any failed operations |

## Escalation Triggers

Escalate to product team if:
- API server latency p99 consistently > 10 seconds
- etcd database size > 8GB
- Repeated leader election changes (> 3 in 1 hour)
- Control plane operations stuck in "InProgress" for > 30 minutes
- 429 throttling affecting system components (not just user workloads)
