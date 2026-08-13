# KQL Query Best Practices for AKS

> Troubleshooting tips, common errors, and performance guidance for AKS Kusto queries.

## Common Query Errors & Fixes

### Error: "Request is invalid and cannot be executed"
**Cause**: Usually a syntax error or invalid column reference.
**Fix**: Check column names against schema. Use `| getschema` to verify:
```kql
cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot | getschema
```

### Error: "has_any requires at least 1 argument"
**Cause**: Empty array passed to `has_any()`.
**Fix**: Always check array is non-empty before using `has_any()`:
```kql
// BAD - fails if list is empty
| where column has_any (dynamicList)

// GOOD - guard against empty list
| where array_length(dynamicList) == 0 or column has_any (dynamicList)
```

### Error: "Query execution has exceeded the allowed limits"
**Cause**: Query scanning too much data.
**Fix**:
1. Narrow time range (use `between()`)
2. Add `cluster_id` filter early
3. Add `take N` or `limit N`
4. Project only needed columns early

### Error: "The expression refers to column that does not exist"
**Cause**: Column name is wrong or table schema has changed.
**Fix**: Common column name mistakes:

| Wrong | Correct | Table |
|-------|---------|-------|
| `ccpNamespace` | `namespace` | ManagedClusterSnapshot |
| `nodeCount` | `size` | AgentPoolSnapshot |
| `kubernetesVersion` | `orchestratorVersion` (nested) | ManagedClusterSnapshot |
| `clusterID` (uppercase D) | `cluster_id` | Most tables |

### Error: "Partial query failure" / Timeout
**Cause**: Query too expensive.
**Fix**:
1. Add `| take 1000` early in the pipeline
2. Use `| sample 1000` for analysis
3. Reduce time range
4. Add more specific filters before aggregation

---

## Query Performance Tips

### 1. Filter Early, Filter Often
```kql
// BAD - scans everything then filters
cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(24h)
| project PreciseTimeStamp, verb, objectRef
| where verb == 'delete'

// GOOD - filter on indexed columns first
cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(24h)
| where cluster_id == qCCP
| where verb == 'delete'
| project PreciseTimeStamp, objectRef
```

### 2. Use `between()` for Historical Queries
```kql
// Good for real-time monitoring
| where PreciseTimeStamp > ago(2h)

// Better for historical investigation (bounded scan)
| where PreciseTimeStamp between(datetime('2026-01-20T10:00:00Z') .. datetime('2026-01-20T12:00:00Z'))
```

### 3. Prefer `has` Over `contains`
```kql
// SLOW - substring search
| where msg contains "error"

// FAST - word boundary search (uses index)
| where msg has "error"

// FASTEST - exact match
| where msg == "specific error message"
```

### 4. Limit Dynamic Field Parsing
```kql
// BAD - parse in every row, then filter
cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(1h)
| extend parsed = todynamic(requestObject)
| where parsed.spec.containers[0].image has "nginx"

// GOOD - use has/contains on raw field first, then parse
cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(1h)
| where requestObject has "nginx"
| extend parsed = todynamic(requestObject)
| where parsed.spec.containers[0].image has "nginx"
```

### 5. Use `take` vs `top`
```kql
// For "any recent record" - faster
| take 1

// For "most recent record" - slower but ordered
| top 1 by PreciseTimeStamp desc

// Best: order then take
| order by PreciseTimeStamp desc
| take 1
```

### 6. Avoid `join` When Possible
```kql
// If you need data from one table but filtered by another,
// use let statements with project to minimize join cost

let targetPods = cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(1h)
| where cluster_id == qCCP and objectRef.resource == 'pods'
| where responseStatus.code >= 400
| distinct tostring(objectRef.name);

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(1h)
| where cluster_id == qCCP
| where tostring(objectRef.name) in (targetPods)
```

---

## Presentation Best Practices

### Formatting Query Results

Always present query results in a structured format:

```markdown
## Query Results: [Description]
**Database**: `[database]` | **Time Range**: `[range]` | **Cluster**: `[name]`

| Column1 | Column2 | Column3 |
|---------|---------|---------|
| value1  | value2  | value3  |

**Key Findings:**
- Finding 1
- Finding 2
```

### Handling Large Result Sets

- Summarize first, then drill into details
- Use `| take 20` for initial overview
- Group by relevant dimensions (`namespace`, `node`, `pod`)
- Show counts/aggregates before raw data

### When Queries Return No Results

1. **Verify the cluster identifier** — try both `cluster_id` and `clusterName`
2. **Expand the time range** — the issue might have occurred earlier
3. **Check the database** — make sure you're querying the right one
4. **Simplify the query** — remove filters one by one to find which filter is too restrictive
5. **Check case sensitivity** — `cluster_id` is case-sensitive; use `=~` for case-insensitive

---

## Troubleshooting Decision Tree

```
Issue reported
├── Need cluster config? → AKSprod (ManagedClusterSnapshot, AgentPoolSnapshot)
├── Need control plane logs? → AKSccplogs (KubeAudit, Etcd)
├── Need operation history? → AKSprod (AsyncQoSEvents)  
├── Need node/pod metrics? → AKSmetrics (InsightsMetrics)
├── Network issue? → Start with AKSprod network query (see cluster-info-queries.md §4.3)
├── Node issue? → guides/node-troubleshooting.md
├── Upgrade issue? → guides/cluster-operations.md
└── Audit/compliance? → guides/audit-logs.md
```

---

## Schema Verification

Before using any table, verify schema with:
```kql
// Check table exists and see columns
TableName | getschema

// See sample data
TableName | take 5

// Check column types
TableName | getschema | where ColumnName == "cluster_id"
```

For complete table schemas, see: `table-schema/` directory (JSON format per database).
For quick schema reference, see: `references/TABLE_SCHEMA_REFERENCE.md`.
