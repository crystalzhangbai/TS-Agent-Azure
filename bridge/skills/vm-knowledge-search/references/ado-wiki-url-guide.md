# ADO Wiki URL Construction Guide

How to build clickable browser links from wiki search results, plus the special handling needed for Code Wikis.

> **Important update (2026-06)**: under Copilot CLI, **csswiki Project Wikis (e.g., AzureIaaSVM) no longer need any path conversion**. `csswiki-search_wiki` returns a `pagePath` field (space-separated, human-readable) which can be fed directly into `csswiki-wiki(action="get_page")`. A single `csswiki-wiki(action="get_page", includeContent=true)` call returns both `page.id` and `page.content` — no two-step lookup needed. This document is kept mainly for Code Wiki edge cases, domain rules, and the known-pageId cache.

> 🚫 **The URLs built here are for humans to click in a browser — do NOT fetch them with `web_fetch` / `fetch_webpage`**. All `supportability.visualstudio.com` and `dev.azure.com/supportability` URLs require AAD SSO; anonymous HTTP requests get 302-redirected to `spsprodcus2.vssps.visualstudio.com/_signin` and return the login-page HTML instead of wiki content. The 302 also can't be used to verify whether a URL is real (every path triggers the same redirect). **For programmatic wiki content access, use the `csswiki-*` MCP tools or the ADO REST API + az-token approach in `mcp-tools-reference.md §2.7`.**

---

## Table of contents

1. [Project Wiki one-step flow (common case)](#1-project-wiki-one-step-flow-common-case)
2. [Code Wiki pageId lookup (paged search)](#2-code-wiki-pageid-lookup-paged-search)
3. [Fallback strategy when pageId lookup fails](#3-fallback-strategy-when-pageid-lookup-fails)
4. [Per-org domain reference](#4-per-org-domain-reference)
5. [URL templates and slug rules](#5-url-templates-and-slug-rules)
6. [Code Wiki content read (repo_file / Git Items fallback)](#6-code-wiki-content-read-repo_file--git-items-fallback)
7. [Known page ID reference (SUSE SAP, etc.)](known-page-ids-suse-sap.md) — moved to a separate file

---

## 1. Project Wiki one-step flow (common case)

Applies to Project Wikis such as Supportability / **AzureIaaSVM**.

```python
# Step 1: search
result = csswiki-search_wiki(searchText="RDP internal error MachineKeys", project=["AzureIaaSVM"], top=5)
# -> result.results[0].pagePath = "/SME Topics/Cant RDP SSH/TSGs/VM Responding/Internal error - MachineKeys_RDP SSH"

# Step 2: one-shot read (returns pageId + content)
page = csswiki-wiki(
    action="get_page",
    wikiIdentifier="AzureIaaSVM",
    project="AzureIaaSVM",
    path=result.results[0].pagePath,
    includeContent=true
)
# -> page.page.id      = 758780
# -> page.page.content = "---\nTags:\n- cw.TSG\n...\n## Symptoms\n..."

# Step 3: build the browser URL (see §5)
url = f"https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/{page.page.id}/Internal-error-MachineKeys_RDP-SSH"
```

> **Key point**: the `pagePath` field is already a space-separated, decoded path. No `-%2D-` substitution, no `.md` stripping — feed it in as-is.

---

## 2. Code Wiki read flow — strip `wiki.mappedPath` from pagePath

`csswiki-search_wiki` always returns a `wiki.mappedPath` field on every result. That field tells you exactly what to strip from `pagePath` before calling `get_page`:

| Wiki type | `wiki.mappedPath` example | What to strip from `pagePath` |
|---|---|---|
| **Project Wiki** (AzureIaaSVM, AzureBackup, AzureSiteRecovery, ...) | `"/"` | nothing — pass `pagePath` as-is |
| **Code Wiki** (AzureLinuxNinjas, AzureSQLVM, SQLServerWindows, most Windows*, msazure repos) | `"/<wikiName>"` (e.g. `"/AzureLinuxNinjas"`) | the value of `mappedPath` (the wiki repo's top-level folder is the wiki name itself, but `get_page` wants the path relative to the wiki root) |

**Universal one-liner** that works for both: `path = pagePath.removeprefix(mappedPath.rstrip("/"))` — when `mappedPath` is `/`, the rstrip yields `""` and `removeprefix("")` is a no-op; when it's `/AzureLinuxNinjas`, the strip happens. No `list_pages` pagination needed.

```python
# 1. Search
result = csswiki-search_wiki(
    searchText="SAP HANA Pacemaker SBD",
    project=["AzureLinuxNinjas"],
    top=5
)
hit = result.results[0]
# hit.pagePath        = "/AzureLinuxNinjas/GeneralPages/Azure/TGs/Azure Linux Clustering/SUSE SAP HANA and Clustering/How to configure Pacemaker Cluster on SUSE VM with SBD fencing"
# hit.wiki.mappedPath = "/AzureLinuxNinjas"

# 2. Strip mappedPath and call get_page
stripped = hit.pagePath.removeprefix(hit.wiki.mappedPath.rstrip("/"))
# stripped = "/GeneralPages/Azure/TGs/Azure Linux Clustering/SUSE SAP HANA and Clustering/How to configure Pacemaker Cluster on SUSE VM with SBD fencing"

page = csswiki-wiki(
    action="get_page",
    wikiIdentifier=hit.wiki.name,
    project=hit.project.name,
    path=stripped,
    includeContent=true
)
# -> page.page.id = 214340, page.page.content = "..."
```

### When strip-mappedPath still 404s (rare edge cases)

If `get_page` 404s even after stripping `mappedPath` — page recently renamed and search index hasn't refreshed, or non-standard layout — fall back in this order:

1. **`list_pages` pagination** (most exhaustive but slow; AzureLinuxNinjas has ~500+ pages, typically 2–5 batches):
   ```python
   csswiki-wiki(action="list_pages", wikiIdentifier="AzureLinuxNinjas",
                project="AzureLinuxNinjas", top=100,
                continuationToken="<last id from previous batch>")
   ```
   If you already know the approximate section (from the directory portion of the search result's `path`), check the [known-pageId cache](known-page-ids-suse-sap.md) first.

2. **`csswiki-repo_file(action="get_content")`** with the raw `path` field (hyphens + `.md` + wiki-name prefix kept) — see §6.

> ⚠️ **Never fabricate a pageId**: search results do **not** contain pageId. Obtain it via `wiki(action="get_page")` (with `mappedPath` stripped) or `wiki(action="list_pages")`. Never invent a number — you'll generate a well-formed but dead link.

---

## 3. Fallback strategy when pageId lookup fails

Try in this priority order:

1. **For Code Wikis: confirm you stripped `wiki.mappedPath` from `pagePath`** (see §2). The most common cause of Code Wiki `get_page` 404s is forgetting this — fixing it is a one-line operation (`pagePath.removeprefix(mappedPath.rstrip("/"))`), not a pagination problem.
2. **Switch to `list_pages` paging** (edge cases: renamed page, non-standard layout — see §2).
3. **Check the §7 known-pageId cache** (avoids re-querying).
4. **Use a `pagePath` URL** (no pageId needed, opens in the browser):
   ```
   https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME%20Topics%2FCant%20RDP%20SSH%2F...
   ```
   URL-encode the `pagePath` field (space → `%20`, `/` → `%2F`, leave the rest).
5. **Wiki search URL fallback** — drop keywords into the search bar:
   ```
   https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas?wikiVersion=GBmaster&pageId=0&_a=search&searchText=Pacemaker+troubleshooting
   ```
6. **Path-only hint** as last resort:
   ```
   > 📍 Wiki path: `/GeneralPages/Azure/TGs/Azure Linux Clustering/SUSE SAP HANA and Clustering/Cluster Troubleshooting TSG`
   > Navigate to this path in the AzureLinuxNinjas Wiki.
   ```

---

## 4. Per-org domain reference

| MCP prefix | ADO org | Correct browser domain | Wrong domain (avoid) |
|---|---|---|---|
| `csswiki-*` (AzureIaaSVM / AzureNetworking / AzureLinuxNinjas / AzureBackup / ...) | Supportability | `supportability.visualstudio.com` | ~~`dev.azure.com/Supportability`~~ |
| `azurewiki-*` | msazure | `msazure.visualstudio.com` | ~~`dev.azure.com/msazure`~~ |

> **Important**: Wiki URLs in the `dev.azure.com/{org}/...` format don't render correctly in the browser (that's the API endpoint, not the page endpoint). **Always use `{org}.visualstudio.com` for links you give to users**. API calls still go through `dev.azure.com`, but that's an MCP-internal detail — never expose it in user-facing links.

---

## 5. URL templates and slug rules

### Canonical URL (with pageId — recommended)

```
https://{org}.visualstudio.com/{project}/_wiki/wikis/{wikiIdentifier}/{pageId}/{page-title-slug}
```

### Fallback URL (no pageId, use pagePath)

```
https://{org}.visualstudio.com/{project}/_wiki/wikis/{wikiIdentifier}?pagePath={urlencoded-pagePath}
```

### Page-title slug conversion rules

| Rule | Description |
|------|-------------|
| Space → `-` | Spaces in the title become hyphens |
| `_` unchanged | Underscores are preserved in the slug |
| `(` `)` `&` unchanged | Special characters are preserved |

> **The slug only affects URL readability**, not page resolution (the pageId is what matters). Derive it from `page.path` in the `csswiki-wiki(action="get_page")` response, or build it from the page title manually.

**Full example**:

| Field | Value |
|---|---|
| page.id | `758780` |
| page.path | `/SME Topics/Cant RDP SSH/TSGs/VM Responding/Internal error - MachineKeys_RDP SSH` |
| page title | `Internal error - MachineKeys_RDP SSH` |
| slug | `Internal-error-MachineKeys_RDP-SSH` |
| Full URL | `https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/758780/Internal-error-MachineKeys_RDP-SSH` |

---

## 6. Code Wiki content read (repo_file / Git Items fallback)

If `csswiki-wiki(action="get_page", includeContent=true)` 404s on a Code Wiki (or any Git-backed Supportability wiki page exposed only through the repo), read the underlying Git repo's markdown file directly:

```python
# 1. Get the repositoryId (note: this is the underlying Git repo GUID, NOT the wiki id)
csswiki-wiki(action="list_wikis")
# -> find the target wiki in the response and read its repositoryId

# 2. Use repo_file to fetch the raw markdown
csswiki-repo_file(
    action="get_content",
    repositoryId="<repositoryId from step 1>",
    project="AzureLinuxNinjas",
    path="/AzureLinuxNinjas/GeneralPages/Azure/TGs/Azure-Linux-Clustering/.../Some-Page.md"   # use the raw `path` from the search result; keep wiki-name prefix when present, hyphens, and .md
)
```

**Variable sources**:

| Variable | Source |
|----------|--------|
| `repositoryId` | `repositoryId` field from `csswiki-wiki(action="list_wikis")` (not the wiki `id`) |
| `project` | `project.name` from the search result |
| `path` | `path` field from the search result (keep the wiki-name prefix when present, hyphens, and the `.md` extension — **do not** use `pagePath`) |

> **Legacy script (PowerShell + Git Items REST API)**: when MCP is unavailable and you need to script bulk operations, you can hit the ADO Git Items REST API directly. Use the same inputs as `csswiki-repo_file`: `project` from the search hit's `project.name`, `repositoryId` from `csswiki-wiki(action="list_wikis")` (not the wiki `id`), and `filePath` from the search hit's raw `path` field (not `pagePath`; keep the wiki-name prefix when present, hyphens, and `.md`). This path is only for batch scripting; day-to-day calls should go through `csswiki-repo_file`.

```powershell
# Backup script: call the ADO Git Items REST API directly
$token = az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv
$headers = @{ Authorization = "Bearer $token" }

$project      = "<project.name from csswiki-search_wiki>"
$repositoryId = "<repositoryId from csswiki-wiki(action='list_wikis')>" # not wiki id
$filePath     = "<raw search-result path; keep wiki-name prefix, hyphens, and .md>"
$escapedPath  = [uri]::EscapeDataString($filePath)

$uri  = "https://dev.azure.com/supportability/$project/_apis/git/repositories/$repositoryId/items?path=$escapedPath&includeContent=true&api-version=7.1"
$item = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
$item.content
```
