# Chat Log Export Skill

### Trigger
`save chatlog`, `export chatlog`, `save log`, `保存聊天记录`

### Description
Exports the current conversation (chat log) as **both a styled HTML file and a Markdown file** to a user-specified local folder. Always outputs dual files (`.html` + `.md`). Includes `/session` info (session ID, workspace summary) and `/usage` metrics (token usage, model, premium requests) as a session metadata block at the top of both files. Useful for archiving troubleshooting sessions, preserving case research, or sharing conversation history with teammates.

### /session and /usage Commands

These are built-in Copilot CLI slash commands that provide session context:

| Command | Description | Output |
|---------|-------------|--------|
| `/session` | Show session info and workspace summary | Session ID, cwd, repository, branch, summary of work done |
| `/usage` | Display session usage metrics and statistics | Token counts, model used, premium request count, context window usage |

**How to capture their output for the chat log:**
- Run `/session` in the current conversation and capture the response text
- Run `/usage` in the current conversation and capture the response text
- Include both as a **Session Metadata** block at the top of the exported HTML and MD files

### Workflow

```
1. User triggers with "save chatlog" / "save log" (or "export chatlog")
2. Capture session metadata:
   a. Run /session  → capture: session ID, cwd, repository, branch, session summary
   b. Run /usage    → capture: model name, token usage, premium requests used
3. Prompt user for:
   a. Target folder path  (e.g., C:\temp or D:\case\areschen)
   b. Filename            (e.g., 2026-03-11_1037_coreidentity-membership-request.html)
      → Default format: yyyy-mm-dd_HHmm_<session-topic-summary>.html
      → Suggest a name based on current local time + session context summary
4. Collect all conversation turns from the current session
5. Generate BOTH output files:
   - <name>.html  — styled HTML (Azure-themed CSS, turn cards, code blocks)
   - <name>.md    — raw markdown (portability, editing, version control)
   Both files include:
     [Section 1] Session Metadata block (/session + /usage output)
     [Section 2] Conversation turns (User/Assistant cards)
6. Create target folder if it does not exist
7. Save both files: Set-Content -Path ... -Encoding UTF8
8. Confirm to user with full file paths for both files
```

### Prompt Sequence

#### Step 1 — Capture /session and /usage
```
Run /session → extract: Session ID, cwd, repository, branch, session summary
Run /usage   → extract: model name, token usage breakdown, premium request count
Store both for inclusion in the metadata block.
```

#### Step 2 — Ask for target folder
```
ask_user:
  question: "Where should I save the chat log? Provide a folder path."
  allow_freeform: true
```

#### Step 3 — Ask for filename
```
ask_user:
  question: "What filename should I use?"
  choices:
    - "yyyy-mm-dd_HHmm_<suggested-topic>.html (Recommended)"
    - "Let me type a custom name"
  # Generate the suggested name from current local time + session context summary
  # Example: 2026-03-11_1037_coreidentity-membership-request.html
  allow_freeform: true
```

#### Step 4 — Generate HTML
Build an HTML document using this template structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Chat Log — [Session Topic]</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; background: #f5f5f5; }
    .turn { background: #fff; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 1px 3px rgba(0,0,0,.12); }
    .turn-user { border-left: 4px solid #0078d4; }
    .turn-assistant { border-left: 4px solid #107c10; }
    .role { font-weight: 600; margin-bottom: .5rem; }
    .role-user { color: #0078d4; }
    .role-assistant { color: #107c10; }
    .action-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: .85rem; margin: 2px; }
    .tag-created { background: #dff6dd; color: #107c10; }
    .tag-updated { background: #fff4ce; color: #6b5900; }
    .tag-researched { background: #d0e8ff; color: #004578; }
    pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 6px; overflow-x: auto; }
    code { font-family: 'Cascadia Code', Consolas, monospace; }
    h1 { color: #0078d4; border-bottom: 2px solid #0078d4; padding-bottom: .5rem; }
    h2 { color: #0078d4; font-size: 1.1rem; margin-top: 1.5rem; }
    .meta { color: #666; font-size: .9rem; margin-bottom: 1.5rem; }
    .session-block { background: #f0f7ff; border: 1px solid #b3d4f5; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; }
    .session-block h2 { color: #004578; margin-top: 0; }
    .session-block table { border-collapse: collapse; width: 100%; }
    .session-block td { padding: 4px 10px; border-bottom: 1px solid #d0e5f7; font-size: .92rem; }
    .session-block td:first-child { font-weight: 600; color: #004578; width: 180px; }
  </style>
</head>
<body>
  <h1>💬 Chat Log — [Session Topic]</h1>
  <div class="meta">Exported on [date] • [N] turns</div>

  <!-- SESSION METADATA BLOCK -->
  <div class="session-block">
    <h2>📊 Session Info &amp; Usage</h2>
    <table>
      <tr><td>Session ID</td><td>[from /session]</td></tr>
      <tr><td>Working Directory</td><td>[from /session]</td></tr>
      <tr><td>Repository</td><td>[from /session]</td></tr>
      <tr><td>Branch</td><td>[from /session]</td></tr>
      <tr><td>Session Summary</td><td>[from /session]</td></tr>
      <tr><td>Model</td><td>[from /usage]</td></tr>
      <tr><td>Total Tokens Used</td><td>[from /usage — input + output]</td></tr>
      <tr><td>Context Window Usage</td><td>[from /usage — % used]</td></tr>
      <tr><td>Premium Requests Used</td><td>[from /usage]</td></tr>
    </table>
  </div>

  <!-- Repeat per turn -->
  <div class="turn turn-user">
    <div class="role role-user">👤 User — Turn N</div>
    <div class="content">[user message content]</div>
  </div>
  <div class="turn turn-assistant">
    <div class="role role-assistant">🤖 Assistant — Turn N</div>
    <div class="content">[assistant actions & summary]</div>
  </div>
</body>
</html>
```

#### Step 5 — Generate MD
Build a markdown document using this structure:

```markdown
# Chat Log — [Session Topic]

**Exported on:** [date] • [N] turns

---

## 📊 Session Info & Usage

| Field | Value |
|-------|-------|
| Session ID | [from /session] |
| Working Directory | [from /session] |
| Repository | [from /session] |
| Branch | [from /session] |
| Session Summary | [from /session] |
| Model | [from /usage] |
| Total Tokens Used | [from /usage] |
| Context Window Usage | [from /usage] |
| Premium Requests Used | [from /usage] |

---

## 👤 User — Turn 1

[user message]

---

## 🤖 Assistant — Turn 1

[assistant actions & summary]

---
```

#### Step 6 — Save & Confirm
```
1. Create folder if missing:  New-Item -ItemType Directory -Force -Path $folder
2. Write MD file:             Set-Content -Path "$folder\$name.md"   -Value $markdown -Encoding UTF8
3. Write HTML file:           Set-Content -Path "$folder\$name.html" -Value $html     -Encoding UTF8
4. Confirm:                   "✅ Chat log saved:
                                 • $folder\$name.md
                                 • $folder\$name.html"
```

### Output Format
- **Always dual output** — both `.md` and `.html` with the same base filename.
  - `.html`: Styled for browser viewing and sharing. Azure-themed CSS (blue #0078d4 headers, green #107c10 assistant cards), dark code blocks (#1e1e1e). Session metadata in a blue info box at the top.
  - `.md`: Raw markdown for portability, editing, and version control. Session metadata as a table at the top.
- **Session metadata block** (first section in both files) populated from `/session` and `/usage` output:
  - `/session`: Session ID, working directory, repository, branch, session summary
  - `/usage`: Model name, total tokens used (input + output), context window % used, premium requests count
- Each conversation turn rendered as a card (HTML) or headed section (MD) with role label and content.

### Notes
- Summarize assistant turns rather than dumping raw tool calls — focus on actions taken and outcomes.
- Tag key actions with color-coded badges: Created, Updated, Researched, Verified, Archived.
- If the conversation is very long, group related turns into logical sections with headings.
- File is standalone HTML — no external dependencies, can be opened in any browser.
- If `/session` or `/usage` data is unavailable (e.g., first turn), use `N/A` for those fields.
