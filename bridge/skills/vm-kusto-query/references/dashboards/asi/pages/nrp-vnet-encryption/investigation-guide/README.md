# NRP - Vnet Encryption — Investigation Guide

Chapter-keyed reference derived from the **NRP - Vnet Encryption** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(RNM Stack) Get Expected Nic Flag](01-rnm-stack-get-expected-nic-flag.md) — 1 queries
- [ARM Incoming Requests](02-arm-incoming-requests.md) — 1 queries
- [Avg Time Taken To Read VNet](03-avg-time-taken-to-read-vnet.md) — 1 queries
- [Get Expected Nic Flag](04-get-expected-nic-flag.md) — 1 queries
- [Get Tenant Cluster Request](05-get-tenant-cluster-request.md) — 1 queries
- [If Put Encrypted Vnet Request Comes from ARM Template Deployment](06-if-put-encrypted-vnet-request-comes-from-arm-template-deployment.md) — 1 queries
- [NRP and Control Path Runner Succeed Rate](07-nrp-and-control-path-runner-succeed-rate.md) — 1 queries
- [Peering Failure Due To Old Api Version](08-peering-failure-due-to-old-api-version.md) — 1 queries
- [Put EncryptedVnet Request Traffic](09-put-encryptedvnet-request-traffic.md) — 1 queries
- [Put EncryptedVnet SuccessOrError](10-put-encryptedvnet-successorerror.md) — 1 queries
- [Put Vnet Encryption Call Outside Supported Regions](11-put-vnet-encryption-call-outside-supported-regions.md) — 1 queries
- [Returned Clusters List when Encryption Capable Cluster is Required](12-returned-clusters-list-when-encryption-capable-cluster-is-required.md) — 1 queries
- [Runner Sub Failure in CRP logs](13-runner-sub-failure-in-crp-logs.md) — 1 queries
- [Runner Sub Failure in NRP logs](14-runner-sub-failure-in-nrp-logs.md) — 1 queries
- [SupportVNetEncryptionFeature Setting](15-supportvnetencryptionfeature-setting.md) — 1 queries
- [SupportVNetEncryptionOnRNMStack  Setting](16-supportvnetencryptiononrnmstack-setting.md) — 1 queries
- [ValidateEncryptionBasedOnVMSizeOnly Setting ](17-validateencryptionbasedonvmsizeonly-setting.md) — 1 queries

**Total queries: 17**

## Query index (by file)

### (RNM Stack) Get Expected Nic Flag

- RNM Get Expected Nic Flag — see [01-rnm-stack-get-expected-nic-flag.md](01-rnm-stack-get-expected-nic-flag.md)

### ARM Incoming Requests

- ARM Incoming Requests — see [02-arm-incoming-requests.md](02-arm-incoming-requests.md)

### Avg Time Taken To Read VNet

- Avg Time Taken To Read VNet — see [03-avg-time-taken-to-read-vnet.md](03-avg-time-taken-to-read-vnet.md)

### Get Expected Nic Flag

- Get Expected Nic Flag — see [04-get-expected-nic-flag.md](04-get-expected-nic-flag.md)

### Get Tenant Cluster Request

- IfEncryptionRequiredInGetTenantCluster — see [05-get-tenant-cluster-request.md](05-get-tenant-cluster-request.md)

### If Put Encrypted Vnet Request Comes from ARM Template Deployment

- ifFromARM — see [06-if-put-encrypted-vnet-request-comes-from-arm-template-deployment.md](06-if-put-encrypted-vnet-request-comes-from-arm-template-deployment.md)

### NRP and Control Path Runner Succeed Rate

- RunnerSucceed — see [07-nrp-and-control-path-runner-succeed-rate.md](07-nrp-and-control-path-runner-succeed-rate.md)

### Peering Failure Due To Old Api Version

- PeeringFailureDueToOldApi — see [08-peering-failure-due-to-old-api-version.md](08-peering-failure-due-to-old-api-version.md)

### Put EncryptedVnet Request Traffic

- put vnet traffic — see [09-put-encryptedvnet-request-traffic.md](09-put-encryptedvnet-request-traffic.md)

### Put EncryptedVnet SuccessOrError

- IfPutVnetWithEncryptionSucceeded — see [10-put-encryptedvnet-successorerror.md](10-put-encryptedvnet-successorerror.md)

### Put Vnet Encryption Call Outside Supported Regions

- callOutsideSupportedRegions — see [11-put-vnet-encryption-call-outside-supported-regions.md](11-put-vnet-encryption-call-outside-supported-regions.md)

### Returned Clusters List when Encryption Capable Cluster is Required

- clustersList — see [12-returned-clusters-list-when-encryption-capable-cluster-is-required.md](12-returned-clusters-list-when-encryption-capable-cluster-is-required.md)

### Runner Sub Failure in CRP logs

- runnerErrorInCRP — see [13-runner-sub-failure-in-crp-logs.md](13-runner-sub-failure-in-crp-logs.md)

### Runner Sub Failure in NRP logs

- runner sub  — see [14-runner-sub-failure-in-nrp-logs.md](14-runner-sub-failure-in-nrp-logs.md)

### SupportVNetEncryptionFeature Setting

- SupportVNetEncryptionFeature — see [15-supportvnetencryptionfeature-setting.md](15-supportvnetencryptionfeature-setting.md)

### SupportVNetEncryptionOnRNMStack  Setting

- SupportVNetEncryptionOnRNMStack  — see [16-supportvnetencryptiononrnmstack-setting.md](16-supportvnetencryptiononrnmstack-setting.md)

### ValidateEncryptionBasedOnVMSizeOnly Setting 

- ValidateEncryptionBasedOnVMSizeOnly — see [17-validateencryptionbasedonvmsizeonly-setting.md](17-validateencryptionbasedonvmsizeonly-setting.md)
