# DFM write-operation safety gate

> Shared fact source — see [`README.md`](README.md). This is the **standing
> write-safety rule** for every sw-skill that mutates DFM (notes, labor, phone
> calls, emails, collaborations, case status/resolve). Read alongside
> [`page-context.md`](page-context.md) (where an operation is allowed to run) and
> [`error-diagnosis.md`](error-diagnosis.md) (what to do when a write fails).

## The core rule

> **Before executing ANY write operation, show the user the exact content that
> will be written and wait for explicit confirmation. Never auto-execute a write
> without the user's go-ahead.**

This applies whether the write goes through the OData core (`Invoke-DfmApi` POST/
PATCH/DELETE) **or** through a UI fill. The transport doesn't change the rule — a
write is a write.

## Show-before-confirm — what to display per operation

| Operation | Owning skill | Show before confirming |
|---|---|---|
| Add Timeline note (annotation) | (DFM Timeline note — manual) | Note **subject + full body** (rendered as it will post; note if `-Html`) |
| Batch notes | (DFM Timeline note — manual) | Per-case **subject + body**, and the full case list being written |
| Record Labor | (future) | Classification, duration, description, date |
| Add Phone Call | (future) | Subject, direction, the contact/party |
| Send / reply email | (draft customer FQR/LQR/RCA manually) | **Full email body + recipients** (To/Cc) |
| Fill Create Collaboration | (Create Collaboration — manual) | Title + body **before** filling; then **stop** — see collab carve-out below |
| Edit SAP | vm-case-triage | Current SAP → target SAP |
| Update case status (PATCH) | (future) | Current status → target status |
| Resolve / Close case | (future) | Resolution subject + the fact it closes the case (and that Open activities must be closed first) |

## Low-risk exceptions — may run without a confirmation prompt

Pure reads and navigation are not writes; run them directly:

- OData **GET** queries via `Invoke-DfmApi` (case fields, notes, emails, labor, ICM details, …)
- `Get-DfmIncidentId`, `Get-DfmCaseStatement` (read/scrape only)
- Opening / navigating a case, switching tabs, refreshing the timeline
- Printing a draft/template to chat for the user to review

> A read that *prepares* a write (e.g. reading the incident to pre-fill a collab)
> is still a read — but the **write that follows it** goes through the gate above.

## Create Collaboration carve-out (Decision D7 — stricter than the base rule)

The collab form has two actions that are **never automated**, even with
confirmation, because they have no rollback once queued:

1. **Support Area Path** — the cascading tree is **human-selected only**. The skill
   *suggests* the path (it may read it from the incident via OData) and *prints*
   it, but never auto-clicks the cascade. Lazy-render + ambiguous segment names +
   schema drift make auto-selection silently mis-route.
2. **Submit** — **never auto-click**. The skill fills Title + Body, runs
   pre-submit validation, then stops on the open form for the engineer to verify
   SAP + content and click Submit manually.

See [`dfm-collab-field-reference.md`](dfm-collab-field-reference.md)
for the full D7 rationale.

## Agent autonomy boundary

What the agent may change on its own vs. what needs explicit human confirmation
(adapted from the proven d365-case-ops boundary table):

| Action | Agent autonomous | Needs human confirm |
|---|:---:|:---:|
| Fix a broken/stale selector | ✅ | |
| Fix a script logic bug | ✅ | |
| Fix an OData endpoint / field-name drift | ✅ | |
| Add a new type-recognition branch (e.g. new Timeline item type) | ✅ | |
| Update docs / selector / API mappings | ✅ | |
| Update the incidentId cache file | ✅ | |
| Create a brand-new script | | ✅ |
| Delete or rename an existing script | | ✅ |
| Change an existing script's behavior logic | | ✅ |
| Execute ANY write operation (add/record/edit/delete/send/submit) | | ✅ |

> The bottom four rows are the hard line: **no new/deleted scripts, no behavior
> changes, and no writes without a human in the loop.** When refactoring touches a
> write path, re-confirm the behavior is unchanged or get sign-off.

## Why this lives in `_shared/dfm/`

Before this, each skill restated (or silently omitted) its own confirmation rule.
Centralizing it means: one rule, one place; every write-capable skill links here
instead of drifting. When you add a new write operation to any skill, add its row
to the show-before-confirm table above.
