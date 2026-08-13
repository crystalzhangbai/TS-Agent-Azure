# SME Team → DFM Support Area Path Map

**Single source of truth** for the mapping from internal SME team names (as used in ICM Owning Team) to the cascading DFM "Support Area Path" tree.

This file lives in `vm-case-triage/references/` and is the local source for route recommendations, SAP transfer guidance, and VM-adjacent owning-team lookups. Do not duplicate this table elsewhere.

## Why this exists

DFM's "Support Area Path" is a 3-5 level cascading dropdown tree. The leaf team name alone is NOT enough — you need the full path so the user can manually click each level. Auto-clicking the tree is explicitly forbidden (see Decision D7) because misrouting silently sends the case / collab to the wrong team.

## How to read

- **SME Team** — the short team name used in ICM Owning Team and case notes
- **Support Area Path** — full path the user must select in DFM (each segment is one dropdown level)
- **Notes** — clarifications when the team name overlaps with other paths

## VM / Storage in scope

| SME Team | Support Area Path | Notes |
|---|---|---|
| XStore_Triage                | `Azure > Storage > XStore > XStore_Triage`                          | Disk blackouts, storage server faults |
| Host Networking\Triage       | `Azure > Network > Host Networking > Triage`                        | VFP drops, AccelNet anomaly, host NIC |
| ANP                          | `Azure > Compute > Node Diagnostics > ANP`                          | Node behavior anomalies not HW/storage |
| Hardware Team                | `Azure > Compute > Hardware > Triage`                               | HardwareFault RCA, WHEA, SEL, MCE |
| Compute Manager              | `Azure > Compute > Compute Manager`                                 | VM lifecycle, allocation, CRP |
| CRP / Compute PG             | `Azure > Compute > Resource Provider`                               | Allocation failures, CRP API errors |
| Azure Files Sync             | `Azure > Storage > Azure Files > Sync`                              | AFS sync errors |
| Disks RP                     | `Azure > Compute > Disks > Resource Provider`                       | Managed disk provisioning |
| Azure Boost / ASAP           | `Azure > Compute > Azure Boost > ASAP`                              | NVMe controller, ASAP issues |

## Often-misrouted (NOT VM scope — use vm-case-triage Stage R for transfer)

| Symptom | Correct Support Area Path | Owning Team |
|---|---|---|
| AKS cluster operations         | `Azure > Containers > AKS > Cluster Operations`              | AKS Team |
| AKS node autoscaler            | `Azure > Containers > AKS > Autoscaler`                      | AKS Team |
| Networking-only (ExR / vWAN)   | `Azure > Network > Connectivity > Triage`                    | Network Team |
| App Gateway                    | `Azure > Network > Application Gateway > Triage`             | AppGW Team |
| Load Balancer (SLB)            | `Azure > Network > Load Balancer > Triage`                   | SLB Team |
| Azure Backup (VM)              | `Azure > Backup > Azure VM Backup > Triage`                  | Backup Team |
| SQL on Azure VM                | `Azure > Compute > Virtual Machines > SQL on VM`             | SQL Team (joint) |
| SAP on Azure VM                | `Azure > Compute > Virtual Machines > SAP on VM`             | SAP Team (joint) |
| Azure Site Recovery            | `Azure > Disaster Recovery > Azure Site Recovery > Triage`   | ASR Team |
| Container Apps                 | `Azure > Containers > Container Apps > Triage`               | Container Apps |
| Functions                      | `Azure > Compute > Functions > Triage`                       | Functions |
| IIS / App Pool / Web Server in-guest config | `Servers > Internet Information Services > Internet Information Services 10.0` | IIS / Windows Server (in-guest, not Azure platform) |

## Maintenance

When you discover a new SME team or a path schema change in DFM:

1. Add or update the row here (never duplicate elsewhere)
2. Re-test by manually walking the cascading dropdowns in DFM and confirming each segment matches

> ⚠️ **DFM SAP tree is owned by Cloudnet — schema changes happen quietly.** When a DFM cascading level reports "level N: '<seg>' not found", re-walk DFM by hand and fix this file.

## Schema TODO (P1 — to be enriched by Fleet Agent A3)

- Add a "Last verified" date column per row
- Add Cloudnet `SupportAreaPathId` GUID per row if the DFM API surfaces it (avoids string-name drift)
- Note the matching ICM/CRI template per row (used when opening an ICM manually via ASC)
