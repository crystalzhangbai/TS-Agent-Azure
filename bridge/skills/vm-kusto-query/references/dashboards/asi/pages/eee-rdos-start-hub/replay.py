#!/usr/bin/env python3
"""
Replay EEE RDOS Start Hub KQL queries against Azure infrastructure clusters,
returning structured results instead of requiring you to read dashboard graphs.

The library file `library.json` sits next to this script and contains 166
queries organized into 31 panels. This script:
  1. Loads the library.
  2. Selects queries by panel name (substring match) or by query name.
  3. Substitutes parameters from the VM placement context (vmid, containerid,
     nodeid, cluster, tenantname, roleInstanceName) and a time range.
  4. Runs each query against its native Kusto cluster (auth via az CLI).
  5. Prints results as a table, JSON, or per-query JSON blob.

Usage:
    # List panels and queries
    python eee_replay.py --list-panels
    python eee_replay.py --list-queries --panel "Container / Tenant Health"

    # Run all queries in a panel
    python eee_replay.py --panel "Container / Tenant Health" \
        --vmid 8432a13d-9f3d-40f0-a372-31ff590600e6 \
        --containerid 1e934b75-fa95-40c9-a8d0-5f418f9cb51c \
        --nodeid 33051df7-8a7e-2a3b-3009-393418783d21 \
        --cluster IAD03PrdGPC06 \
        --tenantname 41ca1dce-7901-4446-903e-8d6df89a659c \
        --role-instance-name _azureeastuseastusseedh100001-dn20251030009-339-001 \
        --start "2026-05-07T23:00:00Z" --end "2026-05-08T01:00:00Z"

    # Run a single query by name
    python eee_replay.py --query-name "VMA Event" --vmid ... --start ... --end ...

Authentication:
    Requires az CLI logged in to the Microsoft Corp tenant
    (72f988bf-86f1-41af-91ab-2d7cd011db47).
"""

import argparse
import io
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# Import the existing kusto_runner helpers for auth + execution from the
# vm-kusto-query skill. This script lives at:
#   <repo>/dashboards/asi/pages/eee-rdos-start-hub/replay.py
# kusto_runner lives at:
#   <repo>/.github/skills/vm-kusto-query/scripts/kusto_runner.py
# Walk up 4 levels to repo root, then descend into the skill scripts dir.
# (kusto_runner already wraps sys.stdout/stderr in UTF-8 TextIOWrapper.)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
KUSTO_RUNNER_DIR = os.path.join(REPO_ROOT, ".github", "skills", "vm-kusto-query", "scripts")
sys.path.insert(0, KUSTO_RUNNER_DIR)
from kusto_runner import create_client, execute_query, MICROSOFT_TENANT_ID  # noqa: E402

# library.json sits next to this script.
LIBRARY_PATH = os.path.join(SCRIPT_DIR, "library.json")


# ---------------------------------------------------------------------------
# Param normalization
# ---------------------------------------------------------------------------
#
# Widget queries use many different param names for the same values. We map
# every observed alias to a canonical "slot" then materialize from the user's
# placement context.

CANONICAL = {
    "startTime": "start",
    "endTime":   "end",
    "containerId": "containerid",
    "nodeId":    "nodeid",
    "vmId":      "vmid",
    "cluster":   "cluster",
    "roleInstanceName": "roleInstanceName",
    "tenantName": "tenantname",
    "subscriptionId": "subscriptionId",
}

ALIASES = {
    # time
    "startTime": ["starttime", "StartTime", "queryFrom", "startTimeFilter", "queryStart", "from", "_starttime"],
    "endTime":   ["endtime", "EndTime", "queryTo", "endTimeFilter", "queryEnd", "to", "_endtime"],
    # ids
    "containerId": ["containerid", "containerId", "queryContainerid", "queryContainerId",
                    "ContainerId", "_containerid", "queryContainerID"],
    "nodeId":    ["nodeid", "nodeId", "queryNodeId", "NodeId", "_nodeid", "queryNodeID"],
    "vmId":      ["vmid", "VmId", "vmId", "virtualMachineUniqueId", "vmUniqueId",
                  "queryVmId", "queryVMID", "queryVMId", "queryVmID", "_vmid", "queryVmUniqueId", "VMUniqueId"],
    "cluster":   ["cluster", "Tenant", "Cluster", "tenant", "clusterName",
                  "queryClusterName", "queryCluster", "_cluster"],
    "roleInstanceName": ["roleInstanceName", "queryRoleInstanceName", "RoleInstanceName", "_roleInstanceName"],
    "tenantName": ["tenantname", "tenantName", "queryTenantName", "_tenantname", "tenantNameId"],
    "subscriptionId": ["subscriptionId", "querySubscriptionId", "SubscriptionId"],
    "instanceName": ["queryInstanceName", "instanceName", "InstanceName"],
}


def alias_lookup(param_name: str):
    """Return the canonical slot ('startTime'/'endTime'/'vmId'/...) for a given query param name, or None."""
    pn = param_name.strip()
    for canon, aliases in ALIASES.items():
        if pn == canon or pn in aliases or pn.lower() in [a.lower() for a in aliases]:
            return canon
    return None


def parse_dt(s):
    """Accept '2026-05-07T23:00:00Z' or '2026-05-07 23:00:00' or '2026-05-07'."""
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    s = s.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized datetime: {s!r}")


def kql_value(val, ptype):
    """Format a Python value as a KQL literal for the given param type."""
    if val is None:
        return None
    if ptype == "datetime":
        if isinstance(val, datetime):
            return f"datetime({val.strftime('%Y-%m-%dT%H:%M:%S.%fZ')})"
        return f"datetime({val})"
    if ptype in ("string", None, ""):
        return f"'{str(val).replace(chr(39), chr(39) + chr(39))}'"
    if ptype in ("long", "int", "real", "double", "decimal", "bool", "boolean"):
        return str(val)
    if ptype == "dynamic":
        return f"dynamic({json.dumps(val)})"
    # default
    return f"'{val}'"


def substitute_params(query_def, ctx):
    """
    Build a 'let' prelude that materializes every parameter the query needs,
    then concatenate with the original query body. Returns (final_kql, missing_params).
    """
    params = query_def.get("params") or []
    if not params:
        return query_def["kustoQuery"], []

    lets = []
    missing = []
    for p in params:
        name = p["name"]
        ptype = p.get("type", "string")
        canon = alias_lookup(name)
        if canon == "startTime":
            val = ctx["start"]
        elif canon == "endTime":
            val = ctx["end"]
        elif canon == "containerId":
            val = ctx.get("containerid")
        elif canon == "nodeId":
            val = ctx.get("nodeid")
        elif canon == "vmId":
            val = ctx.get("vmid")
        elif canon == "cluster":
            val = ctx.get("cluster")
        elif canon == "roleInstanceName":
            val = ctx.get("roleInstanceName")
        elif canon == "tenantName":
            val = ctx.get("tenantname")
        elif canon == "subscriptionId":
            val = ctx.get("subscriptionId")
        elif canon == "instanceName":
            val = ctx.get("roleInstanceName")
        else:
            val = ctx.get(name)  # last-resort raw match

        if val is None:
            if p.get("optional"):
                continue
            missing.append(name)
            continue
        lets.append(f"let {name} = {kql_value(val, ptype)};")

    prelude = "\n".join(lets)
    final = (prelude + "\n" + query_def["kustoQuery"]) if prelude else query_def["kustoQuery"]
    return final, missing


# ---------------------------------------------------------------------------
# Library loading
# ---------------------------------------------------------------------------

def load_library(path=LIBRARY_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_panel(library, panel_query: str):
    """Return list of (panel_name, panel_obj) where panel_query is a case-insensitive substring."""
    q = panel_query.lower()
    matches = [(name, p) for name, p in library["panels"].items() if q in name.lower()]
    return matches


def find_queries_by_name(library, name_q: str):
    """Return list of (panel_name, query) matching by query name substring (case-insensitive)."""
    q = name_q.lower()
    out = []
    for panel_name, panel in library["panels"].items():
        for query in panel["queries"]:
            if q in (query.get("name") or "").lower():
                out.append((panel_name, query))
    return out


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_one(query_def, ctx, tenant=MICROSOFT_TENANT_ID, row_limit=200):
    """Execute a single library query. Returns dict with results or error."""
    final_kql, missing = substitute_params(query_def, ctx)
    result = {
        "name": query_def.get("name"),
        "cluster": query_def["cluster"],
        "database": query_def["database"],
        "panel_widget": query_def.get("widgetTitle"),
        "kql": final_kql,
        "missing_params": missing,
        "rows": None,
        "error": None,
    }
    if missing:
        result["error"] = f"Missing params: {missing}"
        return result

    cluster = query_def["cluster"]
    if not cluster.endswith(".kusto.windows.net") and "kusto.windows.net" not in cluster:
        cluster = f"{cluster}.kusto.windows.net"
    try:
        client = create_client(cluster, tenant)
        # cap rows
        capped_kql = f"{final_kql}\n| take {row_limit}" if "| take" not in final_kql else final_kql
        _, rows = execute_query(client, query_def["database"], capped_kql)
        result["rows"] = rows
    except Exception as e:
        result["error"] = str(e)
    return result


def main():
    ap = argparse.ArgumentParser(
        description="Replay EEE Start Hub KQL queries against Kusto and return structured results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--library", default=LIBRARY_PATH, help="Path to library.json (defaults to ./library.json next to this script)")
    ap.add_argument("--list-panels", action="store_true", help="List all panels and exit")
    ap.add_argument("--list-queries", action="store_true",
                    help="List queries (filtered by --panel if given) and exit")
    ap.add_argument("--panel", help="Panel name (substring match, case-insensitive)")
    ap.add_argument("--query-name", help="Query name (substring, case-insensitive). Overrides --panel for selection.")
    ap.add_argument("--vmid", help="VM unique ID")
    ap.add_argument("--containerid", help="Container ID")
    ap.add_argument("--nodeid", help="Node ID")
    ap.add_argument("--cluster", help="Compute cluster (Tenant), e.g. IAD03PrdGPC06")
    ap.add_argument("--tenantname", help="Tenant name (NIC tenant) GUID")
    ap.add_argument("--role-instance-name", dest="roleInstanceName", help="Role instance name")
    ap.add_argument("--subscription-id", dest="subscriptionId", help="Subscription ID (for CRP queries)")
    ap.add_argument("--start", help="Issue start time (ISO 8601 UTC)")
    ap.add_argument("--end", help="Issue end time (ISO 8601 UTC)")
    ap.add_argument("--row-limit", type=int, default=200,
                    help="Max rows per query (default 200)")
    ap.add_argument("--parallel", type=int, default=6,
                    help="Concurrent queries (default 6)")
    ap.add_argument("--format", choices=["json", "summary"], default="summary",
                    help="Output format")
    ap.add_argument("--include-kql", action="store_true",
                    help="In summary mode, also print the rendered KQL for each query")
    args = ap.parse_args()

    library = load_library(args.library)

    # --list-panels
    if args.list_panels:
        print(f"# Panels in {library['service']} / {library['page']}\n")
        for name, p in library["panels"].items():
            print(f"  [{len(p['queries']):>3}] {name}")
        return

    # --list-queries
    if args.list_queries:
        if args.panel:
            matches = find_panel(library, args.panel)
        else:
            matches = list(library["panels"].items())
        for panel_name, panel in matches:
            print(f"\n## {panel_name}")
            for i, q in enumerate(panel["queries"], 1):
                cl = (q.get("cluster") or "?").replace(".kusto.windows.net", "")
                print(f"  {i:>2}. {q.get('name')} [{cl}/{q.get('database')}] {q.get('type','')}")
        return

    # Selection
    selected = []   # list of (panel_name, query_def)
    if args.query_name:
        selected = find_queries_by_name(library, args.query_name)
    elif args.panel:
        for panel_name, panel in find_panel(library, args.panel):
            for q in panel["queries"]:
                selected.append((panel_name, q))
    else:
        ap.error("Specify --panel or --query-name (or --list-panels / --list-queries).")

    if not selected:
        print("No matching queries.", file=sys.stderr)
        sys.exit(1)

    # Context
    ctx = {}
    if args.start:
        ctx["start"] = parse_dt(args.start)
    if args.end:
        ctx["end"] = parse_dt(args.end)
    for k in ("vmid", "containerid", "nodeid", "cluster", "tenantname",
              "roleInstanceName", "subscriptionId"):
        v = getattr(args, k, None)
        if v:
            ctx[k] = v

    print(f"Selected {len(selected)} query(ies):", file=sys.stderr)
    for panel_name, q in selected:
        print(f"  - [{panel_name}] {q['name']}", file=sys.stderr)
    print(file=sys.stderr)

    # Run
    results = []
    with ThreadPoolExecutor(max_workers=args.parallel) as ex:
        future_map = {ex.submit(run_one, q, ctx, MICROSOFT_TENANT_ID, args.row_limit): (panel_name, q)
                      for panel_name, q in selected}
        for fut in as_completed(future_map):
            panel_name, q = future_map[fut]
            res = fut.result()
            res["panel"] = panel_name
            results.append(res)

    if args.format == "json":
        # Strip kql unless explicitly requested
        if not args.include_kql:
            for r in results:
                r.pop("kql", None)
        print(json.dumps(results, indent=2, default=str))
        return

    # summary
    for r in sorted(results, key=lambda x: (x["panel"], x["name"] or "")):
        rows = r.get("rows")
        err = r.get("error")
        n = "?" if rows is None else len(rows)
        cl = r["cluster"].replace(".kusto.windows.net", "")
        status = f"ERROR: {err}" if err else f"{n} row(s)"
        print(f"== [{r['panel']}] {r['name']}  ({cl}/{r['database']}) ==")
        print(f"   status: {status}")
        if args.include_kql:
            print("   kql:")
            for line in (r.get("kql") or "").strip().split("\n"):
                print(f"     {line}")
        if rows:
            # Print first few rows compactly
            for i, row in enumerate(rows[:10], 1):
                trimmed = {k: (v if v is None or len(str(v)) < 80 else str(v)[:77] + "...") for k, v in row.items()}
                print(f"   row {i}: {json.dumps(trimmed, default=str)}")
            if len(rows) > 10:
                print(f"   ... ({len(rows) - 10} more)")
        print()


if __name__ == "__main__":
    main()
