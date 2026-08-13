# Verification Pack — V2: Kusto / Platform-Log Reasoning Chain

> **V-type:** V2 — *does the Kusto/platform-log reasoning chain actually hold when you re-run it?*
> **Used by:** `vm-kusto-query`, invoked at a closing gate where a
> Kusto-derived root cause is about to reach a customer (RCA / FQR) or an ICM.
> **Contract:** [`_shared/verifier/verifier-subagent.md`](../../_shared/verifier/verifier-subagent.md) ·
> [`_shared/verifier/evidence-ledger.md`](../../_shared/verifier/evidence-ledger.md)

V2 is where the **differential mechanism earns its keep**: the verifier does not judge "does this
RCA read well" — it **re-runs the load-bearing query itself** (it inherits the `kusto` MCP) and
mechanically diffs the claimed value against the returned value. Grounding alone is not enough here
— a cherry-picked query can be fully GROUNDED yet wrong because the **counter-query was never run**.
So V2 weights **falsification ≥ grounding** (design pivot ③).

---

## 1. Truth source — re-run tools (re-run; do NOT trust the ledger's pasted result)

Re-run via the Azure MCP `kusto` tool (same params the maker uses — see `vm-kusto-query/SKILL.md`
Step 3):

| Param | Value |
|---|---|
| `cluster-uri` | `https://{host}.kusto.windows.net` (**never** `cluster` — internal clusters aren't ARM-registered) |
| `database` | e.g. `AzureCM`, `Disks`, `vmadb` |
| `query` | the verbatim KQL from the ledger row |
| `tenant` | `72f988bf-86f1-41af-91ab-2d7cd011db47` (Microsoft Corp — internal **read-only** access) |
| `auth-method` | `Credential` |

Python fallback: `scripts/kusto_runner.py` when MCP is unavailable.

> **SEM0100 schema gate carries over.** Before re-running, the same rule applies: never accept a
> table/column you haven't seen in a `getschema`/template this session. If the ledger query
> references an unverified identifier, run `<Table> | getschema` first. A query that fails
> `Sem0001`/`Sem0011` is a **fabricated-identifier** signal → `CONTRADICTED`.

---

## 2. 命门 (load-bearing claims) for V2

| Is命门 | Is NOT命门 |
|---|---|
| The **query the root-cause sentence is bound to** (the one whose row/value *is* the conclusion). | Queries that only list VM metadata / size / region. |
| The **correlation/join query** that establishes causality (reboot@03:12 ↔ host event@03:10 — `cross-table-join` / `cross-time-correlation` flag). | Descriptive context queries. |
| Any **over-threshold number** that flips the verdict (latency 4200 ms > 1000 ms SLA; N deaths > threshold — `over-threshold-number` flag). | Numbers that don't gate a decision. |

Fragility sort (from the ledger flags): `single-source-causal > over-threshold-number >
cross-table/time`. Re-run the top **2–3**; stakes dial — RCA-to-customer / ICM → 3.

---

## 3. Checklist (per load-bearing claim)

| # | Check | Fail → class |
|---|---|---|
| 1 | **Value ↔ claim binding** — re-run returns the **exact** value the claim states (count, latency, BootReason, timestamp). | Re-run returns a different value → `CONTRADICTED` → FAIL. Returns nothing → `UNSUPPORTED`. |
| 2 | **Falsification** — the `expected_if_false` counter-query was actually run and came back empty (i.e., the refuting result is genuinely absent). | Counter-query never run, or returns rows → `UNSUPPORTED`/`CONTRADICTED`. |
| 3 | **Branch exclusion** — the alternative causes were enumerated and ruled out by data (e.g., Planned-maintenance ruled out before claiming HostFailure). | Unexcluded live branch → `INFERRED` at best; surface the open branch. |
| 4 | **Time-window covers the incident** — the query's absolute window actually contains the reported impact time (not shifted, not a copy from another case). | Window misses the incident → `CONTRADICTED` (result is about the wrong time). |
| 5 | **Causal ≥2 sources** — a causal claim ("host fault caused the reboot") rests on ≥2 independent signals (e.g., NodeFault event **and** the VM↔node placement record), not one. | Single source → `INFERRED`, flag `single-source-causal`. |
| 6 | **Correlation ≠ causation** — a pure time-adjacency (event A near event B, no shared key) is `INFERRED`, never `GROUNDED`. | Treated as proven cause → downgrade to `INFERRED`. |

---

## 4. Schema semantics to inject (so the verifier isn't a text-differ)

The verifier must read meaning, not strings. Common load-bearing semantics:

- `BootReason` / reboot-classification columns: `HostFailure` / `PlannedMaintenance` /
  `Unplanned` carry **placement implications** — `HostFailure` implies a confirmed host-side fault
  with a node-placement record; do not over-dock a claim that correctly relies on that implication,
  and do not accept `HostFailure` **without** the placement record (check #5).
- Service-Healing / NodeFault tables establish the **platform-initiated** branch; a guest-only
  signal cannot prove platform action (hand the guest side to **V3**).
- The exact cluster/database/table for each scenario lives in `vm-kusto-query/references/catalogs/`
  and `playbooks/` — re-derive the命门 query from there, do not invent a table.

> Inject the relevant column semantics into the critic prompt per case (改点 #3). A generic
> text-differ would over-dock the `HostFailure`→placement inference or miss a missing-placement gap.

---

## 5. Existing parts this pack builds on (don't recreate)

| Existing in `vm-kusto-query` | V2 adds |
|---|---|
| S6 Evidence trail + self-Confidence | an **independent** re-run + deterministic verdict (self-confidence is not a verifier) |
| SEM0100 schema gate (Step 2.5) | re-uses it as the fabricated-identifier check (§1) |
| RCA Report Template (Step 5) | the gate that runs **before** the RCA reaches the customer |

---

## 6. Verifier procedure (V2)

1. Pull the root-cause sentence + bound query rows from the ledger; independently re-derive the命门
   set from the conclusion (flag divergence from the maker's `causal-spine` markings).
2. For each命门 query: confirm it carries an **absolute** window (rewrite `ago()/now()` to the
   ledger's frozen window first — 改点 #4), schema-gate any unverified identifier, then **re-run**.
3. Diff returned value vs claimed value → MATCH / MISMATCH / empty.
4. Run the `expected_if_false` counter-query; confirm the refuting result is genuinely absent.
5. Classify (GROUNDED/INFERRED/CONTRADICTED/UNSUPPORTED), score deterministically, emit the verdict
   JSON ([`verifier-subagent.md` §7](../../_shared/verifier/verifier-subagent.md)).
   - 🟢 PASS → present + badge. 🟡 CONCERNS → downgrade unproven causes to "suspected", qualify
     correlations. 🔴 FAIL → any命门 MISMATCH; block, show the diff, ask the human.

> **Iron rule:** re-run only against **internal read-only** clusters via the `kusto` MCP — never
> connect to the customer's subscription to "double-check."
