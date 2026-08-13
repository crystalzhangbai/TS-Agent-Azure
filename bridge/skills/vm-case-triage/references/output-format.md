# IR Output Format — The 6-Section Cockpit

The output of `vm-case-triage` (its triage job) is an **engineer-facing troubleshooting cockpit**, not a customer email. It gives the engineer a fast, structured starting point, the relevant TSG/MS Learn reading, and a clear next move.

## Contents

- [The 6 sections](#the-6-sections)
- [Why this diverges from the customer-email format](#why-this-diverges-from-the-customer-email-format)
- [Confidence and honesty](#confidence-and-honesty)
- [Citing docs](#citing-docs)
- [Redaction rule](#redaction-rule)
- [EN example](#en-example)
- [中文 example](#中文-example)

## The 6 sections

Produce exactly these, in this order. Output language mirrors the user's question language (see SKILL.md § Language).

```
1. Interpretation
   Restate the problem in engineer terms: the symptom, the timing (UTC), the
   affected resource, and the real underlying question. One short paragraph.

2. Scope Questions
   The minimal questions needed to narrow the problem. Tag each:
     [blocking]      — you genuinely cannot proceed without this answer
     [nice-to-have]  — would sharpen the analysis but you can proceed
   Lead with the facts you most need (usually Resource ID + exact UTC time).

3. Possible Root Causes & Resolutions
   Ranked hypotheses. For each, one compact bullet:
     - <root cause> — confirm by: <how> — likely fix: <what> — confidence: high|med|low [^n]
   Put the 2-3 most likely first. It is fine to list a long-shot and label it low.
   Append an inline citation marker [^n] when a TSG / MS Learn doc backs the cause or fix.

4. Step-by-step Troubleshooting Guide
   Ordered, verb-led, runnable steps. PowerShell for Windows, Bash for Linux.
   Annotate which step is best handled by which skill, and cite the doc it follows:
     3. Pull host-side Service Healing events for the reboot window  → vm-kusto-query [^n]

5. Reference Links
   Every TSG / MS Learn / KB doc cited above, deduplicated. For each:
     [^n]: <title> — <URL> — what it covers (one line) — source (CSS Wiki / MS Learn / KB)
   If vm-knowledge-search returned nothing, say so here plainly, e.g.
     "No relevant TSG/MS Learn doc found for <terms>; hypotheses are from model knowledge.
      Rerun vm-knowledge-search with different terms to broaden."

6. Next Skills
   Ranked recommendations from the wired set (vm-kusto-query, vm-log-analyzer,
   this skill's own Stage R for scope/route, or drafting the customer reply manually; vm-knowledge-search only for a follow-up search). Each =
   skill + a one-line trigger + what it will find. The #1 entry is what autopilot runs first.
```

## Why this diverges from the customer-email format

An earlier version of this skill produced the customer-email 4-section shape (Issue / Environment / Analysis / Next Actions) so an FQR handoff was zero-cost. That made sense when the skill's job was *drafting the customer reply*. The job changed: this skill is now the **entry point for figuring out where to start**, so its output is a diagnostic cockpit for the engineer — Scope Questions and a Step-by-step guide are tools for the engineer, not lines a customer should read.

The two formats now coexist by design:

- `vm-case-triage` (triage job) → engineer cockpit (the 6 sections here).
- Customer-facing FQR/RCA (Issue / Environment / Analysis / Next Actions) — drafted manually.

When the engineer is ready to reply, draft the customer FQR/RCA manually, transforming the confirmed findings into the customer format. Don't try to make this skill's output double as a customer email — that's a separate manual step, and forcing it here is what made the old format awkward.

## Confidence and honesty

The first pass is model reasoning **grounded by a doc search** (`vm-knowledge-search`), but it still has **no case-specific tool evidence** — no Kusto, no guest logs. A cited TSG/MS Learn page tells you a *class* of problem exists and how it's usually fixed; it does **not** confirm *this* case is that class. So every root cause stays a **hypothesis with a confidence level and a "confirm by" step**, even when a doc backs it. Citing a doc may raise confidence from low→med; only the next skill (Kusto / log analysis) turns a hypothesis into a confirmed finding. Never present a first-pass guess — cited or not — as a verdict. The whole value proposition is "a good place to start, with the right reading in hand".

## Citing docs

Inline-cite every doc you lean on, then collect them in the Reference Links section:

- Use footnote-style markers `[^1]`, `[^2]` right after the claim, step, or fix the doc supports.
- The Reference Links section resolves each marker: `[^1]: <title> — <URL> — one-line coverage — source`.
- Deduplicate: one marker per doc even if cited in several places.
- Prefer internal CSS Wiki TSGs over public pages when both cover the point; keep MS Learn for product behavior / limits.
- If `vm-knowledge-search` returned nothing relevant, do **not** fabricate links — state in Reference Links that no doc was found and that the hypotheses are model-knowledge only.

## Redaction rule

Even though this is engineer-facing, keep internal backend identifiers out of anything that might be pasted toward a customer (the cockpit often flows into a manually-drafted customer reply). Never surface:

- Cluster names (e.g. `HKG20PrdApp01`), node IDs (host GUIDs), container IDs
- Internal tenant names, deployment IDs, role-instance names (`_VMNAME_0`)
- Internal Kusto cluster/db names (e.g. `AzureCM`, `vmainsight`)
- Datacenter codes (e.g. `HK1`, `BN8`)

Use instead: Subscription ID/name, Resource Group, VM/VMSS name, Azure region **display name** ("East US 2"), full ARM resource ID.

## EN example

> Free-form input: "Our prod VM `myvm01` rebooted unexpectedly around 2026-06-02 03:15 UTC. No maintenance window, we didn't restart it. Linux, East US 2."

```
Interpretation:
A production Linux VM (myvm01, East US 2) underwent an unexpected reboot at
~2026-06-02 03:15 UTC. The customer rules out a maintenance window and manual
action, so the real question is: was this platform-initiated (host repair /
Service Healing) or guest-initiated (kernel panic / OOM)?

Scope Questions:
1. [blocking] Full Resource ID of myvm01 (need subscription + RG to investigate)?
2. [blocking] Exact reboot time in UTC, and is 03:15 from guest logs or your monitoring?
3. [nice-to-have] VM size and OS disk SKU (rules in/out a storage-side stall)?
4. [nice-to-have] Did the workload recover on its own after the reboot?

Possible Root Causes & Resolutions:
- Host Service Healing (platform auto-repair) — confirm by: VMA / Service Healing
  events at the reboot window — likely fix: none needed, expected recovery; send RCA
  — confidence: med [^1]
- Host hardware fault triggering an unplanned host reboot — confirm by: SEL / Hawkeye
  for the node — likely fix: hardware deallocate/redeploy if recurring — confidence: med [^1]
- Guest kernel panic / OOM — confirm by: dmesg/syslog before 03:15 — likely fix: tune
  memory / kernel per the panic signature — confidence: low (no guest symptom reported) [^2]

Step-by-step Troubleshooting Guide:
1. Confirm the Resource ID and exact UTC reboot time with the customer.
2. Pull platform reboot attribution (VMA + Service Healing + SEL) for ±10 min  → vm-kusto-query [^1]
3. If a guest-side cause is suspected, analyze dmesg/syslog around the window  → vm-log-analyzer [^2]
4. Once the trigger is confirmed, draft the RCA for the customer manually        → manual draft

Reference Links:
[^1]: Understand VM reboots in Azure — https://learn.microsoft.com/azure/virtual-machines/maintenance-and-updates —
      what planned vs unplanned platform reboots / Service Healing look like — source: MS Learn
[^2]: (internal TSG) Linux VM unexpected reboot — dmesg/panic triage —
      https://supportability.visualstudio.com/AzureIaaSVM/_wiki/... — guest panic/OOM signatures — source: CSS Wiki
(These links are illustrative; in real output they come verbatim from vm-knowledge-search results.)

Next Skills:
1. vm-kusto-query — "query VMA + ServiceHealing for myvm01 at 2026-06-02 03:15 UTC" —
   tells you if the reboot was platform-initiated and why.
2. vm-log-analyzer — "analyze guest syslog/dmesg around 03:15" — rules guest panic/OOM in or out.
3. Manual draft — "write the reboot RCA" — once the trigger is confirmed.
```

## 中文 example

> 自由文本输入:"我们生产 VM `myvm01` 在 2026-06-02 03:15 UTC 左右非预期重启了,没有维护窗口,我们也没重启它。Linux,East US 2。"

```
问题解读:
一台生产 Linux VM(myvm01,East US 2)在 ~2026-06-02 03:15 UTC 发生非预期重启。客户排除了
维护窗口和手工操作,因此真正要回答的是:这是平台发起的(Host 修复 / Service Healing)还是
Guest 发起的(kernel panic / OOM)?

澄清问题:
1. [blocking] myvm01 的完整 Resource ID(需要订阅 + RG 才能排查)?
2. [blocking] 准确的重启 UTC 时间,03:15 来自 Guest 日志还是你们的监控?
3. [nice-to-have] VM 规格和 OS 盘 SKU(用于排除存储侧卡顿)?
4. [nice-to-have] 重启后业务是否自行恢复?

可能根因与解决:
- Host Service Healing(平台自动修复)— 确认方式:重启窗口的 VMA / Service Healing 事件 —
  可能修复:无需操作,属预期恢复,发 RCA — 置信度:中 [^1]
- Host 硬件故障导致非计划 Host 重启 — 确认方式:该节点的 SEL / Hawkeye — 可能修复:反复出现
  则硬件 deallocate/redeploy — 置信度:中 [^1]
- Guest kernel panic / OOM — 确认方式:03:15 前的 dmesg/syslog — 可能修复:按 panic 特征调内核/内存
  — 置信度:低(未报告 Guest 侧症状)[^2]

分步排查指南:
1. 与客户确认 Resource ID 和准确的 UTC 重启时间。
2. 拉取平台重启归因(VMA + Service Healing + SEL),窗口 ±10 分钟  → vm-kusto-query [^1]
3. 若怀疑 Guest 侧,分析窗口附近的 dmesg/syslog                  → vm-log-analyzer [^2]
4. 触发源确认后,手动给客户起草 RCA                              → 手动起草

参考文档链接:
[^1]: Understand VM reboots in Azure — https://learn.microsoft.com/azure/virtual-machines/maintenance-and-updates —
      平台计划/非计划重启与 Service Healing 的表现 — 来源:MS Learn
[^2]:(内部 TSG)Linux VM 非预期重启 — dmesg/panic 排查 —
      https://supportability.visualstudio.com/AzureIaaSVM/_wiki/... — Guest panic/OOM 特征 — 来源:CSS Wiki
(以上链接为示例;真实输出中由 vm-knowledge-search 返回原文链接。)

下一步可用 skill:
1. vm-kusto-query —「query VMA + ServiceHealing for myvm01 at 2026-06-02 03:15 UTC」—
   判断重启是否平台发起以及原因。
2. vm-log-analyzer —「分析 03:15 附近的 guest syslog/dmesg」— 排除/确认 Guest panic/OOM。
3. 手动起草 —「写重启 RCA」— 触发源确认后再做。
```
