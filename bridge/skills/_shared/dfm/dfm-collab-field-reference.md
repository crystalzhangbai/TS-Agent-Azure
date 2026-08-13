# DFM Create Collaboration — Form Field Reference

Field-by-field reference for the **Create Collaboration** form in DFM (Dynamics Field Management / One Support). Use it when preparing or validating a Create Collaboration draft before the engineer manually selects the Support Area Path and submits.

---

## Field Map

| # | Field Label | Element Type | Selector Strategy | Max Length | Notes |
|---|---|---|---|---|---|
| 1 | **Title** | `<input type="text">` | `input[aria-label="Title"]` → `input[name="title"]` | ~255 chars | React-controlled — use native setter + synthetic events (see §React setter below) |
| 2 | **Body / Description** | CKEditor 5 (most likely) | `.ck-editor__editable` | Uncapped (HTML) | See §Body Editor below. **Never use innerHTML on CKEditor.** |
| 3 | **Support Area Path** | Multi-level cascading dropdown | N/A — do NOT auto-select | N/A | See §Support Area Path below |
| 4 | **Submit** | `<button type="submit">` | `button[data-test-id="submit-collab"]` → `button[type="submit"]` | N/A | **NEVER auto-click** — see §Submit Safety |

---

## Title Field

- **Max length**: ~255 characters. DFM silently truncates beyond that; no client-side validation shown.
- **Recommended format**: `[<TeamShorthand>] <Issue summary> — <CaseId>`
  - Example: `[XStore_Triage] Disk blackout on prod-web-01 data disk — 2605140030002786`
- **Escaping**: Plain text only. Do not insert HTML tags — the field renders as text.
- **Injection method** (React-controlled input):
  ```js
  const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  nativeSetter.call(el, title);
  el.dispatchEvent(new Event('input',  { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  ```
  A plain `el.value = title` bypasses React's change tracker and the form treats the field as empty.

---

## Body Editor

DFM uses **CKEditor 5** for the Body/Description field as of 2026-Q1. The editor element carries the CSS class `.ck-editor__editable`.

### Why you CANNOT use innerHTML

CKEditor 5 maintains an internal document model separate from the DOM. Writing to `innerHTML` directly:
- Bypasses the model → the editor's internal state stays empty
- `getData()` returns empty string even though the DOM shows text
- The form submits an empty body

### Correct injection (CKEditor 5)

```js
const ckRoot = document.querySelector('.ck-editor__editable');
// CKEditor 5 attaches the editor instance to the DOM element as .ckeditorInstance
const ckInstance = ckRoot.ckeditorInstance ||
  Object.keys(ckRoot).map(k => ckRoot[k]).find(v => v && typeof v.setData === 'function');
ckInstance.setData(bodyHtml);  // bodyHtml may be full HTML string or plain text
```

### Timing

CKEditor initialises asynchronously. If `ckRoot.ckeditorInstance` is null:
- The page has not finished loading the editor.
- Wait 1–2 seconds (playwright-cli `wait_for` or `sleep`) and retry.
- Typical symptom: `.ck-editor__editable` exists in DOM but is still `aria-readonly="true"`.

### Fallback order

| Priority | Condition | Method |
|---|---|---|
| 1 | `.ck-editor__editable` visible + instance accessible | `ckInstance.setData(html)` |
| 2 | `[contenteditable="true"]` visible | `el.innerHTML = html` + dispatch `input` |
| 3 | `textarea[aria-label*="Body"]` visible | React native setter + events |

---

## Support Area Path

The **Support Area Path** is a multi-level cascading dropdown tree (3–5 levels deep). It controls which backend team receives the collaboration request.

### Why auto-selection is forbidden (Decision D7)

1. **Lazy render**: child nodes only appear in the DOM after the parent level is expanded and selected. Selecting level 2 before level 1 renders level 2 fails silently.
2. **Ambiguous names**: the same segment string (e.g., `"Triage"`) appears under multiple parents. Matching by text alone mis-routes.
3. **Schema drift**: Cloudnet modifies the path tree without notice. A hardcoded auto-click path quietly routes to the wrong team.
4. **No rollback**: once submitted, the collaboration is in the SME team's queue. Retracting requires admin intervention.

### Correct behaviour

Print the full path from [`../../vm-case-triage/references/support-area-path-map.md`](../../vm-case-triage/references/support-area-path-map.md) and instruct the user to manually click each cascade level:

```
⚠️ Please manually select Support Area Path in DFM:
   Azure  >  Storage  >  XStore  >  XStore_Triage
   (click each level left-to-right in the dropdown tree)
```

### Selector reference (for read-only detection only)

| Selector | Purpose |
|---|---|
| `[data-test-id="support-area-path"]` | Root container of the cascading picker |
| `[aria-label*="Support Area"]` | Aria-based fallback |
| `.sap-dropdown, .sap-tree-picker` | CSS class fallback |

Detection (read-only) is used only to confirm the picker is visible before printing guidance.

---

## Submit Button

| Attribute | Value |
|---|---|
| Selector (primary) | `button[data-test-id="submit-collab"]` |
| Selector (fallback) | `button[type="submit"]` |
| Aria label | `"Submit"` or `"Create"` |

### Why we NEVER auto-click Submit (Decision D5 / D7)

Submitting the collaboration:
- Immediately notifies the backend SME team queue — cannot be recalled without admin access.
- A submitted collab with wrong case ID, wrong team path, or typos causes confusion and repair overhead.
- The engineer must verify Title, Body, and Support Area Path visually before submitting.

After filling Title + Body, leave the browser on the open form and remind the engineer to verify the content, manually select Support Area Path, and submit.

---

## Pre-Submit Validation

To detect form validation errors (red highlights) before the user manually clicks Submit:

```js
// Check for visible error indicators — call via playwright-cli evaluate
const errors = Array.from(document.querySelectorAll(
  '.field-error, [aria-invalid="true"], .ms-TextField-errorMessage, [data-test-id*="error"]'
)).filter(el => el.offsetParent !== null).map(el => el.textContent.trim());
return JSON.stringify({ hasErrors: errors.length > 0, errors });
```

Run this after filling to catch required-field warnings before handing off to the user.

---

## Known Quirks

| Quirk | Impact | Mitigation |
|---|---|---|
| CKEditor initialises asynchronously | `ckeditorInstance` may be null immediately after page load | Wait for `aria-readonly` attribute to disappear from `.ck-editor__editable`, then fill |
| Support Area Path lazy-renders children | Child levels don't exist in DOM until parent is selected | Manual user selection (D7) |
| React-controlled inputs ignore `el.value =` | Form submits empty field | Always use native property setter + synthetic events |
| DFM session timeout (8h) | `playwright-cli goto` redirects to login page | `Update-PwState corp` to refresh; or reuse an already-open DFM session via `Get-PwAccountForUrl` |
| Title field capped at ~255 chars | Silently truncated | Keep title under 200 chars; summary important info first |
