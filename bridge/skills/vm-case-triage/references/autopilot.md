# Autopilot Mode

Autopilot lets `vm-case-triage` keep going on its own after the first cockpit: it auto-picks the single highest-value next skill, runs it, folds the findings back in, and continues — up to a hard cap. It exists so an engineer can say "just chase it for me" and get several diagnostic steps without babysitting each hop. The guardrails below are what make that safe.

> **Note:** `vm-knowledge-search` already ran in the first pass (Step 2), so autopilot's job is the **deeper evidence** skills (`vm-kusto-query`, `vm-log-analyzer`). Only re-run `vm-knowledge-search` here if the first-pass search came back empty/thin and a different search term is worth one more try.
>
> **Decide-or-prompt rule:** whenever autopilot can pick the next step on its own, just run it. The only time it stops for the user is when a `[blocking]` Scope Question genuinely needs them (e.g. the exact Resource ID, which of several VMs) or a guardrail is hit — then prompt the user and wait.

## Contents

- [How autopilot is enabled](#how-autopilot-is-enabled)
- [The loop](#the-loop)
- [Selection table](#selection-table)
- [Stop conditions](#stop-conditions)
- [Safety guardrails (non-negotiable)](#safety-guardrails-non-negotiable)
- [Worked example](#worked-example)

## How autopilot is enabled

Either of:

- **Per-run phrase** in the user's message: `autopilot`, `auto`, `自动排查`, `自动诊断`, `一条龙`, "just chase it", "keep going".
- **Persistent toggle**: the user said something like "turn on autopilot for this session". Record it and honor it until they turn it off:
  ```sql
  INSERT OR REPLACE INTO session_state (key, value) VALUES ('vm_case_ir_autopilot', 'on');
  ```
  (Create the `session_state(key TEXT PRIMARY KEY, value TEXT)` table if it doesn't exist.) Check this key at the start of Step 3.

If autopilot is **off**, just print the cockpit (including its Next Skills section) and stop — let the user pick.

## The loop

```
emit cockpit (6 sections)
        │
   autopilot on?  ── no ──▶ stop; user picks from Next Skills
        │ yes
        ▼
pick the #1 next skill via the selection table
        │
check stop conditions ── any hit? ──▶ stop; explain why; hand back to user
        │ none
        ▼
run that skill NESTED (read-only); capture its findings
        │
fold findings into the cockpit; re-classify; increment step counter
        │
   counter < 3  ── yes ──▶ loop
        │ no
        ▼
stop; print a consolidated summary + remaining recommended steps
```

Every auto-step is **visible** — after each nested skill, surface its findings before moving on. Autopilot is "unattended", not "hidden".

> **Terminal output = the complete-analysis format.** Once autopilot has collected real evidence (Kusto rows / log excerpts from the nested skills), the consolidated stop-summary is **not** another hypothesis cockpit — render it in the shared **complete-analysis format** ([`../../_shared/output/complete-analysis-format.md`](../../_shared/output/complete-analysis-format.md)): 问题描述 / 时间 / 环境(含 Resource URI)/ **已完成诊断分析**(fold each nested skill's `[kusto]` / `[log]` / `[doc]` evidence block into a step — claim + evidence + 解读 + 因此/导向)/ 后续计划. The first-pass 6-section cockpit was the *pre-evidence direction*; this terminal report is the *post-evidence finished analysis*, with every step backed by the proof the nested skills returned.

## Selection table

Pick the single highest-value next skill for the current state (this is the same logic as the cockpit's ranked Next Skills — autopilot just takes #1):

| Current strongest signal | Auto-pick |
|---|---|
| A guest-OS log / path / dump was provided or mentioned | `vm-log-analyzer` |
| Platform fault/reboot with a known Resource ID + time | `vm-kusto-query` |
| Performance case (SKU caps already pulled in the first-pass search) | `vm-kusto-query` (XStore throttling / disk-IO-blip evidence) |
| Advisory — the first-pass MS Learn page already answers it | none; stop (or draft the customer reply manually — draft only) |
| First-pass doc search came back empty/thin | one follow-up `vm-knowledge-search` with different terms; if still empty → `vm-kusto-query` |
| Hypotheses grounded by docs but no case-specific evidence yet | `vm-kusto-query` (platform evidence) |
| Strong signal the case isn't VM/Storage scope | **Stage R** (Scope & Route — recommend only, see guardrails) |
| Root cause confirmed, customer needs a reply | manual (draft customer FQR/LQR/RCA yourself — draft only, see guardrails) |

## Stop conditions

Stop the loop and hand back to the user the moment any of these is true:

1. **Root cause confirmed** at high confidence — print the summary, recommend the reply step, stop.
2. **A `[blocking]` Scope Question is unanswered** and only the user can answer it (e.g. the exact Resource ID, which of multiple VMs). Ask it; don't guess.
3. **The next step would cross a safety guardrail** (below). Stop and ask for explicit confirmation.
4. **Step cap reached** — 3 auto-steps. Summarize what's known and list the remaining recommended steps for the user to continue manually.
5. **The next pick repeats a step already run** with no new input — you're looping; stop and ask the user for direction.
6. **A nested skill failed or returned nothing actionable** twice — stop, report it, ask the user.

## Safety guardrails (non-negotiable)

Autopilot may only chain **read-only, internal** diagnostic work. It must never, without explicit user confirmation:

- **Touch a customer subscription.** No `az login` / `Connect-AzAccount` / `az vm|disk|network` / ARM writes against the customer tenant — ever. This is the global Key Rule and autopilot does not relax it. Internal read-only paths (Kusto, knowledge search, log files already provided) only.
- **Send an email.** A customer FQR/RCA may be **drafted** manually, but autopilot stops before sending — the engineer reviews and sends.
- **Change a Support Area Path / transfer the case.** Stage R (Scope & Route) may be auto-invoked to **assess** scope and **recommend** a SAP, but changing the SAP is a state change the user performs manually.
- **Do anything destructive or irreversible** (redeploy, reimage, resize, delete, restart the customer's resource). Recommend it in the guide; never execute it.

If the best next step is one of these, that's stop condition #3: surface the recommendation and wait for a go.

## Worked example

> User: "VM myvm01 rebooted at 2026-06-02 03:15 UTC, no maintenance. Resource ID /subscriptions/aaaa/.../virtualMachines/myvm01. autopilot"

1. Cockpit emitted (Type A, hypotheses: Service Healing / hardware fault / guest panic). First pass already searched `vm-knowledge-search` → cited the reboot-attribution TSG in Reference Links. Autopilot on.
2. Step 1 — selection: known Resource ID + time, no guest log → `vm-kusto-query` "VMA + ServiceHealing for myvm01 @ 03:15 ±10m". Finding folded in: a Service Healing event at 03:14 on the host.
3. Re-classify: still Type A, now leaning platform-initiated, and the cited TSG matches the Service Healing pattern. Root cause confirmed at high confidence (platform Service Healing, expected auto-recovery) → **stop condition #1**. Recommend drafting the RCA manually (draft only — guardrail), and stop.

Consolidated summary printed; 1 of 3 auto-steps used; the email draft is offered as the user's next action.
