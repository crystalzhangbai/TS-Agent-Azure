---
description: DSAT/CSAT root cause analysis workflow — 5-phase browser-automated case review via OneSupport DFM, timeline extraction, technical quality assessment, and HTML report generation. Use when performing CSAT/DSAT case reviews or quality audits.
---

# DSAT/CSAT Root Cause Analysis Skill

> **Scope**: Automate end-to-end DSAT/CSAT root cause analysis for Azure support cases  
> **Trigger**: DSAT analysis, CSAT analysis, case review, satisfaction analysis  
> **Browser Automation**: Use `playwright-cli` skill as primary; fall back to `playwright-browser_*` MCP tools if `playwright-cli` is unavailable  
> **Last Updated**: 2026-04-03

---

## Workflow Overview

```
Phase 1: Open Case in DFM Browser
    ↓
Phase 2: Extract Case Metadata (Summary + Details + Survey tabs)
    ↓
Phase 3: Read Complete Email & Notes Timeline
    ↓
Phase 4: Analyze & Compile Root Cause
    ↓
Phase 5: Generate HTML Report
```

---

## Phase 1: Open Case in DFM Browser

### Navigate to OneSupport DFM
```
https://onesupport.crm.dynamics.com/main.aspx?appid=101acb62-8d00-eb11-a813-000d3a8b3117&searchText={CASE_ID}
```

**Steps**:
1. Navigate to URL above (loads Dashboard, not case directly)
2. Find global search box → clear → enter case number → press Enter
3. Wait for search results → click on **case title link**
4. Case opens in new session tab — verify: case number, status, severity, assigned to visible

---

## Phase 2: Extract Case Metadata

### Summary Tab

| Field | Required |
|-------|----------|
| Case Number, Customer Title, Severity, Status/Reason | ✅ |
| Assigned To, Support Area Path, Queue | ✅ |
| Customer/Account Name, Primary Contact, All Contacts | ✅ |
| Service Name, Performance Indicators (Age, 24x7) | ✅ |

### Details Tab

| Field | Required |
|-------|----------|
| Created On, Modified On (date + time) | ✅ |
| Source System, Support Channel, Locale, Country/Region | ✅ |
| Time Zone, Owner | ⚪ |

### Survey Feedback Tab
- Count **(0)**: Record "No survey feedback available"
- Count **> 0**: Read all scores and free-text comments

---

## Phase 3: Read Complete Email & Notes Timeline

> **Most critical phase** — every email and note must be read.

### Process
1. Click **Summary** tab → locate Timeline section
2. Click **"Expand all records"** → wait for "Loading timeline Completed"
3. Take verbose snapshot:
   ```
   playwright-browser_snapshot  → filePath: $env:TEMP\snapshot_case_{CASE_ID}.txt, verbose: true
   ```
4. Use `grep` on snapshot to find entries:
   - Emails: `Email from` + `Rich Text Editor Control incident text`
   - Notes: `Note Created by` / `Note from`
5. Read each entry systematically (newest → oldest): date, sender, type, body content
6. For large timelines: scroll down in browser, take additional snapshots

### Critical Items to Flag

| Item | Why It Matters |
|------|---------------|
| **FQR (First Quality Response)** | Timeliness, accuracy, did it address the problem? |
| **Customer's Original Problem** | Was the right problem being solved? |
| **Technical Depth** | KQL queries, log analysis, actionable recommendations? |
| **Customer Satisfaction Signals** | "resolved", "thank you", "still having issues", silence |
| **Follow-up Count & Frequency** | How many? How soon after last response? |
| **Strike Warnings** | During holidays? Appropriate? |
| **Closure Method** | Customer-confirmed vs 3-strike archive vs auto-close |
| **Holiday/Timezone Factors** | Follow-ups during CNY, Diwali, Christmas, etc.? |
| **Handover/Collaboration** | Was transition smooth? Did customer re-explain? |

---

## Phase 4: Compile DSAT Analysis

### Timeline Organization
Group ALL entries into phases with visual indicators:
- **Phase 1**: Case Creation & Initial Response
- **Phase 2**: Active Technical Engagement
- **Phase 3**: Customer Confirmation / Hold
- **Phase 4**: Follow-up & Closure

```
📥 Customer → Engineer (inbound)
📤 Engineer → Customer (outbound)
📝 Internal Note
🤖 System/Auto Note
```

### Technical Quality Assessment
Rate 4 dimensions with ✅/⚠️/❌:

| Dimension | Evaluate |
|-----------|----------|
| **FQR Quality** | Same day? Addressed actual problem? Actionable? |
| **Technical Depth** | KQL queries? Log analysis? Root cause? Specific recommendations? |
| **Responsiveness** | Response time during active engagement |
| **Resolution** | Actually resolved? Customer confirmed? Or gave up? |

### Root Cause Categorization
- 🔴 **High Probability** — Clear evidence in timeline
- 🟡 **Medium Probability** — Some evidence, plausible
- 🟢 **Low Probability** — Possible but limited evidence

For each: what happened (factual) → why it matters → customer's likely perception

---

## Phase 5: Generate HTML Report

### Required Sections
```
1. Case Overview          — Metadata table
2. Stakeholders           — Contacts & IMs table
3. Complete Timeline      — Phase-grouped chronological tables
4. Technical Quality      — 4-dimension assessment with ratings
5. Root Cause Analysis    — High/Medium/Low probability factors
6. Recommendations        — Case-specific + Process-level tables
7. Summary               — Star ratings (★/☆) grid + conclusion box
```

### Styling
```css
--ms-blue: #0078d4;    /* Primary accent */
--ms-dark: #243a5e;    /* Headings */
--red: #d13438;        /* Critical issues */
--yellow: #ffaa44;     /* Warnings */
--green: #107c10;      /* Good items */
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

### Output
Save to: `$env:TEMP\CSAT_Report_{CASE_ID}.html`
Open in browser: `playwright-browser_navigate` with `file:///` URL

---

## Common DSAT Patterns

| # | Pattern | Signal | Root Cause | Recommendation |
|---|---------|--------|------------|----------------|
| 1 | **Archive instead of confirmed close** | Customer said "resolved" → hold → follow-ups → archive | Didn't recognize closing signal | Ask "Can I close this case?" |
| 2 | **Holiday-insensitive follow-ups** | Strikes during CNY/Diwali/Christmas | Process ignores regional calendar | Check region, pause during holidays |
| 3 | **Over-aggressive follow-up** | Follow-up 1-2 days after "no more help needed" | Rigid SOP without context | Extend interval when customer satisfied |
| 4 | **Tech excellence + process failure** | Great analysis but DSAT 1-2 | Focused on tech, neglected lifecycle | Balance depth with case management |
| 5 | **Unresolved concern** | Customer stops replying mid-investigation | Lost patience/confidence | Summarize proactively, ask specific questions |
| 6 | **Handover issues** | Multiple engineers, customer re-explains | Poor handover docs | Warm handover with complete context |

---

## Pre-Flight Checklist

- [ ] Case opened in DFM, all tabs checked (Summary, Details, Survey Feedback)
- [ ] Header metadata complete (case number, customer, severity, dates, score)
- [ ] ALL emails read — FQR through final closure
- [ ] ALL notes read — VDM, case notes, close-out checklist
- [ ] Timeline organized chronologically into phases
- [ ] Technical quality assessed (4 dimensions)
- [ ] Root causes categorized (High/Medium/Low)
- [ ] Recommendations provided (case-specific + process-level)
- [ ] HTML report generated and opened in browser
