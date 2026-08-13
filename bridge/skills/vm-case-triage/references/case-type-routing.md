# Case Type Routing

Different case types need different hypotheses and different next skills. Classify the type **first** in Step 2.0, then shape the cockpit and the Next Skills around it. Skipping classification is the #1 source of misdirected triage (a 2026-05-28 MANA advisory was first read as a "planned reboot" because the type was never identified).

## Contents

- [Taxonomy](#taxonomy)
- [Decision signals](#decision-signals)
- [Per-type recipe + autopilot first step](#per-type-recipe--autopilot-first-step)
- [Subflow A — Fault / Unavailability](#subflow-a--fault--unavailability)
- [Subflow B — Performance](#subflow-b--performance)
- [Subflow C — Advisory / Planned Maintenance](#subflow-c--advisory--planned-maintenance)
- [Subflow D — Post-incident RCA](#subflow-d--post-incident-rca)
- [Subflow E — Quota / Config / How-To](#subflow-e--quota--config--how-to)

## Taxonomy

| Type | Customer pain | Typical entry phrase |
|---|---|---|
| A — Fault / Unavailability | VM down, reboot, BSOD, can't SSH/RDP, agent fail | "VM 重启了 / VM unavailable / 进不去" |
| B — Performance | Slow disk, high CPU, network drop, latency | "性能差 / IOPS 不够 / latency 高" |
| C — Advisory / Planned Maintenance | Got a notification with a tracking ID; wants impact | "advisory XXXX-XXXX / 收到维护通知 / 这条通知什么意思" |
| D — Post-incident RCA | An outage already auto-recovered; wants root cause | "VM 重启过我们没操作 / why did Azure restart my VM / RCA" |
| E — Quota / Config / How-To | Quota request, config or feature question | "如何启用 X / 怎么改 / quota 不够" |

## Decision signals

Run these in order on the problem text. **First match wins.**

| Signal pattern | Type |
|---|---|
| Regex `[A-Z0-9]{4}-[A-Z0-9_]{2,8}` AND any of {advisory, maintenance, notification, upcoming, deprecat, migration, MANA, retirement, 通知} | **C** |
| "RCA" / "root cause" / "为什么" + past-tense reboot/outage + customer says they did NOT initiate | **D** |
| "unavailable" / "down" / "reboot" / "crash" / "BSOD" / "can't SSH/RDP" / "重启了" / "进不去" (current/recent) | **A** |
| "slow" / "latency" / "IOPS" / "throughput" / "high CPU" / "卡" / "慢" / "性能" | **B** |
| "quota" / "limit" / "increase" / "how do I" / "configure" / "enable" / "怎么" / "如何" + no failure | **E** |
| None match | Ask (as a `[blocking]` Scope Question) which of A–E this is |

## Per-type recipe + first-pass search + autopilot first step

The first pass now **reasons (model knowledge) and searches docs** (`vm-knowledge-search`). This table tells you which hypotheses to favor, **what to search for** in the first pass, and which deeper skill autopilot should run first once the cockpit is out.

| Type | Favor these root causes | First-pass doc search (vm-knowledge-search) | Autopilot first deeper step |
|---|---|---|---|
| A Fault | Service Healing, host hardware fault, guest panic/OOM, boot failure | reboot-attribution TSG, panic/boot TSG | `vm-kusto-query` (or `vm-log-analyzer` if a guest log/path was given) |
| B Performance | SKU cap hit, disk throttling, host noisy-neighbor, NIC/AccelNet | the VM size's published IOPS/throughput caps, disk-throttling TSG | `vm-kusto-query` (XStore throttling / disk IO blip) |
| C Advisory | hardware migration (MANA), deprecation, planned reboot, rebootless LM | the MS Learn page for the advisory class | usually none — the cited doc is the answer; draft the customer reply manually |
| D RCA | DiskIOBlip, ServiceHealing, HardwareFault, NodePause, MemoryPreserving | RCA-category TSG for the suspected category | `vm-kusto-query` (VMA / Service Healing / SEL / panic chain) |
| E Config/How-To | misconfig, missing feature, quota | the one MS Learn / KB page that answers it | usually none — the cited doc is the answer |

## Subflow A — Fault / Unavailability

Hypotheses to lead with: platform-initiated reboot (Service Healing), host hardware fault, guest kernel panic / OOM, boot/agent failure. In the first pass, search for the reboot-attribution / panic / boot TSGs and cite them. In the cockpit, your Step-by-step guide typically routes to `vm-kusto-query` for platform attribution and, if a guest log was provided, `vm-log-analyzer` for the guest side. Draft the RCA manually once the trigger is confirmed.

## Subflow B — Performance

Lead with: the VM size's published IOPS/throughput caps, disk-tier throttling, host-side contention, NIC/AccelNet drops. The first-pass doc search pulls the **published limits** and the disk-throttling TSG — cite them in the cockpit; your guide then compares **observed vs SKU cap**, with `vm-kusto-query` (XStore throttling / disk-IO-blip evidence) as the next deeper step.

## Subflow C — Advisory / Planned Maintenance

The subflow most often misread. Advisories announce **upcoming** changes; the customer almost always asks: "Will my VM reboot? Do I need to act? Which VMs are affected? Can I postpone?"

1. Extract the advisory tracking ID (regex `[A-Z0-9]{4}-[A-Z0-9_]{2,8}`).
2. If only the ID was given (no body), make the full notification body a `[blocking]` Scope Question — different advisories with similar IDs have very different impact. Do NOT guess from the ID alone.
3. Classify by keywords in the body:

   | Keyword in body | Class | Customer impact |
   |---|---|---|
   | "MANA" / "Microsoft Azure Network Adapter" / "hardware migration" | Hardware migration | Live-migration, **no reboot**; may need MANA driver readiness in guest |
   | "will be deprecated" / "end of support" / "retirement" + image/SKU | Deprecation | No immediate impact; act before the date |
   | "planned maintenance" / "reboot" / "restart" + tenant update | Planned reboot | Reboot during the window; customer can self-service via Service Health |
   | "rebootless" / "live migration" / "MemoryPreserving" | Rebootless maintenance | Brief pause (<10s), no reboot |
   | "scheduled to be terminated" | Forced action | Customer must act by date X |

4. The first-pass doc search pulls the **MS Learn Service Health / maintenance page** for this advisory class (not a failure TSG — TSGs are for failures, not advisories). Cite it in Reference Links.
5. In the cockpit's Next Actions / Step-by-step, explicitly answer the three universal advisory questions (reboot? action needed? affected VMs?).

**Anti-pattern:** calling MANA migration a "planned maintenance reboot." MANA is live-migration, **not** a reboot — a wrong call here cascades into a wrong FQR.

## Subflow D — Post-incident RCA

The non-ByteDance cousin of the weekly RCA flow.

1. Lead hypotheses with the standard categories: DiskIOBlip, VirtualDiskFault, ServiceHealing, HardwareFault, NodePause, MemoryPreserving, ContainerFault, GuestOS.
2. The confirm path is `vm-kusto-query` (VMA / Service Healing / SEL / kernel-panic chain).
3. Draft the RCA manually (standard FQR/LQR/RCA shape) once the category is confirmed.

## Subflow E — Quota / Config / How-To

1. Usually one MS Learn / KB page is the whole answer — the first-pass `vm-knowledge-search` pulls it; cite it in Reference Links.
2. No platform Kusto needed. Keep the cockpit short; the Step-by-step guide may be just the doc's procedure. Often no deeper next skill is required.
