---
name: css
version: 2.3.0
description: "Microsoft Employee capability to search internal Kusto databases for business-related data including People information, organizational report lines, KPI data, and Microsoft Service Workstation (MSW) data. Also supports browser-automated ICM Incident creation (trigger: create icm, 创建icm, new incident), FQR email drafting via DFM (trigger: draft fqr, fqr email, 首次质量回复), batch D365 case note addition (trigger: add case note, batch note), and SBAManager Bot case assignment (trigger: assign cases). Chat log export (save chatlog) includes /session and /usage output. Jarvis dashboard JSON to skill reference markdown conversion (trigger: convert dashboard, jarvis dashboard, dashboard json)."
---

## Overview

This skill enables Microsoft employees to efficiently query internal Kusto databases and automate browser-based workflows. It provides structured access to employee information, organizational hierarchies, device management data, ICM incident creation, FQR email drafting, and chat log export.

## Usage Guide

### Query Process Workflow

1. **Context Understanding**: Identify which Kusto cluster contains the required data
2. **Schema First**: Always retrieve table schema before writing queries using `TableName | getschema`
3. **Use Azure MCP**: Execute all queries through Azure MCP tools - do not write custom scripts
4. **Filter Appropriately**: Apply proper time ranges and filters to optimize query performance

### Best Practices

- Start with time-bounded queries to limit result sets
- Use specific column selections instead of `*` for better performance
- Apply appropriate filters based on the data source requirements
- Validate schema before joining tables from different databases
- **Always use column names from `references/data-sources.md` sample queries as the source of truth — never rely on session history, summaries, or memory for column names, as these can carry forward mistakes from prior sessions**

## Data Sources Summary

| # | Data Source | Cluster | Database | Key Table(s) |
|---|-----------|---------|----------|---------------|
| 1 | AAD / User Info | `1es.kusto.windows.net` | `AzureActiveDirectory` | `AADUser` |
| 2 | Org Hierarchy | `fimpubameprodwestus.westus.kusto.windows.net` | `AzureGraphMigration` | `People_Person` |
| 3 | SAW (Secure Access Workstation) machine | `kvcy2wf2t0n1epwsyck1cj.australiaeast.kusto.windows.net` | `microsoft` | `sawusage` |
| 4 | Regular Device / Asset (SAW included) | `oneassetkustoprod.eastus.kusto.windows.net` | `OneAssetRO` | `EmployeeDeviceData` |
| 5 | AzureDevOps list | `1es.kusto.windows.net` | `AzureDevOps` | `Commit`, `WorkItem`, `Wiki` |
| 6 | IPAM (IP Allocation / Egress IP) | `ipam.kusto.windows.net` | `IpamReport` | `Allocations_Default` |
| 7 | SSD (Single Secure Device) rollout status | `anptappe.eastus2.kusto.windows.net` | `SSD` | `DeviceData` |

> Full cluster details, sample KQL queries, and column references → [references/data-sources.md](references/data-sources.md)

## Reference Files

| File | Description |
|------|-------------|
| [data-sources.md](references/data-sources.md) | Full Kusto cluster/table details and sample KQL queries for all 7 data sources |
| [coreidentity-request.md](references/coreidentity-request.md) | CoreIdentity entitlement request — 7 fixed entitlements, browser automation workflow |
| [coreidentity-renewal.md](references/coreidentity-renewal.md) | CoreIdentity membership renewal — form types, step-by-step workflow |
| [icm-creation.md](references/icm-creation.md) | ICM incident creation — tool mapping, batch JS fill, field reference, description template |
| [fqr-email.md](references/fqr-email.md) | FQR email drafting via DFM — CKEditor injection, B01 integration, end-to-end workflow |
| [chatlog-export.md](references/chatlog-export.md) | Chat log export — dual HTML/MD output, /session & /usage metadata, templates |
| [dsat-analysis.md](references/dsat-analysis.md) | DSAT/CSAT root cause analysis — 5-phase DFM browser workflow, timeline extraction, quality assessment, HTML report generation |
| [ipam-egress-query.md](references/ipam-egress-query.md) | IPAM Microsoft Egress IP queries — 27-field extraction, Corp Egress / AzVPN / DevBox filters |
| [batch-casenote.md](references/batch-casenote.md) | Batch-add case notes to D365 Timeline via OData API browser injection — PowerShell IIFE generation, no external scripts |
| [sbamanager-bot.md](references/sbamanager-bot.md) | Batch-assign D365 support cases via Teams SBAManager Bot interaction |
| [convert-jarvis-dashboard-to-skill.md](references/convert-jarvis-dashboard-to-skill.md) | Jarvis dashboard → skill reference markdown conversion — step-by-step process, tile extraction, MDM/Kusto identification, confidentiality tagging |

## Trigger Words Reference

| Category | Trigger Words |
|----------|---------------|
| **User Management** | `useralias`, `user`, `alias`, `directory`, `contact` |
| **Organization** | `reportline`, `manager`, `org`, `hierarchy`, `css`, `MCAPS` |
| **SAW/Security** | `saw`, `s360`, `healthy`, `s360 alert`, `saw device`, `security workstation` |
| **Asset Management** | `device`, `asset`, `hardware`, `PC`, `laptop`, `inventory`, `procurement` |
| **AzureDevOps** | `workitem`, `work item`, `code`, `commit`, `project`, `bug`, `issue`, `wiki`, `repo`, `pull request`, `build` |
| **ICM Creation** | `create icm`, `new incident`, `创建icm`, `创建事件`, `file icm` |
| **FQR Email** | `draft fqr`, `fqr email`, `first quality response`, `首次质量回复`, `dfm email` |
| **CoreIdentity** | `coreidentity`, `membership`, `renewal`, `expiring`, `entitlement`, `access renewal` |
| **Chat Log Export** | `save chatlog`, `export chatlog`, `save log`, `保存聊天记录` |
| **IPAM / Egress IP** | `ipam`, `egress ip`, `corp egress`, `azvpn`, `devbox ip`, `vip`, `ip allocation`, `corpnetpublic` |
| **SSD (Single Secure Device)** | `ssd`, `single secure device`, `converted saw`, `convertedsaw`, `convertedcorp`, `autopilot`, `device rollout`, `compliance state`, `enrollment state`, `grouptag`, `mpd`, `mpd_`, `mpd.core.microsoft`, `MPD_<alias>` |
| **Case Note** | `add case note`, `添加 case note`, `batch note`, `批量 note` |
| **Case Assignment** | `assign cases`, `分配 case`, `批量分配`, `assign to me`, `case assignment` |
| **General** | `kusto`, `query`, `business data`, `employee`, `microsoft` |

## Fallback Resources

### Microsoft Service Workstation (MSW) Portal
**When to Use**: After trying all above approaches, you cannot find information in Kusto databases or for project-specific searches

- **URL**: https://aka.ms/msw
- **Method**: Use the **playwright-cli skill** to open and search (it is a skill, not an MCP server)
- **Best for**: Project information, service requests, documentation, specification, name like code name.

## Security & Compliance Notes

- All queries must comply with Microsoft data handling policies
- Ensure appropriate permissions before accessing sensitive organizational data
- Limit data access to business-justified scenarios only
- Follow data retention and privacy guidelines for query results
- Report any unusual data patterns or security concerns through appropriate channels

## Troubleshooting

### Common Issues
1. **Schema Changes**: If queries fail, verify table schema hasn't changed
2. **Permission Errors**: Ensure proper access rights to target databases, if receive error message Access Denied or http 401 , 403, please report out agent cannot access the target datasource.
3. **Performance Issues**: Add time filters and limit result sets
4. **Data Freshness**: Check data ingestion schedules for real-time requirements

### Support Resources
- Azure MCP tool documentation for query execution

