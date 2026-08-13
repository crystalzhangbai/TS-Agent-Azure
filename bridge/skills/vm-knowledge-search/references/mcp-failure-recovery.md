# MCP Failure / Auth Recovery

Reference companion to [`SKILL.md §3.5`](../SKILL.md#step-35-mcp-failure--auth-recovery). When an MCP tool call returns a timeout, auth error, or "tool does not exist", apply the matching fallback below **without waiting for the user**.

---

## A. csswiki timeout (~90 s)

1. **First timeout** → retry once with **shorter keywords** (drop one word, keep error code) AND the same routed `project` list.
2. **Second timeout** → skip csswiki for this query. Continue with MS Learn + tell the user explicitly:
   > "CSS Wiki search timed out; results below are from MS Learn + model knowledge."

Why: csswiki backends throttle long-tail wide-keyword queries first; shorter keywords often succeed on retry.

---

## B. csswiki MCP auth failure

**Triggers**: `AADSTS9010010`, `401 Unauthorized`, or persistent failures across multiple unrelated calls in the same session.

The MCP server's token is broken — retries against the MCP won't help. **Fall back to the ADO REST API directly** (works as long as `az` CLI is signed in to Microsoft Corp tenant). Full PowerShell snippet in [`mcp-tools-reference.md §2.7`](mcp-tools-reference.md#27-ado-rest-api-fallback-when-csswiki-mcp-fails-).

**One-liner gist:**
```powershell
$token = (az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv)
# Resource GUID 499b84ac-... is the constant ADO API resource ID — do not change it.

# Search:
#   POST https://almsearch.dev.azure.com/<org>/<project>/_apis/search/wikisearchresults?api-version=7.1
#   Headers: Authorization: Bearer $token
# Read one page:
#   GET https://dev.azure.com/<org>/<project>/_apis/wiki/wikis/<wikiId>/pages?path=<urlencoded path>&includeContent=true&api-version=7.1
```

Tell the user:
> "csswiki MCP auth failed (token issue), falling back to ADO REST API — recommend re-signing in to the csswiki MCP server for next session."

---

## C. Other MCP failures (mslearn / azurewiki / enghub / icm)

Single 500/timeout retry; on a second failure or auth error (401 / `AADSTS*` / "tool does not exist"), apply the per-source fallback below. Always tell the user **which MCP failed** and **what fallback you used**.

> **Skip the retry** if the first error is `Session not found` / `Not connected` / JSON-RPC code `-32001` — the MCP session is permanently lost (server restarted / session GC'd) and a retry hits the same dead session. Go straight to the per-source fallback.

| MCP source | Fallback | Notes |
|---|---|---|
| **mslearn-* MCP** | `fetch_webpage(urls=["https://learn.microsoft.com/<known-path>"], query="<keywords>")` — only if you have a concrete URL (user pasted it, previous search found it, or well-known doc slug). | Do NOT guess a learn.microsoft.com URL — random paths return a polite 404 that fetch_webpage parses as "content". If no URL is known, skip mslearn for this query. |
| **azurewiki-* MCP** | ADO REST API at `dev.azure.com/msazure` (same pattern as §B, only the org changes from `supportability` → `msazure`). | See [`mcp-tools-reference.md §2.7`](mcp-tools-reference.md#27-ado-rest-api-fallback-when-csswiki-mcp-fails-). |
| **enghub-* MCP** | **No anonymous fallback — do NOT `web_fetch` / `fetch_webpage` `https://eng.ms/...` URLs.** eng.ms is AAD-gated: every path 302-redirects to `login.microsoftonline.com/.../authorize?...redirect_uri=...eng.ms/signin-oidc`, which anonymous fetchers can't follow — it's a guaranteed wasted round-trip returning a login page, not content. If the enghub MCP is down, tell the user "enghub MCP unavailable; eng.ms is login-gated and can't be read anonymously — retry after MCP recovers." | For *discovery only* (finding which eng.ms page exists, not reading it), a `web_search(query="site:eng.ms <keywords>")` is acceptable since it returns public search-index snippets — but the page body still requires the MCP. |
| **icm-* MCP** | **No graceful fallback** — ICM data isn't publicly retrievable. Tell the user "ICM MCP unavailable; recommend retry after MCP recovers, or ask the on-call engineer to query manually." | Do not invent incident IDs / summaries. |
| **Linux Vendor KB (`web_search` site-scoped)** | Single retry with slightly broader keywords (drop one token, keep error code). On second failure, drop the `site:` filter and rerun as a plain `web_search` (effectively early-promote to Step 4.5). | `web_search` itself can transient-fail (rate limit / upstream); the search-engine fallback (no MCP involved) is reasonably reliable. |
| **Public `web_search` (Step 4.5)** | **No fallback** — if `web_search` itself fails, tell the user "Public web search unavailable; analysis below is based on internal sources only / model knowledge." | This is the last tier; nothing to fall back to. |

If everything still fails, go to [`SKILL.md §3 Step 4`](../SKILL.md#step-4-default-sources-empty--cross-source-fallback) (cross-source fallback). Do not block the response on a stuck call indefinitely.

---

## 🚫 Critical: NEVER fetch `supportability.visualstudio.com`, `dev.azure.com/supportability`, or `eng.ms` URLs with `web_fetch` / `fetch_webpage`

These are all AAD-gated and always 302 → SSO sign-in, which anonymous fetchers can't follow:
- **ADO wiki** (`supportability.visualstudio.com`, `dev.azure.com/supportability`) → `spsprodcus2.vssps.visualstudio.com/_signin`.
- **eng.ms** → `login.microsoftonline.com/common/oauth2/v2.0/authorize?...redirect_uri=https%3A%2F%2Feng.ms%2Fsignin-oidc&...`.

The fetched body is a login HTML page, not the content — and the 302 doesn't confirm the URL is real (every path triggers the same redirect, so a "successful" fetch tells you nothing about whether the URL exists). Worse, `web_fetch` refuses to follow the redirect entirely (`WebFetchRedirectError`), so it's a guaranteed wasted round-trip before the skill falls back to the MCP.

Always go through:
1. **ADO wiki** → **csswiki MCP** (preferred — handles auth transparently), OR **ADO REST API + `az`-issued bearer token** (per §B above).
2. **eng.ms** → **`enghub-search` / `enghub-fetch` MCP**. There is no anonymous fallback; if the MCP is down, tell the user the page is login-gated and can't be read anonymously.

---

## Why this skill defends so hard against MCP brokenness

The vm-knowledge-search skill chains 2-6 MCP calls per query. With ~98% per-call reliability, an unguarded 6-call flow fails ~11% of the time. The fallbacks here keep the user-facing reliability >99% even when one or two MCPs are flaky — which is exactly what happens in practice (csswiki occasionally times out under load, enghub auth tokens expire silently, ICM does maintenance).
