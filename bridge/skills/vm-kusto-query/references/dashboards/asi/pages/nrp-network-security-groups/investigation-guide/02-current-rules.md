# Current Rules

> Source: **NRP - Network Security Groups** dashboard, chapter **Current Rules** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Current Rules

### NSG Security Rules

_Widget purpose:_ Security Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Current Rules > Current Rules > Security Rules`

```kusto
// AS :: moved to new Kusto
let nsg = cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isempty(queryHintTime) or timestamp between(datetime_add('hour', -1, queryHintTime) .. datetime_add('hour', 1, queryHintTime))
| where isnotempty(queryName) and (resourceGroup =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId)
| where type == "microsoft.network/networksecuritygroups" and not(partial)
| where name =~ queryName
| top 1 by timestamp desc
| extend Json = parse_json(properties)
| extend Subnets = Json.subnets
| extend defaultSecurityRules = Json.defaultSecurityRules
| extend securityRules = Json.securityRules;
let defaultRules = nsg
| mv-expand securityRule = defaultSecurityRules
| extend Type = 'DefaultSecurityRule';
let securityRules = nsg
| mv-expand securityRule = securityRules
| extend Type = 'CustomSecurityRule';
union kind=outer defaultRules, securityRules
| extend 
    destinationPortRange = securityRule.properties.destinationPortRange,
    destinationPortRanges = securityRule.properties.destinationPortRanges,
    sourcePortRanges = securityRule.properties.sourcePortRanges,
    sourcePortRange = securityRule.properties.sourcePortRange
| extend access = tostring(securityRule.properties.access)
| project 
    name = tostring(securityRule.name),
    provisioningState = tostring(securityRule.properties.provisioningState),
    description = tostring(securityRule.properties.description),
    protocol = tostring(securityRule.properties.protocol),
    sourcePortRange = tostring(coalesce(sourcePortRange, array_strcat(sourcePortRanges, ", "))),
    destinationPortRange = tostring(coalesce(destinationPortRange, array_strcat(destinationPortRanges, ", "))),
    sourceAddressPrefix = iif(
        isempty(securityRule.properties.sourceAddressPrefix), 
        array_strcat(securityRule.properties.sourceAddressPrefixes, ", "),
        tostring(securityRule.properties.sourceAddressPrefix)
        ), 
    destinationAddressPrefix = iif(
        isempty(securityRule.properties.destinationAddressPrefix), 
        array_strcat(securityRule.properties.destinationAddressPrefixes, ", "), 
        tostring(securityRule.properties.destinationAddressPrefix)
        ),
    priority = toint(securityRule.properties.priority),
    direction = tostring(securityRule.properties.direction),
    internalSecurityRuleName = tostring(securityRule.properties.internalSecurityRuleName),
    Type,
    access,
    level = iif(access == "Deny", "error", "info")
| order by priority asc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryName}`, `{queryHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/networksecuritygroups"`

---
