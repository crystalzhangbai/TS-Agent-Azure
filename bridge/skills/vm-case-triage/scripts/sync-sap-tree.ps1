<#
.SYNOPSIS
    Sync SAP tree from CaseBuddy local cache to sap-tree-full.json.

.DESCRIPTION
    Case Buddy (MSIX app) caches the entire DFM Support Area Path tree as JSON
    files in its LocalCache. This script reads all *-SAP.json files, flattens
    the nested tree into a single list of {path, id, name, type, state}, and
    writes it to the skill's references/ directory.

    Run this script whenever Case Buddy refreshes its cache (e.g., after app
    restart or manual refresh in SAP Browser).

.EXAMPLE
    pwsh -File sync-sap-tree.ps1
#>

$ErrorActionPreference = 'Stop'

# Locate CaseBuddy cache
$CaseBuddyCache = Join-Path $env:LOCALAPPDATA 'Packages\f1d3aaed-6716-47ea-8850-ff1b01ff7c88_8wekyb3d8bbwe\LocalCache\Local\CaseBuddy'
if (-not (Test-Path $CaseBuddyCache)) {
    Write-Error "CaseBuddy cache not found at $CaseBuddyCache. Make sure Case Buddy is installed and has loaded SAP data."
    exit 1
}

$OutPath = Join-Path $PSScriptRoot '..\references\sap-tree-full.json'

$py = @'
import json, os, sys

SRC = sys.argv[1]
OUT = sys.argv[2]

def flatten(nodes, prefix=""):
    results = []
    for n in nodes:
        name = n.get("name", "")
        path = f"{prefix} > {name}" if prefix else name
        results.append({
            "path": path,
            "id": n.get("id"),
            "name": name,
            "type": n.get("type"),
            "state": n.get("state")
        })
        children = n.get("tree", [])
        if children:
            results.extend(flatten(children, path))
    return results

all_nodes = []
root_path = os.path.join(SRC, "Root-SAP.json")
with open(root_path, encoding="utf-8-sig") as f:
    root = json.load(f)

for fam in root:
    fam_name = fam["name"]
    fam_file = os.path.join(SRC, f"{fam_name}-SAP.json")
    if os.path.exists(fam_file):
        with open(fam_file, encoding="utf-8-sig") as ff:
            data = json.load(ff)
        for item in data:
            tree = item.get("tree", [])
            all_nodes.extend(flatten(tree, fam_name))
    else:
        all_nodes.append({
            "path": fam_name,
            "id": fam["id"],
            "name": fam_name,
            "type": fam["type"],
            "state": fam["state"]
        })

# Dedupe by path
seen = set()
deduped = []
for n in all_nodes:
    if n["path"] not in seen:
        seen.add(n["path"])
        deduped.append(n)

deduped.sort(key=lambda x: x["path"])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=1)

print(f"Synced {len(deduped)} SAP paths to {OUT}")
'@

$tmpPy = Join-Path $env:TEMP 'sync_sap_tree.py'
Set-Content -Path $tmpPy -Value $py -Encoding UTF8

$env:PYTHONIOENCODING = 'utf-8'
python $tmpPy $CaseBuddyCache $OutPath
