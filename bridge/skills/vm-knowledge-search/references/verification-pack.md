# Verification Pack — V1: Document Faithfulness

> **What this is:** a manual self-check checklist — *is what the AI said actually supported by the
> document it cited?*
> **Run it:** before a doc-derived statement reaches a customer (usually in a manually-drafted reply),
> re-verify it yourself against the cited source.
> **Related:** [`_shared/verifier/evidence-ledger.md`](../../_shared/verifier/evidence-ledger.md)

This pack injects the **V1 schema semantics** so the verifier is a faithfulness checker, not a
generic text-differ. The single load-bearing mechanism is the **forced verbatim quote**: the
customer-facing sentence must be traceable to an *exact* sentence in the re-fetched source —
"cannot paste it ⇒ `UNSUPPORTED`."

---

## 1. Truth source — re-fetch tools (re-fetch, do NOT trust the ledger paraphrase)

| Source | Re-fetch tool | Notes |
|---|---|---|
| **CSS Wiki (AzureIaaSVM + siblings)** | `csswiki-wiki(action="get_page", includeContent=true)` | Returns both `page.id` and `page.content`. Strip `mappedPath` from `pagePath` for Code Wikis (`path = pagePath.removeprefix(mappedPath.rstrip("/"))`). |
| **Microsoft Learn** | `mslearn-microsoft_docs_fetch(url=...)` | Public doc; fetch the full page, not just the search snippet. |
| **EngHub (eng.ms)** | `enghub-fetch(url=...)` | Search returns title+URL only; fetch for body. |
| **ICM** | `icm-get_incident_details_by_id` / `icm-get_ai_summary` | No separate fetch step. |

> ⚠ **Internal wiki: never `web_fetch`.** Internal ADO/EngHub pages must be re-fetched through
> their MCP tool (or `pageId`), never the public `web_fetch` tool. Re-fetching an internal page
> via `web_fetch` either 404s or leaks an auth-gated URL. (Iron rule — do not relax.)

---

## 2. 命门 (load-bearing claims) for V1

| Is命门 | Is NOT命门 |
|---|---|
| The **one or two sentences** the customer-facing statement directly rests on — re-fetch the cited page and confirm the sentence is still there **and still means that**. | Other links in the reference block that the actionable statement does not depend on. |
| A statement carrying an **unstated precondition** (Gen2-only, region-gated, version ≥ X, specific SKU) — the precondition is itself load-bearing. | General background / "see also" context. |

Stakes dial: a doc answer going **straight to the customer** → re-fetch the top 2; a purely
internal lookup → 1.

---

## 3. Checklist (per cited statement)

| # | Check | Fail → class |
|---|---|---|
| 1 | **Faithfulness** — the re-fetched page contains a verbatim sentence that supports the claim. Paste it. | Cannot paste → `UNSUPPORTED`. Page says the **opposite** → `CONTRADICTED`. |
| 2 | **No drift** — the AI did not strengthen/widen the source ("may help" → "fixes it"; "in some cases" → unconditional). | Overstated → `INFERRED` at best; if it inverts meaning → `CONTRADICTED`. |
| 3 | **Applicability** — preconditions in the source (Gen1/Gen2, OS build, region, SKU, version) hold for **this** customer's environment. | Precondition omitted → `UNSUPPORTED` (flag the missing caveat). |
| 4 | **Staleness** — source not >12 months unmodified for a fast-moving topic; if stale, the claim carries a "may be outdated" caveat. | Stale + load-bearing + no caveat → `medium` issue. |
| 5 | **Internal leakage** — if this statement will reach a customer, it carries no internal-only identifiers or auth-gated links (hand off to **V5** for the full send-gate). | Leak present → critical issue, route to V5. |

---

## 4. Migrated grounding assertions (from `evals/evals.json` — now runtime checks)

These were authoring-time eval expectations; as V1 verifier checks they run at the gate:

- **No fabricated `pageId`** — every csswiki link resolves to a **real** `pageId` returned by a
  `get_page` response. A link with an invented/guessed id ⇒ `CONTRADICTED` (the cite does not
  exist).
- **All cited sources have clickable bare URLs**, not just titles. A title with no resolvable URL
  ⇒ `UNSUPPORTED` (uncheckable).
- **No invented IDs** — ICM / work-item / incident numbers must come verbatim from a tool
  response, never fabricated. Invented id ⇒ `CONTRADICTED`.
- **ADO wiki URL domain** — links use `{org}.visualstudio.com`, never `dev.azure.com/Supportability`
  (see [`ado-wiki-url-guide.md`](ado-wiki-url-guide.md)). Wrong domain ⇒ `medium` issue.

---

## 5. Verifier procedure (V1)

1. Pull the **customer-facing statement(s)** from the artifact and the ledger rows that cite docs.
2. **Re-fetch** each cited page with its §1 tool (not `web_fetch` for internal). Pin the page
   `id`/URL from the ledger so you re-fetch the *same* page.
3. For each命门 statement, **paste the verbatim supporting sentence** from the re-fetched content.
   - Found & supports → `GROUNDED`.
   - Found but weaker/conditional than the claim → `INFERRED` (qualify) + note the missing caveat.
   - Page says the opposite → `CONTRADICTED` → **FAIL**.
   - Not present at all → `UNSUPPORTED` → revise one round (downgrade to "the doc suggests…").
4. Run the §4 fabrication checks mechanically.
5. Emit the verdict JSON (schema in
   [`verifier-subagent.md` §7](../../_shared/verifier/verifier-subagent.md)).

> **Why same-model is fine here:** V1 doc interpretation is the *only* place a model swap could
> add value — and the forced verbatim quote removes it. If the critic must paste the exact line,
> "cannot paste ⇒ UNSUPPORTED" is a string comparison, not a judgment a different model would see
> differently.
