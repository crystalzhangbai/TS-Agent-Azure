# Dashboard Reverse-Engineering Workspace

> **Location**: This folder lives inside the `vm-kusto-query` skill at
> `.github/skills/vm-kusto-query/references/dashboards/`. It was moved here
> from the repo root on 2026-06-05 because its sole consumer is this skill.
>
> **Primary purpose**: look up the KQL that powers each ASI/Geneva/etc.
> dashboard panel, so we can run those queries from our playbooks without
> opening the portal. Per-page `replay.py` scripts exist where extracted but
> are *not* the main use case.
>
> **What is committed vs ignored**:
> - ✅ Committed: `library.md`, `library.json`, `meta.json`,
>   `investigation-guide/*.md`, `replay.py`, all tooling
> - ❌ Gitignored: `**/raw/` (per-page API capture, 40+ MB, no KQL value;
>   `library.json` is the extracted subset of `raw/`)

Reverse-engineered query/API libraries behind internal Microsoft dashboards (ASI, Jarvis, Geneva, ARM-based portals, custom service dashboards, …). Each page that you'd otherwise read **visually** (graphs, panels, popups) is decomposed into its underlying **data source** — KQL query, MDM time-series spec, REST API call, etc. — so the data can be replayed by automation and analyzed as structured rows instead of screenshots.

## Why this exists

When debugging a customer case, opening 10+ dashboard tabs and visually scanning graphs is slow and lossy. If we know **exactly which queries** power each panel, we can:

1. Run them headlessly against the underlying data source (Kusto, MDM, ARM, etc.)
2. Filter / join / aggregate the results programmatically
3. Feed structured data into RCA reports without ever opening a browser
4. Replay the same panel across many cases for batch analysis

## Directory layout

```
dashboards/
├── README.md                       ← this file: portal index + workflow
├── source-types.md                 ← classification: how is this dashboard powered?
├── .gitignore                      ← block token files
│
├── <portal>/                       ← one folder per portal namespace
│   ├── README.md                   ← portal-specific auth, API discovery notes
│   ├── _tooling/                   ← portal-specific extractor scripts
│   └── pages/
│       └── <page-slug>/
│           ├── meta.json           ← service, page, URL pattern, params, alias map
│           ├── library.json        ← machine-readable: panel → query/API call
│           ├── library.md          ← human-readable index
│           ├── replay.py           ← page-specific replay script
│           └── raw/                ← intermediate API outputs (optional)
│
└── _playwright-fallback/           ← reusable scraper template for unreverse-engineerable pages
    ├── README.md
    └── template-scraper.py
```

## Portals

| Portal | Folder | Status | Pages extracted |
|--------|--------|--------|----------------:|
| **ASI** (`asi.azure.ms`) | [`asi/`](asi/) | Active — REST API discovered, extractor working | 1 (EEE RDOS / Start Hub: 166 queries / 31 panels) |
| **Jarvis** (Geneva MDM/Logs) | [`jarvis/`](jarvis/) | Stub — awaiting first link | 0 |
| _other portals_ | — | Add namespace as needed |  |

## Workflow for adding a new dashboard

1. **Classify the source.** Open the page in a browser, capture network traffic in DevTools, and consult [`source-types.md`](source-types.md). Decide:
   - KQL-backed (e.g. ASI, Geneva Logs)
   - MDM/Geneva metrics (time-series JSON spec)
   - ARM REST (Azure portal blade-style)
   - Custom service backend
   - Unreverse-engineerable → fall back to [`_playwright-fallback/`](_playwright-fallback/)

2. **If a tooling folder for the portal exists**, run it:
   - ASI: see [`asi/_tooling/README.md`](asi/_tooling/README.md)
   - Jarvis: TBD (will be filled when first dashboard is added)

3. **If no tooling exists yet for that portal**, do a one-off extraction:
   - Capture the relevant API calls + headers from DevTools
   - Save a `library.json` describing the data sources for each panel
   - Use that as a seed to build a reusable extractor later

4. **If the data source genuinely can't be captured** (heavy client-side composition, websocket-only feeds, no addressable API), copy `_playwright-fallback/template-scraper.py` and adapt it.

5. **Write `meta.json`** with URL pattern + param descriptions.

6. **Update the portal table above and the portal README.**

## Security

- **Never commit Bearer tokens / cookies / connection strings.** The `.gitignore` excludes `*token*.txt`, `*.jwt`, etc.
- Token / API access requirements are per portal — see the per-portal README.
- Some Kusto queries require additional database permissions; expect `Access denied` for those if your account lacks the role. Not a bug.

## Replay

Each `pages/<slug>/` contains a `replay.py` you can run directly with the page's input params (vmid, time range, …). Replay scripts depend on the `vm-kusto-query` skill's `kusto_runner.py` for execution.

Example (EEE Start Hub):
```powershell
python dashboards\asi\pages\eee-rdos-start-hub\replay.py `
  --panel "Container / Tenant Health" `
  --vmid <vmid> --containerid <cid> --nodeid <nid> `
  --cluster <cluster> --tenantname <tenant> `
  --role-instance-name <ri> --subscription-id <sub> `
  --start 2026-05-07T23:00:00Z --end 2026-05-08T01:00:00Z
```
