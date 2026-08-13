# NAT Rules

> Source: **NRP - Firewall** dashboard, chapter **NAT Rules** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Firewall - NatRuleCollections

_Widget purpose:_ NAT Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `NAT Rules`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend natRuleCollections = properties.natRuleCollections
| mv-expand natRuleCol = natRuleCollections
| project natRuleCol
| extend id = tostring(natRuleCol.id)
| extend name = tostring(natRuleCol.name)
| extend type = tostring(natRuleCol.type)
| extend etag = tostring(natRuleCol.etag)
| extend provisioningState = tostring(natRuleCol.properties.provisioningState)
| extend priority = tostring(natRuleCol.properties.priority)
| extend rules = natRuleCol.properties.rules
| extend rule_count = array_length(rules)
| extend action_type = tostring(natRuleCol.properties.action.type)
| project-away natRuleCol
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---

## Rules

### Firewall - NatRuleCollections - Rules

_Widget purpose:_ Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `NAT Rules > Rules`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend natRuleCollections = properties.natRuleCollections
| mv-expand natRuleCol = natRuleCollections
| project natRuleCol
| where natRuleCol.id == rule_collection_id
| mv-expand rule = natRuleCol.properties.rules
| project rule
| extend name = tostring(rule.name)
| extend protocols = array_strcat(rule.protocols, ', ')
| extend sourceAddresses = array_strcat(rule.sourceAddresses, '\n')
| extend destinationAddresses = array_strcat(rule.destinationAddresses, '\n')
| extend sourceIpGroups = array_strcat(rule.sourceIpGroups, '\n')
| extend destinationPorts = array_strcat(rule.destinationPorts, '\n')
| extend translatedAddress = tostring(rule.translatedAddress)
| extend translatedPort = tostring(rule.translatedPort)
| project-away rule
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`, `{rule_collection_id}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---
