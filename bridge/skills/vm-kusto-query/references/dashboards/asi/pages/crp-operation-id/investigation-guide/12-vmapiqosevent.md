# VMApiQosEvent

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **VMApiQosEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VMApiQosEvent

### OperationId VMApiQosEvent GET

_Widget purpose:_ VMApiQosEvent - operationId {{operationId}}

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `VMApiQosEvent > VMApiQosEvent > VMApiQosEvent - operationId {{operationId}}`

```kusto
let adjustedStart = datetime_add('hour', -6, local_startDate);
let adjustedEnd = datetime_add('hour', 6, local_endDate);
VMApiQosEvent
| where PreciseTimeStamp between (adjustedStart .. adjustedEnd)
| where operationId =~ local_operationId
| project allocationAction, availabilitySet, availabilitySetKind, extraVMProperties, fabricCluster, fabricTenantName, 
    galleryImage, isManaged, networkSpineIds, oSDiskStorageAccountType, oSProvisionDurationInSeconds, oSType, physicalAvailablityZone, 
    platformImage, preprovisionedVMReuse, proximityPlacementGroup , userVMImage, vMId, vMSize, operationName, errorDetails, resourceName
```

**Params:** `{local_operationId}`, `{local_endDate}`, `{local_startDate}`

---
