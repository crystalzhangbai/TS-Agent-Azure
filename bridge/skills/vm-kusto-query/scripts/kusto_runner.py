#!/usr/bin/env python3
"""
General-purpose Kusto (KQL) query runner.

Single-query mode:
    python kusto_runner.py --cluster azurecm.kusto.windows.net --database AzureCM --query "LogContainerSnapshot | take 5"
    python kusto_runner.py --cluster disks.kusto.windows.net --database Disks --query ".show tables" --format json
    python kusto_runner.py --cluster azurecm.kusto.windows.net --database AzureCM --query-file my_query.kql --format csv

Batch / parallel mode (one shared auth, concurrent execution, per-query timeout):
    python kusto_runner.py --batch queries.json --max-workers 5 --server-timeout 60

    queries.json format:
      [
        {"label": "vm_identity",   "cluster": "azurecm.kusto.windows.net",       "database": "AzureCM",    "query": "..."},
        {"label": "node_fault",    "cluster": "azurecm.kusto.windows.net",       "database": "AzureCM",    "query": "..."},
        {"label": "crp_op",        "cluster": "azcrp.kusto.windows.net",         "database": "crp_allprod","query": "..."}
      ]

    Batch output format:
      - default: per-label headers + table results, plus a timing summary at the end
      - --format json: a single JSON array `[{label, cluster, database, status, elapsed_ms, columns, rows, error}, ...]`
        written to stdout. Suitable for piping into another tool or `_work/<case>/data/*.json`.
"""
import sys
import io
import argparse
import json
import csv as csv_mod
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

# Fix UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.identity import AzureCliCredential

MICROSOFT_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"

# Process-wide cache: one KustoClient per (cluster_uri, tenant_id).
# Reuses the AAD token across queries in the same process — avoids per-query MSAL latency.
_CLIENT_CACHE: dict = {}


def _normalize_cluster_uri(cluster_uri: str) -> str:
    if not cluster_uri.startswith("https://"):
        cluster_uri = f"https://{cluster_uri}"
    return cluster_uri


def create_client(cluster_uri: str, tenant_id: str = MICROSOFT_TENANT_ID) -> KustoClient:
    """Get (or build & cache) an authenticated KustoClient for (cluster_uri, tenant_id)."""
    cluster_uri = _normalize_cluster_uri(cluster_uri)
    key = (cluster_uri, tenant_id)
    client = _CLIENT_CACHE.get(key)
    if client is None:
        cred = AzureCliCredential(tenant_id=tenant_id)
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
            cluster_uri, credential=cred
        )
        client = KustoClient(kcsb)
        _CLIENT_CACHE[key] = client
    return client


def _make_request_properties(server_timeout_seconds: int | None) -> ClientRequestProperties | None:
    """Build ClientRequestProperties with a server-side timeout, if specified."""
    if not server_timeout_seconds or server_timeout_seconds <= 0:
        return None
    crp = ClientRequestProperties()
    crp.set_option(
        ClientRequestProperties.request_timeout_option_name,
        timedelta(seconds=server_timeout_seconds),
    )
    return crp


def execute_query(
    client: KustoClient,
    database: str,
    query: str,
    server_timeout_seconds: int | None = None,
):
    """Execute a KQL query and return (columns, rows). server_timeout_seconds is enforced server-side."""
    query_stripped = query.strip()
    crp = _make_request_properties(server_timeout_seconds)
    # Management commands start with '.'
    if query_stripped.startswith("."):
        response = client.execute_mgmt(database, query_stripped, crp)
    else:
        response = client.execute(database, query_stripped, crp)

    columns = [c.column_name for c in response.primary_results[0].columns]
    rows = []
    for row in response.primary_results[0]:
        rows.append({col: row[col] for col in columns})
    return columns, rows


def format_table(columns: list, rows: list, max_col_width: int = 60) -> str:
    """Format results as a readable text table."""
    if not rows:
        return "(no results)"

    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = min(
            max(len(col), max(len(str(row.get(col, ""))[:max_col_width]) for row in rows)),
            max_col_width,
        )

    # Header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    lines = [header, separator]

    # Rows
    for row in rows:
        line = " | ".join(
            str(row.get(col, ""))[:max_col_width].ljust(col_widths[col]) for col in columns
        )
        lines.append(line)

    lines.append(f"\n({len(rows)} row(s) returned)")
    return "\n".join(lines)


def format_kv(columns: list, rows: list) -> str:
    """Format results as key-value pairs (one record per block), skipping empty values."""
    if not rows:
        return "(no results)"

    blocks = []
    for i, row in enumerate(rows, 1):
        lines = [f"--- Record {i} ---"]
        for col in columns:
            val = row.get(col)
            if val is not None and str(val).strip() and str(val) not in ("0", "False", ""):
                lines.append(f"  {col}: {val}")
        blocks.append("\n".join(lines))

    blocks.append(f"\n({len(rows)} row(s) returned)")
    return "\n".join(blocks)


def format_json_output(columns: list, rows: list) -> str:
    """Format results as JSON."""
    return json.dumps(rows, indent=2, default=str)


def format_csv_output(columns: list, rows: list) -> str:
    """Format results as CSV."""
    output = io.StringIO()
    writer = csv_mod.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: str(v) for k, v in row.items()})
    return output.getvalue()


def run_query(
    cluster: str,
    database: str,
    query: str,
    tenant: str = MICROSOFT_TENANT_ID,
    output_format: str = "table",
    print_query: bool = True,
    server_timeout_seconds: int | None = None,
) -> list:
    """
    High-level function: connect, execute, format, print.
    Returns the list of row dicts for programmatic use.
    """
    client = create_client(cluster, tenant)

    if print_query:
        print(f"\n{'=' * 80}")
        print(f"Cluster:  {cluster}")
        print(f"Database: {database}")
        print(f"Query:")
        for line in query.strip().split("\n"):
            print(f"  {line}")
        print("=" * 80)

    try:
        columns, rows = execute_query(client, database, query, server_timeout_seconds)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return []

    if output_format == "json":
        print(format_json_output(columns, rows))
    elif output_format == "csv":
        print(format_csv_output(columns, rows))
    elif output_format == "kv":
        print(format_kv(columns, rows))
    else:
        print(format_table(columns, rows))

    return rows


def run_queries_parallel(
    specs: list,
    tenant: str = MICROSOFT_TENANT_ID,
    max_workers: int = 5,
    server_timeout_seconds: int = 60,
    wall_timeout_seconds: int = 180,
) -> list:
    """
    Run multiple independent KQL queries concurrently.

    Args:
        specs: list of dicts: {label, cluster, database, query}
        max_workers: thread pool size (default 5; Kusto SDK is thread-safe)
        server_timeout_seconds: Kusto server-side per-query timeout (default 60s)
        wall_timeout_seconds: client-side per-query wait cap (default 180s).
            If a future hasn't returned within this window it is marked timeout
            and skipped — the rest of the batch is unaffected.

    Returns: list of result dicts, ORIGINAL order preserved:
        {label, cluster, database, status: "ok"|"error"|"timeout",
         elapsed_ms, columns, rows, error}

    Auth: a single AzureCliCredential is shared per cluster via _CLIENT_CACHE,
    so MSAL token acquisition happens once per cluster, not once per query.
    """
    # Pre-warm clients (serial) so token acquisition errors surface before fan-out
    clusters_seen = set()
    for spec in specs:
        cu = _normalize_cluster_uri(spec["cluster"])
        if cu not in clusters_seen:
            try:
                create_client(cu, tenant)
            except Exception as e:
                print(f"WARN: client init failed for {cu}: {e}", file=sys.stderr)
            clusters_seen.add(cu)

    def _run_one(idx: int, spec: dict) -> dict:
        label = spec.get("label", f"q{idx}")
        cluster = spec["cluster"]
        database = spec["database"]
        query = spec["query"]
        result = {
            "label": label,
            "cluster": cluster,
            "database": database,
            "status": "error",
            "elapsed_ms": 0,
            "columns": [],
            "rows": [],
            "error": None,
        }
        t0 = time.monotonic()
        try:
            client = create_client(cluster, tenant)
            columns, rows = execute_query(client, database, query, server_timeout_seconds)
            result["status"] = "ok"
            result["columns"] = columns
            result["rows"] = rows
        except Exception as e:
            result["error"] = f"{type(e).__name__}: {e}"
        finally:
            result["elapsed_ms"] = int((time.monotonic() - t0) * 1000)
        return result

    # Submit all
    results: list = [None] * len(specs)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_idx = {
            pool.submit(_run_one, i, spec): i for i, spec in enumerate(specs)
        }
        for fut in as_completed(future_to_idx, timeout=None):
            i = future_to_idx[fut]
            try:
                results[i] = fut.result(timeout=wall_timeout_seconds)
            except Exception as e:
                spec = specs[i]
                results[i] = {
                    "label": spec.get("label", f"q{i}"),
                    "cluster": spec["cluster"],
                    "database": spec["database"],
                    "status": "timeout",
                    "elapsed_ms": wall_timeout_seconds * 1000,
                    "columns": [],
                    "rows": [],
                    "error": f"wall-timeout > {wall_timeout_seconds}s: {e}",
                }
    return results


def print_batch_results(results: list, output_format: str = "table") -> None:
    """Pretty-print batch results to stdout, grouped per label, with a timing summary."""
    if output_format == "json":
        # Strip non-serializable values (datetime, etc.) via default=str
        print(json.dumps(results, indent=2, default=str))
        return

    total_ms = 0
    ok = err = to = 0
    for r in results:
        total_ms += r["elapsed_ms"]
        if r["status"] == "ok":
            ok += 1
        elif r["status"] == "timeout":
            to += 1
        else:
            err += 1
        header = (
            f"\n{'=' * 100}\n"
            f"[{r['status'].upper()}] {r['label']}  "
            f"({r['cluster']} / {r['database']}, {r['elapsed_ms']} ms, "
            f"{len(r['rows'])} rows)\n"
            f"{'=' * 100}"
        )
        print(header)
        if r["status"] == "ok":
            if output_format == "csv":
                print(format_csv_output(r["columns"], r["rows"]))
            elif output_format == "kv":
                print(format_kv(r["columns"], r["rows"]))
            else:
                print(format_table(r["columns"], r["rows"]))
        else:
            print(f"  {r['error']}")

    print(
        f"\n{'-' * 100}\n"
        f"Batch summary: {len(results)} queries  "
        f"({ok} ok, {err} error, {to} timeout)  "
        f"wall-clock-equivalent serial time: {total_ms} ms\n"
        f"{'-' * 100}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Execute KQL query/queries against Azure Data Explorer (Kusto) clusters."
    )
    parser.add_argument(
        "--cluster",
        default=None,
        help="Kusto cluster hostname (e.g., azurecm.kusto.windows.net). Single-query mode only.",
    )
    parser.add_argument("--database", default=None, help="Database name. Single-query mode only.")
    parser.add_argument("--query", default=None, help="KQL query string")
    parser.add_argument("--query-file", default=None, help="Path to a .kql file")
    parser.add_argument(
        "--batch",
        default=None,
        help=(
            "Path to a JSON file with a list of query specs: "
            '[{"label","cluster","database","query"}, ...]. '
            "Runs all entries concurrently with a shared auth pool."
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Batch mode: thread pool size (default 5). Kusto SDK is thread-safe.",
    )
    parser.add_argument(
        "--server-timeout",
        type=int,
        default=60,
        help="Per-query Kusto server-side timeout in seconds (default 60). 0 = no timeout (server default).",
    )
    parser.add_argument(
        "--wall-timeout",
        type=int,
        default=180,
        help="Batch mode: per-query client wall-clock cap in seconds (default 180).",
    )
    parser.add_argument(
        "--tenant",
        default=MICROSOFT_TENANT_ID,
        help=f"Azure AD tenant ID (default: Microsoft Corp {MICROSOFT_TENANT_ID})",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv", "kv"],
        default="table",
        help="Output format (default: table). 'kv' = key-value pairs skipping empty fields.",
    )
    args = parser.parse_args()

    # --- Batch mode ---
    if args.batch:
        with open(args.batch, "r", encoding="utf-8") as f:
            specs = json.load(f)
        if not isinstance(specs, list) or not all(
            isinstance(s, dict) and {"cluster", "database", "query"} <= s.keys() for s in specs
        ):
            parser.error(
                "--batch file must be a JSON list of objects with keys: cluster, database, query (and optional label)"
            )
        results = run_queries_parallel(
            specs,
            tenant=args.tenant,
            max_workers=args.max_workers,
            server_timeout_seconds=args.server_timeout,
            wall_timeout_seconds=args.wall_timeout,
        )
        print_batch_results(results, output_format=args.format)
        # Exit non-zero only if EVERY query failed; partial failure is acceptable
        if results and all(r["status"] != "ok" for r in results):
            sys.exit(2)
        return

    # --- Single-query mode ---
    if not args.cluster or not args.database:
        parser.error("Single-query mode requires --cluster and --database (or use --batch)")
    if not args.query and not args.query_file:
        parser.error("Must specify either --query or --query-file (or use --batch)")

    if args.query_file:
        with open(args.query_file, "r", encoding="utf-8") as f:
            query = f.read()
    else:
        query = args.query

    run_query(
        cluster=args.cluster,
        database=args.database,
        query=query,
        tenant=args.tenant,
        output_format=args.format,
        server_timeout_seconds=args.server_timeout,
    )


if __name__ == "__main__":
    main()
