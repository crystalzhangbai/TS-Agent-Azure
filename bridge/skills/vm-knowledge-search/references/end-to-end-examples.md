# End-to-End Worked Examples

Reference companion to [`SKILL.md`](../SKILL.md). Two examples showing how the 6 main steps + 2 sub-steps actually chain together on realistic Azure VM support flows. Use these to calibrate when to skip / loop-back / escalate.

---

## Example 1 — Standalone mode (user asks directly)

**User query (Chinese)**: 帮我查一下 RHEL 上 SAP HANA Pacemaker fencing 自动重启 VM 的 TSG,SBD 是怎么工作的?

---

**Step 1 — Parse → locate**: Topic is Linux clustering + SAP HA on Azure VM. From [`azureiaasvmwiki-page-index.md`](azureiaasvmwiki-page-index.md), the likely AzureIaaSVM section is `/SME Topics/Linux on Azure` (no dedicated RHEL Pacemaker page in the index). From [`known-page-ids-suse-sap.md`](known-page-ids-suse-sap.md) — that file covers SLES; RHEL is similar but not pre-cached → must search.

**Step 2 — Build keywords**: Chinese → English. Lead with most specific tokens: `Pacemaker` + `SBD` + `fencing` + `SAP HANA`. Drop "RHEL" / "VM" — too generic, will drown ranking. Final: `"SAP HANA Pacemaker SBD fencing"`. Backup query if first thin: `"RHEL Pacemaker stonith SBD Azure"`.

**Step 2.5 — Route**: Triggered rows = `AzureLinuxNinjas` (RHEL/Pacemaker/cluster) + `AzureStrategicWorkloads` (SAP HANA/HPC). Plus baseline `AzureIaaSVM`. Total = 3 projects, within cap. No tie-breaker needed. Final `project=["AzureIaaSVM", "AzureLinuxNinjas", "AzureStrategicWorkloads"]`.

**Step 3 — Parallel default search** (same response, both fire concurrently):

```python
# Cross-cutting (SAP HA on Azure VM) → fire 2 parallel mslearn queries (Azure-anchored + symptom-only)
csswiki-search_wiki(searchText="SAP HANA Pacemaker SBD fencing",
                    project=["AzureIaaSVM", "AzureLinuxNinjas", "AzureStrategicWorkloads"], top=10)
mslearn-microsoft_docs_search(query="SAP HANA Pacemaker SBD fencing Azure")        # Azure-anchored
mslearn-microsoft_docs_search(query="Pacemaker SBD STONITH fencing configuration") # symptom-only
```

**Result check**: csswiki returns 5 hits (3 relevant titles in AzureLinuxNinjas, e.g., "RHEL HA SAP HANA Cluster SBD Setup"). mslearn returns 4 hits (top: `learn.microsoft.com/azure/sap/workloads/high-availability-guide-rhel-pacemaker`). Both default sources have ≥3 relevant hits → **not thin, not empty** per `SKILL.md` §2 threshold → skip Step 3.5 / Step 4 → Step 5.

**Step 5 — Filter + read top 1–2**:
- Top csswiki hit: AzureLinuxNinjas page "RHEL HA SAP HANA Cluster SBD Setup" → call `csswiki-wiki(action="get_page", path=..., includeContent=true)`. Returns 4 KB markdown with `## Configuration` / `## Failure Scenarios` / `## TSG steps` headings → ✅ passes Step 5 quality check (actionable + topical + last edited 2025).
- Top mslearn hit: learn.microsoft.com SAP RHEL HA guide → `mslearn-microsoft_docs_fetch(url=...)`. Returns long official guide with Pacemaker config + SBD device setup steps → ✅ passes too.

Quality check passed without loop-back. Proceed.

**Step 6 — Synthesize + present** (using `SKILL.md` §8 unified template, no disclaimer since high-relevance hits):

```
## SAP HANA Pacemaker Fencing on RHEL — SBD Behavior

[Synthesis combining csswiki TSG steps + mslearn official config guide + brief model knowledge gloss on
how SBD watchdog firmware triggers a hard reboot when the node fails to write its slot in time.]

### Troubleshooting Steps
1. Verify SBD device accessibility on both nodes: `sbd -d /dev/disk/by-id/... list`
2. Check Pacemaker stonith config: `pcs stonith config sbd-stonith`
3. ...

### References
- 📄 RHEL HA SAP HANA Cluster SBD Setup — [csswiki](https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas/<pageId>/...) — Source: ADO Wiki (AzureLinuxNinjas)
- 📄 High availability for SAP on Azure VMs (RHEL/Pacemaker) — [Learn](https://learn.microsoft.com/azure/sap/...) — Source: Microsoft Learn
```

**Total wall time**: ~2 sec (one csswiki + 2 mslearn parallel) + ~1 sec (2 reads parallel) = ~3 sec for the data side, plus synthesis.

---

## Example 2 — Nested mode (called by `vm-case-triage`)

**Context**: `vm-case-triage` is the active parent skill working on case `2606150030001234`. Customer reports: "VM extension provisioning state failed (status code 1) on `CustomScriptExtension` after redeploy." Parent skill calls vm-knowledge-search via `<skill-context>` block to find supporting TSG.

**Lightweight execution** (per `SKILL.md` §10):

1. **Skip Step 1 / Step 2.5 detailed routing** — parent's keywords already say "extension provisioning failed CustomScriptExtension status code 1". Use as-is.

2. **Step 3 — minimal default search** (top 1–2 each, no on-demand sources):
   ```python
   csswiki-search_wiki(searchText="extension provisioning failed status code 1 CustomScript",
                       project=["AzureIaaSVM"], top=5)  # baseline only — nested mode keeps it tight
   mslearn-microsoft_docs_search(query="Azure VM extension provisioning failed status code 1")  # Azure-anchored
   ```

3. **Skip Step 5 deep-read** — search-result `caption` / `highlight` fields usually quote the relevant TSG line directly. Parent only needs the references for its IR analysis.

4. **Skip §3 Step 4 auto-fallback** — even if empty, return `No related docs found.` per `SKILL.md` §10 rule #6. Don't burn enghub+icm+azurewiki MCP calls inside a parent IR flow.

5. **Compact return block** (parent pastes into its IR template):
   ```
   📚 References (from vm-knowledge-search):
   - [csswiki] CustomScriptExtension Provisioning Failures TSG — https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/<pageId>/...
   - [mslearn] Troubleshoot Azure VM extension issues — https://learn.microsoft.com/azure/virtual-machines/extensions/...
   Summary: TSG covers status-code-1 root causes (script exit ≠ 0, missing dependency, timeout, ACL). Parent should also check waagent.log for the failing handler version.
   ```

**Wall time**: ~1.5 sec total (single csswiki + single mslearn parallel). No reads, no rank, no §8 format.

---

> **When in doubt about which mode you're in**: if a `<skill-context>` block for a different skill is visible in the conversation, you're nested. If the user typed the question directly into the chat, you're standalone. Standalone gets the full 6 steps + §8 format + Step 4 fallback; nested gets the lightweight path above.
