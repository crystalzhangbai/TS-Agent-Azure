---
name: confidence-score
version: 1.0.0
description: "Confidence Score framework for naniteAgent. MANDATORY: appends a structured confidence assessment table to EVERY response. Scores Data Source, Query Accuracy, and Diagnosis dimensions with 🟢/🟡/🔴 ratings. Use this skill as the authoritative reference for scoring methodology across all troubleshooting outputs."
---

# Confidence Score Skill

> **Purpose:** Ensure every naniteAgent response includes a reliability assessment  
> **Scope:** ALL responses — troubleshooting, config guides, code review, how-to  
> **Version:** 1.0.0

## Scoring Rules

**🟢 High (85-100%)**
- Query executed via azuremcp MCP with rows returned
- Known troubleshooting pattern from reference files (b01, aks, etc.)
- Official Microsoft documentation referenced
- Schema/table/column names verified before query

**🟡 Medium (50-84%)**
- Partial data returned; query results limited or sparse
- Inference-based diagnosis; pattern partially matches known RCA
- Time range broadened from original request to find data
- Query adapted from reference (not exact match)
- General Azure knowledge applied without live data

**🔴 Low (<50%)**
- Zero query results even after broadening scope
- General knowledge only — no live telemetry queried
- Unverified table/column names used in query
- Speculative root cause with no supporting data
- MCP tool failure — unable to execute query

## Dimensions & Weights

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Data Source** | 40% | Was real telemetry queried via azuremcp, or is this general knowledge? |
| **Query Accuracy** | 35% | Did the KQL execute successfully with relevant results? Were table/column names verified? |
| **Diagnosis** | 25% | Is the conclusion based on observed data patterns, or speculative? |

## Overall Score Calculation

```
Overall = (Data Source × 0.40) + (Query Accuracy × 0.35) + (Diagnosis × 0.25)
```

Icon-to-numeric mapping: 🟢 = 90% · 🟡 = 67% · 🔴 = 25%

## Auto-Scoring Triggers

| Event | Dimension | Action |
|-------|-----------|--------|
| `azuremcp-kusto_query` returned rows > 0 | Data Source | → 🟢 |
| `azuremcp-kusto_query` returned 0 rows | Query Accuracy | → 🔴 |
| MCP server unreachable / error | Data Source | → 🔴 |
| Reference file query used (e.g., vm-dash.md) | Query Accuracy | +10% |
| Schema verified before query execution | Query Accuracy | +5% |
| Time range broadened beyond original | Data Source | → 🟡 |
| Root cause stated with data evidence | Diagnosis | → 🟢 |
| Root cause stated WITHOUT data evidence | Diagnosis | → 🔴 |
| Used "speculative" / "possible" / "might be" language | Diagnosis | → 🟡 |

## Special Cases

| Response Type | Scoring Approach |
|---------------|-----------------|
| Configuration guide / how-to | Data Source 🟢 if from verified docs; Query Accuracy & Diagnosis = N/A |
| Code review / suggestion | Data Source 🟢 if code inspected; Diagnosis = quality of review |
| Dashboard link generation | Data Source 🟢; Query Accuracy = N/A; Diagnosis = N/A |
| Multi-step investigation | Score each step; final score = weighted average of steps |

## Action Recommendations

| Overall Score | Recommended Action |
|--------------|-------------------|
| 85-100% 🟢 | Proceed with confidence; use findings in case notes |
| 50-84% 🟡 | Review findings critically; consider additional queries or escalation |
| < 50% 🔴 | Treat as initial guidance only; escalate or gather more data before acting |

## Reference

For scored examples (High / Medium / Low / Config scenarios), see:
- [confidence-score.md](references/confidence-score.md)
