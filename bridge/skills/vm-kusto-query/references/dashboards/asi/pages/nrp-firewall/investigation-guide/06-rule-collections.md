# Rule Collections

> Source: **NRP - Firewall** dashboard, chapter **Rule Collections** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Firewall - Network Rule Collections

_Widget purpose:_ Rule Collections

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Rule Collections`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend networkRuleCollections = properties.networkRuleCollections
| mv-expand networkRule = properties.networkRuleCollections
| project networkRule
| extend id = tostring(networkRule.id)
| extend name = tostring(networkRule.name)
| extend type = tostring(networkRule.type)
| extend etag = tostring(networkRule.etag)
| extend provisioningState = tostring(networkRule.properties.provisioningState)
| extend priority = tostring(networkRule.properties.priority)
| extend rules = networkRule.properties.rules
| extend rule_count = array_length(rules)
| extend action_type = tostring(networkRule.properties.action.type)
| project-away networkRule
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---

## Rules

### Firewall - NetworkRuleCollections - Rules

_Widget purpose:_ Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Rule Collections > Rules`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend networkRuleCollections = properties.networkRuleCollections
| mv-expand networkRule = properties.networkRuleCollections
| where networkRule.id == rule_collection_id
| mv-expand rule = networkRule.properties.rules
| project rule
| extend name = tostring(rule.name)
| extend description = tostring(rule.description)
| extend protocols = array_strcat(rule.protocols, ', ')
| extend sourceAddresses = array_strcat(rule.sourceAddresses, '\n')
| extend destinationAddresses = array_strcat(rule.destinationAddresses, '\n')
| extend sourceIpGroups = array_strcat(rule.sourceIpGroups, '\n')
| extend destinationIpGroups = array_strcat(rule.destinationIpGroups, '\n')
| extend destinationFqdns = array_strcat(rule.destinationFqdns, '\n')
| extend destinationPorts = array_strcat(rule.destinationPorts, '\n')
| project-away rule
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`, `{rule_collection_id}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---
