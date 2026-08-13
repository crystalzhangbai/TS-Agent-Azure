---
name: vm-case-triage
description: "Azure VM/Storage case TRIAGE + ROUTING entry point — use it when you just got a case and need a direction, or need to decide if it's even ours and where it goes. Two jobs: (1) Triage — from a pasted case body or free-form symptom, reason as a senior engineer AND search TSG/MS Learn (via vm-knowledge-search) into a 6-section troubleshooting cockpit, with optional autopilot (≤3 steps). (2) Scope & Route — decide VM/Storage in-scope vs out; for out-of-scope recommend the correct Support Area Path (SAP) + owning team from 53k+ paths, resolving borderline ownership (SQL-on-VM, Bastion, ASR, etc.). No DFM auto-fetch; the user changes SAP in DFM manually. Triggers: 'where do I start', 'is this in scope', 'who owns this', 'route/transfer case', '不知道怎么排查', '从哪开始查', '自动排查', '是不是我们的', '转单'. Do NOT trigger when the next action is already known (FQR/RCA → draft customer reply manually; scoped Kusto → vm-kusto-query; a specific log → vm-log-analyzer). Full triggers + disambiguation: references/routing-disambiguation.md."
---

# VM Case Triage — Troubleshooting Entry Point + Scope/Route

The front of the case funnel. It does two related jobs and shares one intake:

- **Triage** — turn your senior-engineer reasoning into a fast, structured troubleshooting
  **direction** (the 6-section cockpit), then point to the right deeper skill.
- **Scope & Route** — decide whether the case is even VM/Storage's to own, and when it isn't,
  recommend the correct **Support Area Path (SAP)** and owning team so the user can transfer it.

**This skill is optional for triage.** Reach for it when you're handed a case (or a raw symptom)
and you're not sure where to begin, or you need to settle ownership. If you already know the next
move — pull specific Kusto, analyze a known log file, write an FQR — go straight to that skill.

Companion files (load on demand):

| File | When to read |
|---|---|
| `references/routing-disambiguation.md` | First — full trigger lists (EN/中文), do-NOT-trigger cases, and the triage-vs-route intent split |
| `references/inline-paste-patterns.md` | Step 1 — recognizing the shape of pasted case text |
| `references/case-type-routing.md` | Step 2 — classify the case to shape hypotheses + pick the next skill |
| `references/output-format.md` | Step 2 — the 6-section template + EN/中文 examples |
| `references/autopilot.md` | Step 3 — read before running autopilot |
| `references/scope-decision-tree.md` | Stage R1 — in/out-of-scope rules |
| `references/support-boundary-rules.md` | Stage R1 — 29 borderline-ownership scenarios |
| `references/sap-tree-tool-guide.md` | Stage R2 — search the SAP tree (`sap-tree-full.json`) / online fallback |
| `references/support-area-path-catalog.md` | Stage R2 — scope metadata (in/out of VM scope) |
| `references/support-area-path-map.md` | Stage R2 — VM-adjacent SAP paths with owning-team names |
| `references/verification-pack.md` | Stage R3 — the V6 closing-gate semantics |

---

## Language

Write the **output** in the language the user asked in — Chinese question → Chinese answer,
English question → English answer. Keep technical identifiers (resource IDs, GUIDs, timestamps,
KQL, Event IDs, log paths, **SAP paths**) verbatim regardless of language. The skill files
themselves are English; that is separate from the output language.

---

## Which job? (intent split)

| You have… | Go to |
|---|---|
| A symptom / case body and you need a **direction** | **Triage** — Step 1 → Step 2 → Step 3 |
| "Is this even ours / who owns this / which SAP / transfer it" | **Scope & Route** — jump to **Stage R** |

Both paths share **Step 1 intake**. The triage cockpit's Step 3 (Next Skills) also routes *inward*
to Stage R when it classifies the case as out-of-scope — you don't hop to a separate skill for that.

---

## Step 1 — Take in the problem (user-provided)

This skill works from text the **user** provides — it does not open DFM. Two shapes:

1. **Inline-pasted case body** — a DFM Q&A block, an advisory/notification, or a full DFM dump.
   Recognize the shape and extract fields per `references/inline-paste-patterns.md`.
2. **Free-form symptom description** — the user just describes what's wrong ("prod VM rebooted at
   3am, no maintenance window"). Use it directly.

Pull these fields when present. Don't invent missing ones — either ask (via a Scope Question) or
leave blank:

| Field | Example |
|---|---|
| Resource ID | `/subscriptions/.../virtualMachines/myvm` |
| Subscription | `aaaa-bbbb-...` |
| Resource Group / VM name | from the Resource ID path |
| Problem start time (UTC) | `2026-06-02T03:15:00Z` |
| OS type | Linux / Windows |
| Issue description | free text |
| Advisory tracking ID (if any) | `5RWW-K4G` |

If all you got is a vague one-liner, still give a **provisional** direction — but lead your Scope
Questions with the 1–2 facts you most need (usually Resource ID + exact UTC time). The point of
this skill is to be useful even when information is thin.

---

## Step 2 — First pass (reason, then search docs)

This is the core triage value: a senior Azure VM/Storage engineer's read on the problem **plus**
the relevant TSG / MS Learn reading, delivered together.

**Reason first, then search.** Form your hypotheses from model knowledge (fast direction), *then*
call `vm-knowledge-search` with the symptom + classified case type to pull the TSGs / MS Learn pages
that actually help troubleshoot this problem. Use the returned docs to sharpen the hypotheses, the
troubleshooting steps, and the fixes — and **cite each doc inline** wherever you lean on it (e.g.
after a root cause or a step), then collect them all in the Reference Links section.

**Still do NOT** in this pass: fetch from DFM, run Kusto, or read guest-OS log files. Those are
deeper, slower, and belong to the next skills.

**Search must not block the cockpit.** Fire `vm-knowledge-search` once. If it times out, errors, or
comes back empty, do **not** stall the triage — emit the cockpit from model knowledge and state
plainly in Reference Links that no relevant docs were found (suggest the user rerun
`vm-knowledge-search` with different terms). A wiki-search hiccup must never swallow the whole IR.

Treat every root cause you list as a **hypothesis with a confidence level**, not a verified fact —
even when a doc backs it, the doc describes a *class* of problem, not confirmation that *this* case
matches. Each hypothesis names *how to confirm it* — and that confirmation is what the next skill
(Kusto / log analysis) does. Citing a TSG raises confidence; it does not turn a hypothesis into a
finding.

### 2.0 Classify the case (quick)

A one-glance classification sharpens the hypotheses, the doc-search terms, and the next-skill pick.
Full signals + per-type recipes live in `references/case-type-routing.md`:

| Type | Signal |
|---|---|
| **A** Fault / Unavailability | reboot / crash / BSOD / can't SSH-RDP / 进不去 |
| **B** Performance | slow / latency / IOPS / 卡 / 慢 |
| **C** Advisory / Maintenance | advisory tracking ID + upcoming-change keywords |
| **D** Post-incident RCA | already-recovered outage, customer wants root cause |
| **E** Quota / Config / How-To | how-do-I / quota / configure, no failure mentioned |

> If the classification keeps landing on "this isn't VM/Storage at all" (guest app, AKS,
> networking-only, backup-only), don't force a troubleshooting cockpit — switch to **Stage R**
> and settle scope/ownership instead.

### 2.1 Emit the 6-section cockpit

Produce exactly these six sections, in order. Template + EN/中文 examples in
`references/output-format.md`:

1. **Interpretation** — restate the problem in engineer terms: symptom, timing, affected resource,
   and the real underlying question.
2. **Scope Questions** — the minimal set needed to narrow it down; tag each `[blocking]` (can't
   proceed without it) or `[nice-to-have]`.
3. **Possible Root Causes & Resolutions** — ranked hypotheses; each = cause + how to confirm +
   likely fix + confidence (high/med/low), with an inline doc citation where one applies.
4. **Step-by-step Troubleshooting Guide** — ordered, verb-led, runnable steps (PowerShell for
   Windows, Bash for Linux); note which step is best handled by which skill, and cite the doc a
   step follows.
5. **Reference Links** — every TSG / MS Learn / KB doc you cited above, as a deduplicated list
   (title + URL + one-line "what it covers"). If the search came back empty, say so here.
6. **Next Skills** — see Step 3.

---

## Step 3 — Section 6: Next Skills (+ autopilot)

The cockpit's **sixth** section is a ranked **Next Skills** list — the deeper, slower investigation
skills, drawn only from the currently-wired set. (`vm-knowledge-search` already ran in the first
pass, so list it here only for a *follow-up* search when the first-pass docs were thin.)

| If you need… | Skill | One-line trigger |
|---|---|---|
| Platform-side evidence (VMA / Service Healing / SEL / kernel panic / disk lifecycle / live migration) | `vm-kusto-query` | "query VMA/ServiceHealing for <VM> at <time>" |
| Guest-OS logs (dmesg / waagent / Event logs / IID / dump / sosreport) | `vm-log-analyzer` | "analyze <path>" |
| Decide whether the case is even ours / recommend a new Support Area Path | **Stage R (below)** | jump to Scope & Route |
| Reply to the customer (FQR / LQR / RCA) | manual (draft customer FQR/LQR/RCA yourself) | "write FQR for <case>" |
| A deeper / different doc search (first-pass docs were thin) | `vm-knowledge-search` | "search the TSG for <failure mode>" |

Default #1 is usually `vm-kusto-query` (platform evidence) for a fault/RCA case, or `vm-log-analyzer`
when a guest log path was provided — the first-pass doc search has already grounded the hypotheses,
so the next move is real evidence.

> Escalation and customer-comms are handled manually for now (open an ICM via ASC; draft the
> customer reply yourself) — they are **intentionally not wired into this router**.

### Autopilot

If the user enabled autopilot — they said `autopilot` / `自动排查` / `自动诊断` / `一条龙`, or set a
session toggle — don't stop at the list. Auto-pick the single highest-value next skill, run it
nested, fold its findings back into the cockpit, re-classify, and continue, up to **3 auto-steps**.
**When autopilot can decide the next step on its own, just run it; only when a `[blocking]` Scope
Question genuinely needs the user (e.g. the exact Resource ID) does it stop and prompt the user.**

The selection table, the 3-step cap, the stop conditions, and the non-negotiable safety guardrails
(never touch a customer subscription, never auto-send an email, never auto-change a Support Area
Path) all live in `references/autopilot.md`. **Read it before running autopilot** — the guardrails
are what make unattended chaining safe. Stage R2 may be auto-invoked to **assess** scope and
**recommend** a SAP, but changing the SAP in DFM is always a manual user action.

---

## Stage R — Scope & Route (decide ownership, recommend SAP)

Reach Stage R when the user's question is about ownership/transfer, or when triage Step 2 classifies
the case as out-of-scope. Two capabilities — pick by intent.

### R1: Scope Decision

1. Use the case statement from triage Step 1/2 (or ask the user to paste it).
2. Apply rules from `references/scope-decision-tree.md`:
   - VM lifecycle, disk attach/detach, boot, perf, extensions → **in scope (VM/Storage)**
   - AKS, networking-only, backup-only, etc. → **out of scope**
   - Borderline: invoke `references/support-boundary-rules.md`
3. If still ambiguous, delegate to vm-knowledge-search with query `"support boundary <topic>"`.
4. Output a clear verdict table:

   | Verdict | Reasoning | Suggested next step |
   |---|---|---|
   | ✅ In scope | `<keyword matched>` | Proceed with triage (Step 2) |
   | ❌ Out of scope | `<keyword matched>` | R2 → recommend SAP |
   | ⚠️ Borderline | `<scenario name>` | See support-boundary-rules.md §Scenario N |

### R2: Recommend Support Area Path + Owning Team

After R1 verdict = out-of-scope (or the user explicitly asks):

1. Classify by problem domain (network / AKS / backup / SQL / SAP / IIS / etc.)
2. **Search `references/sap-tree-full.json`** (53k+ SAP paths, all Microsoft products) with keywords
   from the case. Run from the skill directory so the relative path resolves
   (`cd .github/skills/vm-case-triage`), and always pass `encoding='utf-8'` — the file is UTF-8 with
   non-ASCII characters, and Windows' default cp1252 decode will crash with `UnicodeDecodeError`:
   ```python
   python -c "import json; [print(n['path']) for n in json.load(open('references/sap-tree-full.json', encoding='utf-8')) if 'IIS' in n['path']]"
   ```
   Each node is `{path, id, name, type, state}` — match case keywords against `path`.
   > ℹ️ **This file ships in the repo** (~13 MB, committed), so a fresh clone already has it.
   > In the rare case it's missing or you want to refresh it, fall back to the online SAP Tree tool
   > in `references/sap-tree-tool-guide.md`, and if Case Buddy is installed run
   > `pwsh scripts/sync-sap-tree.ps1` to rebuild it.
3. Cross-reference with `references/support-area-path-catalog.md` for scope metadata (in/out of VM
   scope).
4. For VM-adjacent paths, also check `references/support-area-path-map.md` (local curated list with
   owning team names).
5. Return:
   - **Full Support Area Path** (e.g. `Servers > Internet Information Services > Internet Information Services 10.0`)
   - **Owning team name** (if known)
   - **1-line rationale**
6. If no match in local JSON: output the SAP Tree tool URL + suggested search keywords from
   `references/sap-tree-tool-guide.md`.
7. Optional: if the case statement is ambiguous, draft a scope-clarification FQR manually (keep internal identifiers out).

> 💡 **Keep sap-tree-full.json fresh**: Run `pwsh scripts/sync-sap-tree.ps1` after Case Buddy
> refreshes its cache.

> ⚠️ **User action required**: After getting the recommended SAP, the user must go to DFM and change
> the Support Area Path manually, then click Transfer.

### R3: Verification Gate (V6 — Scope / Route)

Before a scope verdict or a recommended SAP reaches DFM (the user clicks **Transfer**), this is a
**closing gate**.

→ **Self-check before transfer.** Before a scope verdict or recommended SAP reaches DFM (the user
clicks **Transfer**), re-verify each load-bearing fact yourself — re-query the local catalogs and
diff the claimed recommendation against what the catalog actually returns. This section declares
what this gate covers.

- **Pack (domain semantics):** [`references/verification-pack.md`](references/verification-pack.md) —
  the truth is the **catalog lookup, not recall**: re-query `sap-tree-full.json` for the recommended
  path, re-check in/out-of-scope against `support-area-path-catalog.md`, and treat any
  borderline-ownership call as `INFERRED` (never `GROUNDED`).
- **Maker obligation:** emit an Evidence Ledger row per load-bearing claim
  ([`_shared/verifier/evidence-ledger.md`](../_shared/verifier/evidence-ledger.md)) — pin the
  verbatim SAP path + the catalog row it came from.
- **Signature FAIL here:** a path that doesn't exist in the tree ⇒ `CONTRADICTED` ⇒ FAIL; a
  borderline dispute settled as if certain ⇒ `INFERRED`; `sap-tree-full.json` missing ⇒
  `UNSUPPORTED` (don't guess).
- **Boundary:** pure local-catalog lookup — no customer subscription, no DFM write. The card is
  advisory; the **user** changes the SAP in DFM and clicks Transfer.

---

## Output artifacts

Default = **chat only**. Per the global Output Delivery Convention, deliver the cockpit / verdict in
chat; don't auto-write files. Only when the user asks ("save it / 留一份 / 写到文件"), write under
`_work/<case-id-or-slug>/reports/triage.md`.

**Two output shapes, by design:**

- **First-pass 6-section cockpit** (this skill's Step 2) — the *pre-evidence direction*: hypotheses
  + scope questions + next skills, no case-specific Kusto/log evidence yet. This is what you emit
  when autopilot is off and the user picks the next move.
- **Terminal complete-analysis** — once next-skills/autopilot have collected real evidence, the
  finished deliverable is the shared **complete-analysis format**
  ([`../_shared/output/complete-analysis-format.md`](../_shared/output/complete-analysis-format.md)):
  问题描述 / 时间 / 环境(含 Resource URI) / 已完成诊断分析(每步分析 + `[kusto]`/`[log]`/`[doc]` 证据 +
  解读 + 导向) / 后续计划. The cockpit *flows into* this report; don't stop at hypotheses once you have
  proof.

---

## Cross-References (the wired set)

| Need | Skill / file |
|------|-------|
| Search TSG / wiki / MS Learn / known issues | `vm-knowledge-search` |
| Platform Kusto investigation | `vm-kusto-query` |
| Guest-OS log analysis | `vm-log-analyzer` |
| Customer email (FQR / LQR / RCA) | manual (draft customer FQR/LQR/RCA yourself) |
| Closing-gate verification of the scope/SAP verdict | manual self-check before send/transfer |
| Search support boundary wiki | `vm-knowledge-search` |
| **Full SAP tree (53k+ paths, all MS products)** | `references/sap-tree-full.json` ← **search here first** |
| Sync SAP tree from Case Buddy cache | `scripts/sync-sap-tree.ps1` |
| VM-adjacent SAP paths with team names | `references/support-area-path-map.md` |
| Scope classification metadata | `references/support-area-path-catalog.md` |
| Borderline ownership scenarios | `references/support-boundary-rules.md` |
| SAP Tree tool URL + search keywords | `references/sap-tree-tool-guide.md` |
