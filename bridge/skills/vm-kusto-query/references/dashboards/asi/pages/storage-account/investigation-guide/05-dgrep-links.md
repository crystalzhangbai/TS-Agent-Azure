# DGrep Links

> Source: **Storage Account Investigation Guide** dashboard, chapter **DGrep Links** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## DGrep Links

### Get Tenant RSRP name

_Widget purpose:_ DGrep Links

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Single` · Widget: `Card`
Source panel: `DGrep Links > DGrep Links`

```kusto
cluster('xstore.kusto.windows.net').database('xstore').GetTenantCatalogLatest()
| where Tenant == tenant
| project Tenant, MDMShoeboxAccountName,MonitoringGcsStorageResourceTagValue,RsrpName
// if Region not found, retuns empty line, instead of ASI exception
| union (       
    print Tenant="", MDMShoeboxAccountName="",MonitoringGcsStorageResourceTagValue="",RsrpName=""
)
| sort by Tenant nulls last
| limit 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{tenant}`

---

### Storage_Regions

_Widget purpose:_ DGrep Links

Cluster: `azcore.centralus` · Database: `Xstore` · Type: `Single` · Widget: `Card`
Source panel: `DGrep Links > DGrep Links`

```kusto
// Any cluster / Database can be used - using the same as to get Redis details - supportrptwus3prod.westus3 / KPISupportData
let RegionMap = case(
location_withoutSpace == "apacsoutheast2", "APAC Southeast 2",
location_withoutSpace == "australiacentral", "Australia Central",
location_withoutSpace == "australiacentral2", "Australia Central 2",
location_withoutSpace == "australiaeast", "Australia East",
location_withoutSpace == "australiasoutheast", "Australia Southeast",
location_withoutSpace == "austriaeast", "Austria East",
location_withoutSpace == "belgiumcentral", "Belgium Central",
location_withoutSpace == "brazilsouth", "Brazil South",
location_withoutSpace == "brazilsoutheast", "Brazil Southeast",
location_withoutSpace == "canadacentral", "Canada Central",
location_withoutSpace == "canadaeast", "Canada East",
location_withoutSpace == "centralindia", "Central India",
location_withoutSpace == "centralus", "Central US",
location_withoutSpace == "centraluseuap", "Central US EUAP",
location_withoutSpace == "chilecentral", "Chile Central",
location_withoutSpace == "denmarkeast", "Denmark East",
location_withoutSpace == "eastasia", "East Asia",
location_withoutSpace == "eastus", "East US",
location_withoutSpace == "eastus2", "East US 2",
location_withoutSpace == "eastus2euap", "East US 2 EUAP",
location_withoutSpace == "francecentral", "France Central",
location_withoutSpace == "francesouth", "France South",
location_withoutSpace == "germanycentral", "Germany Central",
location_withoutSpace == "germanynortheast", "Germany Northeast",
location_withoutSpace == "germanynorth", "Germany North",
location_withoutSpace == "germanywestcentral", "Germany West Central",
location_withoutSpace == "indonesiacentral", "Indonesia Central",
location_withoutSpace == "indiacentral", "India Central",
location_withoutSpace == "indiasouthcentral", "India South Central",
location_withoutSpace == "israelcentral", "Israel Central",
location_withoutSpace == "israelnorthwest", "Israel Northwest",
location_withoutSpace == "italynorth", "Italy North",
location_withoutSpace == "japaneast", "Japan East",
location_withoutSpace == "japanwest", "Japan West",
location_withoutSpace == "jioindiacentral", "Jio India Central",
location_withoutSpace == "jioindiawest", "Jio India West",
location_withoutSpace == "koreacentral", "Korea Central",
location_withoutSpace == "koreasouth", "Korea South",
location_withoutSpace == "malaysiasouth", "Malaysia South",
location_withoutSpace == "malaysiawest", "Malaysia West",
location_withoutSpace == "mexicocentral", "Mexico Central",
location_withoutSpace == "newzealandnorth", "New Zealand North",
location_withoutSpace == "northcentralus", "North Central US",
location_withoutSpace == "northeurope", "North Europe",
location_withoutSpace == "norwayeast", "Norway East",
location_withoutSpace == "norwaywest", "Norway West",
location_withoutSpace == "polandcentral", "Poland Central",
location_withoutSpace == "qatarcentral", "Qatar Central",
location_withoutSpace == "southafricanorth", "South Africa North",
location_withoutSpace == "southafricawest", "South Africa West",
location_withoutSpace == "southcentralus", "South Central US",
location_withoutSpace == "southcentralus2", "South Central US 2",
location_withoutSpace == "southeastasia", "Southeast Asia",
location_withoutSpace == "southeastus5", "Southeast US 5",
location_withoutSpace == "southindia", "South India",
location_withoutSpace == "spaincentral", "Spain Central",
location_withoutSpace == "swedencentral", "Sweden Central",
location_withoutSpace == "swedensouth", "Sweden South",
location_withoutSpace == "switzerlandnorth", "Switzerland North",
location_withoutSpace == "switzerlandwest", "Switzerland West",
location_withoutSpace == "taiwannorth", "Taiwan North",
location_withoutSpace == "taiwannorthwest", "Taiwan Northwest",
location_withoutSpace == "uaecentral", "UAE Central",
location_withoutSpace == "uaenorth", "UAE North",
location_withoutSpace == "uknorth", "UK North",
location_withoutSpace == "uksouth", "UK South",
location_withoutSpace == "uksouth2", "UK South 2",
location_withoutSpace == "ukwest", "UK West",
location_withoutSpace == "westcentralus", "West Central US",
location_withoutSpace == "westeurope", "West Europe",
location_withoutSpace == "westindia", "West India",
location_withoutSpace == "westus", "West US",
location_withoutSpace == "westus2", "West US 2",
location_withoutSpace == "westus3", "West US 3",
"UNKNOWN REGION"
);
print AltRegion=RegionMap
```

**Params:** `{location_withoutSpace}`

---
