# Rule Definition

> Source: **Blob Inventory Investigation Guide** dashboard, chapter **Rule Definition** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Blob Inventory Rule Definition

_Widget purpose:_ Rule Definition

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `Rule Definition`

```kusto
BlobInventoryRuleTaskTable
| where DispatchTime between (startofweek(queryFrom) .. queryTo) and AccountName == trim(@"[\s]+", storageAccountName) and isnotempty( RuleDefinition)
| where PolicyRunId has trim(@"[\s]+", policyRunId)
| summarize min(DispatchTime), max(DispatchTime) by RuleDefinition, RuleName, RuleIdentifier
| parse RuleDefinition with * 'objectType":"' ObjectType '"' * 'schedule":"' Schedule '"' *
| project-reorder RuleName, RuleIdentifier, ObjectType, Schedule, min_DispatchTime, max_DispatchTime, RuleDefinition
| sort by  max_DispatchTime desc, RuleIdentifier asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`, `{policyRunId}`

---
