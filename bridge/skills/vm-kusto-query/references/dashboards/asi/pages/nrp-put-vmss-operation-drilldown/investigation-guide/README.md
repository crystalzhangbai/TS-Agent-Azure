# NRP - PUT VMScaleSet Operation drill down — Investigation Guide

Chapter-keyed reference derived from the **NRP - PUT VMScaleSet Operation drill down** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

**How to use:**

1. Identify which dashboard chapter matches what you're investigating.
2. Open the matching section file from the list below.
3. Pick the query whose name / source panel / filter tips match your symptom.
4. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.
5. Execute via the **vm-kusto-query** skill (`kusto_runner.py`) or via the `replay.py` next to this folder (handles param aliases).

**Companion files (in parent folder):**

- `library.json` — canonical machine-readable source of all queries (panel-organized).
- `library.md`   — same content as flat human-readable index.
- `meta.json`    — pageId, totals, ASI URL.

## Files

- [Action categories during Put Vmss for existing resource](01-action-categories-during-put-vmss-for-existing-resource.md) — 1 queries
- [Action categories during PutVmss operation for existing resources](02-action-categories-during-putvmss-operation-for-existing-resources.md) — 1 queries
- [Batch manager resource lock acquisition failures](03-batch-manager-resource-lock-acquisition-failures.md) — 1 queries
- [BatchManager transaction job dequeue times (ms)](04-batchmanager-transaction-job-dequeue-times-ms.md) — 1 queries
- [Put Vmss Compute only updates](05-put-vmss-compute-only-updates.md) — 1 queries
- [PUT Vmss Compute-only updates per region](06-put-vmss-compute-only-updates-per-region.md) — 1 queries
- [Put Vmss latency (ms)](07-put-vmss-latency-ms.md) — 1 queries
- [Put Vmss Latency (P90 ms) by region ](08-put-vmss-latency-p90-ms-by-region.md) — 1 queries
- [Put Vmss operation failures](09-put-vmss-operation-failures.md) — 1 queries
- [Put Vmss resource type read stats](10-put-vmss-resource-type-read-stats.md) — 1 queries
- [Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins](11-put-vmss-sub-lock-duration-ms-cou-vs-non-cou-per-5-mins.md) — 2 queries
- [Put Vmss sub lock for Peregrine scale down](12-put-vmss-sub-lock-for-peregrine-scale-down.md) — 1 queries
- [Put Vmss subscription lock duration (ms) per 5 mins](13-put-vmss-subscription-lock-duration-ms-per-5-mins.md) — 1 queries
- [Put Vmss top 5 errors ](14-put-vmss-top-5-errors.md) — 1 queries
- [Put Vmss transaction stats (KB) per 5 mins](15-put-vmss-transaction-stats-kb-per-5-mins.md) — 1 queries
- [PutVMScaleSet operation failures](16-putvmscaleset-operation-failures.md) — 1 queries
- [PutVmss errors](17-putvmss-errors.md) — 1 queries
- [PutVmss Ipconfigurations reads](18-putvmss-ipconfigurations-reads.md) — 1 queries
- [PutVmss P50 latency (ms) by region](19-putvmss-p50-latency-ms-by-region.md) — 1 queries
- [PutVmss sub lock COU vs Non-COU ms (per 5min)](20-putvmss-sub-lock-cou-vs-non-cou-ms-per-5min.md) — 1 queries
- [PutVmss sub lock duration (ms) by region](21-putvmss-sub-lock-duration-ms-by-region.md) — 1 queries
- [PutVmss sub lock duration for Peregrine vmss downscale](22-putvmss-sub-lock-duration-for-peregrine-vmss-downscale.md) — 1 queries
- [PutVmss Subnet read stats](23-putvmss-subnet-read-stats.md) — 1 queries
- [PutVmss subscription lock ms (per 5min)](24-putvmss-subscription-lock-ms-per-5min.md) — 1 queries
- [PutVmss transaction stats (KB) by region](25-putvmss-transaction-stats-kb-by-region.md) — 1 queries
- [Top 10 impacted subscriptions with error codes](26-top-10-impacted-subscriptions-with-error-codes.md) — 1 queries
- [Top 15 VMSS resources undergoing updates](27-top-15-vmss-resources-undergoing-updates.md) — 1 queries
- [Top 20 Put Vmss Compute-only updates per region](28-top-20-put-vmss-compute-only-updates-per-region.md) — 1 queries
- [Top 5 error stacks](29-top-5-error-stacks.md) — 1 queries

**Total queries: 30**

## Query index (by file)

### Action categories during Put Vmss for existing resource

- PutVmssActionsPerResource — see [01-action-categories-during-put-vmss-for-existing-resource.md](01-action-categories-during-put-vmss-for-existing-resource.md)

### Action categories during PutVmss operation for existing resources

- PutVmssActionsPerSub — see [02-action-categories-during-putvmss-operation-for-existing-resources.md](02-action-categories-during-putvmss-operation-for-existing-resources.md)

### Batch manager resource lock acquisition failures

- BatchManagerResourceLockingTransactionAquisitionFailurePerSub — see [03-batch-manager-resource-lock-acquisition-failures.md](03-batch-manager-resource-lock-acquisition-failures.md)

### BatchManager transaction job dequeue times (ms)

- BatchManagerDequeueJobTimesPerSub — see [04-batchmanager-transaction-job-dequeue-times-ms.md](04-batchmanager-transaction-job-dequeue-times-ms.md)

### Put Vmss Compute only updates

- CoUPerSubscription — see [05-put-vmss-compute-only-updates.md](05-put-vmss-compute-only-updates.md)

### PUT Vmss Compute-only updates per region

- ComputeOnlyUpdatesPerRegion — see [06-put-vmss-compute-only-updates-per-region.md](06-put-vmss-compute-only-updates-per-region.md)

### Put Vmss latency (ms)

- PutVmssLatencyPerSub — see [07-put-vmss-latency-ms.md](07-put-vmss-latency-ms.md)

### Put Vmss Latency (P90 ms) by region 

- PutVmssP90Latency — see [08-put-vmss-latency-p90-ms-by-region.md](08-put-vmss-latency-p90-ms-by-region.md)

### Put Vmss operation failures

- PutVmssFailuresPerSub — see [09-put-vmss-operation-failures.md](09-put-vmss-operation-failures.md)

### Put Vmss resource type read stats

- PutVmssResourceTypeReadStats — see [10-put-vmss-resource-type-read-stats.md](10-put-vmss-resource-type-read-stats.md)

### Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins

- PutVmssLockDurationCouVsNonCOU — see [11-put-vmss-sub-lock-duration-ms-cou-vs-non-cou-per-5-mins.md](11-put-vmss-sub-lock-duration-ms-cou-vs-non-cou-per-5-mins.md)
- PutVmssSubLockCouVsNonCouPerRes — see [11-put-vmss-sub-lock-duration-ms-cou-vs-non-cou-per-5-mins.md](11-put-vmss-sub-lock-duration-ms-cou-vs-non-cou-per-5-mins.md)

### Put Vmss sub lock for Peregrine scale down

- PutVmssSubLockPeregrineScaleDownPerSub — see [12-put-vmss-sub-lock-for-peregrine-scale-down.md](12-put-vmss-sub-lock-for-peregrine-scale-down.md)

### Put Vmss subscription lock duration (ms) per 5 mins

- PutVmssSubLockPerSub — see [13-put-vmss-subscription-lock-duration-ms-per-5-mins.md](13-put-vmss-subscription-lock-duration-ms-per-5-mins.md)

### Put Vmss top 5 errors 

- PutVmssFailurePerRegion — see [14-put-vmss-top-5-errors.md](14-put-vmss-top-5-errors.md)

### Put Vmss transaction stats (KB) per 5 mins

- PutVmssTransactionStatsPerSub — see [15-put-vmss-transaction-stats-kb-per-5-mins.md](15-put-vmss-transaction-stats-kb-per-5-mins.md)

### PutVMScaleSet operation failures

- PutVmssFailuresPerRegion — see [16-putvmscaleset-operation-failures.md](16-putvmscaleset-operation-failures.md)

### PutVmss errors

- PutVmssFailuresPerVmss — see [17-putvmss-errors.md](17-putvmss-errors.md)

### PutVmss Ipconfigurations reads

- PutVmssIpConfigsPerSubRead — see [18-putvmss-ipconfigurations-reads.md](18-putvmss-ipconfigurations-reads.md)

### PutVmss P50 latency (ms) by region

- PutVmssLatencyPerRegion — see [19-putvmss-p50-latency-ms-by-region.md](19-putvmss-p50-latency-ms-by-region.md)

### PutVmss sub lock COU vs Non-COU ms (per 5min)

- PutVmssSubLockCouVsNonCouPerRes — see [20-putvmss-sub-lock-cou-vs-non-cou-ms-per-5min.md](20-putvmss-sub-lock-cou-vs-non-cou-ms-per-5min.md)

### PutVmss sub lock duration (ms) by region

- PutVmssSubLockPerRegion — see [21-putvmss-sub-lock-duration-ms-by-region.md](21-putvmss-sub-lock-duration-ms-by-region.md)

### PutVmss sub lock duration for Peregrine vmss downscale

- PutVmssSubLockPeregrineVmssScaleDown — see [22-putvmss-sub-lock-duration-for-peregrine-vmss-downscale.md](22-putvmss-sub-lock-duration-for-peregrine-vmss-downscale.md)

### PutVmss Subnet read stats

- PutVmssSubnetReadStats — see [23-putvmss-subnet-read-stats.md](23-putvmss-subnet-read-stats.md)

### PutVmss subscription lock ms (per 5min)

- PutVmssSubLockPerResource — see [24-putvmss-subscription-lock-ms-per-5min.md](24-putvmss-subscription-lock-ms-per-5min.md)

### PutVmss transaction stats (KB) by region

- PutVmssTransactionStatsPerRegion — see [25-putvmss-transaction-stats-kb-by-region.md](25-putvmss-transaction-stats-kb-by-region.md)

### Top 10 impacted subscriptions with error codes

- PutVmssFailuresTopSubs — see [26-top-10-impacted-subscriptions-with-error-codes.md](26-top-10-impacted-subscriptions-with-error-codes.md)

### Top 15 VMSS resources undergoing updates

- TopVmssResourcesPerSub — see [27-top-15-vmss-resources-undergoing-updates.md](27-top-15-vmss-resources-undergoing-updates.md)

### Top 20 Put Vmss Compute-only updates per region

- TopPutVmssCouPerRegion — see [28-top-20-put-vmss-compute-only-updates-per-region.md](28-top-20-put-vmss-compute-only-updates-per-region.md)

### Top 5 error stacks

- PutVmssFailureErrorCodes — see [29-top-5-error-stacks.md](29-top-5-error-stacks.md)
