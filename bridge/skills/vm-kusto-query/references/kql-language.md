# KQL Language Reference — Azure Infrastructure Investigation

Source: Microsoft Learn official docs + AzureIaaSVM wiki best practices

---

## Core Concepts

- KQL is **read-only**, **case-sensitive** (table names, column names, operators, functions)
- Data flows through **pipe `|`** operators sequentially — order matters for performance
- Three statement types: `let` (bind variable), tabular expression (pipeline), `set` (query options)
- Cross-cluster syntax: `cluster('<host>').database('<db>').<Table>`

---

## Operator Quick Reference

### Filtering

| Operator | Purpose | Example |
|----------|---------|---------|
| `where` | Filter rows by predicate | `\| where NodeId == "{NodeId}"` |
| `where` + datetime | Time-window filter | `\| where PreciseTimeStamp between(datetime({Start})..datetime({End}))` |
| `where` + `ago()` | Relative time | `\| where PreciseTimeStamp > ago(2h)` |
| `has` | Token match (fast, indexed) | `\| where Message has "IERR"` |
| `contains` | Substring match (slower) | `\| where Message contains "Fault"` |
| `=~` | Case-insensitive equals | `\| where ServiceName =~ "datapath"` |
| `in` | Membership test | `\| where NodeId in (nodeids)` |
| `!in` | Exclusion test | `\| where EventId !in (504, 505)` |

> **Best practice**: Use `has` over `contains`; use `==` over `=~` when data is consistent case. Place `where` on datetime columns first — Kusto indexes them.

### Column Manipulation

| Operator | Purpose | Example |
|----------|---------|---------|
| `project` | Select/order columns | `\| project PreciseTimeStamp, NodeId, Message` |
| `project-away` | Drop columns | `\| project-away _SomeInternalCol` |
| `project-rename` | Rename column | `\| project-rename NodeId = BladeID` |
| `project-reorder` | Reorder columns | `\| project-reorder PreciseTimeStamp, NodeId` |
| `extend` | Add computed column | `\| extend Duration = EndTime - StartTime` |

### Aggregation

```kusto
// summarize: group + aggregate
cluster('{ClusterHost}').database('{Database}').{Table} | summarize count() by ServiceVersion
cluster('{ClusterHost}').database('{Database}').{Table} | summarize arg_max(PreciseTimeStamp, *) by NodeId   // latest record per NodeId
cluster('{ClusterHost}').database('{Database}').{Table} | summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by NodeId, ContainerId
cluster('{ClusterHost}').database('{Database}').{Table} | summarize make_set(NodeId) by Tenant               // collect into dynamic array
```

Key aggregation functions: `count()`, `sum()`, `avg()`, `min()`, `max()`, `arg_max()`, `arg_min()`, `make_set()`, `make_list()`, `dcount()`

### Sorting & Limiting

```kusto
cluster('{ClusterHost}').database('{Database}').{Table} | sort by PreciseTimeStamp desc
cluster('{ClusterHost}').database('{Database}').{Table} | top 10 by PreciseTimeStamp desc
cluster('{ClusterHost}').database('{Database}').{Table} | take 100        // same as limit, for quick exploration
cluster('{ClusterHost}').database('{Database}').{Table} | distinct NodeId, ContainerId
```

### Joining Tables

```kusto
// Standard join — put smaller table on LEFT
cluster('{LeftClusterHost}').database('{LeftDatabase}').{LeftTable}
| join kind=inner (cluster('{RightClusterHost}').database('{RightDatabase}').{RightTable} | where PreciseTimeStamp between (datetime({Start}) .. datetime({End}))) on $left.NodeId == $right.NodeId

// join kinds: inner, innerunique (default), leftouter, rightouter,
//             fullouter, leftanti, rightanti, leftsemi

// Cross-cluster join — run on the cluster where MOST data lives
let nodeids = cluster('azcore.centralus.kusto.windows.net').database('AzureCP').SomeTable
    | distinct NodeId;
cluster('azurecm.kusto.windows.net').database('AzureCM').SomeTable
| where NodeId in (nodeids)
```

> **Best practice**: Small table on left. Use `in` instead of `left semi join` for single-column filtering. Use `hint.strategy=broadcast` when left side is small (<100MB).

### Multi-Value & Dynamic

```kusto
cluster('{ClusterHost}').database('{Database}').{Table} | mv-expand Events                        // expand dynamic array to rows
cluster('{ClusterHost}').database('{Database}').{Table} | parse Message with "NodeId=" NodeId:string " State=" State:string  // parse fixed format
cluster('{ClusterHost}').database('{Database}').{Table}
| extend props = parse_json(Properties)
| where props.Category == "Fault"
```

### Variables & Reuse

```kusto
// let: bind scalar or tabular expression
let startTime = datetime(2025-01-01);
let endTime = startTime + 2d;
let nodeids =
    cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
    | where subscriptionId == "{SubscriptionId}"
    | distinct NodeId;

// Use materialize() when referencing same tabular expression multiple times
let expensive = materialize(cluster('{ClusterHost}').database('{Database}').{Table} | where PreciseTimeStamp between (datetime({Start}) .. datetime({End})) | summarize count() by NodeId);
cluster('{ClusterHost}').database('{Database}').{RelatedTable}
| where PreciseTimeStamp between (datetime({Start}) .. datetime({End}))
| join kind=inner (expensive) on NodeId
```

### Time Functions

```text
ago(1h)                      // 1 hour before query time
datetime(2025-03-01 10:00)   // literal datetime
now()                        // current UTC time
bin(PreciseTimeStamp, 5m)    // floor to 5-minute buckets
format_datetime(ts, "yyyy-MM-dd HH:mm")
startofday(PreciseTimeStamp)
```

### String Functions

```text
split(MyResourceID, "/")[2]   // extract substring by delimiter
toupper(s) / tolower(s)
strlen(s)
indexof(s, "Seconds")
substring(s, start, length)
trim_end("}", s)
strcat("prefix", col)
```

---

## Azure Infrastructure Investigation Patterns

### Pattern 1: VM Identification (always start here)

```kusto
cluster('Azcsupfollower').database('AzureCM').LogContainerSnapshot
| where subscriptionId == "{SubscriptionId}" and roleInstanceName has "{VMName}"
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) 
    by containerId, nodeId, tenantName, virtualMachineUniqueId
| order by min_PreciseTimeStamp asc
```

### Pattern 2: Time-Window Node Investigation

```kusto
let StartTime = datetime({BeginTime});
let EndTime   = datetime({EndTime});
let NodeId    = "{NodeId}";
cluster('AzureCM').database('AzureCM').TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp between(StartTime..EndTime)
| where BladeID == NodeId
| project PreciseTimeStamp, BladeID, OldState, NewState
```

### Pattern 3: Cross-Cluster Lookup (filter by subscription's nodes)

```kusto
let nodeids =
    cluster('azcore.centralus.kusto.windows.net').database('AzureCP').SomeTable
    | where PreciseTimeStamp > ago(1d)
    | where SubscriptionId == "{SubscriptionId}"
    | distinct NodeId;
cluster('azurecm.kusto.windows.net').database('AzureCM').OtherTable
| where NodeId in (nodeids)
| where PreciseTimeStamp > ago(2h)
| summarize count() by ServiceVersion
```

### Pattern 4: Latest State (arg_max)

```kusto
cluster('{ClusterHost}').database('{Database}').{Table}
| summarize arg_max(PreciseTimeStamp, *) by NodeId
```

### Pattern 5: Resource ID Decomposition

```kusto
let MyResourceID = "{Resource_id}";
let SubID        = tostring(split(MyResourceID, "/")[2]);
let ResourceGrp  = tostring(split(MyResourceID, "/")[4]);
let VMName       = tostring(split(MyResourceID, "/")[-1]);
```

### Pattern 6: Check Table Latency

```kusto
cluster('Azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| summarize max(PreciseTimeStamp)
| extend latency = now() - max_PreciseTimeStamp
| project latency
```

### Pattern 7: Check Table Retention

```
// Run in Kusto Explorer (management command)
.show database AzureCM policy retention
```

---

## Best Practices (from Microsoft Learn)

| Rule | Do | Don't |
|------|----|-------|
| String search | `has` (token-level, indexed) | `contains` (unindexed) |
| Case comparison | `==` (exact) | `=~` (case-insensitive) unless needed |
| Filter order | datetime first, then string, then numeric | Computed columns first |
| Join table size | Smallest table on left | Large fact table on left |
| Named expressions reuse | `materialize()` | Reference same tabular `let` multiple times |
| Cross-cluster join | Run on cluster with most data | Don't run on the small cluster side |
| New query exploration | Add `\| take 100` while developing | Run unbounded queries on unknown data |
| Table reference | `cluster('<host>').database('<db>').<Table>` | Bare table names, even when the execution context has a default database |

---

## Query Discipline — Error Recovery & Safety

### SEM0100 批量修复

查询因 `SEM0100`（列名无法解析）失败时：

1. **禁止只修报错的那一个列就重试** — 必须检查 `project` 和 `where` 中的**所有**列名
2. 对每个不确定的列名，在 catalog 的 §Query Templates 中查找同表模板确认
3. 若模板中也未出现该列，**先执行 `cluster('<host>').database('<db>').<Table> | getschema` 获取真实 schema 再重写**
4. 一次性修复全部列名问题后再提交重试

> 💡 **原理**：SEM0100 只报告遇到的第一个无效列名就停止，后续列名即使也错了也不会出现在报错中。只修一个列重试，很可能再次失败，浪费查询配额和时间。

### 大结果集防护 (E_QUERY_RESULT_SET_TOO_LARGE)

查询返回 64MB 限制错误时，说明过滤条件太宽泛。按优先级执行：

1. **缩小时间窗口**：将 `between` 范围从数小时缩短到 1-2 小时
2. **加精确过滤列**：用更精确的 ID 列（如 `VmId` 而非 `SubscriptionId`，`ContainerId` 而非 `TenantName`）
3. **兜底限制**：对不确定基数的表，首次查询附加 `| take 500`，确认数据量后再放开

### 并发查询列名独立验证

同时发起多个独立查询时：

1. 每个查询的 `project` 列名必须独立验证（不要假设"跟上一个表结构差不多"）
2. 对同一张表的不同查询，共享已验证的 schema 结果，避免重复 `getschema`

### `project` / alias 使用纪律

1. 不要在 `project` 中用 **与原列同名的 alias** 覆盖原列，例如 `project FaultDetails=substring(FaultDetails, 0, 200)`
2. 若需要截断或重命名现有列，优先使用：
    - `extend FaultDetailsShort = substring(FaultDetails, 0, 200)`，然后 `project ... , FaultDetailsShort`
    - 或 `project FaultDetailsShort = substring(FaultDetails, 0, 200), ...`
3. 原因：同名 alias 容易导致解析阶段丢失原列引用，出现误导性的 `SEM0100` / `Failed to resolve scalar expression`

### 同族表切换纪律

1. `FaultHandling*`、`ServiceHealing*`、`TMMgmt*` 这类表名相近的 ETW 表，**禁止**因为上一个查询成功就假设下一张表拥有同名列
2. 一旦从 `...FaultEvent...` 切到 `...RecoveryEvent...`、从 `Tenant...` 切到 `Node...`、从 `Snapshot` 切到 `Events`，必须重新执行一次 `getschema` 或复用已保存的 schema
3. 经验规则：这类表最常错的不是过滤条件，而是 `project` 阶段引用了上一张表才有的列

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `SEM0100: Failed to resolve column 'X'` | Column doesn't exist in this table | **批量检查所有列** → 先 `cluster('<host>').database('<db>').<Table> \| getschema` → 基于真实 schema 重写（见 §Query Discipline） |
| `SEM0100: Failed to resolve scalar expression named 'X'` | 常见于 `project` 中同名 alias 覆盖原列，或把上一张表的列投影到当前表 | 改用 `extend NewName = ...` 或不同 alias；并重新 `getschema` 检查当前表 |
| `E_QUERY_RESULT_SET_TOO_LARGE (64MB)` | Filter too broad for high-cardinality table | 缩小时间窗口 / 加精确 ID 过滤 / 附加 `\| take 500`（见 §Query Discipline） |
| `Summarize group key is of 'dynamic' type` | Grouping by dynamic column | Add `tostring()` or `toint()` cast |
| `Unknown column 'X'` | Column dropped by earlier `summarize` | Add missing column to `by` clause |
| `Cross-cluster queries not supported` | Wrong cluster for join | Move heavy query to the remote cluster side |
| Query times out | No time filter on large table | Always filter by `PreciseTimeStamp` first |

---

## 文件角色边界说明

本文件（`kql-language.md`）的职责范围：

| 包含 | 不包含 |
|---|---|
| KQL 语法、算子、函数速查 | 如何分层调查 Azure 基础设施问题 |
| 查询编写规范（过滤顺序、join 方向、string 搜索策略） | subsystem 层次模型（属于 `SKILL.md §Phase 0`）|
| 错误恢复规则（SEM0100、大结果集、schema guard） | cluster/table 路由映射（属于 catalog 文件）|
| 跨集群查询模式 | TSG/MSLearn 知识的检索与应用（走 `csswiki` / `mslearn`）|

**调查方法论**（分层查询、Gap 检测、Architecture Grounding）→ `SKILL.md §Phase 0`  
**cluster/table 字典** → `references/catalogs/*.md` / `references/catalog-AzureNetworking.md` / `references/catalogs/*custom*` when present
