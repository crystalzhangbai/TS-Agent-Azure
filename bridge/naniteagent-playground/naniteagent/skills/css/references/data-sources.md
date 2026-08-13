# Data Sources & Cluster Mapping

### 1. Azure Active Directory & User Information
**Primary Use**: User details, aliases, full names, titles, directory lookups

- **Cluster**: `https://1es.kusto.windows.net`
- **Database**: `AzureActiveDirectory`
- **Primary Table**: `AADUser`
- **Contains**: Complete user directory information, aliases, contact details
- **Trigger Words**: `useralias`, `user`, `alias`, `directory`, `contact`

> **Join guidance**: Use `AzureActiveDirectoryId` when both sides expose the AAD object ID. For sources that only expose a corp alias (e.g. SSD `DeviceData`), join the normalized alias to `AADUser.MailNickname` — but note `MailNickname` is **not** fully unique (~4,430 duplicate values, mostly disabled/guest accounts), so filter `isnotempty(MailNickname)` and expect occasional row multiplication. Avoid joining on `UserPrincipalName` (also has ~49 guest duplicates).


**Important Columns** (schema verified 2026-06-24 via `AADUser | getschema`):

| Column | Type | Description |
|--------|------|-------------|
| `AzureActiveDirectoryId` | string | **Primary key** — unique AAD object ID; use for all joins |
| `UserPrincipalName` | string | UPN / sign-in name (near-unique; guest accounts can duplicate) |
| `MailNickname` | string | Mail alias (the short corp alias) |
| `DisplayName` | string | Full display name |
| `GivenName` / `Surname` | string | First / last name |
| `Mail` | string | Primary email address |
| `JobTitle` | string | Job title |
| `Department` | string | Department name |
| `CompanyName` / `CompanyCode` | string | Employing company / code |
| `AccountEnabled` | bool | Whether the account is enabled |
| `City` / `CityName` / `StateProvinceCode` / `CountryShortCode` / `ZipCode` | string | Location attributes |
| `BuildingId` / `BuildingName` / `OfficeLocation` | long/string | Office / building |
| `CostCenterCode` / `ProfitCenterCode` | string | Finance allocation codes |
| `PersonnelNumber` | string | HR personnel number (links to People_Person) |
| `ReportsToFullName` / `ReportsToEmailName` / `ReportsToPersonnelNbr` | string/long | Manager attributes |
| `OnPremisesSamAccountName` / `OnPremisesUserPrincipalName` / `OnPremisesSecurityIdentifier` | string | On-prem AD identity |
| `OnPremisesSyncEnabled` / `OnPremisesLastSyncDateTime` | bool/datetime | Hybrid sync state |
| `UsageLocation` | string | Licensing usage country |
| `EtlIngestDate` / `EtlProcessDate` / `EtlLastUpdateDate` | datetime | ETL refresh timestamps |


**Sample Query**:
```kql
AADUser
| where UserPrincipalName contains "alias"
| project DisplayName, UserPrincipalName, JobTitle, AccountEnabled, Department, City, ReportsToFullName, AzureActiveDirectoryId , MailNickname
| limit 100
```

> **Unique key / duplicates** (verified 2026-06-24, 1,022,488 rows): `AzureActiveDirectoryId` is the clean primary key (fully unique, 0 duplicates). `UserPrincipalName` is **almost** unique but has ~49 duplicated UPNs (~98 rows) — all external guest accounts (`…#ext#@microsoft.onmicrosoft.com`), often the same guest appearing once enabled and once disabled. **Join on `AzureActiveDirectoryId`, not UPN.**

### 2. Organizational Hierarchy & Reporting Structure
**Primary Use**: Organizational chart data, reporting lines, management structure

- **Cluster**: `https://fimpubameprodwestus.westus.kusto.windows.net`
- **Database**: `AzureGraphMigration`
- **Primary Table**: `People_Person`
- **Contains**: Job titles, reporting relationships, organizational structure
- **Trigger Words**: `reportline`, `manager`, `org`, `hierarchy`, `css`, `MCAPS`

**Important Columns** (schema verified 2026-06-24 via `People_Person | getschema`):

| Column | Type | Description |
|--------|------|-------------|
| `Alias` | string | **Key** — corp alias (unique among non-empty; ~29% empty for non-employees) |
| `PersonnelNumber` | long | HR personnel number (links to AADUser) |
| `FullName` / `ActualDisplayName` / `DisplayName` | string | Name variants |
| `PreferredFirstName` / `FirstName` / `LastName` | string | Name parts |
| `Title` | string | Job title |
| `EmailAddress` | string | Email address |
| `IsActiveEmployee` | bool | Whether currently an active employee |
| `OrgLevel` | long | Depth in the org hierarchy |
| `CostCenterCode` | string | Cost center |
| `ManagerAlias` / `ManagerPersonnelNumber` | string/long | Direct (HR) manager |
| `ActiveManagerAlias` / `ActiveManagerPersonnelNumber` / `ActiveManagerDisplayName` | string/long | Current effective manager (use these for live reporting) |
| `Managers` | dynamic | Full manager chain (array) |
| `OrgHierarchy` / `OrgHierarchyPersonnelNumbers` | string | Full L1→Ln alias / personnel-number chain |
| `ActiveOrgHierarchy` / `ActiveOrgHierarchyPersonnelNumber` | string | Current effective org chain |
| `PreviousManagerAlias` / `ManagerChangeDate` | string/datetime | Reorg tracking |
| `ServiceAwardDate` | datetime | Hire/service anniversary date |
| `TerminationDate` | datetime | Termination date (null = active) |
| `LatestUpdateDate` | datetime | Record last-updated timestamp |


**Sample Query**:
```kql
People_Person
| where Alias contains "alias"
| project Alias, DisplayName, Title, ActiveManagerAlias, CostCenterCode, IsActiveEmployee, Managers, ServiceAwardDate
| limit 50
```

> **Unique key / duplicates** (verified 2026-06-24, 902,598 rows): `Alias` is unique among populated values (643,460 distinct, 0 duplicates), but **259,138 rows (~29%) have an empty `Alias`** (non-employee / contact records). **Filter `isnotempty(Alias)` before keying or joining on it.**

### 3. Secure Access Workstation (SAW) Management
**Primary Use**: SAW device status, health monitoring, S360 alerts

- **Cluster**: `https://kvcy2wf2t0n1epwsyck1cj.australiaeast.kusto.windows.net`
- **Database**: `microsoft`
- **Primary Table**: `sawusage`
- **Contains**: SAW device health, usage patterns, security compliance
- **Trigger Words**: `saw`, `s360`, `healthy`, `s360 alert`, `saw device`, `security workstation`

**Important Columns** (schema verified 2026-06-24 via `sawusage | getschema`):

| Column | Type | Description |
|--------|------|-------------|
| `SerialNo` | string | **Primary key** — device serial (fully unique) |
| `AssetNo` | string | Asset number |
| `SAWName` | string | SAW machine / hostname |
| `Alias` | string | Assigned user's alias |
| `LastLogonUserAlias` / `LastLogonUserDomain` | string | Last interactive logon user |
| `S360Status` | string | S360 security compliance status |
| `IsSawAdmin` | bool | Whether the user is a SAW admin |
| `AMEExclusive` | bool | AME-exclusive device flag |
| `DeviceTypeName` | string | Device model/type |
| `OsVersionName` | string | OS version |
| `DaysSinceTurningOn` / `DaysSinceLogin` | long | Inactivity indicators |
| `LogonCount` | long | Total logon count |
| `LastLogonDate` / `LastRefreshed` | datetime | Last logon / data refresh time |
| `L1_Alias` … `L5_Alias` | string | Management chain (levels 1–5) |
| `OrganizationName` | string | Org name |
| `IsEmployeeActive` | bool | Whether the assigned employee is active |
| `DeliveryDate` / `WarrantyEndDate` | datetime | Procurement / warranty dates |
| `PONumber` | string | Purchase order number |


**Sample Query**:
```kql
sawusage
| where LastRefreshed >= ago(7d)
| where Alias =~ "user_alias"
| project Alias,LastLogonUserAlias,AssetNo,SerialNo,AMEExclusive,IsSawAdmin,S360Status,DeviceTypeName,DaysSinceTurningOn,DaysSinceLogin,LastRefreshed,LastLogonDate,LastLogonUserDomain,LogonCount,SAWName,L1_Alias,L2_Alias,L3_Alias,L4_Alias,L5_Alias,OrganizationName,DeliveryDate,OsVersionName,PONumber,IsEmployeeActive,WarrantyEndDate
```

> **Unique key / duplicates** (verified 2026-06-24, 125,722 rows): `SerialNo` is the clean primary key — fully unique (125,722 distinct = total rows, 0 empty, 0 duplicates). Reliable device key for joins.

### 4. Employee Device & Asset Management
**Primary Use**: Hardware inventory, asset tracking, procurement details

- **Cluster**: `https://oneassetkustoprod.eastus.kusto.windows.net`
- **Database**: `OneAssetRO`
- **Primary Table**: `EmployeeDeviceData` (other `Employee*` tables exist but the columns/keys below apply to `EmployeeDeviceData`)
- **Contains**: Hardware specifications, asset IDs, purchase orders, device lifecycle
- **Trigger Words**: `device`, `asset`, `hardware`, `PC`, `laptop`, `inventory`, `procurement`

**Important Columns** (schema verified 2026-06-24 via `EmployeeDeviceData | getschema`):

| Column | Type | Description |
|--------|------|-------------|
| `Id` | int | **Primary key** — unique record ID; use for joins/dedup |
| `SerialNumber` | string | Device serial (NOT unique — placeholders like `N/A`/`NA`; do not key on it) |
| `AssetTag` | string | Asset tag (~17% empty) |
| `AssetStatus` | string | Lifecycle status (in use, retired, etc.) |
| `RecordType` / `RecordSource` | string | Record classification / source system |
| `CustodianName` / `DiscoveredAlias` / `AssignedUser` / `Owner` / `AdminAlias` | string | People associated with the device |
| `Manufacturer` / `Model` / `Name` | string | Hardware make/model/name |
| `DeviceType` / `DeviceSubType` / `ItemType` / `ItemSubType` / `AssetCategory` | string | Device classification |
| `IsAllocatedPrimaryDevice` / `IsActive` | bool | Allocation / active flags |
| `RAM` / `ProcCount` / `CPUType` / `DriveAllTotalSize` | int/decimal | Hardware specs |
| `BuildingId` / `BuildingName` / `Room` / `DeviceLocation` | int/string | Physical location |
| `CompanyCode` / `CompanyName` / `CostCenter` / `ProfitCenterCode` / `InternalOrder` | string/int | Org / finance attributes |
| `PurchaseOrderNumber` / `POAssetDescription` / `Cost` / `CurrencyKey` | string/decimal | Procurement |
| `AssetMainNumber` / `AssetSubNumber` / `AssetClassCode` / `AssetGroupId` / `AssetGroupName` | int/string | SAP asset accounting |
| `AcquisitionDate` / `CapitalizationDate` / `RetiredDate` / `AssetStartDate` | datetime | Asset lifecycle dates |
| `WarrantyStartDate` / `WarrantyEndDate` | datetime | Warranty window |
| `SAPTransactionStatus` / `TransactionType` / `GLNumber` / `AccumulatedDepreciation` | string/int/decimal | SAP/GL bookkeeping |
| `Created` / `Modified` / `LastInventoryDate` | datetime | Record audit timestamps |
| `ProgramName` | string | Provisioning program |


**Sample Query**:
```kql
EmployeeDeviceData
| where CustodianName contains "alias" or Owner contains "alias"
| project Id,RecordType,RecordSource,AssetStatus,AssetTag,SerialNumber,CustodianName,DiscoveredAlias,BuildingId,BuildingName,Room,Manufacturer,Model,Name,CompanyCode,AssetMainNumber,AssetSubNumber,CostCenter,InternalOrder,CapitalizationDate,AcquisitionDate,RetiredDate,PurchaseOrderNumber,POAssetDescription,Cost,CurrencyKey,AssetInCustodyFlag,AssetClassCode,AssetGroupId,AssetGroupName,AssetType,Comment,Created,CreatedBy,Modified,LastInventoryDate,ModifiedBy,ProfitCenterCode,GLCompanyCode,SAPTransactionStatusId,SAPTransactionStatus,GLNumber,AccumulatedDepreciation,TransactionTypeId,TransactionType,ErrorMessage,StatusBar,ItemType,ItemSubType,AssetCategory,AdminAlias,DeviceLocation,AssignedUser,CompanyName,IsActive,ProgramName,RAM,ProcCount,CPUType,DriveAllTotalSize,WarrantyStartDate,WarrantyEndDate,Owner,AssetStartDate,DeviceType,DeviceSubType,IsAllocatedPrimaryDevice
```

> **Unique key / duplicates** (verified 2026-06-24, 1,791,537 rows): `Id` is the clean primary key — fully unique (0 duplicates). **`SerialNumber` is heavily NOT unique** — 7,129 duplicated serials and 53,188 empty, with placeholder values dominating: `N/A` (265,313 rows), `NA` (64,911), `00000`/`0`/`0000…` (thousands). **Key/dedup on `Id`, never `SerialNumber`.** If matching by serial, exclude `N/A`, `NA`, and all-zero placeholders.

### 5. AzureDevOps Wiki, Workitem, Commit query
**Primary Use**: AzureDevOps Microsoft internal data collection including Organization, Project, Repo, Workitem, Commit, Wiki

- **Cluster**: `https://1es.kusto.windows.net`
- **Database**: `AzureDevOps`
- **Tables**: `Commit`, `WorkItem`, `Wiki`, `Team`, `WorkItemLink`, `Repository`, `Project`, `Build`
- **Contains**: Azure DevOps metadata — commits, work items (bugs/tasks/features), wiki pages, teams, work-item links, repositories, projects, and builds
- **Trigger Words**: `workitem`, `code`, `commit`, `project`, `bug`, `issue`

> **Note**: This is an overview-only entry — schemas vary per table. Verify each table's columns with `<TableName> | getschema` before querying. Common keys: `Commit` by `CommitId`, `WorkItem` by `WorkItemId`, `Wiki` by `Path`/`ProjectId`.

**Sample Query** (recent work items):
```kql
WorkItem
| where ChangedDate >= ago(30d)
| project WorkItemId, WorkItemType, Title, State, AssignedTo, AreaPath, ChangedDate
| take 50
```

### 6. IPAM (IP Allocation / Microsoft Egress IP)
**Primary Use**: Microsoft IP address allocations and egress IP lookups (Corp Egress, AzVPN, DevBox, etc.)

- **Cluster**: `https://ipam.kusto.windows.net`
- **Database**: `IpamReport`
- **Primary Table**: `Allocations_Default`
- **Contains**: IP prefix allocations with CIDR ranges, tags (CorpNetPublic / MsftAzVPN / DevBox), and ownership metadata
- **Trigger Words**: `ipam`, `egress ip`, `corp egress`, `azvpn`, `devbox ip`, `vip`, `ip allocation`, `corpnetpublic`

> **Full details** (27-field schema, Corp Egress / AzVPN / DevBox filter patterns, sample queries) → [ipam-egress-query.md](ipam-egress-query.md). Key columns: `Prefix` (CIDR), `PrefixFirstAddress`/`PrefixLastAddress`, `AddressCount`, `Tags` (semicolon-delimited), `Identifier`, `IsIpv4`.

**Sample Query** (Corp Egress IPs):
```kql
Allocations_Default
| where Tags contains 'CorpNetPublic' and Tags contains 'Corp to Internet Edge'
| project Prefix, PrefixFirstAddress, PrefixLastAddress, AddressCount, Identifier, Tags
| take 50
```

### 7. SSD (Single Secure Device) Rollout Status
**Primary Use**: Microsoft internal Single Secure Device (SSD) rollout / migration status — device enrollment, compliance, and encryption state for the SAW→SSD conversion program.

- **Cluster**: `https://anptappe.eastus2.kusto.windows.net`
- **Database**: `SSD`
- **Primary Table**: `DeviceData`
- **Contains**: Per-device Intune-style enrollment, compliance, encryption and rollout (GroupTag) state for the internal SSD program. **Current-snapshot table** — one row per device, fully refreshed daily (all rows share a single `ETLDate`).
- **Trigger Words**: `ssd`, `single secure device`, `converted saw`, `convertedsaw`, `convertedcorp`, `autopilot`, `device rollout`, `compliance state`, `enrollment state`, `grouptag`, `mpd`, `mpd_`, `mpd.core.microsoft`, `MPD_<alias>`

**Rollout cohorts — `GroupTag` distribution** (snapshot 2026-06-23):

| GroupTag | Count | Meaning |
|----------|-------|---------|
| (empty) | 45,273 | Not yet tagged / general fleet |
| `Microsoft MPD – Zones Autopilot` | 6,134 | New devices provisioned via Autopilot |
| `ConvertedSAW` | 1,320 | SAW devices converted to SSD |
| `ConvertedCorp` | 12 | Corp devices converted to SSD |

> Note: `GroupTag` uses an en-dash (`–`) in `Microsoft MPD – Zones Autopilot`, not a hyphen. Many records are sparsely populated — of ~52.7K rows only ~18.8K have a non-empty `UPN`/`MemberName` and ~15.2K have `ComplianceState`/`Manufacturer`/`OSBuild`. Always filter `isnotempty(...)` on the columns you need.

**Important Columns** (schema verified via `DeviceData | getschema`):

| Column | Type | Description |
|--------|------|-------------|
| `SerialNumber` | string | Device hardware serial (primary device identifier; always populated) |
| `DeviceName` | string | Hostname (e.g. `DESKTOP-FCVH4TU`) |
| `EmployeeId` | string | Owning employee ID |
| `UPN` | string | User Principal Name of the assigned user — format `MPD_<alias>@mpd.core.microsoft` (extract `<alias>` to join AADUser/People_Person/sawusage) |
| `MemberName` | string | Display name of the assigned member |
| `Email` | string | User email |
| `ComplianceState` | string | `compliant` / `noncompliant` / `inGracePeriod` / `unknown` |
| `ComplianceGracePeriodExpirationDate` | datetime | When the compliance grace period expires |
| `DeviceRegistrationState` | string | e.g. `registered` |
| `EnrolledDate` | datetime | Intune enrollment timestamp |
| `IsEncrypted` | bool | Whether the device disk is encrypted (BitLocker) |
| `DeviceTypeName` | string | Device/model type code |
| `Manufacturer` | string | e.g. `LENOVO` |
| `OSBuild` | string | OS build number (e.g. `10.0.26200.8390`) |
| `PONUmber` | string | Purchase order number (note: column name is `PONUmber`) |
| `EnrollmentState` | string | `enrolled` / `notContacted` |
| `GroupTag` | string | Rollout cohort tag (see distribution above) |
| `LastLogonDate` | datetime | Last user logon |
| `LastLogonUser` | string | Last logon user — format `mpd_<alias>` (corp alias, joinable like UPN) |
| `ETLDate` | datetime | Snapshot/refresh date — single value across the whole table (current-snapshot, full daily refresh; no per-device history) |

**Sample Query — rollout summary by cohort + compliance**:
```kql
DeviceData
| where isnotempty(GroupTag)
| summarize Devices=count(),
            Compliant=countif(ComplianceState == "compliant"),
            NonCompliant=countif(ComplianceState == "noncompliant"),
            Encrypted=countif(IsEncrypted == true)
    by GroupTag
| sort by Devices desc
```

**Sample Query — non-empty device records for a cohort**:
```kql
DeviceData
| where GroupTag == "ConvertedSAW"
| where isnotempty(UPN) and isnotempty(ComplianceState)
| project SerialNumber, DeviceName, UPN, MemberName, ComplianceState,
          DeviceRegistrationState, EnrollmentState, IsEncrypted,
          Manufacturer, OSBuild, EnrolledDate, LastLogonDate, ETLDate
| take 50
```

**Sample record** (`ConvertedSAW`, fully populated):

| SerialNumber | DeviceName | ComplianceState | EnrollmentState | IsEncrypted | Manufacturer | OSBuild | GroupTag |
|---|---|---|---|---|---|---|---|
| PF4LFVKL | DESKTOP-FCVH4TU | compliant | enrolled | true | LENOVO | 10.0.26200.8390 | ConvertedSAW |

> **Unique key / duplicates** (verified 2026-06-24, 52,739 rows): `SerialNumber` is the clean primary key — fully unique (52,739 distinct = total rows, 0 empty, 0 duplicates). `DeviceName` is unreliable — 37,516 rows (~71%) are empty, and the placeholder hostname `DELLSSD` is shared by 2 distinct devices. **Key/dedup on `SerialNumber`, not `DeviceName`.**

> **Identity format & cross-table joins** (verified 2026-06-24): In `DeviceData`, `UPN` is formatted as `MPD_<alias>@mpd.core.microsoft` (e.g. `MPD_atouchstone@mpd.core.microsoft`) and `LastLogonUser` as `mpd_<alias>` (e.g. `mpd_ltummala`). The embedded `<alias>` is the standard corp alias and can be joined to other tables — `AADUser.MailNickname`, `People_Person.Alias`, or `sawusage.Alias`. Extract it with a case-insensitive regex and normalize case before joining:
>
> ```kql
> DeviceData
> | where isnotempty(UPN)
> | extend Alias = tolower(extract("[Mm][Pp][Dd]_([^@]+)", 1, UPN))                 // owner alias from UPN
> | extend LastLogonAlias = tolower(extract("[Mm][Pp][Dd]_([^@\\s]+)", 1, LastLogonUser)) // last-logon alias
> | project SerialNumber, DeviceName, UPN, Alias, LastLogonUser, LastLogonAlias, ComplianceState, GroupTag
> ```
> Cross-cluster join example (DeviceData alias → AAD user). Run with database `SSD` selected on cluster `anptappe.eastus2.kusto.windows.net`, or fully qualify `DeviceData` as shown:
> ```kql
> cluster('anptappe.eastus2.kusto.windows.net').database('SSD').DeviceData
> | where isnotempty(UPN)
> | extend Alias = tolower(extract("[Mm][Pp][Dd]_([^@]+)", 1, UPN))
> | join kind=leftouter (
>     cluster('1es.kusto.windows.net').database('AzureActiveDirectory').AADUser
>     | where isnotempty(MailNickname)          // MailNickname not fully unique — see Section 1 join guidance
>     | extend Alias = tolower(MailNickname)
>     | project Alias, DisplayName, JobTitle, Department, AccountEnabled
>   ) on Alias
> | project SerialNumber, Alias, DisplayName, JobTitle, Department, ComplianceState, GroupTag
> ```
> The same `Alias` joins to `People_Person` (`Alias`, filter `isnotempty(Alias)` — ~29% empty) for org/manager data or `sawusage` (`Alias`) for SAW history. Note: alias-only joins will not resolve guest/external users whose `MPD_` alias has no matching corp `MailNickname`.
