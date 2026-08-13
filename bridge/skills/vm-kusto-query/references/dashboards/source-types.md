# Dashboard Source-Type Classification

When you point at a new dashboard, the **first** question is: *where does its data come from?* The answer determines which extraction strategy applies.

## Decision tree

```
Is there a network request that returns the panel's data?
├─ Yes
│   └─ What kind?
│       ├─ POST /api/queries/search + KQL body                       → KQL/Kusto (ASI pattern)
│       ├─ POST to Kusto cluster endpoint (.kusto.windows.net)       → Direct Kusto
│       ├─ POST to https://*.metrics.nsatc.net/public/monitoringAccount/.../metricSeriesSet
│       │  or *.geneva.com/api/v2/query                              → Geneva MDM (time-series)
│       ├─ Geneva Logs / DGrep query (KQL over Geneva Logs)          → Geneva Logs (KQL variant)
│       ├─ https://management.azure.com/... (ARM REST)               → ARM REST
│       ├─ Custom service backend (per-team REST/gRPC)               → Custom backend
│       └─ GraphQL                                                   → GraphQL
└─ No (page assembles entirely from cached/embedded data, or uses websockets/SignalR)
    → Playwright fallback
```

## Source types

### 1. KQL / Kusto (ADX-backed)

**Pattern**: Dashboard config stores KQL strings; on render the portal POSTs them to a Kusto cluster (or a proxy that wraps Kusto).

**How to identify**:
- Network tab shows requests to `*.kusto.windows.net` or `/api/queries/*` returning JSON with `Tables`/`Rows` structure
- Response payload contains rows of typed values
- Request body contains a `kustoQuery` or `csl` field with KQL-looking text (`where`, `summarize`, `extend`, `project`, …)

**Examples**: ASI, ADX dashboards, parts of Geneva Logs, Azure Data Explorer web UI, parts of Jarvis.

**Extraction strategy**: Discover the dashboard's metadata API (e.g. ASI's `/api/services/<svc>/pages/<page>` + `/api/queries/search`), bulk-fetch query bodies + params + cluster/db, store as a panel-organized library, then replay via `vm-kusto-query/scripts/kusto_runner.py`.

**Replay engine**: `kusto_runner.py` (Python, uses azure-kusto-data SDK).

---

### 2. MDM / Geneva metrics (time-series)

**Pattern**: Numeric time-series stored in Geneva MDM. Query language is a **JSON spec** (account, namespace, metric, dimensions, sampling, aggregation), not KQL.

**How to identify**:
- Requests to `*.metrics.nsatc.net` or `*.metrics.geneva.com` or `metrics.geneva.com/public/monitoringAccount/<acct>/...`
- Request body is JSON with fields like `metricFilter`, `seriesResolutionInMinutes`, `aggregations`, `samplingTypes`
- Response is arrays of (timestamp, value) tuples

**Examples**: Most Jarvis time-series tiles, host-level performance counters surfaced in Azure portal.

**Extraction strategy**: Capture the JSON request templates from the dashboard config; parameterize on time range + dimension values (subscription, resource id, host, …).

**Replay engine**: Direct HTTPS POST to the MDM endpoint with refreshed Bearer token (audience varies — usually `https://metrics.geneva.com`). No Python SDK shortcut; use `requests` + auth.

---

### 3. Geneva Logs (KQL over log streams)

**Pattern**: Like (1) — KQL — but executed against Geneva Logs accounts via DGrep / dgrep-prod endpoints rather than a public Kusto cluster.

**How to identify**:
- Requests to `*.warmpath.msftcloudes.com` or `*.dgrep.msftcloudes.com`
- KQL-looking body, but cluster/database not on the standard `*.kusto.windows.net` list

**Extraction strategy**: Same as KQL/Kusto for the query side; replay engine needs to POST to the Geneva Logs endpoint with proper Geneva auth.

---

### 4. ARM REST (Azure Resource Manager)

**Pattern**: Azure portal blades / Resource Health / Activity Log pull from `management.azure.com`.

**How to identify**:
- Requests to `https://management.azure.com/...?api-version=...`
- Bearer token audience: `https://management.azure.com/`

**Extraction strategy**: Capture the URL templates + the path/query parameters that the page binds; document them as a JSON library.

**Replay engine**: `az rest` or Python `requests` + `DefaultAzureCredential`.

---

### 5. Custom service backend

**Pattern**: Each Azure service team often has its own backend (VMDash, CRP Portal, DiskRP Portal, Health Hub, …). The dashboard hits service-specific URLs returning service-specific JSON.

**How to identify**:
- Hostname is service-specific (e.g. `vmdash.azure.com`, `crpportal.azurewebsites.net`)
- Response schema is service-specific (no Kusto/Tables structure, no MDM time-series structure)

**Extraction strategy**: Document the API as-is (URL pattern + params + response shape). Replay via `requests`. Sometimes the backend is itself a thin wrapper over Kusto — in that case look at the Kusto cluster name in the response and treat as type (1).

---

### 6. GraphQL

**Pattern**: Single endpoint, queries embedded in request body, schema introspection possible.

**How to identify**: POST to `/graphql` with `query: "..."` body.

**Extraction strategy**: Capture all `operationName` + `query` + `variables` combinations. Replay via `requests`.

---

### 7. Playwright fallback

Use **only** when:
- The dashboard composes data entirely client-side (no addressable API per panel)
- The transport is websocket / SignalR / Server-Sent Events with stateful streaming we can't easily replay
- The data is behind aggressive anti-automation (CAPTCHA, CSRF rotation)
- We have a deadline and reverse-engineering would take too long for a one-off case

What to capture instead:
- Full-page screenshot (`playwright-cli screenshot`)
- Accessibility snapshot (`playwright-cli snapshot --raw`) — often has the table values as text
- Specific element screenshots for key panels
- Optionally `playwright-cli eval` to extract DOM text content

See [`_playwright-fallback/`](_playwright-fallback/) for template.

---

## How to investigate a new dashboard

1. Open the page logged in.
2. Open DevTools → Network → filter `Fetch/XHR`, clear, then reload the page.
3. After load, **filter out** noise: static assets, telemetry beacons (`/v2/track`, `applicationinsights`, `1ds.apm.js`), auth (`/authorize`, `/token`).
4. Sort by **response size** (large = likely a data payload) or **time** (request → response order matches panel render order).
5. For each suspicious request:
   - Inspect the **Request URL** → matches one of the patterns above?
   - Inspect the **Request Body** → KQL? JSON metric spec? GraphQL?
   - Inspect the **Response** → table-like? time-series? service-specific?
6. Cross-reference panel titles to API calls by **scrolling** different panels into view and watching new requests fire (lazy-loaded panels are common).
7. Once classified, write up the extraction strategy in the portal's `README.md`.

## Tooling cheat sheet

| Source type | Replay tool | Auth |
|-------------|-------------|------|
| KQL/Kusto | `kusto_runner.py` (azure-kusto-data) | `az login` → AAD device-flow → Kusto cluster |
| MDM Geneva metrics | `requests.post` to metrics.nsatc.net / geneva.com | Bearer for `https://metrics.geneva.com` (or `https://gcs.prod.monitoring.core.windows.net/`) |
| Geneva Logs | `requests.post` to dgrep endpoint | Bearer for Geneva Logs (varies) |
| ARM REST | `az rest` or `requests` + `DefaultAzureCredential` | Bearer for `https://management.azure.com/` |
| Custom backend | `requests` | varies — capture from browser |
| GraphQL | `requests.post` to `/graphql` | varies |
| Playwright | `playwright-cli` | persistent profile / state file |
