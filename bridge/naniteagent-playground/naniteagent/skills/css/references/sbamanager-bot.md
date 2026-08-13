---
description: Batch-assign D365 support cases via Teams SBAManager Bot. Generic reference applicable to all product lines.
---
## Case Assignment — SBAManager Bot Interaction

### Overview

When you need to assign one or more D365 support cases to a specific engineer, use the **SBAManager Bot** in Teams for automated assignment. This approach is more reliable than the D365 OData API (API PATCH `ownerid` returns 204 but the assignment does not take effect).

### Trigger Keywords

`assign cases`, `分配 case`, `批量分配`, `assign to me`, `case assignment`

### Prerequisites

1. Browser has Teams open (`https://teams.microsoft.com`)
2. Navigated to the **SBAManager Bot** 1:1 chat
3. Case ID list is known

### Interaction Flow (Single Case)

```
Step 1: Type "please assign {case_id} to me" in the message box → Send
         │
         ▼  (~8-12s)
Step 2: Bot replies "Yawn...Rebooting..."
         │
         ▼
Step 3: Bot displays a Booking Reason card (20 options)
         → Bot prompts "Please click on an option. Alternatively, please type a number from 1-20"
         │
         ▼
Step 4: Type "7" → Send  (selects "Manual Initial Bot Assignment")
         │
         ▼  (~5-8s)
Step 5: Bot replies "Ok Let Me Set Manual Initial Bot Assignment"
         │
         ▼
Step 6: Bot replies "There you go {Name}. I have created a request to book {case_id} for {Name} ({email})."
         │
         ▼
Step 7: SMEIntelligentBot sends confirmation: "{case_id} => {Name} Assignment from Manually Assigned"
```

### Batch Assignment Flow

**Key optimization**: Type the number "7" instead of clicking a button, avoiding the snapshot → find ref → click overhead.

```
for each case_id in case_list:
    1. Locate the message box (textbox "Type a message")
    2. Type "please assign {case_id} to me" → Enter
    3. Wait for Bot reply "Please click on an option" or "type a number from 1-20" (timeout 15s)
    4. Type "7" → Enter  (select Manual Initial Bot Assignment)
    5. Wait for Bot reply "There you go" (timeout 15s)
    6. ⏱️ Wait an additional 10s (prevent DFM backend overload causing assignment failures)
    7. Proceed to the next case
```

> **⚠️ Important**: After each case assignment completes, you **must wait 10 seconds** before sending the next assignment request.
> The backend DFM (Duty/Field Manager) system needs time to process assignments; rapid consecutive requests may cause failures or missed assignments.

**Per-case duration**: ~35s (including 10s gap) vs ~60-90s (manual snapshot approach)

### Browser Automation Reference

#### Chrome DevTools MCP Approach

```
// Step 1: Find message box uid (snapshot → look for textbox "Type a message")
// Step 2: click uid → type_text "please assign {case_id} to me" + submitKey: Enter
// Step 3: wait_for ["Please click on an option", "type a number from 1-20"] timeout: 15000
// Step 4: type_text "7" + submitKey: Enter
// Step 5: wait_for ["There you go"] timeout: 15000
// Step 6: wait_for ["PLACEHOLDER_WAIT_10S"] timeout: 10000  (uses timeout to enforce 10s gap)
```

#### Playwright Approach

```javascript
const msgBox = page.getByRole('textbox', { name: 'Type a message' });

// Send assignment request
await msgBox.fill('please assign {case_id} to me');
await msgBox.press('Enter');

// Wait for Bot to show Booking Reason options
await page.waitForText(['Please click on an option', 'type a number from 1-20'], { timeout: 15000 });

// Enter Booking Reason number
await msgBox.fill('7');
await msgBox.press('Enter');

// Wait for Bot to confirm assignment
await page.waitForText(['There you go'], { timeout: 15000 });

// 10s gap to prevent DFM backend overload
await page.waitForTimeout(10000);
```

### Booking Reason Reference

| # | Reason | Use Case |
|---|--------|----------|
| 1 | Timezone - Business hours support requested | Timezone rotation |
| 2 | Timezone - After hours support requested | After-hours handoff |
| 3 | Out of Office (planned) | OOF takeover |
| 4 | New SE assignment (customer request) | Customer requests new engineer |
| 5 | Manager Request | Manager-directed assignment |
| 6 | Peer swap (agreed) | Agreed peer exchange |
| 7 | Skills-based (SME needed) | SME expertise required |
| **8** | **Manual Initial Bot Assignment** | **⭐ Most common — manual initial assignment** |
| 9 | Escalation re-assignment | Escalation reassignment |
| 10 | Collaboration needed | Collaboration required |

### Important Notes

1. **First interaction**: Bot may first ask "Which Bookable Resources do you want to use?" — click your own name link. Subsequent interactions in the same session skip this step.
2. **OData API unreliable**: `PATCH /api/data/v9.0/incidents({id})` modifying `ownerid@odata.bind` returns HTTP 204 but the assignment **does not take effect** (D365 may require the Assign bound action or workflow mechanism). Use SBAManager Bot instead.
3. **Verify assignment**: After Bot confirmation, verify via OData API `GET /api/data/v9.0/incidents({id})?$select=_ownerid_value` that the owner has changed.
4. **Error handling**: If Bot times out without responding, resend the assignment message (idempotent operation).
5. **Assign to others**: Replace "to me" with "to {alias}" to assign to another engineer (verify Bot support).

---
