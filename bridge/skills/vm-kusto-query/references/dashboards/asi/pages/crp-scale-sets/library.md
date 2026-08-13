# CRP — Scale Sets: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:29:25.317Z.
> Total: 16 unique KQL queries across 9 panels (16 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 8

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Scale Sets" | ResourceGet | azcrpbifollower | bi_allprod | local_resourceGroupName, local_subscriptionId, local_VMScaleSetId, local_vmssName, globalFrom, globalTo |
| 2 | Find OS Prov Failures | IssueDetector | azcrpbifollower | bi_allprod | qFrom, qTo, qSub, qRG, qVMSS |
| 3 | Query SF Extension  | Single | azcrpbifollower | bi_allprod | queryFrom, queryTo, queryResourceGroup, querySubId, queryVmssName, queryParam5 |
| 4 | Locate SF Cluster  | Single | sflogs | SFRP | queryFrom, queryTo, queryVmssArmId |
| 5 | VMSS Request Deltas | Timeline | azcrp | crp_allprod | querySubscriptionId, queryResourceGroupName, queryScaleSetName, queryFrom, queryTo |
| 6 | VMSS State | Timeline | azcrpbifollower | bi_allprod | qFrom, qTo, qRG, qSub, qVMSS |
| 7 | VMSS Operations | Timeline | azcrp | crp_allprod | qFrom, qTo, qRG, qSub, qVMSS |
| 8 | Query ResourceHealthAzureActivityLogEvent | Table | icmbrain | AzureResourceHealth | queryFrom, queryTo, queryResourceId, querySubId |

### Extension Provisioning Failures
Path: `Extension Provisioning Failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ScaleSet Extension Failures | Table | azcrp | crp_allprod | qFrom, qTo, qSub, qVMSS |

### Fabric Placements
Path: `Fabric Placements`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FabricPlacements | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryVmssUniqueId |

### Insights
Path: `Insights`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetVMSSImpactEvents | Table | Azcrp | crp_allprod | querySubId, queryResourceGroupName, queryVmssName, queryBegin, queryEnd |

### Ocular > Ocular > Control Plane Traces
Path: `Ocular > Ocular > Control Plane Traces`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Ocular Summary Logs with Resource Name | CoBeTimeline | ocularcentralus.centralus | FunctionDB | querySubscriptionId, queryResourceGroupName, queryResourceName, queryFrom, queryTo |

### Requests
Path: `Requests`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS Requests | Table | azcrp | crp_allprod | querySubscriptionId, queryResourceGroupName, queryScaleSetName, queryFrom, queryTo |

### VMs > Instance Details > Sale Set Instances
Path: `VMs > Instance Details > Sale Set Instances`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query VMSS Instance from BI | Table | azcrpbifollower | bi_allprod | querySubscriptionId, queryResourceGroup, queryVmssName, queryFrom, queryTo |

### VMs > Instance Health > Instance Health
Path: `VMs > Instance Health > Instance Health`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Scaleset instance health | Timeline | azcrpbifollower | bi_allprod | qFrom, qTo, qSub, qRG, qVMSS |

### VMSS Extensions
Path: `VMSS Extensions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query VMSS Extensions | Table | azcrpbifollower | bi_allprod | queryFrom, queryTo, querySubId, queryResourceGroup, queryVmssName |
