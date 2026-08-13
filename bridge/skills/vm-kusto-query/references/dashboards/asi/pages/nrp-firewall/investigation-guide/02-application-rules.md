# Application Rules

> Source: **NRP - Firewall** dashboard, chapter **Application Rules** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Firewall - ApplicationRuleCollections

_Widget purpose:_ Application Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Application Rules`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend applicationRuleCollections = properties.applicationRuleCollections
| mv-expand appRuleCol = applicationRuleCollections
| project appRuleCol
| extend id = tostring(appRuleCol.id)
| extend name = tostring(appRuleCol.name)
| extend type = tostring(appRuleCol.type)
| extend etag = tostring(appRuleCol.etag)
| extend provisioningState = tostring(appRuleCol.properties.provisioningState)
| extend priority = tostring(appRuleCol.properties.priority)
| extend rules = appRuleCol.properties.rules
| extend rule_count = array_length(rules)
| extend action_type = tostring(appRuleCol.properties.action.type)
| project-away appRuleCol
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---

## Rules

### Firewall - ApplicationRuleCollections - Rules

_Widget purpose:_ Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Application Rules > Rules`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend applicationRuleCollections = properties.applicationRuleCollections
| mv-expand appRuleCol = applicationRuleCollections
| where appRuleCol.id == rule_collection_id
| mv-expand rule = appRuleCol.properties.rules
| project rule
| extend name = tostring(rule.name)
| extend priority = toint(rule.priority)
| extend protocols = array_length(rule.protocols)
| extend protocol = strcat(rule.protocols[0].protocolType, ' (', rule.protocols[0].port, ')')
| extend sourceAddresses = array_strcat(rule.sourceAddresses, '\n')
| extend sourceIpGroups = array_strcat(rule.sourceIpGroups, '\n')
| extend direction = tostring(rule.direction)
| extend fqdnTags = array_strcat(rule.fqdnTags, '\n')
| extend targetFqdns = array_strcat(rule.targetFqdns, '\n')
| extend actions = array_strcat(rule.actions, ', ')
| project-away rule
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`, `{rule_collection_id}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---
