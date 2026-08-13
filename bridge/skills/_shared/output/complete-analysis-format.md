# Complete Analysis Format — engineer-facing output contract (shared)

> Status: **infrastructure (P1)**. The single authority for what a *finished investigation*
> looks like when an investigation skill (vm-case-triage, vm-kusto-query, vm-log-analyzer,
> vm-knowledge-search) hands its result back to the engineer.
>
> **This is the presentation layer.** The data layer is
> [`../verifier/evidence-ledger.md`](../verifier/evidence-ledger.md): the ledger pins, *by
> construction*, the verbatim query/result/source for every claim. This file says how to **render
> those ledger rows inline** into a complete, evidence-backed report — so the engineer gets the
> whole thing in one shot instead of having to ask "and what's the evidence for that?" five times.

---

## 0. Why this exists (the one paragraph that matters)

The default output of each investigation skill used to be a **terse summary** (kusto S6 =
"concise summary", log-analyzer = "short answer", case-ir = un-evidenced hypotheses). The engineer
then had to drill in, step by step, to recover the per-step analysis and its proof. This contract
flips that: the **complete, evidence-inline analysis is the default deliverable**. Every analytical
sentence carries its supporting evidence right next to it, and every step points forward to the next
step or to the root cause. Nothing load-bearing is left implicit.

---

## 1. Audience & redaction (read first)

- **Audience = the engineer (internal).** This artifact is *your* working analysis — for your own
  understanding, for DFM case notes, for handoff to a collaborating team. **Keep all internal
  identifiers** verbatim: Kusto `cluster('…').database('…')` names, node/container GUIDs, cluster
  names (`HKG20PrdApp01`), datacenter codes, deployment IDs. They are the evidence; do not redact.
- **The customer email is a *separate, downstream* artifact.** When this analysis becomes a
  customer reply (FQR / LQR / RCA), draft it manually and redact internal identifiers yourself
  before anything reaches the customer — strip every internal identifier. **Never** send
  this raw complete-analysis to a customer.

---

## 2. The 5-section envelope

Produce exactly these five sections, in order. Output language mirrors the user's question
language (中文 question → 中文 report; English question → English report). Identifiers (resource
IDs, GUIDs, UTC timestamps, KQL, Event IDs, log paths) stay verbatim **and in full — repeated
completely on every mention, never abbreviated to leading/trailing characters** — regardless of
language.

```
1. 问题描述 / Issue
   The symptom in engineer terms: what failed, observed behavior, the real underlying question.

2. 问题时间 / Time (UTC)
   The exact UTC timestamp or window of the symptom. If the customer gave local time, convert and
   show both. If the window is fuzzy, say so and name what you assumed.

3. 环境信息 / Environment
   - Resource URI: /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm>
                   (or .../Microsoft.Storage/storageAccounts/<sa>)
   - Subscription, Resource Group, VM/SA name, Region (display name), OS type/build, VM size/SKU,
     disk SKU — whatever is known and relevant. Leave blank what you don't know; don't invent.
   - Write each identifier (SubscriptionId, NodeId, ContainerId, VmUniqueId, VM/RoleInstance name)
     in full here. Every later mention in sections 4–5 must repeat the same value **completely** —
     never an abbreviated form or a "the same node/VM" back-reference (see §3 hard rule 6).

4. 已完成的诊断分析 / Completed Diagnostic Analysis        ← THE HEART (see §3)
   Ordered, evidence-backed steps. Each step ends by pointing forward. Closes with Root cause
   (or "inconclusive — here's what's missing").

5. 后续计划 / Next Actions
   Concrete next steps — for the engineer (run X / escalate to Y / collect Z) and/or for the
   customer (do A / provide B). Tie each to what the analysis showed.
```

Sections 1–3 are usually 1–4 lines each. Section 4 is where the length lives. Don't pad 1/2/3/5 —
the value is the evidence in section 4.

---

## 3. Section 4 — the per-step pattern (the whole point)

Section 4 is a sequence of **steps**. Each step is one analytical move, and it has a fixed shape:

```
Step N — <分析结论,一句话 / one-sentence analytical claim>
   <evidence block — one or more, see §4>
   解读 / Interpretation: <what the evidence actually means — not a restatement of the claim>
   → 因此 / Therefore: <forward link — either "so the next step is …" OR "this confirms part of
                        the root cause: …">
```

Then, after the last step:

```
根因 / Root cause: <the conclusion, traceable to the steps above>
置信度 / Confidence: high | medium | low — if below high, name what would raise it.
```

### Hard rules (non-negotiable — this is what stops the output being "笼统")

1. **Every analytical sentence in section 4 carries ≥1 evidence block.** If a sentence has no
   evidence behind it, it is not analysis — either delete it, or explicitly tag it
   `(假设/待确认 — hypothesis, not yet proven)` and say how it would be confirmed. No silent
   assertions.
2. **Each step ends with a forward link** (`→ 因此/Therefore`). A step either *advances* toward the
   root cause or *triggers the next query/log read*. The reader must always see why this step
   mattered and what it led to. (Scenario 2's core requirement: 每一步导向 root cause 或 next step.)
3. **Interpretation is mandatory and distinct from the claim.** "解读" explains what the raw
   evidence says; it is not a paraphrase of the one-line claim. A KQL result with no 解读 is half
   an evidence block.
4. **Negative evidence is evidence.** A query returning 0 rows ("no Service Healing event in the
   window") or a log with no matching line is a valid, citable result — render it the same way and
   interpret what its absence means.
5. **No fabricated identifiers.** Every cluster/database/table/column, every doc URL, every log
   path/line must be real and verbatim-recoverable. If you cannot pin it, you cannot claim it.
   (Mirrors the evidence-ledger §5 self-audit.)
6. **Identifiers always in full — never abbreviate.** Every NodeId, ContainerId, VmUniqueId,
   SubscriptionId, resource URI, GUID, cluster name, deployment ID, and VM/RoleInstance name is
   written **complete on every occurrence** throughout the report — Environment, every Section-4
   step, Root cause, and Next Actions alike. **Never** shorten to leading/trailing characters
   (`a1b2…f9`, "node …e228", "the VM ending in 001"), and never substitute a vague back-reference
   ("the same node / that VM / this sub"). The downstream consumers (manual ICM/CRI escalations, escalation collabs,
   internal notes) copy these verbatim into escalations — a truncated ID there is unusable and forces
   a re-lookup. If a value is long, repeat it in full; do **not** introduce a short alias.

---

## 4. Evidence block sub-templates (one per scenario family)

An evidence block is the verbatim proof rendered from an evidence-ledger row
([`../verifier/evidence-ledger.md` §1](../verifier/evidence-ledger.md)). Pick the sub-template that
matches the evidence source. A single step may stack more than one (e.g. a causal claim wants ≥2
sources — see ledger `single-source-causal` fragility flag).

### 4a. `[doc]` — documentation / knowledge (Case scenario 1)

For answers grounded in a wiki TSG, MS Learn page, KB article, ICM, or PG doc. **Quote the original
sentence verbatim** — a link alone is not enough.

```
   [doc] <doc title> — <URL or wiki page id> — source: CSS Wiki | MS Learn | EngHub | ICM | KB
         原文 / Verbatim: "<the exact sentence(s) from the document that support the claim>"
```

> Rule: the quote must be the *exact* text from the re-fetched source. If you can't paste the
> verbatim sentence, you don't have a `[doc]` evidence block — downgrade the claim to a hypothesis.

### 4b. `[kusto]` — platform Kusto evidence (Case scenarios 2, 4, 5)

For platform-side findings from KQL. **Fully-qualified query + actual result + interpretation.**
**Every `[kusto]` query MUST be immediately followed by its `Result` block** — a query printed
without its returned data right beneath it is not an evidence block (a bare KQL proves nothing).
Never print a query and defer, summarize-away, or omit the result.

Render the result as a **markdown table**, shaped by the result's form. Emit the table as **live
markdown — NOT wrapped in a ``` code fence** — so it renders as a grid in VS Code chat (the KQL
above it may sit in a fenced/monospace block, but the table itself must stay render-able).

**(i) Multi-row, or ≤6 narrow columns → horizontal table** (header row + data rows):

```
   [kusto] cluster('<host>').database('<db>').<Table>
           <verbatim KQL — parameters inlined, absolute UTC window, copy-pasteable>
```
   Result (<rows_total> rows):

   | Col1 | Col2 | Col3 |
   |---|---|---|
   | v11 | v12 | v13 |
   | v21 | v22 | v23 |

   解读 / Interpretation: <what this result proves; which interpretation rule fired;
                          what the key column value means>

**(ii) Single-row WIDE** (many columns / full GUIDs that must not be truncated — identity rows,
VMA verdict) → **transposed 2-column `Field | Value` table** (reads top-to-bottom so long IDs never
overflow; **bold** the decisive fields; an inline `✓ / ←` note on a value is allowed):

```
   [kusto] cluster('<host>').database('<db>').<Table>
           <verbatim KQL>
```
   Result (1 row):

   | Field | Value |
   |---|---|
   | subscriptionId | 0e9367ff-1d01-483d-ba59-1a5d51c00128 |
   | **RCALevel2** | pCIuncorrectable - GPU |

   解读 / Interpretation: <…>

**(iii) Scalar** (a count / single value) → one inline line, no table: `Result: 12`.

> Rules:
> - **Result is mandatory after every query.** No `[kusto]` block ships a query without its
>   returned data right beneath it. (Pairing is non-negotiable: 1 query ⇒ 1 result block.)
> - KQL **must** start with `cluster('…').database('…').<Table>` (global Key Rule — never a bare
>   table name). The window **must** be absolute (`datetime(...) .. datetime(...)`), never
>   `ago()`/`now()` (evidence-ledger §4).
> - **Row budget — up to 10 representative rows.** If the full result has **≤10 rows, print ALL of
>   them.** If it has **more than 10**, print a **full 10** — at least 10, never trimmed to 2–3 just
>   because the conclusion looks obvious — and mark the truncation `(showing 10 of <N>)`, choosing
>   the rows that carry the signal (the failing / outlier / boundary rows, not blindly the first 10).
> - **0 rows is a valid result** — render `Result (0 rows):` and interpret what the absence means.
> - Keep every identifier in full inside table cells (§3 hard rule 6) — never truncate a GUID to fit
>   a column; that is exactly what the transposed (ii) form is for.

### 4c. `[log]` — guest-OS / system log evidence (Case scenario 3)

For findings from a guest log, serial console, evtx export, dump, sosreport, etc. **Cite the file +
line range and paste the verbatim excerpt.**

```
   [log] <filename>:<line-range>   (e.g. /var/log/messages:1840-1846  or  System.evtx Event 1001)
         原文 / Verbatim excerpt:
         <the exact log lines — do not paraphrase; keep timestamps and the full error string>
         解读 / Interpretation: <what these lines mean; the signature; cause vs symptom>
```

> Rules: paste the **exact** lines (full error message, verbatim — never paraphrase). A
> binary-format (`.evtx`/`.dmp`/`.etl`) "read" is not valid evidence — require a text export first
> (vm-log-analyzer V3 rule). Normalize timestamps to UTC in the 解读 if the log is in local time.

---

## 5. When to emit this format (default-on)

| Skill | Emit complete-analysis when… | Otherwise |
|---|---|---|
| **vm-kusto-query** | **Default** at S6 REPORT — any investigation that ran ≥1 query. | n/a — this replaces the old "concise summary". |
| **vm-log-analyzer** | **Default** for analysis / RCA requests ("analyze this", "why did X", "RCA"). | Pure one-liner definitional Qs ("what does bugcheck 0x7B mean") stay short; **nested/lightweight mode** (called from a parent skill) stays compact per that skill's §Nested rules. |
| **vm-knowledge-search** | When the answer feeds a diagnostic claim — render the `[doc]` block (title + URL + **verbatim quote**) so the parent can drop it straight into a step. | A pure "find me the TSG link" ask can stay a curated link list. |
| **vm-case-triage** | **Terminal** deliverable — after next-skills / autopilot collect real evidence, render the full report. | The **first-pass 6-section cockpit** stays as-is: it is the *pre-evidence direction* layer (hypotheses + scope questions + next skills), not a finished analysis. |

> **Two formats, by design.** The vm-case-triage 6-section cockpit = "where do I start" (no case
> evidence yet, hypotheses only). This complete-analysis format = "here's the finished, proven
> analysis" (evidence collected). The cockpit *flows into* this report once the next skills run.

---

## 6. Relationship to the evidence-ledger (don't duplicate work)

- The **ledger** ([`../verifier/evidence-ledger.md`](../verifier/evidence-ledger.md)) is built *by
  construction* during the investigation (snapshot-before-drop). Each ledger row already holds
  `claim` + `source` + `query` + `result_verbatim` + `expected_if_true/false`.
- This report **renders** those rows: ledger `claim` → the step's one-line claim; ledger
  `source`+`query`+`result_verbatim` → the evidence block; ledger `expected_if_*` informs the 解读
  and the forward link.
- So you do **not** maintain two stores. Pin to the ledger while investigating; render the ledger
  into this 5-section envelope at report time. If a verification gate runs, the same ledger feeds
  the verifier — the report and the verifier read the same pinned evidence.

---

## 7. EN example (skeleton — real reports inline real KQL/log/doc output)

```
1. Issue
   Production Linux VM myvm01 (East US 2) rebooted unexpectedly; customer rules out maintenance
   window and manual action. Question: platform-initiated (host repair) or guest-initiated (panic)?

2. Time (UTC)
   2026-06-02 03:15:00Z (customer monitoring; guest local time was 2026-06-02 03:15 UTC-equivalent).

3. Environment
   - Resource URI: /subscriptions/aaaa.../resourceGroups/prod-rg/providers/Microsoft.Compute/virtualMachines/myvm01
   - Subscription aaaa-...  | RG prod-rg | Region East US 2 | OS RHEL 8.8 | Size Standard_D4s_v5

4. Completed Diagnostic Analysis
   Step 1 — The reboot was a platform-initiated host repair, not a guest action.
      [kusto] cluster('vmainsight.kusto.windows.net').database('vmadiag').VMA
              VMA
              | where PreciseTimeStamp between (datetime(2026-06-02T03:00:00Z) .. datetime(2026-06-02T03:30:00Z))
              | where vmId == "<vmId>"
              | project PreciseTimeStamp, RCALevel1, RCALevel2, BootReason
              Result (1 row):
              | PreciseTimeStamp | RCALevel1 | RCALevel2 | BootReason |
              |---|---|---|---|
              | 2026-06-02T03:12:44Z | ServiceHealing | HostHardwareFault | UnplannedHostReboot |
              解读: RCALevel1=ServiceHealing + RCALevel2=HostHardwareFault means the platform
                    auto-recovered the VM after a host hardware fault — not a guest panic.
      → 因此: guest-side panic is now unlikely; confirm the hardware trigger on the node (Step 2).

   Step 2 — The host fault was a corrected/uncorrected memory error on the node (hardware trigger).
      [kusto] cluster('sparkledata.kusto.windows.net').database('sparkle').SELLog
              SELLog
              | where TIMESTAMP between (datetime(2026-06-02T03:00:00Z) .. datetime(2026-06-02T03:20:00Z))
              | where NodeId == "<nodeId>"
              | project TIMESTAMP, SensorName, EventDescription
              Result (1 row):
              | TIMESTAMP | SensorName | EventDescription |
              |---|---|---|
              | 2026-06-02T03:11:58Z | Memory | Uncorrectable ECC error, DIMM A1 |
              解读: an uncorrectable ECC error on DIMM A1 at 03:11:58Z — ~46s before the VMA
                    ServiceHealing event — is the hardware trigger for the host repair.
      → 因此: this corroborates Step 1 (two independent sources, hardware → ServiceHealing →
              VM reboot). Root cause is established.

   根因 / Root cause: an uncorrectable memory (ECC) fault on the host node triggered platform
   Service Healing, which restarted myvm01 on a healthy node. No guest-OS or customer-config issue.
   置信度: high (two corroborating sources: VMA RCALevel + Sparkle SEL, timeline-consistent).

5. Next Actions
   - Engineer: confirm the node was flagged for DIMM replacement (hardware-queries.md); if not,
     raise hardware repair.
   - Customer: no action needed — platform auto-recovered; draft the reboot RCA manually (keep internal identifiers out).
```

---

## 8. 中文 example (skeleton)

```
1. 问题描述
   生产 Linux VM myvm01(East US 2)非预期重启;客户排除维护窗口和手工操作。要回答:是平台
   发起(host 修复)还是 guest 发起(panic)?

2. 问题时间(UTC)
   2026-06-02 03:15:00Z(来自客户监控)。

3. 环境信息
   - Resource URI: /subscriptions/aaaa.../resourceGroups/prod-rg/providers/Microsoft.Compute/virtualMachines/myvm01
   - 订阅 aaaa-... | RG prod-rg | 区域 East US 2 | OS RHEL 8.8 | 规格 Standard_D4s_v5

4. 已完成的诊断分析
   Step 1 — 此次重启是平台发起的 host 修复,而非 guest 行为。
      [kusto] cluster('vmainsight.kusto.windows.net').database('vmadiag').VMA
              VMA
              | where PreciseTimeStamp between (datetime(2026-06-02T03:00:00Z) .. datetime(2026-06-02T03:30:00Z))
              | where vmId == "<vmId>"
              | project PreciseTimeStamp, RCALevel1, RCALevel2, BootReason
              Result(1 行):
              | PreciseTimeStamp | RCALevel1 | RCALevel2 | BootReason |
              |---|---|---|---|
              | 2026-06-02T03:12:44Z | ServiceHealing | HostHardwareFault | UnplannedHostReboot |
              解读:RCALevel1=ServiceHealing + RCALevel2=HostHardwareFault,说明是平台在 host
                    硬件故障后自动恢复了 VM —— 不是 guest panic。
      → 因此:guest 侧 panic 基本排除;下一步在节点上确认硬件触发源(Step 2)。

   Step 2 — host 故障是该节点的内存(ECC)错误,即硬件触发源。
      [kusto] cluster('sparkledata.kusto.windows.net').database('sparkle').SELLog
              SELLog
              | where TIMESTAMP between (datetime(2026-06-02T03:00:00Z) .. datetime(2026-06-02T03:20:00Z))
              | where NodeId == "<nodeId>"
              | project TIMESTAMP, SensorName, EventDescription
              Result(1 行):
              | TIMESTAMP | SensorName | EventDescription |
              |---|---|---|
              | 2026-06-02T03:11:58Z | Memory | Uncorrectable ECC error, DIMM A1 |
              解读:03:11:58Z 在 DIMM A1 出现不可纠正 ECC 错误,比 VMA ServiceHealing 事件早 ~46s,
                    即此次 host 修复的硬件触发源。
      → 因此:与 Step 1 相互印证(两个独立来源,硬件 → ServiceHealing → VM 重启),根因成立。

   根因:host 节点的不可纠正内存(ECC)故障触发平台 Service Healing,将 myvm01 在健康节点上
   重启。与 guest OS / 客户配置无关。
   置信度:高(VMA RCALevel 与 Sparkle SEL 两源印证,时间线一致)。

5. 后续计划
   - 工程师:确认该节点是否已标记 DIMM 更换(hardware-queries.md);若无则发起硬件维修。
   - 客户:无需操作,平台已自动恢复;手动起草重启 RCA(注意去除内部标识)。
```

---

## 9. Cross-references

- Data layer (per-claim pinning): [`../verifier/evidence-ledger.md`](../verifier/evidence-ledger.md)
- Verification gate (closing-gate critic): [`../verifier/verifier-subagent.md`](../verifier/verifier-subagent.md)
- Customer-facing (redacted) variant: draft the customer reply manually and redact internal identifiers yourself.
- Pre-evidence direction layer: `vm-case-triage/references/output-format.md` (the 6-section cockpit)
