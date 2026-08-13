"""
build-investigation-guide.py — Generate chapter-keyed investigation guide from library.json

Generic generator for any ASI page library. Uses the **natural panel hierarchy**
(panelPath[0] = top-level chapter, panelPath[1] = sub-group) rather than
page-specific symptom heuristics. Produces one .md per chapter under <out>/,
plus README.md as the index.

If a chapter file would exceed `--max-md-size` bytes (default 45 KB), it is
auto-split by 2nd-level sub-group into sibling files: e.g.

    08-emerging-issues.md  (small leaders)
    08a-emerging-issues--nvme.md
    08b-emerging-issues--network.md
    ...

Individual KQL bodies larger than 30 KB are extracted to a sibling `.kql` file
and the main .md keeps a stub + 60-line preview. The full body is preserved
verbatim in the .kql file — nothing is truncated.

Usage:
    python build-investigation-guide.py \\
      --library ../pages/wf-unexpected-restart/library.json \\
      --out     ../pages/wf-unexpected-restart/investigation-guide \\
      --title   "EEE RDOS — WF Unexpected Restart"
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OVERSIZE_KQL_THRESHOLD = 30 * 1024     # KQL bodies > 30 KB → sidecar .kql
DEFAULT_MAX_MD_SIZE = 45 * 1024        # chapter .md > 45 KB → split by sub-group


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "x"


def write_text_binary(path: Path, content: str) -> None:
    """Write text without Windows newline translation.

    `library.json` already contains CRLF inside `kustoQuery` strings; writing
    through text mode on Windows translates each `\\n` to `\\r\\n`, turning
    embedded `\\r\\n` into `\\r\\r\\n` and breaking content equality with the
    original. Writing bytes preserves whatever line endings the source had.
    """
    path.write_bytes(content.encode("utf-8"))


FILTER_TIP_RE = re.compile(
    r'where\s+([A-Za-z_][\w\.]*)\s*'
    r'(==|=~|has|contains|startswith|endswith|!=|<>)\s*'
    r'("([^"]+)"|\'([^\']+)\')',
    re.IGNORECASE,
)


def extract_filter_tips(kql: str, limit: int = 8) -> list[str]:
    seen: set = set()
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


# ---------------------------------------------------------------------------
# Auto-derive a "what this query does" purpose line from the KQL body.
# Pure structural parse — no LLM. Picks up:
#   * primary tables (camelCase identifiers preceding `|`, plus cluster().database().T forms)
#   * cross-cluster references (cluster("x").database("y").Table)
#   * summarize / count / top aggregations
#   * the final `project` column list (what the result row looks like)
# ---------------------------------------------------------------------------

CROSS_CLUSTER_RE = re.compile(
    r"""cluster\(\s*['"]([^'"]+)['"]\s*\)
        \s*\.\s*database\(\s*['"]([^'"]+)['"]\s*\)
        \s*\.\s*([A-Za-z_][\w]*)""",
    re.IGNORECASE | re.VERBOSE,
)

# Bare table at the start of a pipeline statement: a line whose first token
# is a CapitalCase identifier followed (eventually) by `|`. We accept tables
# starting an expression after `let X = ` too.
BARE_TABLE_RE = re.compile(
    r"""(?:^|[\n;\(])
        \s*(?:let\s+[A-Za-z_]\w*\s*=\s*)?
        ([A-Z][A-Za-z0-9_]{2,})        # CapitalCase table name, 3+ chars
        \s*(?=\n?\s*\|)""",            # next pipe
    re.MULTILINE | re.VERBOSE,
)

SUMMARIZE_RE = re.compile(
    r"\|\s*summarize\s+(.+?)(?:\s+by\s+([^\n|;]+))?(?=\n\s*\||;|\n\s*let\s|\n\s*$|\Z)",
    re.IGNORECASE | re.DOTALL,
)

TOP_RE = re.compile(
    r"\|\s*top\s+(\d+)\s+by\s+([^\n|]+)",
    re.IGNORECASE,
)

PROJECT_RE = re.compile(
    r"\|\s*project(?:-away|-rename|-reorder)?\s+([^\n|]+?)(?=\n\s*\||\n\s*$|\Z)",
    re.IGNORECASE | re.DOTALL,
)

# Words that look like KQL operators / keywords, not column names.
KQL_RESERVED = {
    "where", "summarize", "project", "extend", "join", "kind", "inner", "outer",
    "leftouter", "rightouter", "fullouter", "leftsemi", "rightsemi", "leftanti",
    "rightanti", "on", "by", "take", "limit", "top", "order", "asc", "desc", "let",
    "true", "false", "null", "and", "or", "not", "in", "contains", "has", "startswith",
    "endswith", "matches", "regex", "between", "ago", "datetime", "todatetime",
    "tostring", "toint", "tolong", "todouble", "iff", "case", "make_list", "make_set",
    "distinct", "count", "dcount", "sum", "avg", "min", "max", "arg_max", "arg_min",
    "any", "all",
}


def _norm_table_list(items, limit=6):
    seen = []
    for t in items:
        if t in seen:
            continue
        if t.lower() in KQL_RESERVED:
            continue
        seen.append(t)
        if len(seen) >= limit:
            break
    return seen


def _extract_tables(kql: str) -> list[str]:
    """Return the distinct table names referenced (cross-cluster + bare)."""
    tables: list[str] = []
    for m in CROSS_CLUSTER_RE.finditer(kql):
        tables.append(m.group(3))
    for m in BARE_TABLE_RE.finditer(kql):
        tables.append(m.group(1))
    return _norm_table_list(tables, limit=6)


def _extract_project_cols(kql: str) -> list[str]:
    """Return the column list of the LAST top-level project (the output schema)."""
    matches = list(PROJECT_RE.finditer(kql))
    if not matches:
        return []
    cols_blob = matches[-1].group(1)
    # `project A=expr, B, C=...` -> grab the lhs names
    cols: list[str] = []
    depth = 0
    cur = []
    for ch in cols_blob:
        if ch in "([{":
            depth += 1
            cur.append(ch)
        elif ch in ")]}":
            depth = max(0, depth - 1)
            cur.append(ch)
        elif ch == "," and depth == 0:
            cols.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        cols.append("".join(cur).strip())
    out: list[str] = []
    for c in cols:
        if not c:
            continue
        # `A = expr` -> A
        lhs = c.split("=", 1)[0].strip()
        # `project-rename Foo=Bar` keeps Foo
        # strip stray quotes/whitespace
        lhs = lhs.strip("`'\" ")
        if not lhs:
            continue
        if lhs.lower() in KQL_RESERVED:
            continue
        out.append(lhs)
        if len(out) >= 10:
            break
    return out


def _extract_aggregations(kql: str) -> list[str]:
    """Pick out short hint of summarize/count/top operations."""
    bits: list[str] = []
    for m in SUMMARIZE_RE.finditer(kql):
        agg = re.sub(r"\s+", " ", m.group(1)).strip().rstrip(";").strip()
        by = m.group(2)
        if by:
            by = re.sub(r"\s+", " ", by).strip().rstrip(";").strip()
            bits.append(f"summarize {agg[:80]} by {by[:80]}")
        else:
            bits.append(f"summarize {agg[:80]}")
        if len(bits) >= 2:
            break
    for m in TOP_RE.finditer(kql):
        bits.append(f"top {m.group(1)} by {m.group(2).strip()[:60]}")
        if len(bits) >= 3:
            break
    return bits


def derive_purpose(kql: str) -> dict:
    """Return {tables, output_cols, aggregations} structural summary of the KQL."""
    return {
        "tables": _extract_tables(kql),
        "output_cols": _extract_project_cols(kql),
        "aggregations": _extract_aggregations(kql),
    }


def render_query(q: dict, out_dir: Path, file_slug: str) -> str:
    """Render a single query record into markdown.

    If the KQL body exceeds OVERSIZE_KQL_THRESHOLD, write it to a sidecar
    .kql file and emit a stub + preview in the main markdown.
    """
    name = q.get("name") or "(unnamed)"
    description = (q.get("description") or "").strip()
    cluster = q.get("cluster") or "?"
    database = q.get("database") or "?"
    qtype = q.get("type") or "?"
    widget_type = q.get("widgetType") or ""
    widget_title = q.get("widgetTitle") or ""
    panel_path = q.get("panelPath") or []
    kql = (q.get("kustoQuery") or "").strip()
    params = q.get("params") or []

    lines: list[str] = []
    lines.append(f"### {name}")
    lines.append("")
    if description:
        lines.append(f"_{description}_")
        lines.append("")
    if widget_title and widget_title != name:
        lines.append(f"_Widget purpose:_ {widget_title}")
        lines.append("")
    extra = f" · Widget: `{widget_type}`" if widget_type and widget_type != qtype else ""
    lines.append(
        f"Cluster: `{cluster}` · Database: `{database}` · Type: `{qtype}`{extra}"
    )
    if panel_path:
        lines.append(f"Source panel: `{' > '.join(panel_path)}`")
    lines.append("")

    # Auto-derived "What it does" block
    purpose = derive_purpose(kql)
    purpose_lines: list[str] = []
    if purpose["tables"]:
        purpose_lines.append(
            "**Tables:** " + ", ".join(f"`{t}`" for t in purpose["tables"])
        )
    if purpose["aggregations"]:
        purpose_lines.append(
            "**Aggregations:** " + " · ".join(f"`{a}`" for a in purpose["aggregations"])
        )
    if purpose["output_cols"]:
        purpose_lines.append(
            "**Output columns:** " + ", ".join(f"`{c}`" for c in purpose["output_cols"])
        )
    if purpose_lines:
        lines.extend(purpose_lines)
        lines.append("")

    if len(kql) > OVERSIZE_KQL_THRESHOLD:
        side_name = f"{file_slug}--{slugify(name)}.kql"
        side_path = out_dir / side_name
        side_path.write_bytes((kql + "\n").encode("utf-8"))
        lines.append(
            f"> ⚠️ Verbose machine-generated KQL ({len(kql)//1024} KB, e.g. "
            f"histogram aggregations expanded across many bins). Full body "
            f"extracted to [`{side_name}`]({side_name}); the opening lines "
            f"are shown below for context. Nothing is truncated — the full "
            f"query is preserved verbatim in the `.kql` file."
        )
        lines.append("")
        preview = "\n".join(kql.splitlines()[:60])
        lines.append("```kusto")
        lines.append(preview)
        lines.append(f"// ... [truncated — see {side_name} for full body]")
        lines.append("```")
    else:
        lines.append("```kusto")
        lines.append(kql)
        lines.append("```")
    lines.append("")

    if params:
        param_names = [p.get("name") for p in params if p.get("name")]
        if param_names:
            lines.append("**Params:** " + ", ".join(f"`{{{p}}}`" for p in param_names))
            lines.append("")

    tips = extract_filter_tips(kql)
    if tips:
        lines.append("**Signal filters seen in KQL:** " + " · ".join(tips))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Chapter assembly
# ---------------------------------------------------------------------------

def collect_chapters(panels: dict) -> "list[tuple[str, list[dict]]]":
    """Group query records by top-level chapter (panelPath[0]).

    Returns ordered list of (chapter_name, [queries...]) in the order chapters
    first appear in `panels`.
    """
    chapters: "dict[str, list[dict]]" = {}
    chapter_order: list[str] = []
    for panel_name, panel in panels.items():
        path = panel.get("panelPath") or []
        if not path:
            chapter = "(top-level)"
        else:
            chapter = path[0]
        if chapter not in chapters:
            chapters[chapter] = []
            chapter_order.append(chapter)
        for q in panel.get("queries", []):
            qcopy = dict(q)
            qcopy["_panel"] = panel_name
            chapters[chapter].append(qcopy)
    return [(c, chapters[c]) for c in chapter_order]


def subgroup_key(q: dict) -> str:
    """2nd-level path segment, used for sub-grouping inside a chapter."""
    path = q.get("panelPath") or []
    if len(path) >= 2:
        return path[1]
    return "(no subgroup)"


def render_chapter_body(
    chapter_name: str,
    queries: "list[dict]",
    out_dir: Path,
    file_slug: str,
    page_title: str,
) -> str:
    """Render the body for one chapter file.

    Queries are grouped under H2 by their 2nd-level path segment. Within each
    group queries are rendered with `render_query`.
    """
    # Preserve original order; bucket by sub-group
    groups: "dict[str, list[dict]]" = {}
    group_order: list[str] = []
    for q in queries:
        sg = subgroup_key(q)
        if sg not in groups:
            groups[sg] = []
            group_order.append(sg)
        groups[sg].append(q)

    body: list[str] = []
    body.append(f"# {chapter_name}")
    body.append("")
    body.append(
        f"> Source: **{page_title}** dashboard, chapter **{chapter_name}** "
        f"({len(queries)} queries across {len(groups)} sub-groups)."
    )
    body.append("")
    body.append(
        "Each KQL block is preserved verbatim from the dashboard. Substitute "
        "params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute "
        "via vm-kusto-query / kusto_runner.py / replay.py."
    )
    body.append("")
    body.append("---")
    body.append("")

    for sg in group_order:
        qs = groups[sg]
        body.append(f"## {sg}")
        body.append("")
        for q in qs:
            body.append(render_query(q, out_dir, file_slug))
            body.append("---")
            body.append("")
    return "\n".join(body)


def split_chapter_by_subgroup(
    chapter_name: str,
    queries: "list[dict]",
    chapter_slug: str,
    out_dir: Path,
    page_title: str,
    max_md_size: int,
) -> "list[tuple[str, str, int]]":
    """Split a chapter into sub-files by 2nd-level segment.

    Returns list of (file_slug, file_title, query_count) tuples.
    """
    # Group by sub
    groups: "dict[str, list[dict]]" = {}
    group_order: list[str] = []
    for q in queries:
        sg = subgroup_key(q)
        if sg not in groups:
            groups[sg] = []
            group_order.append(sg)
        groups[sg].append(q)

    # Pack sub-groups into bins; each bin becomes one file
    bins: "list[list[tuple[str, list[dict]]]]" = []
    current: "list[tuple[str, list[dict]]]" = []
    current_size = 0
    HEADER_OVERHEAD = 600  # rough overhead per file

    for sg in group_order:
        qs = groups[sg]
        # Rough size estimate: sum of all kustoQuery lengths in group + 500 per query
        approx = sum(len(q.get("kustoQuery") or "") + 500 for q in qs) + 200
        if current and current_size + approx > max_md_size:
            bins.append(current)
            current = []
            current_size = 0
        current.append((sg, qs))
        current_size += approx
    if current:
        bins.append(current)

    # Render each bin
    out_meta: "list[tuple[str, str, int]]" = []
    letters = "abcdefghijklmnopqrstuvwxyz"
    for i, bin_items in enumerate(bins):
        sub_letter = letters[i] if i < len(letters) else f"z{i}"
        if len(bins) == 1:
            file_slug = chapter_slug
        else:
            # Use first sub-group's name as hint
            first_sg = bin_items[0][0]
            file_slug = f"{chapter_slug.rstrip('0123456789-')}{sub_letter}-{slugify(first_sg)}"
            # Preserve the leading number from chapter_slug
            num_match = re.match(r"(\d+)", chapter_slug)
            if num_match:
                num = num_match.group(1)
                file_slug = f"{num}{sub_letter}-{slugify(chapter_name)}--{slugify(first_sg)}"

        all_queries_in_bin: list[dict] = []
        for _sg, qs in bin_items:
            all_queries_in_bin.extend(qs)

        body: list[str] = []
        title = f"{chapter_name} — {bin_items[0][0]}" if len(bins) > 1 else chapter_name
        if len(bins) > 1 and len(bin_items) > 1:
            title = f"{chapter_name} (part {i+1}/{len(bins)})"

        body.append(f"# {title}")
        body.append("")
        body.append(
            f"> Source: **{page_title}** dashboard, chapter **{chapter_name}** "
            f"({len(all_queries_in_bin)} queries"
            + (f", part {i+1} of {len(bins)}" if len(bins) > 1 else "")
            + ")."
        )
        body.append("")
        body.append(
            "Each KQL block is preserved verbatim from the dashboard. Substitute "
            "params (`{globalFrom}`, `{nodeId}`, etc.) with case values."
        )
        body.append("")
        body.append("---")
        body.append("")

        for sg, qs in bin_items:
            body.append(f"## {sg}")
            body.append("")
            for q in qs:
                body.append(render_query(q, out_dir, file_slug))
                body.append("---")
                body.append("")

        path = out_dir / f"{file_slug}.md"
        write_text_binary(path, "\n".join(body))
        out_meta.append((file_slug, title, len(all_queries_in_bin)))
        print(f"  wrote {path.name:60s} ({len(all_queries_in_bin):3d} queries, {path.stat().st_size//1024} KB)")

    return out_meta


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build chapter-keyed investigation guide from library.json")
    parser.add_argument("--library", required=True, help="Path to library.json")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--title", default="", help="Page title to show in headers (default: read from library.meta)")
    parser.add_argument("--max-md-size", type=int, default=DEFAULT_MAX_MD_SIZE,
                        help=f"Max bytes per .md before auto-split (default {DEFAULT_MAX_MD_SIZE})")
    args = parser.parse_args()

    library_path = Path(args.library).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    library = json.loads(library_path.read_text(encoding="utf-8"))
    panels = library.get("panels", {})
    service = library.get("service", "")
    page = library.get("page", "")
    page_title = args.title or f"{service} — {page}" if (service or page) else "Dashboard"

    chapters = collect_chapters(panels)
    print(f"Found {len(chapters)} chapters across {sum(len(qs) for _, qs in chapters)} query refs")

    # Order chapters numerically; emerging-issues style chapters often appear
    # later — keep original order from source
    file_index: list[tuple[str, str, int, str]] = []  # (file_slug, title, count, chapter_name)

    for i, (chapter_name, queries) in enumerate(chapters, start=1):
        if not queries:
            continue
        chapter_slug = f"{i:02d}-{slugify(chapter_name)}"

        # Render single-file first; check size
        single_body = render_chapter_body(chapter_name, queries, out_dir, chapter_slug, page_title)
        single_size = len(single_body.encode("utf-8"))

        if single_size <= args.max_md_size:
            path = out_dir / f"{chapter_slug}.md"
            write_text_binary(path, single_body)
            print(f"  wrote {path.name:60s} ({len(queries):3d} queries, {single_size//1024} KB)")
            file_index.append((chapter_slug, chapter_name, len(queries), chapter_name))
        else:
            print(f"  chapter '{chapter_name}' is {single_size//1024} KB > {args.max_md_size//1024} KB — splitting")
            split_meta = split_chapter_by_subgroup(
                chapter_name, queries, chapter_slug, out_dir, page_title, args.max_md_size
            )
            for file_slug, file_title, count in split_meta:
                file_index.append((file_slug, file_title, count, chapter_name))

    # Build README
    readme: list[str] = []
    readme.append(f"# {page_title} — Investigation Guide")
    readme.append("")
    readme.append(
        f"Chapter-keyed reference derived from the **{page_title}** dashboard. "
        f"Every KQL query backing the dashboard is included here, organized by "
        f"the dashboard's own chapter hierarchy (no curation, no symptom-based "
        f"re-categorization). An AI agent or human investigator can route from "
        f"the chapter title (e.g. *\"Hardware Investigation\"*, *\"Service Healing\"*) "
        f"directly to the queries that answer it."
    )
    readme.append("")
    readme.append("**How to use:**")
    readme.append("")
    readme.append("1. Identify which dashboard chapter matches what you're investigating.")
    readme.append("2. Open the matching section file from the list below.")
    readme.append("3. Pick the query whose name / source panel / filter tips match your symptom.")
    readme.append("4. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.")
    readme.append("5. Execute via the **vm-kusto-query** skill (`kusto_runner.py`) "
                  "or via the `replay.py` next to this folder (handles param aliases).")
    readme.append("")
    readme.append("**Companion files (in parent folder):**")
    readme.append("")
    readme.append("- `library.json` — canonical machine-readable source of all queries (panel-organized).")
    readme.append("- `library.md`   — same content as flat human-readable index.")
    readme.append("- `meta.json`    — pageId, totals, ASI URL.")
    readme.append("")
    readme.append("## Files")
    readme.append("")
    total = 0
    # Group by chapter for nicer index
    seen_chapters: set = set()
    for file_slug, file_title, count, chapter_name in file_index:
        if chapter_name not in seen_chapters:
            seen_chapters.add(chapter_name)
        readme.append(f"- [{file_title}]({file_slug}.md) — {count} queries")
        total += count
    readme.append("")
    readme.append(f"**Total queries: {total}**")
    readme.append("")

    # Query index by file
    readme.append("## Query index (by file)")
    readme.append("")

    # Re-walk panels to associate query name → file slug
    file_for_chapter: "dict[str, list[str]]" = {}
    for file_slug, file_title, count, chapter_name in file_index:
        file_for_chapter.setdefault(chapter_name, []).append(file_slug)

    for file_slug, file_title, count, chapter_name in file_index:
        readme.append(f"### {file_title}")
        readme.append("")
        # Pull query names from the rendered file
        md_text = (out_dir / f"{file_slug}.md").read_text(encoding="utf-8")
        for m in re.finditer(r"^### (.+?)$", md_text, re.MULTILINE):
            readme.append(f"- {m.group(1)} — see [{file_slug}.md]({file_slug}.md)")
        readme.append("")

    write_text_binary(out_dir / "README.md", "\n".join(readme))
    print(f"  wrote README.md (index of {total} queries across {len(file_index)} files)")
    print()
    print(f"Done. {total} queries → {len(file_index)} files in {out_dir}")


if __name__ == "__main__":
    main()
