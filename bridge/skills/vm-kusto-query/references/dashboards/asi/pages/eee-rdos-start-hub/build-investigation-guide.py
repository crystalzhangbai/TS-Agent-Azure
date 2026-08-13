"""
build-investigation-guide.py — Generate symptom-keyed markdown reference from library.json

Reads library.json (panel-organized query library) and produces a set of
investigation-intent markdown files under investigation-guide/ matching the
style of vm-kusto-query/references/*-queries.md.

Every query is categorized into exactly one section. ALL queries are included
(no curation). Categorization is rule-based on (panel_path, query_name).

Output layout:
    investigation-guide/
        README.md
        01-vm-availability-and-lifecycle.md
        02-container-and-tenant-state.md
        03-host-node-state-and-faults.md
        04-host-hardware-faults.md
        05-network-and-tor.md
        06-services-on-node.md
        07-node-update-and-maintenance.md
        08-performance-metrics.md
        09-guest-agent-and-extensions.md
        10-automated-detectors.md
        11-helpers-and-lookups.md

Usage: python build-investigation-guide.py
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIBRARY_PATH = ROOT / "library.json"
OUT_DIR = ROOT / "investigation-guide"


# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------
# Each section: (slug, title, intro)
SECTIONS = [
    (
        "01-vm-availability-and-lifecycle",
        "VM Availability & Lifecycle",
        "Use when investigating: **VM down / unexpected restart / unavailability / "
        "redeploy / customer-reported VM outage**. These queries answer "
        "*\"why did the VM stop working\"*, who initiated it, and what the "
        "platform did about it. Always start here for VM-level incidents.",
    ),
    (
        "02-container-and-tenant-state",
        "Container & Tenant State",
        "Use when investigating: **container state machine transitions, container "
        "OS state, container faults, CreateContainer/DestroyContainer failures, "
        "tenant-level events**. These queries answer *\"what state was the "
        "container in and how did it change\"*.",
    ),
    (
        "03-host-node-state-and-faults",
        "Host Node State & Faults",
        "Use when investigating: **host node faulted / OFR (Out For Repair) / "
        "HumanInvestigate / unallocatable / cluster-wide node health / service "
        "healing / live migration of containers off a node**. These queries "
        "answer *\"is the node healthy, and if not, why\"*.",
    ),
    (
        "04-host-hardware-faults",
        "Host Hardware Faults",
        "Use when investigating: **bugcheck (BSOD on host), WHEA, memory errors, "
        "disk hardware errors, SEL events, NVMe controller issues, host hardware "
        "fingerprint**. These queries identify physical hardware failure root cause.",
    ),
    (
        "05-network-and-tor",
        "Network & TOR",
        "Use when investigating: **network packet loss, TOR (top-of-rack) switch "
        "issues, NMAgent failures, SoC/FPGA/Overlake host networking, wireserver, "
        "VFP**. These queries cover the platform side of guest network problems.",
    ),
    (
        "06-services-on-node",
        "Services on Node",
        "Use when investigating: **host agent processes (PfAgent, PilotFish, "
        "ApSvcMgr, ApLauncher, Wire Service, Node Service) crashing or stopped**. "
        "Agent failures often precede or cause container faults.",
    ),
    (
        "07-node-update-and-maintenance",
        "Node Update & Maintenance",
        "Use when investigating: **planned maintenance / update events impacting "
        "the VM (PF, Host OS, CM, AzPE, FPGA updates)**. These help distinguish "
        "platform-initiated downtime from unexpected failure.",
    ),
    (
        "08-performance-metrics",
        "Performance Metrics",
        "Use when investigating: **host CPU saturation, host memory pressure, "
        "container IO performance**. These return time-series for the resource "
        "consumption side of incidents.",
    ),
    (
        "09-guest-agent-and-extensions",
        "Guest Agent & Extensions",
        "Use when investigating: **guest agent provisioning failures, extension "
        "install failures, scheduled events, ICM impact reports**. These cover "
        "guest-side platform integration.",
    ),
    (
        "11-helpers-and-lookups",
        "Helpers & Resource Lookups",
        "Metadata and helper queries: resolve ARM resource IDs, find Shoebox "
        "accounts, look up node hardware properties, container policy, billing, "
        "attached disks, etc. Use these to gather context before/after running "
        "the diagnostic queries above.",
    ),
]

SECTION_INDEX = {slug: i for i, (slug, *_) in enumerate(SECTIONS)}


# ---------------------------------------------------------------------------
# Categorization rules
# ---------------------------------------------------------------------------

def categorize(panel_name: str, q_name: str, q_type: str) -> str:
    """Return the section slug for a query."""

    p = panel_name
    n = q_name

    # ---- Automated detectors: route to per-subgroup section --------------
    if q_type == "IssueDetector" or p == "Automated Detector":
        return detector_subgroup(n)

    # ---- Helpers / lookups -----------------------------------------------
    helper_names = {
        "PageInputHelper", "GetARMResourceId", "GetShoeboxAccount",
        "VmssIdHelper", "JarvisDashTimeHelper", "Unix Time Helper",
        "TorDeviceInfo", "vfpMDM", "OverlakeNodeMap",
        "Node Hardware Properties", "Container Features",
        "AIPromptGenerator", "Retrieve Resource \"Start Hub\"",
        "ContainerPolicyQuery", "CRP VM Snapshot",
        "Azure Host VM Blobs", "Compute Hour Usage Table",
    }
    if n in helper_names:
        return "11-helpers-and-lookups"
    if p.startswith("VM") or p in ("AI Tool", "General Tool Links",
                                   "Network / TOR", "Node (Physical)",
                                   "Overlake / SoC", "Tenant / Container / Node",
                                   "(top-level)"):
        return "11-helpers-and-lookups"

    # ---- Performance metrics ---------------------------------------------
    if "Host Available Memory" in p or "Host CPU Utilization" in p:
        return "08-performance-metrics"
    if p.startswith("At-A-Glance Performance"):
        return "08-performance-metrics"

    # ---- Node update / maintenance ---------------------------------------
    if p.endswith("Node Update"):
        return "07-node-update-and-maintenance"

    # ---- Services on Node ------------------------------------------------
    if p.endswith("Services on Node"):
        return "06-services-on-node"

    # ---- Network Health --------------------------------------------------
    if p.endswith("Network Health"):
        return "05-network-and-tor"

    # ---- Guest Agent & Extensions ----------------------------------------
    if "Guest Agent" in p or n in ("Tenant Scheduled Events", "ICM Report",
                                    "GuestAgentAndExtensionTimeline"):
        return "09-guest-agent-and-extensions"

    # ---- Host hardware faults --------------------------------------------
    hw_names = {
        "Azure Watson", "Kernel/Driver Events",
        "Remarkable Event - Disk", "Remarkable Event - WHEA",
        "Remarkable Event - Memory", "Remarkable Event - HyperV",
        "DCM SEL", "DCM SEL (Sparkle)",
    }
    if n in hw_names:
        return "04-host-hardware-faults"

    # ---- Host node state & faults ----------------------------------------
    if p.endswith("Node Health"):
        return "03-host-node-state-and-faults"
    if p.endswith("Cluster Health"):
        return "03-host-node-state-and-faults"
    if "HumanInvestigate Node Count" in p:
        return "03-host-node-state-and-faults"
    if "OutForRepair Node Count" in p:
        return "03-host-node-state-and-faults"
    if "Ready Node Count" in p:
        return "03-host-node-state-and-faults"
    if "Unhealthy Node Count" in p:
        return "03-host-node-state-and-faults"

    # ---- Container & tenant state ----------------------------------------
    if "Container Transition" in p:
        return "02-container-and-tenant-state"
    if "CRP Operation" in p:
        return "02-container-and-tenant-state"

    container_state_names = {
        "Container State", "Container OS State", "Container Lifecycle",
        "Container Fault", "VMAL Ops", "Node Service Error - Container",
        "Hyper-V StorageStack", "Hyper-V Events",
        "Holmes Events", "RH Annotation Report",
        "Anvil Event - Container",
    }
    if n in container_state_names:
        return "02-container-and-tenant-state"

    # ---- VM availability & lifecycle (the rest of Container/Tenant Health)
    if p.endswith("Container / Tenant Health"):
        return "01-vm-availability-and-lifecycle"

    # Fallback (shouldn't happen)
    return "11-helpers-and-lookups"


# ---------------------------------------------------------------------------
# Detector sub-grouping (within section 10)
# ---------------------------------------------------------------------------

# Detector subgroups become their own section files (10a, 10b, ...). Order
# matters: the first matching keyword wins, so put more-specific keywords first
# (e.g. NVMe before Disk, LM_ before Container).
DETECTOR_GROUPS: list[tuple[str, str, str, list[str]]] = [
    ("10a-detectors-host-crash-bugcheck",
     "Detectors — Host Crash / Bugcheck",
     "Host OS bugcheck / kernel crash / power-loss signatures. Run these when "
     "the host node rebooted unexpectedly or VMs on a node all went down together.",
     ["bugcheck", "Crash", "BcRefere", "BcPfn", "HbLld", "HYPERVISOR_ERROR",
      "node_bugcheck", "Sudden_Power_Loss"]),
    ("10b-detectors-live-migration",
     "Detectors — Live Migration / Service Healing",
     "Live Migration and Service Healing failure signatures. Run when LM or "
     "SH was attempted around the incident time and did not complete cleanly.",
     ["LM_", "LMFailed", "LMFailure", "ServiceHealing",
      "VFPRestoreFailure", "VFPSerialization", "FlexibleIODevice",
      "End_of_Life", "NetAssistMonitor"]),
    ("10c-detectors-nvme-storage-disk",
     "Detectors — NVMe / Storage / Disk",
     "Local NVMe, BlobCache, data-disk, and storage driver signatures. Run "
     "when disk IO blips, missing local NVMe, or storage-related crashes are suspected.",
     ["NVMe", "NVME", "DiskBlip", "BlobCache", "AirDiskBlip",
      "Local_NVMe", "DataDisk", "datadisk", "stornvme", "Flush_latencies",
      "Ultra_PremV2"]),
    ("10d-detectors-network-tor",
     "Detectors — Network & TOR",
     "TOR switch and platform network failure signatures. Run when guest "
     "network connectivity dropped or TOR failures are flagged.",
     ["TORFailures", "TOR_DegradedUnhealthyEvents", "NetworkIssue",
      "NetworkContainer", "TOR"]),
    ("10e-detectors-soc-overlake-fpga",
     "Detectors — SoC / Overlake / FPGA",
     "Smart-NIC / Overlake host networking / FPGA-related signatures.",
     ["SoC", "Overlake", "FPGA", "Backplane", "GFT", "HostNetworkIssue"]),
    ("10f-detectors-vm-create-start-failures",
     "Detectors — VM Start / CreateContainer Failures",
     "VM provisioning, CreateContainer, and start-time failure signatures. "
     "Run when a VM failed to start or be created.",
     ["CreateContainer", "VM_creation", "VMs_Fail_to_Start", "VM reboot",
      "VMAL_error", "VMAL_ASAPPF", "Unable_to_create_VM",
      "fail_to_start", "fails_start", "Key_Vault_Encryption",
      "OSProvisioningTimedOut", "IBManagerError", "TPM_fails",
      "Attaching_Multiple_DataDisks"]),
    ("10g-detectors-node-lifecycle",
     "Detectors — Node Lifecycle / Unallocatable",
     "Unallocatable node, node-restart-due-to-PM, staging, and cluster-wide "
     "node health signatures.",
     ["Unallocatable", "UnallocatableNode", "TooManyUnhealthyNode",
      "Node_Restart", "Booting_of_host", "StagingNodeImages",
      "AKS_Linux_instances", "RHSends", "DppPlugin", "CRUD",
      "Resource_Health_Unavailable", "AzSMServiceHealing"]),
    ("10h-detectors-cpu-memory-power",
     "Detectors — Host CPU / Memory / Power",
     "Host CPU throttle, memory pressure, and thermal signatures.",
     ["HighHostCPU", "Low_Memory", "temp_throttle"]),
    ("10i-detectors-update-maintenance",
     "Detectors — Update / Maintenance",
     "Update-related signatures (TOR update, SoC update, driver update).",
     ["TOR_Update", "SoC_Update", "VDC_driver"]),
    ("10j-detectors-other",
     "Detectors — Other / Uncategorized",
     "Detectors that did not match any specific group.",
     []),
]


def detector_subgroup(name: str) -> str:
    """Return the slug of the detector subgroup."""
    for slug, _title, _intro, keywords in DETECTOR_GROUPS:
        for kw in keywords:
            if kw in name:
                return slug
    return "10j-detectors-other"


# ---------------------------------------------------------------------------
# KQL formatting & filter-tip extraction
# ---------------------------------------------------------------------------

# Heuristics: scan KQL for `where X == "Y"`, `has`, `contains` lines that look
# like meaningful signal filters; surface them so the reader knows what the
# query is testing.
FILTER_TIP_RE = re.compile(
    r'where\s+([A-Za-z_][\w\.]*)\s*'
    r'(==|=~|has|contains|startswith|endswith|!=|<>)\s*'
    r'("([^"]+)"|\'([^\']+)\')',
    re.IGNORECASE,
)


def extract_filter_tips(kql: str, limit: int = 8) -> list[str]:
    seen = set()
    tips: list[str] = []
    for m in FILTER_TIP_RE.finditer(kql):
        col, op, _full, q1, q2 = m.groups()
        val = q1 or q2
        key = (col.lower(), op.lower(), val)
        if key in seen:
            continue
        seen.add(key)
        tips.append(f"`{col} {op} \"{val}\"`")
        if len(tips) >= limit:
            break
    return tips


def write_text_binary(path: Path, content: str) -> None:
    """Write text without Windows newline translation.

    `library.json` already contains CRLF inside `kustoQuery` strings; if we
    write through text mode on Windows, each `\\n` gets translated to `\\r\\n`,
    turning embedded `\\r\\n` into `\\r\\r\\n` and breaking content equality
    with the original. Writing bytes preserves whatever line endings the
    builder produced.
    """
    path.write_bytes(content.encode("utf-8"))


def render_query(q: dict, out_dir: Path | None = None, slug: str | None = None) -> str:
    name = q.get("name") or "(unnamed)"
    cluster = q.get("cluster") or "?"
    database = q.get("database") or "?"
    qtype = q.get("type") or "?"
    panel_path = q.get("panelPath") or []
    widget_title = q.get("widgetTitle") or ""
    kql = (q.get("kustoQuery") or "").strip()
    params = q.get("params") or []

    lines: list[str] = []
    lines.append(f"### {name}")
    lines.append("")
    if widget_title and widget_title != name:
        lines.append(f"_Purpose:_ {widget_title}")
        lines.append("")
    lines.append(
        f"Cluster: `{cluster}` · Database: `{database}` · Type: `{qtype}`"
    )
    if panel_path:
        lines.append(f"Source panel: `{' > '.join(panel_path)}`")
    lines.append("")

    # If KQL is huge, split it to its own file to keep the section browsable
    OVERSIZE_THRESHOLD = 30 * 1024  # 30 KB
    if len(kql) > OVERSIZE_THRESHOLD and out_dir is not None and slug is not None:
        side_name = f"{slug}--{slugify(name)}.kql"
        side_path = out_dir / side_name
        # Write as bytes to avoid Windows line-ending translation doubling
        # the \r characters present in source KQL (library.json uses CRLF).
        side_path.write_bytes((kql + "\n").encode("utf-8"))
        lines.append(
            f"> ⚠️ Verbose machine-generated KQL ({len(kql)//1024} KB, e.g. "
            f"histogram aggregations expanded across many bins). Full body "
            f"extracted to [`{side_name}`]({side_name}); the opening lines "
            f"are shown below for context. Nothing is truncated — the full "
            f"query is preserved verbatim in the `.kql` file."
        )
        lines.append("")
        # Show first ~60 lines as preview
        preview = "\n".join(kql.splitlines()[:60])
        lines.append("```kusto")
        lines.append(preview)
        lines.append("// ... [truncated — see " + side_name + " for full body]")
        lines.append("```")
    else:
        lines.append("```kusto")
        lines.append(kql)
        lines.append("```")
    lines.append("")

    # Params
    if params:
        param_names = [p.get("name") for p in params if p.get("name")]
        if param_names:
            lines.append("**Params:** " + ", ".join(f"`{{{p}}}`" for p in param_names))
            lines.append("")

    # Filter tips
    tips = extract_filter_tips(kql)
    if tips:
        lines.append("**Signal filters seen in KQL:** " + " · ".join(tips))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    library = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    panels = library.get("panels", {})

    # Build the combined list of (slug, title, intro) including detector sub-files
    all_sections: list[tuple[str, str, str]] = list(SECTIONS)
    for slug, title, intro, _ in DETECTOR_GROUPS:
        all_sections.append((slug, title, intro))

    # Group queries by section slug
    buckets: dict[str, list[dict]] = {slug: [] for slug, *_ in all_sections}
    for panel_name, panel in panels.items():
        for q in panel.get("queries", []):
            slug = categorize(panel_name, q.get("name", ""), q.get("type", ""))
            qcopy = dict(q)
            qcopy["_panel"] = panel_name
            buckets[slug].append(qcopy)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Write each section file ----------------------------------------
    section_summaries: dict[str, list[tuple[str, str]]] = {}
    for slug, title, intro in all_sections:
        qs = buckets[slug]
        if not qs:
            # Skip empty buckets (e.g. detector "Other" if everything matched)
            continue
        path = OUT_DIR / f"{slug}.md"
        body: list[str] = []
        body.append(f"# {title}")
        body.append("")
        body.append(f"> Source: EEE RDOS Start Hub dashboard ({len(qs)} queries).")
        body.append("")
        body.append(intro)
        body.append("")
        body.append("---")
        body.append("")
        section_summaries[slug] = []
        for q in qs:
            body.append(render_query(q, out_dir=OUT_DIR, slug=slug))
            body.append("---")
            body.append("")
            section_summaries[slug].append((q.get("name", ""), q.get("type", "")))

        write_text_binary(path, "\n".join(body))
        print(f"  wrote {path.name:50s} ({len(qs):3d} queries)")

    # ---- Write README.md (index) ----------------------------------------
    readme: list[str] = []
    readme.append("# EEE RDOS Start Hub — Investigation Guide")
    readme.append("")
    readme.append(
        "Symptom-keyed reference derived from the EEE RDOS Start Hub dashboard. "
        "Every KQL query backing the dashboard is included here, classified by "
        "investigation intent so an AI agent (or human) can route from a "
        "natural-language symptom directly to the queries that answer it."
    )
    readme.append("")
    readme.append(
        "**How to use:**"
    )
    readme.append("")
    readme.append(
        "1. Identify what you are investigating (VM down? host hardware? network?)."
    )
    readme.append("2. Open the matching section file.")
    readme.append(
        "3. Pick the query whose name / source panel / filter tips match your "
        "symptom. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with "
        "case values."
    )
    readme.append(
        "4. Execute via the vm-kusto-query skill (`kusto_runner.py`) or via "
        "`replay.py` next to this folder (the latter handles all 30+ param "
        "aliases automatically)."
    )
    readme.append("")
    readme.append("**Companion files (in parent folder):**")
    readme.append("")
    readme.append("- `library.json` — canonical machine-readable source of all 172 queries (panel-organized).")
    readme.append("- `library.md` — same content as flat human-readable index.")
    readme.append("- `replay.py` — execution engine; resolves param aliases and runs queries.")
    readme.append("- `link-inventory.md` — non-KQL links found on the page (other dashboards, aka.ms shortcuts).")
    readme.append("")
    readme.append("## Sections")
    readme.append("")
    total = 0
    for slug, title, _intro in all_sections:
        if slug not in buckets or not buckets[slug]:
            continue
        n = len(buckets[slug])
        total += n
        readme.append(f"- [{title}]({slug}.md) — {n} queries")
    readme.append("")
    readme.append(f"**Total queries: {total}**")
    readme.append("")
    readme.append("## Query index (by section)")
    readme.append("")
    for slug, title, _ in all_sections:
        entries = section_summaries.get(slug, [])
        if not entries:
            continue
        readme.append(f"### {title}")
        readme.append("")
        for name, qtype in entries:
            readme.append(f"- `[{qtype}]` **{name}** — see [{slug}.md]({slug}.md)")
        readme.append("")
    write_text_binary(OUT_DIR / "README.md", "\n".join(readme))
    print(f"  wrote README.md (index of {total} queries)")
    print()
    print(f"Done. {total} queries across {len(SECTIONS)} files in {OUT_DIR}")


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


if __name__ == "__main__":
    main()
