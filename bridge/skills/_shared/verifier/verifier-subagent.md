# Verifier Sub-Agent — verifier-side contract (shared)

> Status: **infrastructure (P1)**. The fresh-context critic that runs at a **closing gate**
> (send customer / transfer / file ICM / deliver RCA) and returns a verdict card. It is an
> **assistant**: it produces `verdict + pinned evidence`, it never sends/transfers/submits.
> Consumes the [`evidence-ledger.md`](evidence-ledger.md) the maker emits; loads the relevant
> per-skill [`references/verification-pack.md`](evidence-ledger.md#per-v-pack) for schema semantics.

The core idea is **differential, not judgment.** Do not ask the critic *"is this conclusion
good?"* (soft). For each load-bearing claim (命门), **re-run / re-fetch and diff**: the claim says
X, the re-execution returns Y, mechanically compare. The verdict lands on the diff, not on a model
opinion. This is what makes it stronger than a static evidence reader (which a fabricated quote
fools) or a self-score (which "confidently wrong → 🟢" defeats).

---

## 1. Who runs it — fresh-context, same model, no swap

| Property | Choice | Why |
|---|---|---|
| **Context** | **Fresh sub-agent** (launched via the `task` tool, not the maker's context). | Cross-agent kills *motivated reasoning* — a clean critic has no prior reasoning chain to defend. This is the dominant effect. |
| **Model family** | **Same family (Claude). Do NOT swap models.** | Re-execution (§4) yields ground truth mechanically, independent of critic model. Cross-model's only residual value is in non-re-runnable doc interpretation (V1) — and that is covered deterministically by the **forced verbatim-quote backstop** below, which is more reliable than betting another model "happens to see it." |
| **V1 backstop** | **Forced verbatim quote.** | For any doc/knowledge claim the critic must paste the *exact* supporting sentence from the re-fetched source. **Cannot paste it ⇒ `UNSUPPORTED`.** This degrades "judgment" into string comparison — same-family critic catches it. |
| **MCP access** | The sub-agent **inherits the MCP servers** (kusto / csswiki / mslearn / enghub …). | Verified feasible: a fresh sub-agent can connect to the cluster and re-run the命门 query itself. The verifier does not need the main agent to run queries for it. |

> Future signal (not now): if real cases repeatedly fail on "the model family *collectively*
> misremembers an Azure behavior — not re-runnable, not catchable by verbatim quote," that is the
> data-driven trigger to reopen cross-model. Until then, same family + verbatim backstop.

---

## 2. Inputs

1. **The artifact** — the draft about to go out (email / CRI / SAP change / doc answer).
2. **The Evidence Ledger** — all rows, per [`evidence-ledger.md`](evidence-ledger.md).
3. **The V-type(s)** in play → load the matching `references/verification-pack.md`(s) for
   re-fetch tools, schema/column semantics, and the per-V checklist (改点 #3: never a generic
   text-differ — the pack injects domain meaning).

---

## 3. Selecting命门 (load-bearing claims) — verifier does this independently

> **命门 = a claim such that, if removed or overturned, the closing action no longer stands.**
> Anchored to the **button about to be pressed**, never to "the longest / most conclusion-shaped
> query."

Three-stage funnel:

1. **Structural filter (mechanical):** only ledger rows with `role: causal-spine` **and** a
   non-empty `drives_action` enter the candidate pool. `context` rows (VM size, region, OS build)
   are out — and are **not scored** (§6, 改点 #2).
2. **Fragility sort (mechanical):** order the pool by `fragility_flags`
   (`single-source-causal > over-threshold-number > cross-table/time`).
3. **Independent re-derivation (judgment, but cross-checked):** from the **final conclusion**, the
   critic reasons *back* to "which claims actually prop up this action" and forms its **own**命门
   set. **If the critic's set ≠ the maker's `causal-spine` markings, that divergence is itself a
   red flag** — the maker may have buried a load-bearing claim as `supporting`. Surface it; treat
   the hidden claim as命门.

**How many to re-run:** top **2–3** by fragility, dialed by stakes —
irreversible/customer-facing/ICM → 3; internal-only note → 1.
Tie-break priority: **irreversible action > single-source-causal > over-threshold-number >
correlation join.**

**The cap is also an over-reasoning detector:** if a conclusion genuinely rests on **>3
independent, each load-bearing** unverified chains, it is too fragile — **press the verdict down
(🔴) directly** rather than re-running six queries.

---

## 4. Verification depth (self-tuned by stakes × ambiguity)

Escalate only as far as the claim warrants — not a fixed pipeline:

```
static diff (every ledger row)
   └─ verbatim quote present in result_verbatim?  classify (§5)
      │
      ▼  for the top 2–3命门 only
re-run / re-fetch (inherit MCP) → diff claim X vs actual Y → mechanical compare
      │
      ▼  for reasoning claims (V2/V3)
falsification: run the expected_if_false / counter-query; confirm which branches were excluded
      │
      ▼  Lab commands (V4)
static by default; actually execute ONLY when the user explicitly says so (vm-lab rule intact)
```

> **Re-run precondition (改点 #4):** before re-running, confirm the命门 query carries an
> **absolute** window. If it still has `ago()/now()`, rewrite to the ledger's frozen absolute
> window first — otherwise a shifted window yields a **false MISMATCH**.

---

## 5. Per-claim classification (改点 #1 — split UNGROUNDED)

For each claim, find the supporting evidence (or re-execution result) and classify. The critical
change from a naive critic: **a missing-evidence claim and a contradicted claim are not the same
failure.**

| Class | Meaning | Trigger | Severity |
|---|---|---|---|
| **GROUNDED** | Verbatim evidence / re-execution **directly** supports the claim. | Exact quote present; re-run matches. | ok |
| **INFERRED** | Logically follows but not directly stated (timing correlation, single-source causal). | Reasonable but not verbatim. | −5 |
| **CONTRADICTED** | Re-run / re-fetch returns the **opposite** of the claim (raw says X, claim says not-X). | `MISMATCH` on a命门 — the maker's evidence is *refuted*. | **critical → hard FAIL** |
| **UNSUPPORTED** | **No** evidence found for the claim (raw is silent / verbatim quote cannot be pasted). | Absence of support — not refutation. | **high → revise one round** |

> **Why the split matters (learned from feasibility testing):** lumping both into one `−20
> UNGROUNDED` bucket either over-punishes an honest evidence gap or under-punishes an outright
> refutation. `CONTRADICTED` (raw打脸) is a hard stop; `UNSUPPORTED` (raw沉默) is a fix-one-version
> caveat.

**Strict rules (apply during classification):**
- Timing correlation = `INFERRED`, never `GROUNDED`.
- Causal claim needs **≥2** corroborating sources to be `GROUNDED`; one source ⇒ `INFERRED` at best.
- Numeric claim must **exactly** match the evidence to be `GROUNDED`.
- **Cannot paste the verbatim supporting line ⇒ not GROUNDED** (the V1 backstop, applies everywhere).

---

## 6. Scoring (deterministic — computed, never self-reported)

```
start = 100
for each scored claim:
    CONTRADICTED (命门)   → critical issue (see verdict rules) ; −20
    UNSUPPORTED (load-bearing) → −20
    INFERRED              → −5
    GROUNDED             →   0
for each issue:
    critical             → −15
    medium               → −5
context-role claims      →   N/A — NOT scored (改点 #2)
score = max(0, start - deductions)
```

**改点 #2 — context claims are N/A.** A claim with `role: context` (e.g. VM size, region) is
**never** penalized for "no raw evidence." Missing raw on a non-load-bearing field is expected, not
a defect. Only `causal-spine` / `supporting` claims are scored. (Feasibility testing showed a
generic critic wrongly docking −20 on VM-size/region rows twice.)

**Verdict bands:**
| Verdict | Rule | Assistant action |
|---|---|---|
| **PASS** | score ≥ 75 **and** no critical issue. | Present + green badge. |
| **CONCERNS** | 50 ≤ score < 74, or ≥75 with a critical issue. | Revise **one** round — downgrade `UNSUPPORTED`/`INFERRED` claims to "suspected"/"likely"; re-present (do not re-verify). |
| **FAIL** | score < 50, **or any命门 `CONTRADICTED`/diff MISMATCH**. | Do **not** send. List the contradicted/missing claims and ask the human how to proceed. |

> A命门 diff `MISMATCH` (`CONTRADICTED`) is a **critical issue by definition** and forces FAIL,
> regardless of the arithmetic score — a refuted load-bearing claim cannot be "averaged away" by
> other grounded claims.

---

## 7. Output schema (the verdict card)

The sub-agent returns JSON only:

```json
{
  "verdict": "PASS | CONCERNS | FAIL",
  "score": 0,
  "confidence": 0.0,
  "summary": "one line",
  "linchpins": [
    {
      "claim_id": "C1",
      "drives_action": "RCA email tells customer no action needed",
      "method": "rerun | refetch | table-lookup | static",
      "claim_value": "BootReason=HostFailure (hardware)",
      "actual_value": "BootReason=PlannedMaintenance",
      "result": "MATCH | MISMATCH | UNSUPPORTED",
      "evidence_quote": "verbatim line from re-execution, or null"
    }
  ],
  "claims": [
    {
      "claim": "…",
      "role": "causal-spine | supporting | context",
      "classification": "GROUNDED | INFERRED | CONTRADICTED | UNSUPPORTED | N/A",
      "evidence_quote": "exact text, or null",
      "reason": "why this classification"
    }
  ],
  "issues": [
    { "severity": "low|medium|high|critical", "description": "…" }
  ],
  "hidden_linchpin_flag": "set if verifier's命门 set != maker's causal-spine markings",
  "spot_check": ["the 1-2 claims a human should eyeball before pressing send"]
}
```

The main agent renders a one-line badge (🟢/🟡/🔴 + score) plus the `spot_check` lines, and **stops
there** — the human presses send/transfer/submit.

---

## 8. Reading the verdict (assistant-mode, human keeps the gate)

- **🟢 PASS** → "Verified (NN/100) — N grounded, N inferred." Human scans ~30s, sends.
- **🟡 CONCERNS** → fix the flagged lines (one round), qualify soft claims, re-present.
- **🔴 FAIL** → block. Show the `CONTRADICTED` / `UNSUPPORTED`命门 and the diff; ask the human
  whether to gather more data or send with explicit caveats. **Never auto-send on FAIL.**

What it does **not** replace: the decision to send/transfer/submit, customer politics and wording
nuance, and novel root causes no checklist covers. It replaces the *manual labor of redoing
grounding*, not the *responsibility of the call*.

---

## 9. Prompt template (for launching the sub-agent)

Launch via the `task` tool, `general-purpose` agent, fresh context. **Stay in the Claude
family** (§1 — no cross-family swap; this is *not* a "swap", just tier selection inside Claude).
**Default model/effort:** `model: 'claude-opus-4.8'`, `reasoning_effort: 'xhigh'` — the strongest
tier, because the residual judgment-heavy steps (命门 selection §3, falsification §4, verbatim
matching §5) benefit from it; the deterministic re-run diff (§6) is model-agnostic, so this only
adds margin, never changes the mechanics. Dial down to `high` / `medium` for internal-only,
low-stakes gates. Same-family rule + forced verbatim-quote backstop remain intact.

```
You are a conclusion-verification critic with a FRESH context — you did NOT run this
investigation. Your job is differential, not judgmental: for each load-bearing claim, RE-RUN or
RE-FETCH the evidence yourself (you have the same MCP servers) and mechanically diff claim-value
vs actual-value. Do not decide "is this good"; decide "does the re-execution match."

INPUTS:
- ARTIFACT: <the draft>
- EVIDENCE LEDGER: <paste full ledger>
- VERIFICATION PACK: <paste the relevant references/verification-pack.md>

DO THIS:
1. From the artifact's CLOSING ACTION, independently re-derive which claims are load-bearing
   (命门). Compare to the ledger's role=causal-spine rows; if they differ, set
   hidden_linchpin_flag and treat the buried claim as a命门.
2. For the top 2-3命门 (fragility-sorted), RE-RUN/RE-FETCH using the pack's tools. Pin the
   ABSOLUTE time window from the ledger before running (no ago()/now()). Diff claim vs actual.
3. For every other ledger row, static-diff: is the verbatim quote actually present in
   result_verbatim? You MUST paste the exact supporting line or it is UNSUPPORTED.
4. For reasoning claims (V2/V3), run the expected_if_false counter-check.
5. Classify each claim (GROUNDED/INFERRED/CONTRADICTED/UNSUPPORTED/N-A), score deterministically
   (§6), and emit the JSON in §7. context-role claims are N/A — never scored.

Rules: timing=INFERRED; causal needs >=2 sources; numbers exact-match; cannot-paste=UNSUPPORTED;
命门 MISMATCH = CONTRADICTED = critical = FAIL.
Respond with JSON only.
```
