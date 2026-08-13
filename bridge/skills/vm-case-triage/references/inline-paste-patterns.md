# Inline-Paste Patterns

When the user pastes a case body, recognize its shape and pull the structured fields. This skill never fetches from DFM — the text always comes from the user, in one of the shapes below (or as a free-form description, which needs no parsing — use it directly).

## Contents

- [The shapes at a glance](#the-shapes-at-a-glance)
- [Pattern 1: DFM Q&A block](#pattern-1-dfm-qa-block)
- [Pattern 2: Free-form description](#pattern-2-free-form-description)
- [Pattern 3: Advisory / Maintenance notification full text](#pattern-3-advisory--maintenance-notification-full-text)
- [Pattern 4: Full DFM dump](#pattern-4-full-dfm-dump)
- [Extraction regexes](#extraction-regexes)

## The shapes at a glance

| You see… | Pattern | What it carries |
|---|---|---|
| `Question:` / `Answer:` pairs | 1 | The customer's answers to the DFM intake questions |
| A paragraph of the customer's own narrative | 2 | Symptom + maybe a Resource ID / timestamp inline |
| An advisory/notification email body, often with a tracking ID | 3 | Upcoming-change details; route to case-type C |
| A big dump including `<Start:Agent_Additional_Properties_Do_Not_Edit>` | 4 | Structured fields — the most reliable source |

If the pasted text is very short or ambiguous, don't stall — give a provisional cockpit and make the missing facts `[blocking]` Scope Questions.

## Pattern 1: DFM Q&A block

The most common shape — DFM's Restricted Information section, copy-pasted.

```
Question: Did you receive a maintenance notification for your resource?
Answer: Yes

Question: What is the tracking ID of the notification that you received?
Answer: 8PJS-_48

Question: Description
Answer: Marketplace Windows Server 2022 images with .NET 6 preinstalled will be deprecated ...
```

**Extract:**

| Field | Method |
|---|---|
| Issue Description | Concatenate all `Answer:` blocks; the longest is usually the full description |
| Advisory tracking ID | Look for `Answer: [A-Z0-9]{4}-[A-Z0-9_]{2,8}` after a "tracking ID" question |
| Subscription / Resource ID | Search the whole block for `/subscriptions/<guid>/...` |
| Customer-reported start time | An `Answer:` containing a UTC timestamp |

## Pattern 2: Free-form description

The user pastes a paragraph or two of their own narrative.

```
Our prod VMSS in eastus2 rebooted at 03:15 UTC on 2026-06-02. Resource ID is
/subscriptions/aaaa-bbbb/resourceGroups/prod/providers/Microsoft.Compute/virtualMachineScaleSets/web.
No maintenance window was scheduled. We see Event 41 in System.evtx.
```

**Extract:**

| Field | Method |
|---|---|
| Resource ID | Regex (see below) |
| Timestamp | First UTC timestamp; if local time, ask for the UTC offset as a Scope Question |
| Symptom keywords | Free-text; feed to `case-type-routing.md` |
| Logs mentioned | "Event 41 in System.evtx" → recommend `vm-log-analyzer` as a next step |

## Pattern 3: Advisory / Maintenance notification full text

The user pastes the full advisory email body.

```
You're receiving this notification because you're running one or more Azure
virtual machine workloads that may be affected by an upcoming infrastructure
change.

Starting on 26 May 2026, Azure may begin deploying the following virtual
machines (VMs) on Microsoft Azure Network Adapter-enabled hardware ...
```

**Extract:**

| Field | Method |
|---|---|
| Advisory tracking ID | Often in the subject line: regex `[A-Z0-9]{4}-[A-Z0-9_]{2,8}`; if absent, ask |
| Advisory class | Match keywords (MANA / hardware migration / deprecation / retirement / reboot / live migration) — see `case-type-routing.md` subflow C |
| Start date | "Starting on <date>" — usually the first paragraph |
| Affected SKUs / images | VM size lists (Dsv5, Esv5, ...) or image names |

Then route to **subflow C** in `case-type-routing.md`.

## Pattern 4: Full DFM dump

The user pastes everything — Q&A block + the `<Start:Agent_Additional_Properties_Do_Not_Edit> ... <End:...>` system block + service tier, etc.

```
Support Tips: ...
Question: ...
Answer: ...
...
<Start:Agent_Additional_Properties_Do_Not_Edit>
AzureProductSubscriptionID: aaaa-bbbb-cccc-dddd
ResourceUri: /subscriptions/.../resourceGroups/.../providers/Microsoft.Compute/virtualMachines/myvm
ProblemStartTime: 2026-06-02T03:15:00Z
SupportPlanDisplayName: Premier
...
<End:Agent_Additional_Properties_Do_Not_Edit>
```

**This is the most reliable shape** — the system block has clean structured fields:

| Structured field | Maps to |
|---|---|
| `AzureProductSubscriptionID` | Subscription |
| `ResourceUri` | Resource ID (parse RG + VM name from the path) |
| `ProblemStartTime` | Issue Time |
| `SupportPlanDisplayName` | Support Plan |
| `Description` | Issue Description |

If both the Q&A and the structured block are present, prefer the structured block.

## Extraction regexes

| Field | Regex (PowerShell / Python compatible) |
|---|---|
| Subscription GUID | `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |
| Resource ID | `/subscriptions/[0-9a-f-]{36}/resourceGroups/[^/]+/providers/Microsoft\.[A-Za-z]+/[^/\s]+/[^\s'\"<>]+` |
| Advisory tracking ID | `\b[A-Z0-9]{4}-[A-Z0-9_]{2,8}\b` (test against `5RWW-K4G`, `8PJS-_48`) |
| UTC timestamp | `\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(Z| ?UTC)?` |
| VM size SKU | `Standard_[A-Z]+\d+[a-z]*_v?\d*` |
| Tenant ID GUID | Same as Subscription GUID; disambiguate by surrounding text ("tenant" vs "subscription") |
