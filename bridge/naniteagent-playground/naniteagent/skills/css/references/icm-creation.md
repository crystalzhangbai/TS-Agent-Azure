# Create ICM Incident (Browser Automation)

**Primary Use**: Automate ICM Incident creation via `playwright-cli` skill (fall back to MCP Playwright `playwright-browser_*` tools if `playwright-cli` is unavailable)  
**URL**: `https://portal.microsofticm.com/imp/v3/incidents/create`  
**Tool**: Use `playwright-cli` skill (fallback: `playwright-browser_*` — navigate, click, type, snapshot, evaluate, wait_for, press_key)  
**Trigger Words**: `create icm`, `new incident`, `创建icm`, `创建事件`, `file icm`

#### Tool Mapping Reference

| Action | Playwright Tool | Notes |
|--------|----------------|-------|
| Open page | `playwright-browser_navigate` url=... | |
| Get page state | `playwright-browser_snapshot` | Returns `ref=eXX` identifiers for elements |
| Click element | `playwright-browser_click` ref=eXX | Use `ref` from latest snapshot |
| Type text | `playwright-browser_type` ref=eXX text=... | Fills input/textbox |
| Select dropdown | `playwright-browser_select_option` ref=eXX values=[...] | For native `<select>` |
| Run JS | `playwright-browser_evaluate` function=... | For complex DOM manipulation |
| Wait | `playwright-browser_wait_for` time=N / text=... | Wait seconds or for text |
| Press key | `playwright-browser_press_key` key=... | e.g. `ArrowDown`, `Enter` |

#### Workflow Steps

> **PERFORMANCE PRINCIPLE**: Minimize snapshot count. Use a single `evaluate` call to batch-set all JS-operable fields. Only use snapshot+click for fields that require DOM interaction (Owning Team search, Impacted Regions select2).

```
Step 1: Navigate → https://portal.microsofticm.com/imp/v3/incidents/create
        ⚠️ SSO Identity Provider Selection page may appear first:
          - If page title = "Identity Provider Selection - IcM":
            click the "Sign in" link ref (Entra ID is pre-selected)
          - Then wait_for text="Create Incident" (15s timeout for SSO redirect)
        If already authenticated, wait_for text="Create Incident" directly.

Step 2: snapshot → Select Owning Team
        - find combobox "Owning Team" ref
        - type team name with slowly=true (triggers search as you type)
        - snapshot → find treeitem matching team name → click ref
        - click "Next" button ref via evaluate: document.querySelector('[data-test-id="next-button"]').click()

Step 3: Select Incident Type → default LSI/CRI is fine
        - click "Next" via evaluate: document.querySelector('[data-test-id="next-button"]').click()
        - wait_for time=3

Step 4: ONE snapshot → then batch-fill ALL fields (see Batch Fill below)

Step 5: Impacted Regions (requires snapshot+click interaction, cannot be batched)
        - snapshot → type region name slowly → snapshot → click option ref

Step 6: TA Approver (appears after TA Vertical is set in batch)
        - snapshot → find TA Approver select ref → select_option

Step 7: Pre-submit validation via evaluate → click "Submit"

Step 8: Verify → page redirects to incident detail page with new Incident ID
```

#### Batch Fill via Single evaluate (Step 4)

> **This is the key optimization.** Instead of filling fields one-by-one with snapshot→type→snapshot cycles, use ONE `evaluate` call to set Title, Description, Environment, Severity, Customer/SLA Impact, Cloud Instance, Subscription Id, TA Vertical, Support Product, Resource URI, and Impact Timestamp all at once.

```js
// Single evaluate call — replaces ~15 individual snapshot+type/click operations
(title, descriptionHtml, severity, customerImpact, cloudInstance, subscriptionId, taVertical, supportProduct, resourceUri, impactTimestamp) => {
  const results = [];

  // 1. Title
  const titleInput = document.querySelector('input[aria-label="Title"]');
  if (titleInput) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    nativeInputValueSetter.call(titleInput, title);
    titleInput.dispatchEvent(new Event('input', { bubbles: true }));
    titleInput.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('title: ok');
  }

  // 2. Description (contentEditable div)
  const editables = document.querySelectorAll('[contenteditable="true"]');
  if (editables[0]) {
    editables[0].innerHTML = descriptionHtml;
    editables[0].dispatchEvent(new Event('input', { bubbles: true }));
    results.push('description: ok');
  }

  // 3. Environment → PROD
  const envSelect = document.querySelector('select[aria-label="Environment"]');
  if (envSelect) {
    envSelect.value = 'PROD';
    envSelect.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('environment: ok');
  }

  // 4. Severity (radio — direct click, no pointer interception in evaluate)
  const sevRadio = document.querySelector(`input[name="customizedForm-Severity"][value="${severity}"]`);
  if (sevRadio) { sevRadio.click(); results.push('severity: ok'); }

  // 5. Customer/SLA Impact (radio)
  const impactRadio = document.querySelector(`input[name="customizedForm-IsCustomerSlaImpacting"][value="${customerImpact}"]`);
  if (impactRadio) { impactRadio.click(); results.push('customerImpact: ok'); }

  // 6. Cloud Instance (select2 — trigger programmatically)
  const cloudLink = document.querySelector('a[aria-label*="Cloud Instance"]');
  if (cloudLink) {
    // Open select2 dropdown
    cloudLink.click();
    // Find and click the option after a microtask
    setTimeout(() => {
      const options = document.querySelectorAll('.select2-results .select2-result-label');
      for (const opt of options) {
        if (opt.textContent.trim() === cloudInstance) { opt.click(); break; }
      }
    }, 300);
    results.push('cloudInstance: triggered');
  }

  // 7. Subscription Id
  const subInput = document.querySelector('input[aria-label="Subscription Id"]');
  if (subInput) {
    nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    nativeInputValueSetter.call(subInput, subscriptionId);
    subInput.dispatchEvent(new Event('input', { bubbles: true }));
    subInput.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('subscriptionId: ok');
  }

  // 8. TA Vertical (native select)
  const taSelect = document.querySelector('select[aria-label="TA Vertical"]');
  if (taSelect) {
    taSelect.value = taVertical;
    taSelect.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('taVertical: ok');
  }

  // 9. Support Product (native select)
  const spSelect = document.querySelector('select[aria-label="Support Product"]');
  if (spSelect) {
    // Find option by text content match
    for (const opt of spSelect.options) {
      if (opt.text === supportProduct) { spSelect.value = opt.value; break; }
    }
    spSelect.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('supportProduct: ok');
  }

  // 10. Resource URI
  const uriInput = document.querySelector('input[aria-label*="Resouce URI"], input[aria-label*="Resource URI"]');
  if (uriInput) {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(uriInput, resourceUri);
    uriInput.dispatchEvent(new Event('input', { bubbles: true }));
    uriInput.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('resourceUri: ok');
  }

  // 11. Impact Timestamp
  const tsInput = document.querySelector('input[aria-label="Impact Timestamp"]');
  if (tsInput) {
    const setter2 = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter2.call(tsInput, impactTimestamp);
    tsInput.dispatchEvent(new Event('input', { bubbles: true }));
    tsInput.dispatchEvent(new Event('change', { bubbles: true }));
    results.push('impactTimestamp: ok');
  }

  return results.join(', ');
}
```

**After batch fill, only 3 more interactions needed:**
1. **wait_for time=1** — let Cloud Instance select2 close
2. **Impacted Regions** — snapshot → type slowly → snapshot → click option (select2, cannot batch)
3. **TA Approver** — snapshot → select_option ref (appears after TA Vertical is set)
4. **Impact Timestamp confirmation** — press_key ArrowDown → press_key Enter

#### Field Reference (for fallback individual filling)

| # | Field | Type | How to Fill (Playwright) |
|---|-------|------|------------------------|
| 1 | **Title** * | `textbox "Title"` | `type` ref=... text="..." |
| 2 | **Description** * | `contentEditable` div (NOT iframe) | `evaluate` — set innerHTML + dispatch input event |
| 3 | **Environment** * | `combobox "Environment"` | `select_option` ref=... values=["PROD"] — Options: `DOGFOOD` \| `INT` \| `PPE` \| **`PROD`** \| `STAGING` \| `TEST` |
| 4 | **Severity** * | radio (by name `customizedForm-Severity`) | ⚠️ Must use `evaluate` (pointer interception) — values: `1` \| `2` \| `25` \| **`3`** \| `4` |
| 5 | **Cloud Instance** * | select2 dropdown via link | `click` link ref → snapshot → `click` option ref. Options: `BlackForest` \| `Bleu` \| `China/Gallatin` \| `Delos` \| `EUDB` \| `Fairfax/ITAR` \| `GovSG` \| **`Public`** \| `Schnitzel` \| `USNat` \| `USSec` |
| 6 | **Impacted Services** * | `combobox "Impacted Services"` | Auto-filled from Owning Team's Service |
| 7 | **Customer/SLA Impact** * | radio (Yes/No) | Must use `evaluate` (pointer interception) |
| 8 | **Impacted Regions** * | `combobox "Impacted Regions"` (multi-select) | `type` slowly → snapshot → `click` option ref |

#### Team-Specific Required Fields (Cloudnet EEE example)

| # | Field | Type | How to Fill (Playwright) |
|---|-------|------|------------------------|
| 9 | **Subscription Id** * | `textbox "Subscription Id"` | `type` ref=... text="GUID" |
| 10 | **TA Vertical** * | `combobox "TA Vertical"` | `select_option` ref=... values=["Other"] — Options: `Hybrid` \| `Layer7` \| `MonCon` \| `Other` \| `VirtualNetwork` |
| 11 | **Support Product** * | `combobox "Support Product"` | `select_option` ref=... values=["product name"] (see full list below) |
| 12 | **Resource URI** * | `textbox "Resouce URI"` | `type` ref=... text="/subscriptions/.../providers/..." |
| 13 | **Impact Timestamp** * | `combobox "Impact Timestamp"` | `evaluate` to set value → `press_key` ArrowDown → Enter |

**Support Product options**: Application Gateway, Application Gateway for Containers, Azure CDN, Azure DNS, Azure Firewall, Azure Front Door, Azure Private Link / Azure Private Endpoint, Azure Route Server, Azure Traffic Manager, Azure Virtual Network Manager, Bastion, DDOS Protection, ExpressRoute / ExpressRoute Direct, IP Services, Load Balancer, NAT Gateway, Network Security Perimeter, Network Virtual Applicatiance (NVA), Network Watcher, Peering Service, VPN Gateway, Virtual Network, Virtual WAN, Web Application Firewall (WAF) - AFD, Web Application Firewall (WAF) - App Gateway

#### Conditional Required: TA Approver

When a TA Vertical is selected, a corresponding **TA Approver** `<select>` dropdown becomes required:

| TA Vertical | Approver Field Selector |
|-------------|------------------------|
| VirtualNetwork | `select[aria-label="TA Approver Virtual Network"]` |
| Layer7 | `select[aria-label="TA Approver L7"]` |
| MonCon | `select[aria-label="TA Approver MonCon"]` |
| Hybrid | `select[aria-label="TA Approver Hybrid"]` |
| Other | `select[aria-label="TA Approver Other"]` |

**How to set**: `select_option` ref=... values=["Approver Name"] — native `<select>` element, works directly with `select_option`.

#### Implementation Notes (Gotchas)

1. **SSO Login**: First navigation redirects to Identity Provider Selection page (title: "Identity Provider Selection - IcM"). Entra ID radio is pre-selected. Click the "Sign in" link ref, then `wait_for` text="Create Incident" with generous timeout (15s). SSO auto-completes with cached credentials.
2. **Minimize snapshots**: Only take snapshots when you MUST interact with DOM refs (Owning Team search, Impacted Regions, TA Approver, Submit button). For all other fields, use the batch `evaluate` call.
3. **Cloud Instance in batch evaluate**: The select2 dropdown is opened and option clicked via `setTimeout(300ms)` in the same evaluate. If it fails, fallback: `click` link ref → snapshot → `click` option ref.
4. **Customer/SLA Impact**: Direct `click` on snapshot ref ALWAYS fails (pointer interception); handled in batch evaluate via `document.querySelector(...).click()`.
5. **Severity**: Direct `click` on snapshot ref ALWAYS fails (pointer interception by tooltip span); handled in batch evaluate.
6. **Impacted Regions**: Uses select2 multi-select — CANNOT be batched. Must: `type` with `slowly=true` into the combobox ref → snapshot → `click` matching option ref.
7. **Description**: Uses `contentEditable` `<div>` elements (NOT iframe). Set via batch evaluate: `editables[0].innerHTML = html` + dispatch input event.
8. **Next button (Steps 2→3)**: Direct `click` on snapshot ref may fail ("element is not visible"). Use `evaluate`: `document.querySelector('[data-test-id="next-button"]').click()`
9. **Owning Team search**: Use `type` with `slowly=true` — this triggers the search as characters are typed. The team combobox transitions to a `treeitem` list. Take a snapshot after typing to find the correct treeitem ref to click. Recently selected teams appear first under "S Recently selected" group.
10. **Pre-submit validation**: Use `evaluate` to check for any remaining red "Please select/enter" error messages before clicking Submit.
11. **TA Approver**: Automatically appears after selecting TA Vertical. It's a native `<select>` — use `select_option` with the approver's display name (e.g., `values=["Frank Shi"]`).

#### Description Content Template

   **Default template** (always use this structured EEE ICM format):

   > **CRITICAL**: The Description must contain **concrete investigation findings** from KQL queries, NOT generic placeholders.
   > Before filling the Description, complete the investigation (B01 queries, NRP/GWM log analysis) to gather:
   > - Exact error codes, timestamps, operation IDs
   > - CRUD flow timeline with results
   > - Root cause chain from logs
   > - Platform-wide impact data (if applicable)
   > - Specific ASK questions to EEE/PG

   ```html
   <p><b>TA Approver:</b> [TA approver alias]</p>
   <br/>

   <h3>General Details</h3>
   <table cellpadding="4">
   <tr><td><b>Resource ID:</b></td><td><code>[full ARM resource ID]</code></td></tr>
   <tr><td><b>ASC Case Link:</b></td><td><a href="https://azuresupportcenter.msftcloudes.com/caseoverview?srId=[case_number]">ASC [case_number]</a></td></tr>
   <tr><td><b>Region:</b></td><td>[region]</td></tr>
   <tr><td><b>SKU:</b></td><td>[Standard_v2 / WAF_v2 / etc.]</td></tr>
   <tr><td><b>VNet / Subnet:</b></td><td>[vnet-name] / [subnet-name]</td></tr>
   <tr><td><b>Problem Type:</b></td><td>[Resource create/update/delete/connectivity]</td></tr>
   </table>

   <h3>Problem Description</h3>
   <p>[Concrete description of what happened, including SDK/tool used, exact error returned, how many attempts failed, etc.]</p>

   <h3>Required Information</h3>
   <table cellpadding="4">
   <tr><td><b>Reproducible on demand?</b></td><td>[Yes/No]</td></tr>
   <tr><td><b>Last failure timestamp (UTC):</b></td><td>[exact UTC timestamp from KQL]</td></tr>
   <tr><td><b>Attempted via CLI/REST/SDK?</b></td><td>[Yes - specify tool/SDK version]</td></tr>
   </table>

   <h3>TA/SME Analysis</h3>
   <p><b>CRUD Flow Timeline:</b></p>
   <table cellpadding="6" style="border:1px solid #ddd;">
   <tr style="background:#0078d4;color:white;"><th>Time (UTC)</th><th>Stage</th><th>Event</th><th>Result</th></tr>
   [Insert rows from actual KQL results — each row = one step in the operation lifecycle]
   </table>

   <p><b>Root Cause Analysis:</b></p>
   <ol>
   [Numbered list of failure chain from logs — each step with specific error codes/messages]
   </ol>

   <p><b>Key Identifiers:</b></p>
   <table cellpadding="4" style="border:1px solid #ddd;">
   [GatewayId, OperationId, ActivityId, CorrelationRequestId, etc. from KQL results]
   </table>

   <p><b>Platform-Wide Impact (if applicable):</b></p>
   <table cellpadding="4" style="border:1px solid #ddd;">
   [Aggregated failure trend data from KQL — failure count, distinct subscriptions, distinct resources by time window]
   </table>

   <h3>ASK to EEE/PG</h3>
   <ol>
   <li>[Specific question 1 — what needs PG investigation, with exact error/component]</li>
   <li>[Specific question 2 — is this a known issue, provide ETA]</li>
   <li>[Specific question 3 — what remediation for the customer's resource]</li>
   </ol>

   <br/>
   <hr/>
   <p><b>ADDITIONAL INFORMATION FROM AZURE SUPPORT CENTER</b></p>
   <p>Support Request Number: <b>[case number]</b></p>
   <p>Subscription Id: <code>[subscription id]</code></p>
   <p>Resource Group: [resource group]</p>
   <p>Resource Uri: <code>[full ARM resource URI]</code></p>
   <p>Tenant Id: <code>[tenant id]</code></p>
   <p>Problem start time: [UTC timestamp from case]</p>
   ```

   **Template usage rules:**
   - **DO NOT** use generic placeholders like "Please investigate" — every section must contain data from actual KQL queries
   - The CRUD Flow table should have real timestamps and operation results from `FrontendOperationEtwEvent`
   - Root Cause should trace the exact failure chain (e.g., StorageResourceNotFoundException → KV cert 404 → ARM ResourceNotFound)
   - ASK questions must be specific enough for PG to act without re-investigating
   - If platform-wide impact exists, include the aggregated trend table — this helps PG prioritize
7. **Impact Timestamp**: Set input value via `evaluate`, then `press_key` `ArrowDown` + `Enter` to confirm selection.
8. **Select/Combobox fields**: For native `<select>` elements (Environment, TA Vertical, TA Approver, Support Product), `select_option` works directly. For select2/Angular custom comboboxes (Cloud Instance, Impacted Regions), use `type` with `slowly=true` or `click` link to open, then `click` option ref.
9. **Owning Team search**: Use `type` with `slowly=true` — this triggers the search as characters are typed. The team combobox transitions to a `treeitem` list. Take a snapshot after typing to find the correct treeitem ref to click. Recently selected teams appear first under "S Recently selected" group.
10. **Pre-submit validation**: Use `evaluate` to check for any remaining red "Please select/enter" error messages before clicking Submit.
11. **TA Approver**: Automatically appears after selecting TA Vertical. It's a native `<select>` — use `select_option` with the approver's display name (e.g., `values=["Frank Shi"]`).

#### User Information Collection Template

When user requests ICM creation, use `ask_user` to collect:

```
Please provide the following information to create an ICM:

**Basic fields:**
1. Title - Incident title
2. Description - Incident description (HTML/Markdown supported)
3. Owning Team - Target team (e.g., Cloudnet\EEE Cloudnet)
4. Environment - DOGFOOD/INT/PPE/PROD/STAGING/TEST
5. Severity - 1/2/25/3/4
6. Cloud Instance - Public/Fairfax/China etc.
7. Customer/SLA Impact - Yes/No
8. Impacted Regions - Azure region (e.g., East US)

**Team custom fields (Cloudnet EEE example):**
9. Subscription Id - Azure subscription GUID
10. TA Vertical - Hybrid/Layer7/MonCon/Other/VirtualNetwork
11. Support Product - Network product name
12. Resource URI - ARM resource URI
13. Impact Timestamp - UTC timestamp
```
