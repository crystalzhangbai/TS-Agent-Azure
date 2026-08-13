# ASI Dashboard Query Extractor

Re-runnable Node.js tooling that reverse-engineers the KQL queries behind any ASI page (`https://asi.azure.ms/services/<svc>/pages/<page>`), by walking the ASI REST API tree:

```
GET /api/services/<svc>/pages/<page>            # page widget tree
GET /api/compoundWidgetGroups/<id>              # recursive sub-panels
POST /api/queries/search  body { selectors }    # full KQL bodies
```

Each extraction produces a self-contained workspace under `../pages/<page-slug>/`.

## Pages already extracted

| Slug | Service / Page | Queries | Panels |
|------|----------------|---------|--------|
| `eee-rdos-start-hub` | EEE RDOS / Start Hub | 166 | 31 |

## How to extract a new page

1. **Capture a fresh Bearer token** for `api://eb092fbe-b5f4-492f-bd9a-3787232fbdeb`:
   - Open the ASI page in a browser, sign in.
   - DevTools → Network → pick any `asi.azure.ms/api/*` request → copy the `Authorization: Bearer ...` header value (just the JWT, no `Bearer ` prefix).
   - Save it to a file e.g. `token.txt` (DO NOT commit — token lifetime ~82 min).

2. **Edit `extract.js`**: set `SERVICE` and `PAGE` constants near the top to match the URL. Set `OUT_DIR` if you want a different output folder.

3. **Run extraction**:
   ```powershell
   cd asi-dashboards\extractor
   node extract.js ..\..\token.txt ..\pages\<page-slug>\raw
   ```

4. **Build the library**:
   ```powershell
   node build-library.js ..\pages\<page-slug>\raw ..\pages\<page-slug>\library
   ```
   Produces `library.json` + `library.md`.

5. **Add a meta.json** (service, page, URL pattern, params, source URL — see existing examples).

6. **Update the table above** and the top-level `asi-dashboards/README.md`.

## Outputs per page (under `raw/`)

- `page.json` — raw page widget tree
- `compound-widget-groups.json` — every CWG referenced from the page (recursive)
- `queries.json` — full KQL bodies + params + schema (deduped by groupId+majorVersion)
- `query-refs.json` — every widget→query reference with panel path
- `extraction-summary.json`

## Replay

Pages that have a panel-organized `library.json` can be replayed via the `vm-kusto-query` skill's `eee_replay.py` (currently hard-coded to EEE Start Hub). For other pages, copy the script and update `LIBRARY_PATH` + page-specific param aliases.

