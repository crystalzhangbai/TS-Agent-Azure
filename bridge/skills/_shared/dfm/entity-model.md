# DFM (OneSupport Dynamics 365) entity model

> Shared fact source — see [`README.md`](README.md) for orientation and the
> canonical `_shared/dfm_odata_helpers.ps1` helper. This file is what skills
> consult when building an `Invoke-DfmApi` query and need the right entity name,
> binding, or status value.

## Entity relationship map (rooted at the Case)

The Case is the `incident` entity. Everything hangs off `incidentid` (GUID):

```
incident (Case)            key: ticketnumber (16-digit) / incidentid (GUID)
├── annotation                  (Notes)           objectid        -> incidentid
├── email                       (Emails)          regardingobjectid -> incidentid
├── phonecall                   (Phone Calls)     regardingobjectid -> incidentid
├── task                        (Tasks)           regardingobjectid -> incidentid
├── appointment                 (Appointments)    regardingobjectid -> incidentid
├── msdfm_labor                 (Labor)           msdfm_CaseId      -> incidentid   ⚠️ PascalCase binding
├── msdfm_caserestrictedattributes (Customer Statement etc.)  nav: msdfm_CaseRestrictedAttributesId  ⚠️ nav-only
├── msdfm_icmdetail             (ICM links)       msdfm_caseid     -> incidentid
├── msdfm_dtmattachmentmetadata (Attachments)     msdfm_caseid     -> incidentid
├── msdfm_customerprogram                          msdfm_caseid     -> incidentid
├── connection                  (Contacts/Roles)  record1id        -> incidentid
├── queueitem                                      objectid         -> incidentid
├── postfollow                                     regardingobjectid -> incidentid
└── activitypointer             (Timeline rollup) regardingobjectid -> incidentid
```

> ⚠️ Three of these have non-obvious access rules — see [`error-diagnosis.md`](error-diagnosis.md):
> - `msdfm_labor` — the **entity set is `msdfm_labors`** (not `msdfm_efforts`), and the bind field is **PascalCase** `msdfm_CaseId@odata.bind`.
> - `msdfm_caserestrictedattributes` — must be read through the **`incident` navigation property** `msdfm_CaseRestrictedAttributesId`; a direct FetchXML/entity-set query 404s.

## Case status — `statuscode` (with parent `statecode`)

### Active — `statecode = 0`

| `statuscode` | Status label | 中文 |
|---|---|---|
| `1` | In progress | 进行中（默认） |
| `2` | On hold | 暂停 |
| `3` | Waiting for details | 等待详情 |
| `4` | Researching | 研究中 |
| `847050000` | Initial contact pending | 等待初次联系 |
| `847050001` | Identifying the issue | 识别问题 |
| `847050002` | Troubleshooting | 排障中 |
| `847050003` | Pending customer response | 等客户回复 |
| `847050004` | Waiting for customer confirmation | 等客户确认 |
| `847050005` | Waiting for product team | 等产品组 |
| `847050013` | Audit | 审计 |
| `847050015` | Transferred to external | 转外部 |
| `847050016` | Transferred from external | 从外部转入 |
| `847050017` | Request to resolve by customer | 客户请求关闭 |
| `847050020` | Mitigated | 已缓解 |
| `847050021` | Pending closure | 待关闭 |

### Resolved — `statecode = 1`

| `statuscode` | Status label |
|---|---|
| `5` | Problem solved |
| `1000` | Information provided |
| `847050006` | Disconnect/Hang-up |
| `847050007` | Duplicate |
| `847050008` | Resolved |
| `847050009` | Resolved external |
| `847050010` | Resolved by customer |
| `847050011` | Un-resolved |
| `847050012` | Transferred to external |
| `847050014` | Created as tombstone |
| `847050019` | Contractual reasons |

### Cancelled — `statecode = 2`

| `statuscode` | Status label |
|---|---|
| `6` | Cancelled |
| `2000` | Merged |

> **Email-type detection** maps a subset of these to email types
> (Initial contact pending → FQR; Pending/Waiting customer → Follow-up/Strike;
> Request to resolve / Mitigated → Closure/LQR) when drafting a customer reply;
> this table is the authoritative value list behind it.

## Email status — `email` entity

| `statecode` | `statuscode` | Meaning |
|---|---|---|
| `0` (Open) | `1` | Draft |
| `1` (Completed) | `2` | Completed |
| `1` (Completed) | `4` | Sent |
| `2` (Canceled) | `6` | Canceled |

(Some tenants also expose `3` = Pending Send.)

## Labor classification — `msdfm_labor.msdfm_classification` (Picklist / Int32)

| Value | Label |
|---|---|
| `337818` | Troubleshooting |

> `msdfm_classification` is a **Picklist** — pass the integer, never the string.
> Full option-set dump (if a new value is needed):
> `GET /api/data/v9.0/EntityDefinitions(LogicalName='msdfm_labor')/Attributes(LogicalName='msdfm_classification')/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$select=LogicalName&$expand=OptionSet`

## OData `@odata.bind` naming conventions

Polymorphic lookup binds follow:
`{lookupfield}_{targetentity}_{owningentity}@odata.bind` (the owning-entity suffix
is required only when the lookup is polymorphic).

| Relationship | Binding | Note |
|---|---|---|
| Note → Case | `objectid_incident@odata.bind` | value `"/incidents(<guid>)"` |
| Email → Case | `regardingobjectid_incident_email@odata.bind` | |
| Phone Call → Case | `regardingobjectid_incident_phonecall@odata.bind` | ⚠️ needs the `_phonecall` suffix |
| Labor → Case | `msdfm_CaseId@odata.bind` | ⚠️ **PascalCase** SchemaName; lowercase → HTTP 400 |
| Incident resolution → Case | `incidentid@odata.bind` | used by `CloseIncident` |

> Bind values are always **relative** entity-set paths: `"/incidents(<guid>)"`,
> `"/contacts(<guid>)"`, etc. — never absolute URLs.

## Cross-references

- Endpoints that use these entities/bindings → [`api-reference.md`](api-reference.md)
- What goes wrong (404/400/403) and how to fix → [`error-diagnosis.md`](error-diagnosis.md)
