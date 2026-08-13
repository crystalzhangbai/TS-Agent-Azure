# Convert Jarvis Dashboard to Skill Reference

This document describes the end-to-end workflow for converting a Jarvis dashboard JSON export into a skill `references/` markdown file, using the RDOS Shoebox VMPerf dashboard as the worked example.

---

## Overview

Jarvis dashboards contain tiles backed by MDM metrics, Kusto queries, or a mix of both. The goal is to produce a structured markdown reference that the agent can use at runtime to:
- Know which data source (MDM account/namespace, Kusto cluster/database/table) backs each tile
- Understand the query logic and dimension filters for each tile
- Flag confidential tiles that must not be surfaced to external customers

---

## Prerequisites

| Item | Notes |
|------|-------|
| Jarvis dashboard JSON | Export from Jarvis → **Share → Download JSON**. File is typically 100–300 KB |
| Dashboard account/path | E.g. `RDOS / Shoebox / VMPerf-WithParameters` |
| Template parameter list | Identify which parameters drive MDM account, time range, resource IDs |
| Confidentiality policy | Know which tiles (if any) are internal-only |

---

## Step-by-Step Workflow

### Step 1 — Download the Dashboard JSON

1. Open the Jarvis dashboard in your browser.
2. Click **Share** (top-right) → **Download JSON**.
3. Save the file with a descriptive name, e.g. `RDOS_Shoebox_VMPerf_WithParameters.json`.

---

### Step 2 — Discover and Document Template Parameters

Read the `templateParameters` array near the top of the JSON. Each element is a dashboard-level variable that tiles can reference at runtime.

#### 2a — Extract raw parameter attributes

For each parameter, extract:

| JSON Attribute | What It Tells You |
|----------------|-------------------|
| `name` | The token name used to reference this parameter (e.g. `{ParamName}`) |
| `displayName` | Human-readable label shown in the Jarvis UI |
| `defaultValue` | Seed value; reveals the shape of the expected input |
| `type` | `string`, `list`, `datetime`, `bool` — narrows expected values |
| `required` | Whether the dashboard breaks without it |
| `queryParam` | Present only when the parameter overrides a specific MDM dataSource field (e.g. `account`, `namespace`) |
| `hasHint` / `hintQuery` | KQL or MDM query that populates the parameter picker dropdown |
| `allowedValues` | If present, an enumeration of valid values |

#### 2b — Trace each parameter to its tile-level usage

Search the JSON for each parameter `name` (e.g. `"paramName"`) outside of the `templateParameters` block. Parameters appear in tile dataSources in two ways:

1. **MDM dataSource field override** — look for `"overrides"` or `"paramOverride"` arrays inside `dataSources[]`. Each override maps a `queryParam` (e.g. `"account"`) to the parameter name. This means every tile that has this override resolves the MDM field dynamically from the parameter value at query time.

2. **Dimension filter value substitution** — look for `"conditionValue": "{ParamName}"` (or `"value": "{ParamName}"`) inside `dataSources[].filters[].dimensionFilters[]`. This means the filter value is replaced by the parameter at runtime (e.g. filtering by a resource ID or subscription).

3. **Kusto query inline substitution** — look for `{ParamName}` tokens embedded in the KQL text of `dataSources[].kustoClusters[].query`. These are string-replaced before the query is sent.

4. **Time range** — parameters of type `datetime` or named `startTime`/`endTime` control the query time window.

#### 2c — Build the Parameters summary table

For each parameter, record:

| Column | Meaning |
|--------|---------|
| **Name** | Token name as referenced in tiles |
| **Display Name** | Label shown in the UI |
| **Type** | Data type |
| **Default / Example** | From `defaultValue` or `allowedValues` |
| **Used As** | MDM account override / Dimension filter / KQL substitution / Time range |
| **Affected Tiles** | List of tile numbers or "All MDM tiles" |
| **Hint Query** | KQL/MDM query that drives the dropdown, if any |

> **Why this matters:** When the agent generates a query from the skill reference, it must substitute real values for every `{ParamName}` token. Without this mapping, the agent cannot produce runnable queries. The "Used As" and "Affected Tiles" columns make that substitution explicit.

**Example (RDOS VMPerf — for illustration only):**

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles |
|------|-------------|------|-------------------|---------|----------------|
| `Region` | Region | string | `WestUS2` → `AzComputeShoeboxWUS2` | MDM `account` field override | All MDM tiles |
| `VMID` | VM Resource ID | string | `/subscriptions/.../virtualMachines/myVM` | Dimension filter `ResourceId == {VMID}` | Tiles 2–23 |

Record these in the output markdown as a **Parameters** section at the top of the tile reference file.

---

### Step 3 — Enumerate All Tiles by Type

Find the `widgetGroups` / `widgets` / `widgetConfig` array. Each tile is one element.

First check `dataSources[].datasourceType` to classify the tile, then apply the matching schema below.

---

#### 3a — MDM Tile Schema

Applies when `datasourceType == "MDM"` (all dataSources are MDM).

| Field | JSON Path | Notes |
|-------|-----------|-------|
| **Title** | `title` | |
| **Type** | `type` | `MetricsChart`, `Chart` |
| **Data Source** | `dataSources[].datasourceType` | Always `MDM` |
| **MDM Account** | `dataSources[].account` | If `""`, resolved at runtime from a template parameter — see Step 2b. Document as `Dynamic — from \`{ParamName}\` (e.g. \`<resolved-example>\`)` |
| **MDM Namespace** | `dataSources[].namespace` | |
| **Metric(s)** | `dataSources[].metricName` or `dataSources[].metrics[]` | List all metric names if multiple |
| **Sampling Type** | `dataSources[].samplingTypes[]` | `Average`, `Max`, `Min`, `Sum`, `Count` |
| **Dimension Filters** | `dataSources[].filters[].dimensionFilters[]` | For each: `dimensionName`, operator, `conditionValue`. If value is `{ParamName}`, note it is parameter-substituted |
| **Split By** | `dataSources[].groupBy[]` | Dimension used to split chart series, if any |

> **Do not capture:** `width`, `height`, `position`, color settings, or render hints — these are layout-only.

---

#### 3b — Kusto Tile Schema

Applies when `datasourceType == "Kusto"` (all dataSources are Kusto).

| Field | JSON Path | Notes |
|-------|-----------|-------|
| **Title** | `title` | |
| **Type** | `type` | `Chart`, `Grid`, `SuperGrid`, `Logs`, `Table` |
| **Data Source** | `dataSources[].datasourceType` | Always `Kusto` |
| **Cluster** | `dataSources[].kustoClusters[].clusterUrl` | Full URI, e.g. `https://azcore.centralus.kusto.windows.net` |
| **Database** | `dataSources[].kustoClusters[].database` | |
| **Table(s)** | Parsed from `query` | The primary table(s) referenced in the KQL |
| **Key KQL Logic** | `dataSources[].kustoClusters[].query` | Trim to the readable core logic; redact raw data values. Preserve `{ParamName}` tokens and annotate them |
| **Parameter Tokens** | `{ParamName}` occurrences in `query` | List every token and which Step-2 parameter it maps to |

> **KQL trimming guidance:** Keep `let` bindings that define key variables, the main `from` table reference, `where` filters (especially those using `{ParamName}`), and the final `project` / `summarize`. Remove boilerplate or redundant `extend` lines.

---

#### 3c — Mixed Tile Schema

Applies when a single tile has multiple dataSources with **different** `datasourceType` values (e.g. one MDM + one Kusto).

Document as two sub-sections within the same tile entry, one per dataSource, using the MDM schema (3a) and Kusto schema (3b) respectively. Add a note explaining what each source contributes (e.g. "Kusto provides the theoretical maximum; MDM provides the live measured value").

---

#### 3d — Static / HTML Tile Schema

Applies when `datasourceType == "None"` or `type == "MarkDown"` / `type == "Text"`.

| Field | JSON Path | Notes |
|-------|-----------|-------|
| **Title** | `title` | |
| **Type** | `type` | `MarkDown`, `Text`, `Html` |
| **Content summary** | `content` or `markdownText` | One-line description of what the tile displays (links, permission table, onboarding info, etc.) |

> These tiles carry no queryable data. Document them briefly and move on.

---

#### Tile Classification Summary

| Category | `datasourceType` | Tile `type` examples | Schema to use |
|----------|-----------------|---------------------|---------------|
| **MDM** | `MDM` | `MetricsChart`, `Chart` | 3a |
| **Kusto** | `Kusto` | `Chart`, `Grid`, `SuperGrid`, `Logs` | 3b |
| **Mixed** | Both in same tile | Any | 3c (3a + 3b combined) |
| **Static / HTML** | `None` | `MarkDown`, `Text`, `Html` | 3d |

---

### Step 4 — Flag Confidential Tiles

Mark any tile as **[CONFIDENTIAL]** if it:
- Sources data from internal host-level Kusto clusters (e.g. `azcore.centralus.kusto.windows.net`, `azurecm.kusto.windows.net`)
- Exposes infrastructure topology (node IDs, physical rack locations, blade info)
- Exposes internal tooling links (HostAnalyzer, ASI, NetVMA, Node Datapath)
- Is explicitly labeled internal in the dashboard description

Add a warning block at the top of the output markdown:
```
> ⚠️ Tiles marked **[CONFIDENTIAL]** must NOT be shared with external customers.
```

---

### Step 5 — Write the Output Markdown

#### File naming convention
Place the output in the skill's `references/` folder:
```
references/<dashboard-short-name>-tiles.md
```
E.g. `references/rdos-shoebox-vmperf-tiles.md`

#### File header

Every output file starts with this block:
```markdown
# <Dashboard Display Name> — Tile Reference

**Dashboard:** `<Account> / <Path>`

## Template Parameters

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles |
|------|-------------|------|-------------------|---------|----------------|
| `<ParamName>` | <label> | string | <example> | MDM `account` override / Dimension filter `<Dim>` / KQL substitution / Time range | All MDM tiles / Tiles N–M |

> ⚠️ Tiles marked **[CONFIDENTIAL]** must NOT be shared with external customers.

---
```

#### Per-tile blocks

**MDM tile:**
```markdown
## Tile N — <Title>
| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{<ParamName>}` parameter (e.g. `<resolved-example>`) |
| **MDM Namespace** | `<Namespace>` |
| **Metric(s)** | `<MetricName>` |
| **Sampling Type** | Average / Max / Min / Sum |
| **Dimension Filter** | `<DimensionName>` = `{<ParamName>}` *(runtime-substituted)* |
| **Split By** | `<DimensionName>` *(if applicable)* |
```

**Kusto tile:**
````markdown
## Tile N — <Title> [CONFIDENTIAL if applicable]
| Field | Value |
|-------|-------|
| **Type** | Kusto chart / Kusto grid |
| **Data Source** | Kusto |
| **Cluster** | `<clusterUrl>` |
| **Database** | `<database>` |
| **Table(s)** | `<TableName>` |

**Key KQL logic:**
```kql
// {ParamName} = runtime value from template parameter
<trimmed readable query>
```
````

**Mixed tile:**
````markdown
## Tile N — <Title> [CONFIDENTIAL if applicable]
### Kusto Source
| Field | Value |
|-------|-------|
| **Data Source** | Kusto |
| **Cluster** | `<clusterUrl>` |
| **Database** | `<database>` |
| **Table(s)** | `<TableName>` |

**Key KQL logic:**
```kql
<trimmed readable query>
```

### MDM Source
| Field | Value |
|-------|-------|
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{<ParamName>}` (e.g. `<resolved-example>`) |
| **MDM Namespace** | `<Namespace>` |
| **Metric(s)** | `<MetricName>` |
| **Sampling Type** | Average / Max / Min / Sum |
| **Dimension Filter** | `<DimensionName>` = `{<ParamName>}` *(runtime-substituted)* |
````

**Static / HTML tile:**
```markdown
## Tile N — <Title>
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | <one-line description of what the tile shows> |
```

#### Summary table (end of file)

Append a summary table for quick lookup:
```markdown
## Summary Table

| # | Tile Title | Source | Metrics / Tables | Confidential |
|---|-----------|--------|-----------------|:------------:|
| 1 | ... | MDM | `MetricName` | |
| 2 | ... | Kusto `cluster/db` | `TableName` | ✅ |
```

---

### Step 6 — Add Reference to SKILL.md

Append a row to the **Reference Files** table in `SKILL.md`:

```markdown
| [<short-name>-tiles.md](references/<short-name>-tiles.md) | <Dashboard name> tile reference — MDM accounts, metrics, Kusto clusters, dimension filters, KQL logic |
```

---

## Output Quality Checklist

| ✅ | Item |
|----|------|
| ☐ | All template parameters documented in the Parameters table (name, type, default, used-as, affected tiles) |
| ☐ | Every `{ParamName}` token in tile tables traced back to a parameter in the Parameters table |
| ☐ | Hint queries (if any) noted so the agent knows how to resolve valid values |
| ☐ | All N tiles documented (count matches JSON `widgets` array length) |
| ☐ | MDM Account is never blank — always shows `Dynamic — from {ParamName}` with resolved example |
| ☐ | Dimension filter parameter substitutions labeled with *(runtime-substituted from template parameter)* |
| ☐ | KQL query tokens (`{ParamName}`) identified and annotated in KQL blocks |
| ☐ | `Width` field omitted from all tile tables |
| ☐ | Confidential tiles marked with `[CONFIDENTIAL]` heading and ✅ in summary table |
| ☐ | Kusto tiles include trimmed KQL block |
| ☐ | Mixed tiles have both Kusto and MDM sections |
| ☐ | Summary table present at end of file |
| ☐ | Reference row added to SKILL.md |

---

## Worked Example

Dashboard: `RDOS / Shoebox / VMPerf-WithParameters`  
Output file: `D:\source_git\b01sample\skillcovert\asset\RDOS_Shoebox_VMPerf_Dashboard_Tiles.md`

| Stat | Value |
|------|-------|
| Total tiles | 25 |
| MDM tiles | 19 (tiles 2–8, 10–11, 13–23) |
| Kusto-only tiles | 3 (tiles 9, 12, 25) |
| Mixed tiles | 1 (tile 24) |
| HTML / static | 1 (tile 1) |
| Confidential | 4 (tiles 9, 12, 24, 25) |
| Template parameters | `Region` (MDM account), `VMID` (ResourceId filter) |
| MDM namespace | `Shoebox` |
| Kusto clusters | `azcore.centralus.kusto.windows.net/Fa`, `azurecm.kusto.windows.net/AzureCM`, `aznwsdn.kusto.windows.net/aznwmds`, `vmainsight.kusto.windows.net/CAD` |
