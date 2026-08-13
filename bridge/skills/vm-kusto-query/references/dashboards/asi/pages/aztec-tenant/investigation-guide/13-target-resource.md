# Target Resource

> Source: **Aztec — Tenant** dashboard, chapter **Target Resource** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Locate Resource by Tenant Name

_Widget purpose:_ Target Resource

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Target Resource`

```kusto
let vmssTenant = VmssVMApiQosEvent
| where fabricTenantName == queryFabricTenantName
| extend resourceGroupName = tolower(resourceGroupName)
| extend resourceName = tolower(resourceName)
| distinct subscriptionId, resourceGroupName, vMScaleSetName
| extend armId = strcat("/subscriptions/",subscriptionId, "/resourceGroups/", resourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/", vMScaleSetName)
| extend resourceType = "VMSS";
let vmTenant = VMApiQosEvent
| where fabricTenantName == queryFabricTenantName
| where availabilitySetKind != "VMScaleSet"
| extend resourceGroupName = tolower(resourceGroupName)
| extend resourceName = tolower(resourceName)
| distinct subscriptionId, resourceGroupName, resourceName, vMId
| extend armId = strcat("/subscriptions/",subscriptionId, "/resourceGroups/", resourceGroupName, "/providers/Microsoft.Compute/virtualMachines/", resourceName)
| extend resourceType = "VM";
let csesTenant = cluster("Azcrp").database("vsmprod").ApiQosEvent
| where fabricTenantName == queryFabricTenantName
| extend resourceGroupName = tolower(resourceGroupName)
| extend resourceName = tolower(resourceName)
| distinct subscriptionId, resourceGroupName, resourceName
| extend armId = strcat("/subscriptions/",subscriptionId, "/resourceGroups/", resourceGroupName, "/providers/Microsoft.Compute/cloudServices/", resourceName)
| extend resourceType = "CSES";
union vmssTenant, vmTenant, csesTenant
| order by armId asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFabricTenantName}`

**Signal filters seen in KQL:** `availabilitySetKind != "VMScaleSet"`

---
