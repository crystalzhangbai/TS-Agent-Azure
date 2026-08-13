# Verification Pack — V3: OS-Log Analysis Conclusion

> **V-type:** V3 — *is the guest-OS-log conclusion faithful to the raw log lines and the
> correlation rules?*
> **Used by:** `vm-log-analyzer`, invoked at a closing gate where a log-derived root cause is about
> to reach a customer (remediation steps / RCA) or trigger an escalation.
> **Contract:** [`_shared/verifier/verifier-subagent.md`](../../_shared/verifier/verifier-subagent.md) ·
> [`_shared/verifier/evidence-ledger.md`](../../_shared/verifier/evidence-ledger.md)

V3 verifies two distinct failure shapes: (a) **paraphrase drift** — the conclusion quotes a log
line that does not say what the conclusion claims, and (b) **false correlation** — two events near
in time are asserted as cause→effect without the keyword/key match the
[`correlation-rules.md`](correlation-rules.md) window requires. The verifier **re-reads the cited
log segment** and re-applies the correlation rule mechanically. Like V2, falsification ≥ grounding.

---

## 1. Truth source — re-read, do NOT trust the paraphrase

| Source | Re-read method |
|---|---|
| Text logs (syslog / dmesg / journal / waagent / cloud-init / Event-log **text export** / sosreport) | `view` the exact filename + line range cited in the ledger; `grep` the verbatim signature. |
| Correlation claims | Re-apply the matching rule from [`correlation-rules.md`](correlation-rules.md) — trigger, expected effect, **time window**, keyword match. |
| Unknown signature ↔ KB/TSG | The signature cited must match the TSG returned by `vm-knowledge-search` (hand the doc-faithfulness sub-check to **V1**). |

> ⚠ **Binary-format trap (hard rule).** `.evtx` / `.dmp` / `.etl` are **binary** — the model cannot
> read bytes. A claim derived from "reading" `Security.evtx` / a raw dump directly is
> `UNSUPPORTED` (or `CONTRADICTED` if presented as fact). Valid evidence must come from a **text
> export** (`wevtutil epl`, `Get-WinEvent -Path ... -FilterHashtable`, windbg `!analyze -v`,
> `xperf`) or the engineer pre-analysis files (`xray_ISSUES-FOUND_*.txt`, `findings.txt`,
> `system_errors.txt`).

---

## 2. 命门 (load-bearing claims) for V3

| Is命门 | Is NOT命门 |
|---|---|
| The **"loud" line** the root cause rests on (kernel panic, Event 41/1001 bugcheck, OOM kill, GRUB failure, `hv_utils: Shutdown request received`). | Incidental WARN lines not in the causal chain. |
| The **cross-layer correlation** that links cause and effect (OOM → DB connection-refused; NIC down → app timeout — `cross-time-correlation` flag). | Routine periodic log noise. |
| A **guest-vs-platform attribution** ("Azure shut your VM down") — `single-source-causal` from guest logs alone. | Guest-side config findings fully proven in-guest. |

Re-read the top **2–3**; stakes dial — customer remediation / RCA → 3.

---

## 3. Checklist (per load-bearing claim)

| # | Check | Fail → class |
|---|---|---|
| 1 | **No paraphrase drift** — the cited line, re-read **verbatim**, actually says what the claim says (full error message, not a softened/strengthened paraphrase). | Line says something else → `CONTRADICTED`. Line absent → `UNSUPPORTED`. |
| 2 | **Correlation rule satisfied** — trigger + expected effect both present, **within the rule's time window**, with the **keyword** match (not time-proximity only). | In-window, no keyword → `INFERRED` (medium). Time-proximity only → `INFERRED` (low / coincidence). |
| 3 | **Timestamp normalization** — both events converted to UTC at second precision (no `+0800`/`EDT`/local-time mismatch faking a correlation). | Unnormalized → re-check; bogus correlation → `CONTRADICTED`. |
| 4 | **Causal ≥2 sources** — a causal attribution rests on ≥2 independent signals, not one loud line. | Single source → `INFERRED`, flag `single-source-causal`. |
| 5 | **Guest-vs-platform** — a platform-action claim ("host initiated shutdown") is **not** asserted from guest logs alone; it is confirmed in Kusto (chain to **V2** / `vm-kusto-query`) or held. | Platform claim from guest log only → `UNSUPPORTED` — downgrade to "suspected platform; confirm in Kusto". |
| 6 | **Signature ↔ KB** — an unknown code/module's meaning matches the cited TSG (not a guessed interpretation). | Guessed meaning, no TSG → `UNSUPPORTED` (route to V1). |

---

## 4. Correlation confidence → classification mapping

Map the [`correlation-rules.md`](correlation-rules.md) confidence algorithm onto the verifier
classes (改点 #3 — inject this so the critic isn't a generic differ):

| correlation-rules confidence | Condition | V3 class |
|---|---|---|
| **High** | hit inside window **+ keyword** match | `GROUNDED` (if ≥2 sources for a causal claim) |
| **Medium** | inside window, **no keyword** | `INFERRED` — qualify as "suspected correlation" |
| **Low** | time proximity only | `INFERRED` (coincidence) — needs human judgement, never `GROUNDED` |

---

## 5. Migrated grounding assertions (from `evals/evals.json` — now runtime checks)

- **"Cites at least one raw log line as evidence"** — a conclusion with no verbatim log line is
  `UNSUPPORTED` (nothing to re-read).
- **Pre-analysis cited first** — when an IID package has `xray_ISSUES-FOUND_*.txt` / `findings.txt`,
  the conclusion reflects it; contradicting the pre-analysis without explanation = `CONTRADICTED`.
- **Binary not read raw** — if `.evtx`/`.dmp` is discussed, the evidence path is
  `Get-WinEvent`/`wevtutil`/`!analyze -v`, not a raw `view`/`Get-Content` (§1 trap).

---

## 6. Verifier procedure (V3)

1. Pull the root-cause sentence + cited log rows (filename + line range + verbatim signature) from
   the ledger; independently re-derive the命门 set from the conclusion.
2. **Re-read** each cited segment with `view`/`grep`; confirm the verbatim line is present and
   unaltered. Reject binary-format "reads" (§1).
3. For each correlation claim, re-apply the [`correlation-rules.md`](correlation-rules.md) rule:
   normalize timestamps to UTC, check trigger+effect within the window, check keyword → map to a
   class per §4.
4. For guest-vs-platform attributions, confirm the ≥2-source / Kusto-confirmation requirement;
   otherwise downgrade.
5. Classify, score deterministically, emit the verdict JSON
   ([`verifier-subagent.md` §7](../../_shared/verifier/verifier-subagent.md)).
   - 🟢 PASS → present + badge. 🟡 CONCERNS → qualify correlations as "suspected", downgrade
     platform claims to "confirm in Kusto". 🔴 FAIL → drifted quote or false correlation; block,
     show the re-read line, ask the human.

> Same-model critic is fine here: log re-reading + correlation-rule application are deterministic
> re-checks (re-read the line, re-apply the window), not a judgment a different model would change.
