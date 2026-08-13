# (top-level)

> Source: **NRP - DeleteTenantOperation without Lock in Sync Part- Analysis** dashboard, chapter **(top-level)** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### delete tenant perf improvement enabled

_Widget purpose:_ DeleteTenant Perf Improvement Enabled

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
let f1=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where OperationName == "DeleteTenantOperation"
| where SliceNum(SourceAssemblyFileVersion) < 10
| where EventCode == "BackgroundTaskRequestValidationEnd"
| summarize by Region, ReleaseBuild=ReleaseBuild(SourceAssemblyFileVersion, IgnoreBuild=true);
f1
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `OperationName == "DeleteTenantOperation"` · `EventCode == "BackgroundTaskRequestValidationEnd"`

---

### ExistingVsNewDeleteTenantPerf

_Widget purpose:_ Existing Vs New Behavior Sync Part Performance

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
let f1=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where EventCode == "BackgroundTaskRequestValidationEnd"
| take 10000
| summarize make_set(OperationId);
let bgTaskWithValidation = QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where BackgroundTaskQos == true
| where Success == true
| where OperationId in (f1)
| extend behavior = "newBehavior"
| summarize dcount(OperationId), max(SynchronousDurationInMilliseconds), avg(SynchronousDurationInMilliseconds), percentiles(SynchronousDurationInMilliseconds, 50, 75, 90, 99.9) by behavior;
let existingBehavior = QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where BackgroundTaskQos == true
| where Success == true
| where OperationId !in (f1)
| project OperationId, SynchronousDurationInMilliseconds
| take 10000
| extend behavior = "existingBehavior"
| summarize dcount(OperationId), max(SynchronousDurationInMilliseconds), avg(SynchronousDurationInMilliseconds), percentiles(SynchronousDurationInMilliseconds, 50, 75, 90, 99.9) by behavior
| union bgTaskWithValidation
;
existingBehavior
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`, `{querySubscription}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `OperationName == "DeleteTenantOperation"` · `EventCode == "BackgroundTaskRequestValidationEnd"`

---

### Already Deleted Tenants Sync Time

_Widget purpose:_ Already Deleted Tenants Performance

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
let f1=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where EventCode == "TenantAlreadyDeleted"
| take 10000
| summarize make_set(OperationId);
let tenantAlreadyDeleted = QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where BackgroundTaskQos != true
| where Success == true
| where OperationId in (f1)
| extend behavior = "newBehavior"
| summarize dcount(OperationId),  max(DurationInMilliseconds), avg(DurationInMilliseconds), percentiles(DurationInMilliseconds, 50, 75, 90, 99.9) by behavior;
let f2=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where Message endswith "already deleted."
| take 10000
| summarize make_set(OperationId);
let existingBehavior = QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where BackgroundTaskQos != true
| where Success == true
| where OperationId in (f2)
| extend behavior = "existingBehavior"
| summarize dcount(OperationId), max(DurationInMilliseconds), avg(DurationInMilliseconds), percentiles(DurationInMilliseconds, 50, 75, 90, 99.9) by behavior
| union tenantAlreadyDeleted
;
existingBehavior
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `EventCode == "TenantAlreadyDeleted"` · `OperationName == "DeleteTenantOperation"` · `Message endswith "already deleted."`

---

### Count of Tenants Already Deleted

_Widget purpose:_ Already Deleted Tenant Logical Timstamp Info

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
let f1=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where EventCode == "TenantAlreadyDeleted"
| where Message startswith "New LogicalTimestampResource was added for tenant "
| summarize count();
let f2=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where EventCode == "TenantAlreadyDeleted"
| extend newTs = Message startswith "LogicalTimestampResource already exists for a deleted tenant" // if already exists, could be equal to exisiing saved value or greater. See table 3 for how many greater
| summarize make_set(OperationId);
let f3=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where OperationId in (f2)
| where Message endswith " - allow operation to proceed"
| where Message contains "is less than current "
| parse Message with "Latest logical timestamp "tsSavedInkvs" for tenant "tenant" is less than current "incomingTs" - allow operation to proceed"
| project Message, tsSavedInkvs, incomingTs
| summarize count() by incomingTimestampGreaterThanExisting = (toint(tsSavedInkvs) < toint(incomingTs)), incomingTimestampEqualToExisting = (toint(tsSavedInkvs) == toint(incomingTs))
| union f1
| extend logicalTimestamp = iff (incomingTimestampEqualToExisting, "incomingTimestampEqualToExisting", iff (incomingTimestampGreaterThanExisting, "incomingTimestampGreaterThanExisting", "timestampDoesntExistSoCreatedNewOne"))
| project logicalTimestamp, count_
;f3
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegion}`, `{querySubscription}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `OperationName == "DeleteTenantOperation"` · `EventCode == "TenantAlreadyDeleted"` · `Message startswith "New LogicalTimestampResource was added for tenant "` · `Message endswith " - allow operation to proceed"` · `Message contains "is less than current "`

---

### Errors for Tenants Already Deleted

_Widget purpose:_ Errors when Tenant Already Deleted

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `Table`

```kusto
// Errors returned when tenant already deleted
let f1=FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where EventCode == "TenantAlreadyDeleted"
| summarize make_set(OperationId);
QosEtwEvent
| where TIMESTAMP between (queryFrom ..queryTo )
| where queryRegion == "*" or Region == queryRegion
| where querySubscription == "*" or SubscriptionId == querySubscription
| where OperationName == "DeleteTenantOperation"
| where Success != true
| where OperationId in (f1)
| project TIMESTAMP, ErrorCode, ErrorDetails, OperationId, CorrelationRequestId, Region, BackgroundTaskQos
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryRegion}`

**Signal filters seen in KQL:** `queryRegion == "*"` · `querySubscription == "*"` · `OperationName == "DeleteTenantOperation"` · `EventCode == "TenantAlreadyDeleted"`

---
