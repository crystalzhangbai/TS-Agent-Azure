# RdAgent Tables

> Source: **Azure Host — Azure Host Node** dashboard, chapter **RdAgent Tables** (5 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VMAL Container Operations

### Azure Host VMAL Container Operations

_Widget purpose:_ VmServiceContainerOperations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `RdAgent Tables > VMAL Container Operations > VMAL Container Operations > VmServiceContainerOperations`

```kusto
VmServiceContainerOperations
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage,  ContainerSize, ResultCode, DurationMillis
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VMAL Disk Lease Operations

### Azure Host VmServiceLeaseManagementOperation

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `RdAgent Tables > VMAL Disk Lease Operations > VMAL Disk Lease Operations`

```kusto
VmServiceLeaseManagementOperation
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, BlobPath, Operation, ExistingLease, NewLease, ResultCode, LocalFileName
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VMAL Disk Operations

### Azure Host VMAL Disk Service Table

_Widget purpose:_ VmServiceVirtualDiskOperations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `RdAgent Tables > VMAL Disk Operations > VMAL Disk Operations > VmServiceVirtualDiskOperations`

```kusto
VmServiceVirtualDiskOperations
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage,  DiskType, DiskFullPath, DiskBackingStore, ResultCode, DurationMillis, DiskLocation
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VMAL Service Events

### Azure Host VmServiceEventsEtwTable

_Widget purpose:_ VmServiceEventsEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `RdAgent Tables > VMAL Service Events > VMAL Service Events > VmServiceEventsEtwTable`

```kusto
VmServiceEventsEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ContainerId, Context, AgentPackage, Message
| sort by PreciseTimeStamp
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VMAL Service Init

### Azure Host VMAL Service Init

_Widget purpose:_ VmServiceInitialization

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `RdAgent Tables > VMAL Service Init > VMAL Service Init > VmServiceInitialization`

```kusto
VmServiceInitialization
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, Operation, Stage, ResultCode, ServiceMode, VhdProvider, SerialNumber, DiskPreparation, StorageType
| sort by PreciseTimeStamp
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
