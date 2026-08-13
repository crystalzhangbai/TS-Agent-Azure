# (top-level)

> Source: **Network Manager - Nic Interfaces (Merlin)** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Nic Interfaces (Merlin)"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
NetworkServiceManagerEvents
| where TIMESTAMP > local_StartTime - 1d
| where Message contains local_NicId
| where TaskName in ('LogMerlinNetworkInterfaceInstanceConfigAddToPublish', 'LogMerlinNotificationHandled', 'LogNetworkInterfacePersistedForContainerInterface') 
| project 
    TIMESTAMP,
    Region,
    Tenant,
    data1 = extract_all('containerInterfaceId="(.*?)" bladeId="(.*?)".*NetworkInterfaceId\\\\": (.*?),', Message)[0],
    data2 = extract_all('Received NIC list for container with VmUniqueId: (.*), Expected NIC list: (.*)"', Message)[0],
    data3 = iff(TaskName  == 'LogNetworkInterfacePersistedForContainerInterface', extract('containerInterfaceId="(.*)"', 1, Message) , '')
| where isnotempty(data1) or isnotempty(data2) or isnotempty(data3)
| project 
    Region,
    Tenant,
    PublishedData = tostring(pack ("Published_Timestamp", TIMESTAMP, "Published_ContainerInterfaceId", tostring(data1[0]), "Published_BladeId",tostring(data1[1]) , "Published_NicId", tostring(data1[2]))),
    ExpectedData = tostring(pack ("Expected_Timestamp", TIMESTAMP, "Expected_VmId", tostring(data2[0]), "Expected_Nics",  tostring(data2[1]))),
    PersistedData = tostring(pack ("Persisted_Timestamp", TIMESTAMP, "Persisted_ContainerInterfaceId",  tostring(data3))),
    ContentSelector = case (
                        isnotempty(tostring(data1[0])), 0,
                        isnotempty(tostring(data2[0])), 1,
                        2)
| summarize 
    PublishedData = todynamic(anyif(PublishedData, ContentSelector == 0)), 
    ExpectedData = todynamic(anyif(ExpectedData, ContentSelector == 1)), 
    PersistedData = todynamic(anyif(PersistedData, ContentSelector == 2)),
    Region = any(Region),
    Tenant = any(Tenant)
| project data = bag_merge(PublishedData, ExpectedData, PersistedData), Region, Tenant
| project 
    todatetime(data.Published_Timestamp),
    tostring(data.Published_NicId),
    tostring(data.Published_ContainerInterfaceId),
    tostring(data.Published_BladeId),
    tostring(data.Published_NicId),
    todatetime(data.Expected_Timestamp),
    tostring(data.Expected_VmId),
    tostring(data.Expected_Nics),
    todatetime(data.Persisted_Timestamp),
    tostring(data.Persisted_ContainerInterfaceId),
    Region,
    Tenant
```

**Params:** `{local_NicId}`, `{local_StartTime}`

---
