# Kubernetes Audit Logs Investigation Guide

This guide covers using Kubernetes audit logs from the control plane for deep investigation of cluster activity and API operations.

## When to Use This Guide

Use this guide when you need to answer:
- **What happened?** - What operations were performed
- **When did it happen?** - Exact timestamps of operations
- **Who initiated it?** - Which user or service account
- **On what resource?** - Specific pods, deployments, services
- **Where was it observed?** - Which namespace
- **From where was it initiated?** - Source IP, user agent

---

## Database Information

**Database:** `AKSccplogs` (via ControlPlaneEvents and ControlPlaneEventsNonShoebox tables)

The `kube-audit` logs record all Kubernetes API activities including create, update, patch, and delete operations on cluster resources.

---

## Before Querying

Ask the user for:
- Resource type (e.g., pods, deployments, services)
- Specific resource name (if known)
- User/service account (if known)
- Verb/operation (create, update, delete, patch)

---

## Basic Audit Query Template

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}')..datetime('{endTime}')) 
| where ccpNamespace == '{ccpNamespace}' 
| where category == 'kube-audit'
| extend Pod = extractjson('$.pod', properties, typeof(string))
| extend Log = extractjson('$.log', properties, typeof(string))
| extend _jlog = parse_json(Log)
| extend requestURI = tostring(_jlog.requestURI)
| extend verb = tostring(_jlog.verb)
| extend user = tostring(_jlog.user.username)
| where verb !in ('get', 'list', 'watch')
| project PreciseTimeStamp, requestURI, verb, user, Log
| order by PreciseTimeStamp asc
| take 100
```

---

## Check Pod Status Changes in Audit Log

Track create, update, patch, and delete operations on pods:

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}' 
| where category == 'kube-audit'
| where properties has @'\/pods'
| where properties has '{pod-name}'  // Optional: filter specific pod
| extend props = todynamic(properties)
| extend logData = tostring(props.log)
| extend auditLog = parse_json(logData)
| extend requestURI = tostring(auditLog.requestURI)
| extend verb = tostring(auditLog.verb)
| extend user = tostring(auditLog.user.username)
| extend podName = tostring(auditLog.objectRef.name)
| extend podNamespace = tostring(auditLog.objectRef.namespace)
| where verb !in ('get', 'list', 'watch')
| where verb in ('create', 'update', 'patch', 'delete')
| project PreciseTimeStamp, podNamespace, podName, verb, user, requestURI
| order by PreciseTimeStamp asc
| take 100
```

---

## Node NotReady Investigation - Check Node Heartbeats

**Ask the user** for the node name before running this query.

This query checks node lease renewals (heartbeats) to diagnose NotReady issues:

```kql
let aksNode = '{node-name}';
let apiPrefix = '/apis/coordination.k8s.io/v1/namespaces/kube-node-lease/leases/';
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}' 
| where category == 'kube-audit'
| extend props = todynamic(properties)
| extend log = tostring(props.log)
| where log contains 'ResponseComplete'
| extend audit = parse_json(log)
| extend requestURI = tostring(audit.requestURI),
         verb = tostring(audit.verb),
         statusCode = toint(audit.responseStatus.code),
         userAgent = tostring(audit.userAgent),
         userName = tostring(audit.user.username),
         stage = tostring(audit.stage),
         receivedTs = todatetime(audit.requestReceivedTimestamp),
         stageTs = todatetime(audit.stageTimestamp)
| extend latencyMs = datetime_diff('millisecond', stageTs, receivedTs),
         leaseNode = extract(@'/leases/([^?/\s]+)', 1, requestURI)
| where verb in ('update', 'patch')
| where requestURI contains apiPrefix
| where leaseNode contains aksNode
| project PreciseTimeStamp, ccpNamespace, stage, requestURI, verb,
          status = tostring(statusCode), userAgent,
          user = iff(userName contains '@', '<redacted-AAD-user>', userName),
          latencyMs, auditID = tostring(audit.auditID)
| order by PreciseTimeStamp asc
```

**Analysis:** Look for gaps in heartbeat updates or failed lease renewals.

---

## Find Clients Overloading the API Server

This query identifies the top 10 user agents sending the most requests:

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox  
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| where category == 'kube-audit'  
| extend props = todynamic(properties)  
| extend auditLog = parse_json(tostring(props.log))  
| where auditLog.stage == 'ResponseComplete'  
| where auditLog.objectRef.subresource !in ('proxy', 'exec')  
| extend verb = tostring(auditLog.verb)  
| extend resource = tostring(auditLog.objectRef.resource)  
| extend agent = tostring(auditLog.userAgent)  
| extend userName = tostring(auditLog.user.username)  
| extend latencyMs = datetime_diff('Millisecond', 
    todatetime(auditLog.stageTimestamp), 
    todatetime(auditLog.requestReceivedTimestamp))  
| summarize RequestCount = count(), 
            MaxLatency = max(latencyMs), 
            P50_Latency = percentile(latencyMs, 50),
            P95_Latency = percentile(latencyMs, 95),
            P99_Latency = percentile(latencyMs, 99)
            by agent, userName, verb  
| order by RequestCount desc  
| take 10
```

**Analysis tips:** 
- High request counts (>1000/min) may indicate problematic clients
- Watch for inefficient "list" operations without resourceVersion
- P99 latency >1000ms suggests API server overload
- Common culprits: custom controllers, monitoring agents, CI/CD tools
