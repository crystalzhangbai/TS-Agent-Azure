# Evidence Ledger — maker-side contract (shared)

> Status: **infrastructure (P1)**. Loaded by any skill that produces a customer-facing or
> escalation artifact (RCA email, FQR/LQR, CRI, SAP change, doc answer). The ledger is what
> turns verification from *"redo the whole investigation"* into *"scan two flagged lines"*.

This file defines the **Evidence Ledger** every *maker* skill emits **alongside** its artifact.
The companion [`verifier-subagent.md`](verifier-subagent.md) consumes this ledger; the per-skill
[`references/verification-pack.md`](#per-v-pack) supplies the V-type schema semantics.

The ledger is **not** documentation written after the fact. It is built *by construction* during
the investigation — its single most load-bearing rule is **snapshot before drop** (§3).

---

## 0. Why this exists (the one paragraph that matters)

A long investigation compacts. The query that actually proved the root cause gets dropped from
context, and the final artifact ends up asserting a conclusion whose proof is gone. The ledger
forces the maker to **pin the verbatim query + result the moment a hypothesis resolves**, so the
verifier can re-run it deterministically instead of trusting a paraphrase. Pinning *also* forces
the maker to really fetch/run (you cannot pin what you never ran), which incidentally kills
fabrication.

---

## 1. Per-claim row schema

Every claim that appears in the artifact gets one ledger row. A *claim* = any factual assertion
the reader could act on or be misled by.

```yaml
- id: C1
  claim: "Root cause is a host hardware fault on the node hosting VM-X at 03:12 UTC."
  role: causal-spine            # causal-spine | supporting | context
  drives_action: "RCA email tells customer no action needed; platform auto-recovered."
  source: cluster=AzureCM; database=...; table=LogNodeSnapshot
  window_utc: 2026-05-09T03:00:00Z .. 2026-05-09T04:00:00Z   # ABSOLUTE — see §4
  query: |
    <verbatim KQL / tool call, copy-pasteable, parameters inlined>
  result_verbatim: |
    <≤10 representative rows OR the exact returned scalar, PII redacted>
  rows_total: 1
  classification_hint: GROUNDED   # maker's self-tag; verifier re-derives independently
  fragility_flags: [single-source-causal]   # see §2 — drives命门 selection
  expected_if_true: "BootReason=HostFailure present on the host event in-window."
  expected_if_false: "No host fault event; reboot is Planned/Unplanned guest-side."
  applicability: "Applies to this VM only; Gen2; East Asia. Not generalizable to the subscription."
```

### Field rules

| Field | Rule |
|---|---|
| `role` | **Forced choice, not a judgment call.** `causal-spine` = the conclusion stands or falls on it. `supporting` = corroborates but is not load-bearing. `context` = metadata (VM size, region, OS build). Only `causal-spine` rows with a non-empty `drives_action` enter the命门 candidate pool. |
| `drives_action` | Name the **specific closing action** this row props up (the button about to be pressed). If you cannot, the row is `context`, not `causal-spine`. |
| `source` | Concrete target. Kusto → cluster+database+table. Doc → page id / URL. Log → filename + line range. **Never** "general knowledge" — that row is not evidence. |
| `query` | Verbatim, copy-pasteable, parameters inlined. For docs: the exact fetch call + the **verbatim sentence(s)** quoted. |
| `result_verbatim` | The actual returned value/rows — not a summary. This is what the verifier diffs against. |
| `fragility_flags` | Mechanical flags (§2). Drive命门 priority. |
| `expected_if_true` / `expected_if_false` | **Required for reasoning claims (V2/V3).** The built-in falsification: name the result that would *refute* the claim, and confirm you checked for it. |
| `applicability` | Scope envelope — what this claim does and does **not** generalize to. Prevents a single-VM finding being sent as a fleet-wide statement. |

---

## 2. Fragility flags (mechanical — drive命门 selection)

Reasoning fails most often in exactly three places. Flag them so the verifier re-runs the
weakest links first. These are observations, not penalties:

| Flag | Meaning | Why it is fragile |
|---|---|---|
| `single-source-causal` | A causal conclusion ("X caused Y") resting on **one** query/source. | A causal claim needs ≥2 corroborating sources to be GROUNDED; one source is the most fragile shape. |
| `over-threshold-number` | A numeric claim that crosses a decision threshold (4200 ms > 1000 ms SLA; 142 deaths > 100). | One transposed digit flips the verdict — exact-match territory. |
| `cross-table-join` / `cross-time-correlation` | A correlation joined across tables or time windows (reboot@03:12 ↔ host event@03:10). | Timing correlation is `INFERRED`, not `GROUNDED` — the #1 over-claim. |

Flag every applicable shape. The verifier sorts the命门 candidate pool by these flags
(`single-source-causal > over-threshold-number > cross-table/time`).

---

## 3. Snapshot before drop (the load-bearing discipline)

Run this **the moment** a hypothesis flips off `pending` (confirmed / refuted / inconclusive) —
**not** at the end:

1. Capture the **verbatim** query + result that classified it, into the ledger row.
2. Pin the **absolute** time window (§4).
3. Record `expected_if_true`/`expected_if_false` and which branches you excluded.

If you skip this and let context compact, the final self-audit (§5) will flag
`verbatim_unavailable` and **block** the conclusion. Capturing now is the cheap path.

> **One-line rule:** *snapshot before drop.*

---

## 4. Absolute time window (hard rule — learned from feasibility testing)

Every命门 query in the ledger **must** pin an absolute window
(`datetime(2026-05-09T03:00:00Z) .. datetime(2026-05-09T04:00:00Z)`).

**Never** leave `ago()` / `now()` in a ledger query. When the verifier re-runs minutes later, a
relative window shifts and produces a **false MISMATCH** — the conclusion gets wrongly torpedoed.
This is *the* reason snapshot-before-drop is load-bearing: the window must be frozen with the
result.

If a maker query used relative time, rewrite it to absolute **before** pinning it to the ledger.

---

## 5. Fail loud + 5-item self-audit (before emitting the artifact)

Run the 5-item self-check **per hypothesis/causal-spine claim, independently**. Any item fails →
the artifact **must not** state a conclusion for that claim. Surface the gap; do not paper over it.

| # | Item |
|---|------|
| 1 | Query syntax valid; table/column names real and verbatim-recoverable (no fabricated identifiers). |
| 2 | Time window matches **this** case's reported window — absolute, not copy-pasted from another case. |
| 3 | Sample size sufficient — "a pattern" needs N ≥ 10 unless explicitly justified. |
| 4 | Result **actually** supports the claim — not adjacency coincidence ("errors near deploy time" needs the deploy time, not vague proximity). |
| 5 | No conflicting evidence ignored or dropped (the `expected_if_false` branch was genuinely checked). |

**Fail loud:** if working evidence is missing, **refuse to emit the artifact**. A blocker raised
here is the cheapest possible failure; the most expensive is shipping a wrong root cause. Do not
produce false-confidence output.

---

## 6. What the maker hands to the verifier

At a closing gate (send customer / transfer / file ICM / deliver RCA), the maker hands off:

1. **The artifact** (draft email / CRI / SAP change / doc answer).
2. **The full Evidence Ledger** (all rows, this schema).
3. **The relevant V-type(s)** so the verifier loads the right
   `references/verification-pack.md` (V1 doc, V2 Kusto, V3 OS-log, V5 send-gate, V6 route, V7 ICM).

The verifier then re-derives the命门 set independently, diffs the top 2–3, and returns a verdict.
See [`verifier-subagent.md`](verifier-subagent.md).

<a id="per-v-pack"></a>
---

## 7. Per-V verification packs (where schema semantics live)

The ledger is V-type-agnostic. The **meaning** of a given table column, doc source, or redaction
rule lives in each skill's `references/verification-pack.md`, so the verifier is never a generic
text-differ:

| V | Pack |
|---|---|
| V1 doc faithfulness | `vm-knowledge-search/references/verification-pack.md` |
| Other types | added as needed |
