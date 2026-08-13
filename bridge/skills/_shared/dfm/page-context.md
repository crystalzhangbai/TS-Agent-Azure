# DFM page-context model

> Shared fact source — see [`README.md`](README.md). DFM (OneSupport Dynamics 365)
> is a UCI (Unified Client Interface) app with distinct page states. This doc says
> **which state an operation needs to be in**. Pairs with
> [`write-safety.md`](write-safety.md) (whether you're allowed to run it) and
> [`api-reference.md`](api-reference.md) (the OData calls themselves).

## Why context matters (and when it doesn't)

- **OData reads/writes via `Invoke-DfmApi` are context-light**: the only
  requirement is that the session is on **some** authenticated DFM page
  (`onesupport.crm.dynamics.com`). A `fetch()` from `about:blank` returns 401. You
  do **not** need to be on the specific case's form to query its `incident` via
  OData — you query by `incidentid`. This is the big advantage of the OData path
  over DOM scraping.
- **UI-fill and DOM-scrape operations are context-heavy**: they require a specific
  page state (the Create Collaboration form must be open; `Get-DfmCaseStatement`
  needs the case's Summary tab with Restricted information expandable). Validate
  the state before acting; fail loudly if it's wrong rather than guessing.

## DFM page states

```
┌───────────────────────────────────────────────────────────────┐
│ Banner: App launcher | "Dynamics 365" | App name | Search | … │
├──────────┬────────────────────────────────────────────────────┤
│ Session  │ Tab list (Dashboard tab | Case tabs)               │
│ list     ├────────────────────────────────────────────────────┤
│ (left)   │ Main content area: Dashboard / Case Form / Dialog  │
│ - Home   │                                                    │
│ - Hub    │ Copilot panel (right, collapsible)                 │
└──────────┴────────────────────────────────────────────────────┘
```

| State | What it is | How you get there | Operations that need it |
|---|---|---|---|
| **Dashboard** | Support Engineer Dashboard (default Home tab) | `Open-DfmHome` lands here | List/search cases; pick a case to open |
| **Case Form** | A case open in a tab — Summary / Timeline / Details / Attachments / Resolve / More Tabs | Open a case from Dashboard or search | DOM scrape (`Get-DfmCaseStatement`); UI edits to case fields; opening the Create Collaboration / email dialogs |
| **Create Collaboration form** | The collab dialog (Title, Body=CKEditor 5, Support Area Path cascade, Submit) | From a Case Form → Create Collaboration | (Create Collaboration — filled manually); **SAP + Submit stay manual — see write-safety D7** |
| **Email editor** | New / reply email (CKEditor 5 body + signature) | From a Case Form timeline / command bar | compose/reply UI fill (draft customer FQR/LQR/RCA manually) |
| **(any DFM page)** | Just authenticated on `onesupport.crm.dynamics.com` | any of the above | **All `Invoke-DfmApi` OData calls** — they target entities by id, not the current tab |

## Session vs Tab model

- **Session list** (left rail): each session is an independent context. `Open-DfmHome`
  uses the `Home` session.
- Opening a case does **not** create a new session — it adds a **Tab** in the
  current session (titled with the case number). You can switch between the
  Dashboard tab and Case tabs.
- Opening a case from global **search** can spawn a new session; opening from the
  Dashboard adds a tab. Either way, an authenticated tab is all the OData path needs.

## iframe note (UI ops only)

- The **App Landing Page** is inside the `#AppLandingPage` iframe — only relevant
  while picking an app. Once a case is open, **all UI operations are on the main
  page** (no `frameLocator`).
- `ClientApiFrame_*`, OneVoice, and Copilot iframes are internal/side-panel — leave
  them alone.

## Context-validation pattern (for UI-fill scripts)

Before a UI fill, confirm the expected element exists and fail clearly if not —
don't guess an alternative:

```powershell
# e.g. before filling the collab form, confirm the dialog is open
$ok = & playwright-cli "-s=$sid" --raw eval "() => !!document.querySelector('.ck-editor__editable')" 2>$null
if (($ok -join '').Trim() -ne 'true') {
    Write-Warning "Create Collaboration form not detected — open it first (don't guess)."; return
}
```

This mirrors d365-case-ops' `Ensure-CaseFormContext` discipline: **verify the page
state, act only if it matches, otherwise stop with a clear message.**

## Practical guidance for ChinaVMSkills

| If you need… | Prefer | Context required |
|---|---|---|
| Case fields (status, severity, SAP, title) | `Invoke-DfmApi` GET on `incident` | any DFM page |
| Customer Statement / Restricted attributes | `Invoke-DfmApi` nav-prop read (fast) **or** `Get-DfmCaseStatement` (DOM, expands the toggle) | OData: any DFM page · DOM: Case Form Summary tab |
| Notes / emails / labor / ICM list | `Invoke-DfmApi` GET | any DFM page |
| Fill a collab Title/Body | UI fill (no verified collab OData entity) | Create Collaboration form open |
| Compose/reply an email body | UI fill (CKEditor) | Email editor open |
