# Routing & Disambiguation — vm-case-triage

Full trigger lists and the do-NOT-trigger boundary for `vm-case-triage`. The `SKILL.md`
description carries only a short subset to stay within the loader's 1024-char budget; this file is
the authoritative, complete reference. It also documents the **triage-vs-route intent split** so the
skill picks the right job.

---

## The two jobs (intent split)

`vm-case-triage` merges what used to be two skills. Decide which job the request wants:

| Intent signal | Job | Entry |
|---|---|---|
| "I just got a case / a symptom, where do I start, give me a direction" | **Triage** (6-section cockpit) | SKILL.md Step 1 → 2 → 3 |
| "Is this even ours / who owns this / which queue / change the SAP / transfer it" | **Scope & Route** | SKILL.md Stage R |

They share Step 1 intake. Triage's Step 3 (Next Skills) routes *inward* to Stage R when it decides
the case is out of VM/Storage scope — there is no separate skill to hop to.

---

## Triggers — Triage

**EN:** `case ir`, `run IR on this`, `triage this case`, `where do I start`, `where do I even start`,
`how do I troubleshoot this`, `I'm stuck on this case`, `give me a direction`, `help me look at this case`,
`new case, take a look`, `what could be causing this`.

**中文:** `不知道怎么排查`, `从哪开始查`, `怎么入手`, `帮我理一下排查思路`, `新接了个case帮我看看`,
`给个排查方向`, `这个case怎么查`, `帮我看看这个case`.

**Autopilot (chains deeper skills automatically):** `autopilot`, `自动排查`, `自动诊断`, `一条龙`.

---

## Triggers — Scope & Route

**EN:** `scope check`, `is this in scope`, `is this ours`, `is this our team's`, `do we handle this case`,
`who owns this`, `who owns this boundary`, `whose case is this`, `which team owns this`,
`ownership unclear`, `borderline case`, `route case`, `transfer case`, `transfer to another team`,
`who to transfer to`, `not our scope`, `not ours`, `wrong team`, `misrouted case`,
`change support area path`, `SAP lookup`, `find SAP`.

**中文:** `是不是我们的`, `这个case归谁`, `谁负责`, `属于哪个队列`, `要不要转单`, `转单`, `转给谁`,
`改 SAP`, `换 Support Area Path`, `这个不是我们的scope`, `应该转给哪个团队`.

---

## Do NOT trigger when the next action is already known

This skill is the *entry point* — skip it once you know your next move. Route directly instead:

| The user already knows they want… | Go straight to |
|---|---|
| FQR / LQR / RCA / follow-up / strike email | manual (draft customer FQR/LQR/RCA yourself) |
| A specific scoped Kusto / platform pull | `vm-kusto-query` |
| Analysis of a specific / pasted log or dump | `vm-log-analyzer` |
| Query / file an ICM or CRI | open an ICM manually via ASC (Escalate ticket) to the right EEE/PG team |
| Validate commands in the lab | `vm-lab` (explicit-trigger only) |
| Verify a finished artifact before send/transfer | manual self-check before send/transfer |

Examples that should **not** start a triage cockpit:

- "Write FQR for case 2606020030001234" → the action is known → draft the customer FQR manually.
- "Pull Service Healing for myvm at 03:15 UTC" → known scoped Kusto → `vm-kusto-query`.
- "Analyze this dmesg" + a log path → known log analysis → `vm-log-analyzer`.

A bare 16-digit case ID with **no body** is not enough — this skill does **not** auto-fetch from
DFM. Ask the user to paste the case body / advisory / dump or describe the symptom, then proceed.
