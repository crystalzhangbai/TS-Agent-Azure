# NSG

> Source: **NRP - Subnets** dashboard, chapter **NSG** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Network Security Group

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Container`
Source panel: `NSG`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnotempty(queryNSGName) and (resourceGroup =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId)
| where type == "microsoft.network/networksecuritygroups" and not(partial)
| where name =~ queryNSGName
| top 1 by timestamp desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryNSGName}`

**Signal filters seen in KQL:** `type == "microsoft.network/networksecuritygroups"`

---

## Current Rules

### NSG Security Rules

_Widget purpose:_ Security Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `NSG > Current Rules > Current Rules > Security Rules`

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

## NSG Updates

### NSG Updates

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `NSG > NSG Updates`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where isnotempty(queryNSGName) and (SubscriptionId == querySubscriptionId and ResourceGroup =~ queryResourceGroupName and HttpMethod != "GET")
| where (ResourceType == "networkSecurityGroups" and ResourceName == queryNSGName) or (ResourceType == "securityRules")
| where ResourceType in ("networkSecurityGroups", "securityRules")
| extend StartTime = todatetime(StartTime)
| extend Content = case(
    ResourceType == "networkSecurityGroups", OperationName, 
    strcat(OperationName, " - ", ResourceName)
) 
| project-reorder ResourceGroup, ResourceName, HttpMethod, OperationName, ResourceType
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryNSGName}`, `{queryFrom}`, `{queryTo}`

---

## Snapshots

### Graph NSG Snapshots

_Widget purpose:_ NSG Snapshots (ARG)

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `NSG > Snapshots > Snapshots > NSG Snapshots (ARG)`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where (isempty(queryHintTime) and timestamp > (queryFrom - 5d)) 
    or timestamp between(datetime_add('day', 1, queryHintTime) .. datetime_add('hour', 6, queryHintTime))
| where name =~ queryName and resourceGroup =~ queryResourceGroupName
| where subscriptionId =~ querySubscriptionId and type == "microsoft.network/networksecuritygroups"
| where not(partial)
| extend JSON = properties
| extend provisioningState = JSON.provisioningState
| extend resourceGuid = JSON.resourceGuid
| order by timestamp desc
// because we are descending, we need next instead
| extend PreviousJSON = next(properties)
| project-away properties
| project-reorder timestamp, deleted, source, provisioningState, type, rowId
| where strlen(tostring(JSON)) != strlen(tostring(PreviousJSON))
```

**Params:** `{queryName}`, `{queryResourceGroupName}`, `{querySubscriptionId}`, `{queryHintTime}`, `{queryFrom}`

---
