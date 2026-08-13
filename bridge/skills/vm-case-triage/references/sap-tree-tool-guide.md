# SAP Tree Tool Guide

The **SAP Tree tool** (Support Area Path Tree) is the canonical way to browse and verify the full cascading DFM Support Area Path before changing it in a case or collab request. Use it to look up unfamiliar teams or verify path segment names.

---

## Local SAP Tree (Recommended — Fast & Offline)

We now have a **full local copy** of the SAP tree synced from Case Buddy cache:

```
references/sap-tree-full.json      # 53,000+ SAP paths, flattened
scripts/sync-sap-tree.ps1          # Re-sync from Case Buddy cache
```

### Quick search (PowerShell)
Run from the skill directory (`cd .github/skills/vm-case-triage`) so the relative path resolves, and always pass `encoding='utf-8'` — the file is UTF-8 with non-ASCII characters and Windows' default cp1252 decode crashes on it (`UnicodeDecodeError`):
```powershell
# Search for IIS paths
python -c "import json; [print(n['path']) for n in json.load(open('references/sap-tree-full.json', encoding='utf-8')) if 'IIS' in n['path']]"
```
> Each node is `{path, id, name, type, state}` — match keywords against `path`. This file **ships in the repo** (~13 MB, committed), so a fresh clone already has it. To refresh it (or if it's ever missing), use the online tool below or run `pwsh -File scripts/sync-sap-tree.ps1`.

### Re-sync after Case Buddy refresh
```powershell
pwsh -File scripts/sync-sap-tree.ps1
```

The JSON is sourced from Case Buddy's `LocalCache\Local\CaseBuddy\*-SAP.json` files (updated whenever Case Buddy loads SAP Browser).

---

## Online Tool URL (Fallback)

```
https://dfm.support.microsoft.com/supportAreaPath/search
```

> If the above URL redirects or times out, try the alternate Supportability portal entry point:
> ```
> https://supportability.visualstudio.com/AzureVMPOD/_wiki/wikis/AzureVMPOD.wiki/Support-Area-Path-Tree
> ```

---

## How to search

1. **Open the SAP Tree tool** in your browser (Edge with your microsoftsupport.com account).
2. In the search box, enter one of:
   - A **keyword** (e.g., `AKS`, `backup`, `ExpressRoute`)
   - A **team name** (e.g., `XStore Triage`, `ANP`, `Host Networking`)
   - A **support product** (e.g., `Azure Kubernetes Service`, `Azure Files`)
3. The tree expands to show the full cascading path.
4. **Copy each segment exactly** — DFM tree matching is case-sensitive.

---

## Search tips

- **Ambiguous keywords**: Many keywords appear in multiple paths (e.g., `backup` matches both `Azure VM Backup` and `SQL Backup`). Always verify the top-level product family before selecting.
- **Short abbreviations**: Search for the full name first (`Express Route`, not `ExR`). Abbreviations may not match.
- **New paths / schema drift**: DFM's SAP tree is maintained by Cloudnet and can change without notice. If a DFM cascading level reports "'<seg>' not found" while you walk the path, re-search in the SAP Tree tool to find the current segment name and update `support-area-path-map.md`.
- **Verify path correctness**: After finding a path in the SAP Tree tool, walk the DFM cascading dropdown manually for one real case to confirm every level resolves.

---

## Common search terms by domain

### Compute / VM
| Search term | Expected path (short) |
|---|---|
| `Virtual Machines` | Azure > Compute > Virtual Machines |
| `CRP` / `Resource Provider` | Azure > Compute > Resource Provider |
| `Compute Manager` | Azure > Compute > Compute Manager |
| `Hardware` / `WHEA` | Azure > Compute > Hardware > Triage |
| `Azure Boost` / `NVMe` / `ASAP` | Azure > Compute > Azure Boost > ASAP |
| `ANP` / `Node Diagnostics` | Azure > Compute > Node Diagnostics > ANP |

### Storage
| Search term | Expected path (short) |
|---|---|
| `XStore` / `disk blackout` | Azure > Storage > XStore > XStore_Triage |
| `Managed Disk` / `Disks RP` | Azure > Compute > Disks > Resource Provider |
| `Azure Files` / `SMB` / `NFS` | Azure > Storage > Azure Files |
| `Azure Files Sync` / `AFS` | Azure > Storage > Azure Files > Sync |
| `Elastic SAN` | Azure > Storage > Elastic SAN |

### Network
| Search term | Expected path (short) |
|---|---|
| `Host Networking` / `VFP` / `AccelNet` | Azure > Network > Host Networking > Triage |
| `Express Route` / `ExR` | Azure > Network > Connectivity > Triage |
| `Application Gateway` / `WAF` | Azure > Network > Application Gateway > Triage |
| `Load Balancer` / `SLB` | Azure > Network > Load Balancer > Triage |
| `VPN Gateway` | Azure > Network > VPN Gateway > Triage |

### Containers
| Search term | Expected path (short) |
|---|---|
| `AKS` / `Kubernetes` | Azure > Containers > AKS |
| `Cluster Operations` | Azure > Containers > AKS > Cluster Operations |
| `Autoscaler` | Azure > Containers > AKS > Autoscaler |
| `Container Apps` | Azure > Containers > Container Apps > Triage |

### Backup / DR
| Search term | Expected path (short) |
|---|---|
| `Azure Backup` / `VM Backup` | Azure > Backup > Azure VM Backup > Triage |
| `Site Recovery` / `ASR` | Azure > Disaster Recovery > Azure Site Recovery > Triage |
| `Backup Vault` | Azure > Backup > Recovery Services Vault |

### Database
| Search term | Expected path (short) |
|---|---|
| `SQL on VM` / `SQL Server on Azure VM` | Azure > Compute > Virtual Machines > SQL on VM |
| `SAP on VM` / `SAP HANA` | Azure > Compute > Virtual Machines > SAP on VM |
| `Cosmos DB` | Azure > Databases > Cosmos DB |

### Serverless / PaaS
| Search term | Expected path (short) |
|---|---|
| `Functions` / `Function App` | Azure > Compute > Functions > Triage |
| `App Service` / `Web App` | Azure > App Service > Web App > Triage |

---

## Workflow: unknown team → correct SAP

1. Identify the key symptom (e.g., "KEDA autoscaling not working").
2. Search the SAP Tree tool for the product name (`KEDA` or `Container Apps`).
3. Note the full cascading path from the tree.
4. Cross-reference with `support-area-path-map.md` — if the path is not there, add it.
5. Hand the full cascading path to the user — they set it manually in DFM (Support Area Path dropdown) and click Transfer. This skill does not edit DFM directly.
