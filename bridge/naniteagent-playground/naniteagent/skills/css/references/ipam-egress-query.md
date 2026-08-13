# IPAM Microsoft Egress IP Query

**Cluster**: `ipam.kusto.windows.net`  
**Database**: `IpamReport`  
**Table**: `Allocations_Default`

## Common Filters

| Filter | Tags Pattern | Description |
|--------|-------------|-------------|
| Corp Egress | `Tags contains 'CorpNetPublic' and Tags contains 'Corp to Internet Edge'` | Microsoft Corp Network Egress IPs |
| AzVPN | `Tags contains 'MsftAzVPN'` | Microsoft Corp AzVPN IPs |
| DevBox | `Tags contains 'CorpNetPublic' and Tags contains 'Devbox' and Tags contains 'SLBv2: ANYCAST'` | Microsoft DevBox Egress IPs |

## Table Schema — Allocations_Default

> ⚠️ **Always use these verified column names in `project` and queries. Do NOT guess.**

| Column | Type | Description |
|--------|------|-------------|
| `Id` | string | Allocation record ID |
| `Prefix` | string | IP prefix in CIDR notation (e.g. `104.43.2.0/23`) |
| `PrefixFirstAddress` | string | First IP address of the prefix range |
| `PrefixLastAddress` | string | Last IP address of the prefix range |
| `AddressCount` | real | Number of IP addresses in the prefix |
| `PrefixLength` | int | CIDR prefix length (e.g. 23) |
| `Tags` | string | Semicolon-delimited key=value metadata string |
| `CreatedBy` | string | Creator identity |
| `CreatedOn` | datetime | Creation timestamp |
| `ModifiedBy` | string | Last modifier identity |
| `ModifiedOn` | datetime | Last modified timestamp |
| `Identifier` | string | Human-readable identifier |
| `ParentId` | string | Parent allocation ID |
| `ChildIds` | string | Child allocation IDs |
| `ExtendConstraints` | string | Extension constraint metadata |
| `LocalTags` | string | Local tag overrides |
| `AddressSpaceId` | string | Address space identifier |
| `IsIpv4` | bool | Whether the prefix is IPv4 |
| `IsReuse` | bool | Whether the prefix is a reuse allocation |
| `DumpTime` | datetime | Data dump timestamp |

> ⚠️ **Common mistake**: Do NOT use `StartIp` / `EndIp` / `NumAddresses` — these columns do NOT exist and cause `SEM0100` errors.  
> Correct columns: `PrefixFirstAddress`, `PrefixLastAddress`, `AddressCount`, `Prefix`

**Standard project columns for IP queries:**

> ⚠️ `Region`, `PhysicalNetwork`, `Description`, `SystemServiceGroup`, `SystemServiceScope`, `VipScope`, and `CommunityName` are **not** native table columns — they are embedded in `Tags` and must be extracted with `extend` before you can `project` them. Use the complete snippet below:

```kql
cluster('ipam.kusto.windows.net').database('IpamReport').Allocations_Default
| where Tags contains 'CorpNetPublic' and Tags contains 'Corp to Internet Edge'  // adjust filter as needed
| extend Region             = extract(@'Region=([^;]+)',             1, Tags)
| extend PhysicalNetwork    = extract(@'PhysicalNetwork=([^;]+)',    1, Tags)
| extend Description        = extract(@'Description=([^;]+)',        1, Tags)
| extend SystemServiceGroup = extract(@'SystemServiceGroup=([^;]+)', 1, Tags)
| extend SystemServiceScope = extract(@'SystemServiceScope=([^;]+)', 1, Tags)
| extend VipScope           = extract(@'VipScope=([^;]+)',           1, Tags)
| extend CommunityName      = extract(@'CommunityName=([^;]+)',      1, Tags)
| project Prefix, PrefixFirstAddress, PrefixLastAddress, AddressCount, PrefixLength, Region, PhysicalNetwork, Description, SystemServiceGroup, SystemServiceScope, VipScope, CommunityName
```

---

## Full 27-Field Extraction Query

> Replace the `where` filter with the appropriate scenario below.

```kql
cluster('ipam.kusto.windows.net').database('IpamReport').Allocations_Default
| where Tags contains 'CorpNetPublic' and Tags contains 'Corp to Internet Edge'  // Microsoft Corp Network Egress
// | where Tags contains 'MsftAzVPN'                                              // Microsoft Corp AzVPN
// | where Tags contains 'CorpNetPublic' and Tags contains 'Devbox' and Tags contains 'SLBv2: ANYCAST'  // Microsoft DevBox
| extend ActivationWorkflow    = extract(@'ActivationWorkflow=([^;]+)',    1, Tags)
| extend AllocationType        = extract(@'AllocationType=([^;]+)',        1, Tags)
| extend BlockIdentifier       = extract(@'BlockIdentifier=([^;]+)',       1, Tags)
| extend BlockPriviledges      = extract(@'BlockPriviledges=([^;]+)',      1, Tags)
| extend Cloud                 = extract(@'Cloud=([^;]+)',                 1, Tags)
| extend CommunityName         = extract(@'CommunityName=([^;]+)',         1, Tags)
| extend Continent             = extract(@'Continent=([^;]+)',             1, Tags)
| extend DCFolder              = extract(@'DCFolder=([^;]+)',              1, Tags)
| extend DeploymentService     = extract(@'DeploymentService=([^;]+)',     1, Tags)
| extend Description           = extract(@'Description=([^;]+)',           1, Tags)
| extend Geo                   = extract(@'Geo=([^;]+)',                   1, Tags)
| extend IPScope               = extract(@'IPScope=([^;]+)',               1, Tags)
| extend Metering              = extract(@'Metering=([^;]+)',              1, Tags)
| extend NetworkType           = extract(@'NetworkType=([^;]+)',           1, Tags)
| extend PhysicalNetwork       = extract(@'PhysicalNetwork=([^;]+)',       1, Tags)
| extend PropertyGroup         = extract(@'PropertyGroup=([^;]+)',         1, Tags)
| extend RangeType             = extract(@'RangeType=([^;]+)',             1, Tags)
| extend Region                = extract(@'Region=([^;]+)',                1, Tags)
| extend RouteRegistry         = extract(@'RouteRegistry=([^;]+)',         1, Tags)
| extend SystemClassification  = extract(@'SystemClassification=([^;]+)',  1, Tags)
| extend SystemOperator        = extract(@'SystemOperator=([^;]+)',        1, Tags)
| extend SystemPlatform        = extract(@'SystemPlatform=([^;]+)',        1, Tags)
| extend SystemService         = extract(@'SystemService=([^;]+)',         1, Tags)
| extend SystemServiceGroup    = extract(@'SystemServiceGroup=([^;]+)',    1, Tags)
| extend SystemServiceScope    = extract(@'SystemServiceScope=([^;]+)',    1, Tags)
| extend Title                 = extract(@'Title=([^;]+)',                 1, Tags)
| extend VipScope              = extract(@'VipScope=([^;]+)',              1, Tags)
| project-away Tags
```

## Tags Format Reference

Raw Tags string format (semicolon-delimited key=value pairs wrapped in `{}`):
```
{Key1=Value1;Key2=Value2;...;LastKey=LastValue;}
```

- Use `extract(@'KeyName=([^;]+)', 1, Tags)` to extract any field
- Missing fields return empty string (sparse rows expected)
- `extractjson` cannot be used — Tags is not valid JSON
