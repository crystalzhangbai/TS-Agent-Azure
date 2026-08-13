#!/usr/bin/env python3
"""
Playwright-fallback scraper template.

Copy this to dashboards/<portal>/pages/<page-slug>-playwright/scraper.py and
customize:

  - URL                    the dashboard page to open
  - PROFILE_DIR            persistent browser profile (so auth survives)
  - PANELS                 list of (panel_name, selector_or_ref) to capture
  - capture_panel()        per-panel extraction logic (text / table / chart)

Pre-reqs:
  - playwright-cli on PATH (see .claude/skills/playwright-cli/SKILL.md)
  - At least one prior `playwright-cli open --persistent` to seed the profile

Usage:
  python scraper.py --start 2026-05-07T23:00:00Z --end 2026-05-08T01:00:00Z \
                    --vmid <vmid> --out ./output

Output:
  output/
    snapshot.yaml         full accessibility tree
    screenshot.png        full-page screenshot
    panels/
      <panel-slug>.txt    extracted text per panel
      <panel-slug>.png    optional element screenshot
    summary.json          structured per-panel data
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Configure per-page
# ---------------------------------------------------------------------------
URL_TEMPLATE = "https://example.dashboard/path?vmid={vmid}&from={start}&to={end}"
PROFILE_DIR = ".pw-profile"   # relative to scraper.py
SESSION = "scraper"            # playwright-cli session name

PANELS = [
    # (panel_name, css_selector or ref)
    # Example:
    # ("Container Health", "section[data-panel='container-health']"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def run(cmd, check=True, capture=False):
    print(f"$ {' '.join(cmd)}", file=sys.stderr)
    if capture:
        r = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return r.stdout
    return subprocess.run(cmd, check=check).returncode


def pw(*args, raw=False, capture=False):
    cmd = ["playwright-cli", f"-s={SESSION}"]
    if raw:
        cmd.append("--raw")
    cmd.extend(args)
    return run(cmd, capture=capture)


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def capture_panel(panel_name, selector, out_dir):
    slug = slugify(panel_name)
    txt_path = os.path.join(out_dir, "panels", f"{slug}.txt")
    png_path = os.path.join(out_dir, "panels", f"{slug}.png")
    os.makedirs(os.path.dirname(txt_path), exist_ok=True)

    text = pw("eval", f"el => el.innerText", selector, raw=True, capture=True)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text or "")

    pw("screenshot", selector, f"--filename={png_path}")

    return {"name": panel_name, "selector": selector,
            "text_path": txt_path, "screenshot_path": png_path,
            "text_preview": (text or "")[:500]}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--vmid")
    ap.add_argument("--out", default="./output")
    args = ap.parse_args()

    url = URL_TEMPLATE.format(start=args.start, end=args.end, vmid=args.vmid or "")
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    profile = os.path.abspath(PROFILE_DIR)

    # Open browser with persistent profile (auth re-used)
    pw("open", url, f"--profile={profile}")

    # Save full-page snapshot + screenshot
    pw("snapshot", f"--filename={os.path.join(out, 'snapshot.yaml')}")
    pw("screenshot", f"--filename={os.path.join(out, 'screenshot.png')}")

    # Per-panel extraction
    panel_results = []
    for name, selector in PANELS:
        try:
            panel_results.append(capture_panel(name, selector, out))
        except subprocess.CalledProcessError as e:
            panel_results.append({"name": name, "selector": selector, "error": str(e)})

    summary = {
        "url": url,
        "captured_at": datetime.utcnow().isoformat() + "Z",
        "panels": panel_results,
    }
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    pw("close")
    print(f"\nWrote results to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
