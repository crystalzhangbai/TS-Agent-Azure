---
description: Confidence Score examples and extended scoring methodology. This file supplements the SKILL.md with concrete scored examples for agent reference.
---

# Confidence Score — Examples & Extended Reference

> This file contains **examples only**. For rules, triggers, and dimensions, see `../SKILL.md`.

## Positive Triggers (raise score)

| Event | Dimension | Action |
|-------|-----------|--------|
| End-to-end physical path traced (full SOP) | Diagnosis | +10% |
| Multiple data sources cross-validated | Diagnosis | +5% |
| Query from B01 reference file matched exactly | Query Accuracy | +10% |

## Negative Triggers (lower score)

| Event | Dimension | Action |
|-------|-----------|--------|
| Unverified table/column names used | Query Accuracy | → 🟡 |
| `sXInterfaceTable` with wrong column names | Query Accuracy | → 🔴 |
| Cross-cluster join (potential staleness) | Data Source | note in justification |

## Examples

### Example 1: High Confidence (Data-Backed Troubleshooting)

> Queried ER circuit health, found BGP flap pattern matching known RCA.

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Data Source | 🟢 | MCP query returned 47 rows from `cluster('Hybridnetworking').database('aznwmds')` |
| Query Accuracy | 🟢 | Verified query from `expressroute-circuit.md` reference |
| Diagnosis | 🟢 | BGP flap pattern matches known RCA for ER circuit reset |
| **Overall** | **92%** | |

### Example 2: Medium Confidence (Partial Data)

> Query returned limited results after broadening time range. Pattern partially matches.

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Data Source | 🟡 | Query returned 3 rows after broadening from 1h to 24h |
| Query Accuracy | 🟢 | Used verified query from `vpn-gateway.md` |
| Diagnosis | 🟡 | Partial match to known IKE timeout pattern; needs more data |
| **Overall** | **71%** | |

### Example 3: Low Confidence (No Data Found)

> No telemetry data in any time range. General troubleshooting guidance provided.

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Data Source | 🔴 | Query returned 0 rows even with 7d range |
| Query Accuracy | 🟡 | Query syntax verified but no data to validate |
| Diagnosis | 🔴 | General guidance only, no data-backed conclusion |
| **Overall** | **35%** | |

### Example 4: Config/How-To Response

> Provided step-by-step configuration guide based on verified documentation.

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Data Source | 🟢 | Based on verified repo structure and official docs |
| Query Accuracy | N/A | No KQL query involved |
| Diagnosis | N/A | Configuration guidance, not diagnosis |
| **Overall** | **90%** | Factual guidance from verified sources |
