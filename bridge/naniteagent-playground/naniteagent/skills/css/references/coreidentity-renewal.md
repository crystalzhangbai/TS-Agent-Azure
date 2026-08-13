# CoreIdentity Membership Renewal

**Primary Use**: Automate renewal of expiring entitlements and access permissions

- **URL**: `https://coreidentity.microsoft.com/`
- **Method**: Use `playwright-cli` skill for browser automation (fall back to MCP playwright if `playwright-cli` is unavailable)
- **Contains**: Entitlement management, membership renewals, access requests
- **Trigger Words**: `renew membership`, `renew coreidentity`, `expiring access`, `entitlement renewal`, `coreidentity renewal`

#### Prerequisites
- `playwright-cli` skill available (or Playwright MCP as fallback)
- User authenticated to CoreIdentity portal

#### Workflow Steps

1. **Navigate to Dashboard**
   - Open `https://coreidentity.microsoft.com/`
   - Click "Expiring Memberships (N)" tab

2. **Identify Items to Renew**
   - Skip items with existing "Renewal Request ID"
   - Process only items without a Request ID

3. **Select & Renew (One at a Time)**
   - Click checkbox cell (not the name link), press `Space` to select
   - Click **Renew** button at top of grid

4. **Complete Renewal Form**

   **Simple Form:**
   - Fill Business Justification: `TA in CSS Azure Network support and involve troubleshooting Azure`
   - Click **Submit**

   **Complex Form (with radio buttons/T&C):**
   - Select appropriate radio option (e.g., "Logic Apps CSS" for CSS role)
   - Check "I have read the terms and conditions"
   - Click **Submit**

5. **Verify Submission**
   - Wait for "Submitted" status in dialog
   - Close dialog (Escape or Close button)
   - Confirm "Renewal Request ID" column now shows a number

6. **Repeat** for remaining items without Request IDs

#### Best Practices
- Select "for myself" when prompted
- Prefer "Reader" role when given role choice
- Different entitlements have different forms - adapt accordingly
- Process one item at a time to avoid UI errors
