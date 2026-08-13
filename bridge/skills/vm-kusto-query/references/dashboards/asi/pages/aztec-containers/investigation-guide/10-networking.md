# Networking

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Networking** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Networking Links

### Get Container Info

_Widget purpose:_ Networking Links

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Single` · Widget: `Card`
Source panel: `Networking > Networking Links`

```kusto
// mapping region names to their vfp mdm accounts for dashboard links
// https://msazure.visualstudio.com/One/_git/Networking-nfv?path=%2Fsrc%2Fgateway%2FGatewayTenant%2FGatewayTenantCore%2FExpressRoute%2FVfpMdmAccountNameReader.cs&_a=contents&version=GBdevelop2
let vfpMdmAccounts = datatable(Region: string, vfpMdmAccount: string) [
    "eastus2euap", "VfpMdmBN",
    "centraluseuap", "VfpMdmDM",
    "japanwest", "VfpMdmOS",
    "southcentralus", "VfpMdmSN",
    "australiaeast", "VfpMdmSY",
    "eastus2", "VfpMdmBN",
    "westcentralus", "VfpMdmCY",
    "northcentralus", "VfpMdmCH",
    "westeurope", "VfpMdmAM",
    "eastus", "VfpMdmBL",
    "qatarc", "VfpMdmqatarcentral",
    "qatarcentral", "VfpMdmqatarcentral",
    "uaecentral", "VfpMdmAUHDXB",
    "southeastasia", "VfpMdmSG",
    "westus", "VfpMdmBY",
    "northeurope", "VfpMdmDB",
    "australiasoutheast", "VfpMdmML",
    "uksouth", "VfpMdmLN",
    "brazilsouth", "VfpMdmCQ",
    "polandcentral", "VfpMdmpolandcentral",
    "eastasia", "VfpMdmHKN",
    "westus2", "VfpMdmMWH",
    "norwayeast", "VfpMdmOSL",
    "westus3", "VfpMdmwestus3",
    "centralus", "VfpMdmDM",
    "switzerlandnorth", "VfpMdmZRH",
    "koreacentral", "VfpMdmSE",
    "japaneast", "VfpMdmKWTY",
    "ukwest", "VfpMdmCW",
    "francesouth", "VfpMdmMRS",
    "germanywestcentral", "VfpMdmFRA",
    "centralindia", "VfpMdmPN",
    "uaenorth", "VfpMdmAUHDXB",
    "southafricawest", "VfpMdmJNBCPT",
    "germanynorth", "VfpMdmBER",
    "westindia", "VfpMdmBM",
    "southindia", "VfpMdmMA",
    "francecentral", "VfpMdmPAR",
    "jioindiawest", "VfpMdmjioindiawest",
    "norwaywest", "VfpMdmSVG",
    "australiacentral", "VfpMdmCBR",
    "canadacentral", "VfpMdmYT",
    "brazilsoutheast", "VfpMdmBrazilSoutheast",
    "southafricanorth", "VfpMdmJNBCPT",
    "koreasouth", "VfpMdmPS",
    "swedensouth", "VfpMdmswedensouth",
    "canadaeast", "VfpMdmYQ",
    "jioindiacentral", "VfpMdmjioindiacentral",
    "swedencentral", "VfpMdmswedencentral",
    "switzerlandwest", "VfpMdmGVA",
    "eastusslv", "VfpMdmeastusslv",
    "eastusstg", "VfpMdmUSSTAGEE",
    "uknorth", "VfpMdmMM",
    "uksouth2", "VfpMdmLO",
    "usgovvirginia", "VfpMdmFF",
    "usgoviowa", "VfpMdmFF",
    "usdodcentral", "VfpMdmFF",
    "usdodeast", "VfpMdmFF",
    "usgovtexas", "VfpMdmFF",
    "usgovarizona", "VfpMdmFF",
    "chinanorth", "VfpMdmMC",
    "chinaeast", "VfpMdmMC",
    "chinaeast2", "VfpMdmMC",
    "chinanorth2", "VfpMdmMC",
    "chinanorth3", "VfpMdmMC",
    "chinaeast3", "VfpMdmMC",
    "germanycentral", "VfpMdmBF",
    "germanynortheast", "VfpMdmBF",
    "usseceast", "VfpMdmUSSec",
    "ussecwest", "VfpMdmUSSec",
    "usnateast", "VfpMdmUSNat",
    "usnatwest", "VfpMdmUSNat"
];
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where containerId == qContainer
| take 1
| project containerId, Tenant, nodeId, tenantName, virtualMachineUniqueId, roleInstanceName, RegionFriendlyName, queryFrom, queryTo
| join kind=leftouter (vfpMdmAccounts) on $left.RegionFriendlyName == $right.Region
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qContainer}`

---

## NM Agent Health (1 is Health)

### Container NMAgent

_Widget purpose:_ NM Agent Health (1 is Health)

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Networking > NM Agent Health (1 is Health)`

```kusto
let metricNamespace = "NMAgent";
let metric = "VM Availability";
let dimensions = "'Cluster', 'NodeId', 'ContainerId', 'EventSource'";
let samplingType = "NullableAverage";
let eventSourceFilter = "'NMAGENT_PORT_STATE','NMAGENT_PORT_PROGRAMMING','NMAGENT_DS_MAPPING','NMAGENT_MAPPING_SYNC'";
let query = strcat("| where ContainerId == '", queryContainerId,"' | where EventSource in (", eventSourceFilter,") | top 40 by Avg(NullableAverage) desc");
let request = strcat("metricNamespace('", metricNamespace,"').metric('", metric,"').dimensions(", dimensions,").samplingTypes('", samplingType,"') ", query);
let theSchema = datatable (EventSource:string, TimestampUtc:datetime, NullableAverage:double) [];
let metrics = evaluate geneva_metrics_request(
 "VNetMDMNorthEurope",
 request,
 queryFrom,
 queryTo
);
union theSchema, metrics
| project Timestamp = TimestampUtc, EventSource, NullableAverage
| summarize Avg = avg(NullableAverage) by EventSource, bin(Timestamp, 10m)
```

**Params:** `{queryContainerId}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `ContainerId == "", queryContainerId,""`

---
