# Investigation Loop — the state machine every case follows

> The vm-kusto-query skill is built around three resource layers (catalogs → playbooks → dashboard IGs) plus a schema-exploration fallback. This file defines the **state machine** the agent walks for every case so the iteration loop "find KQL → run → interpret → pick next query" is explicit, not implicit.

---

## States

```
                              ┌───────────────────────────┐
                              │   S0 IDENTIFY             │
                              │   sub / VM / disk / SA /  │
                              │   resource + time window  │
                              └─────────────┬─────────────┘
                                            │
                                            v
                              ┌───────────────────────────┐
                              │   S1 ROUTE                │
                              │   SKILL.md Scenario       │
                              │   Routing → playbook /    │
                              │   catalog / dashboard IG  │
                              └─────────────┬─────────────┘
                                            │
                                ┌───────────v──────────┐
                                │  S2 FIND-AND-RUN     │ ◄────────────┐
                                │  pick KQL by lookup  │              │
                                │  order (Enh 5) and   │              │
                                │  execute via MCP/Py  │              │
                                └───────────┬──────────┘              │
                                            │                         │
                                            v                         │
                                ┌──────────────────────┐              │
                                │  S3 INTERPRET        │              │
                                │  apply result-       │              │
                                │  interpretation.md   │              │
                                │  rules for that      │              │
                                │  pivot query         │              │
                                └───────────┬──────────┘              │
                                            │                         │
                  ┌─────────────────────────┼─────────────────────────┤
                  │                         │                         │
                  v                         v                         │
       ┌──────────────────┐    ┌──────────────────────┐    ┌──────────────────┐
       │ S4a CONCLUDE     │    │ S4b BRANCH           │    │ S5 EXPAND        │
       │ deterministic    │    │ next anchor in       │    │ no/empty result  │
       │ RCA → S6         │    │ same playbook        │    │  → cross-domain  │
       └────────┬─────────┘    └──────────┬───────────┘    │  → schema explore│
                │                         │                └─────────┬────────┘
                │                         └──────────────────────────┤
                │                                                    │
                │                                                    │
                v                                                    v
       ┌──────────────────┐                              ┌──────────────────┐
       │  S6 REPORT       │                              │  ABORT / ESCALATE│
       │  RCA + KQL trail │                              │  collab / PG /   │
       │  + next actions  │                              │  ASMS / Strike   │
       └──────────────────┘                              └──────────────────┘
```

---

## S0 — Identify

Resolve the case into a stable key:

| Investigation type | Key fields | Source |
|---|---|---|
| VM downtime / restart | subscriptionId, vmName (or resourceId), startUTC, endUTC | DFM Customer Statement, ICM Customer Impact, user message |
| Disk lifecycle | subscriptionId, diskName (or diskRPInternalId), region | DFM, ARM |
| CRP operation | subscriptionId, vmName, correlationRequestId or operationId | DFM, ARM error response |
| Storage Account | storageAccountName, region | DFM |
| Host issue | nodeId or cluster + datacenter | Already-running `LogContainerSnapshot` |

If S0 cannot resolve the key, **stop and ask the user**. Don't guess a sub/VM.

Output of S0 is a small JSON the agent re-uses in every later query:
```json
{"sub":"…","vm":"…","startUTC":"2026-06-10T03:00:00Z","endUTC":"2026-06-10T05:00:00Z"}
```

---

## S1 — Route

Match the user's natural-language intent against [`../../SKILL.md`](../../SKILL.md) "Scenario Routing" table. Pick **one** playbook (A–L) or, when intent is just "look up KQL", one catalog. Record the route — the report later cites this choice.

Tie-breakers:
- Time-bounded incident with measurable VM impact → **A** (restart) / **C** (perf) / **F** (disk lifecycle) / **G** (deploy failure)
- Stateful action (create/start/stop/delete/resize) → **B**
- Operation came from CRP/ARM control plane → **B** or **G**
- Maintenance / LM / ADH context → **D**
- Scale set → **E**
- Agent/extension/encryption keyword → **H**
- IMDS/MSI/SAC → **I**
- Storage Account control-plane / billing / recovery → **J**
- Storage perf/throttling → **K**
- Azure Files / AFS → **L**

---

## S2 — Find and Run

For the playbook step you're on, find the KQL in this **lookup order** (see [`conventions.md`](conventions.md#query-lookup-order)):

1. **catalogs/** — curated, stable signature, RCA context
2. **playbook deep file inline §** — playbook-specific, when no catalog version exists
3. **dashboards/<portal>/pages/<slug>/investigation-guide/**.md — bulk fallback
4. **Schema exploration** — see [`schema-exploration-workflow.md`](schema-exploration-workflow.md), only when 1-3 yield nothing

Then run. Default execution: **Azure MCP `kusto` tool**; fall back to `scripts/kusto_runner.py` only when MCP can't (cross-tenant, very large result, ADX-only management commands). Default guardrails from [`operational-discipline.md`](operational-discipline.md): `let _t1/_t2`, time window ≤ 6h on chatty tables, `| take 1000`.

> **Before running any non-template query** apply the **SEM0100 gate** — classify the query (verbatim template → run; only filters changed → run; table/column name changed or ad-hoc → `getschema` first). Full rule in [SKILL.md § Step 2.5](../../SKILL.md#step-25--verify-query-before-sharing-mandatory--the-sem0100-gate); phantom-table / high-hallucination-column blacklist in [`operational-discipline.md` § Known Schema Pitfalls](operational-discipline.md#known-schema-pitfalls--the-sem0100-blacklist-single-source-of-truth). This is also the mid-loop recovery path on any `Sem0001`/`Sem0011` failure.

---

## S3 — Interpret

Look up the query in [`result-interpretation.md`](result-interpretation.md). For pivot queries the file says: "rowCount == 0 → X", "field Y == 'foo' → next anchor §Z". If the query is not listed, fall back to the playbook deep file's narrative.

If interpretation is genuinely ambiguous (multiple plausible faults co-existing), don't guess — collect the next 1–2 supporting queries before deciding.

---

## S4 — Branch

Three exits from S3:
- **S4a CONCLUDE** — interpretation rule says "this is the RCA" deterministically. Go to S6.
- **S4b BRANCH** — rule says "next anchor is §X" or "next pivot query is Q2". Go back to S2 with the new query.
- **S5 EXPAND** — rule says "result empty" or "doesn't match any known pattern". Go to S5.

---

## S5 — Expand

When the standard playbook didn't yield a conclusion, escalate breadth in this order:

1. **Widen time window** — many incidents have precursor signals 2–6h earlier. Bump `_t1` back 4h and re-run the pivot query.
2. **Try the sibling playbook** — A and C both touch VM impact; A and D both touch maintenance; B and G both touch CRP. If you started in the "wrong" one, the routing table's first column will usually have a more specific row.
3. **Cross-domain** — disk failures often start in storage (F → K); restart can be triggered by maintenance (A → D) or hardware (A → hardware-queries.md). Each playbook deep file has a "Cross-link" footer.
4. **Schema exploration** — only when 1–3 give nothing. Use [`schema-exploration-workflow.md`](schema-exploration-workflow.md) to enumerate tables in the cluster that owns the symptom, sample 1 row, then write a one-off KQL. If the cluster.db or table was not previously documented, add it to the relevant catalog per [`conventions.md`](conventions.md#cataloging-new-queries) so the next case finds it in S2.

---

## S6 — Report

**Default output = the shared complete-analysis format** ([`../../../_shared/output/complete-analysis-format.md`](../../../_shared/output/complete-analysis-format.md)) — *not* a terse summary. The whole reason a user used to have to keep asking "and the evidence?" is that S6 used to emit only a digest. Emit the full evidence-inline report by default (chat only; do not write a file unless asked — see top-level output convention).

Render the 5-section envelope:

1. **问题描述 / Issue** — one sentence.
2. **问题时间 / Time (UTC)** — the absolute window you investigated.
3. **环境信息 / Environment** — Resource URI + sub / RG / VM-or-SA / region / size, as identified in S0.
4. **已完成的诊断分析 / Completed Diagnostic Analysis** — **the heart.** One *step* per meaningful query the loop ran (S2→S3). Each step uses the `[kusto]` evidence block from the contract:
   ```
   Step N — <one-line analytical claim>
      [kusto] cluster('<host>').database('<db>').<Table>
              <verbatim KQL — absolute UTC window, parameters inlined, copy-pasteable>
              Result (<N> rows): <≤10 representative rows OR the exact scalar>
              解读: <which result-interpretation rule fired; what the key column value means>
      → 因此: <next query this triggered, OR the part of the root cause it confirms>
   ```
   Reuse the rows you already pinned to the Evidence Ledger (snapshot-before-drop) — the ledger row *is* the evidence block. **Every analytical sentence carries its KQL+result+解读; negative results (0 rows) are rendered the same way and interpreted.** Close with **根因 / Root cause** (traceable to the steps) + **置信度 / Confidence** (below high → name what would raise it, e.g. "Sparkle SEL would confirm the memory ECC trigger").
5. **后续计划 / Next Actions** — for the engineer / for the customer.

> **Nested under a parent skill** (e.g. vm-case-triage autopilot): don't emit the full 5-section report — return the pinned `[kusto]` evidence blocks (query + result + 解读 per step) compactly so the **parent** renders them into *its* complete-analysis report. The parent owns the user-facing artifact.

---

## Stop conditions (apply at every transition)

The loop **must abort and report** when any of these triggers:

| Trigger | Action |
|---|---|
| ≥ 30 KQL run on one case | Stop, summarize what's known + what was tried |
| Same cluster returned 401/403 twice in a row | Stop, route to JIT request ([`operational-discipline.md`](operational-discipline.md#cluster-permission-matrix)) |
| Schema exploration ran for > 5 tables without finding a useful signal | Stop, ask user / escalate to SME |
| User said "stop" / "够了" / "summarize" | Stop immediately, summarize at current state |
| Pivot query consistently returns 0 rows across 3 time-window widenings | Stop, conclude "no platform signal in our data" — hand off to vm-log-analyzer (guest-side) or escalate to the platform PG by opening an ICM manually via ASC (Escalate ticket) |

---

## Cross-references

- Resource layer rules: [`conventions.md`](conventions.md#query-lookup-order)
- Permission, budget, error classification: [`operational-discipline.md`](operational-discipline.md)
- Pivot result → next step: [`result-interpretation.md`](result-interpretation.md)
- Tier-2 schema fallback: [`schema-exploration-workflow.md`](schema-exploration-workflow.md)
- KQL syntax / patterns: [`kql-language.md`](kql-language.md)
- Standard placeholders: [`conventions.md`](conventions.md#variable-convention) + [`_shared-vm-identification.md`](_shared-vm-identification.md)
