# Playwright Fallback — for dashboards we can't reverse-engineer

When a dashboard's underlying data source can't be cleanly captured (heavy client-side composition, websocket-only streaming, no addressable per-panel API, anti-automation), drive the page through a browser with [`playwright-cli`](../../.claude/skills/playwright-cli/SKILL.md) and capture what you can:

- Full-page screenshot
- Accessibility snapshot (often contains tabular data as plain text)
- Targeted element screenshots / text extraction via `eval`
- DOM-state dumps via `eval`

## When to use this (and when NOT to)

| ✅ Use Playwright when… | ❌ Don't — reverse-engineer the API instead |
|------------------------|------------------------------------------|
| Data composed entirely client-side from cached state | Each panel maps cleanly to one Fetch/XHR call |
| Websocket / SignalR / SSE streaming-only | Calls return JSON or KQL results |
| Heavy CSRF/anti-bot defenses | The portal has a metadata API (like ASI's `/api/services/<svc>/pages/<page>`) |
| One-off urgent case, no time to reverse | You'll re-use this page many times |

## Files

- [`template-scraper.py`](template-scraper.py) — copyable skeleton that opens a page, waits, captures snapshot + screenshot, and dumps panel text. Adapt per-page.

## Workflow

1. Copy `template-scraper.py` to `../pages/<page-slug>-playwright/scraper.py` and customize the URL + extraction logic.
2. Record the **snapshot** (accessibility tree) — often this alone has every visible number/label.
3. Identify the visual elements you actually need (panel titles, chart legends, table cells).
4. Use `playwright-cli eval` snippets to pull innerText / dataset attributes from those elements.
5. If charts are SVG/Canvas with no text, fall back to screenshot + (later) OCR. Avoid OCR if possible — pixel data is fragile.

## Notes

- A persistent profile is essential so you don't re-auth every run: use `playwright-cli open --persistent` or `--profile=...`.
- Save the post-login state via `playwright-cli state-save auth.json` and re-use for headless runs.
- For dashboards that lazy-load panels on scroll, scroll into view before snapshotting.
