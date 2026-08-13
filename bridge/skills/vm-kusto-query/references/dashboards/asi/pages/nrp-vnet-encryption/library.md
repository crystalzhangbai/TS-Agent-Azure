# NRP — Vnet Encryption: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.920Z.
> Total: 17 unique KQL queries across 17 panels (17 widget refs).

## Page inputs (URL params)


## Panels

### (RNM Stack) Get Expected Nic Flag
Path: `(RNM Stack) Get Expected Nic Flag`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RNM Get Expected Nic Flag | Table | https://nrp | mdsnrp | startTime, endTime, region |

### ARM Incoming Requests
Path: `ARM Incoming Requests`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM Incoming Requests | Table | https://armprod | ARMProd | region, startTime, endTime |

### Avg Time Taken To Read VNet
Path: `Avg Time Taken To Read VNet`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Avg Time Taken To Read VNet | TimeSeries | https://nrp/ | mdsnrp | region, startTime, endTime |

### Get Expected Nic Flag
Path: `Get Expected Nic Flag`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Expected Nic Flag | Table | https://nrp | mdsnrp | region, startTime, endTime |

### Get Tenant Cluster Request
Path: `Get Tenant Cluster Request`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IfEncryptionRequiredInGetTenantCluster | Table | https://nrp | mdsnrp | region, startTime, endTime |

### If Put Encrypted Vnet Request Comes from ARM Template Deployment
Path: `If Put Encrypted Vnet Request Comes from ARM Template Deployment`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ifFromARM | Table | https://nrp/ | mdsnrp | startTime, endTime |

### NRP and Control Path Runner Succeed Rate
Path: `NRP and Control Path Runner Succeed Rate`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RunnerSucceed | Table | aznwsdn | aznwmds | region, startTime, endTime |

### Peering Failure Due To Old Api Version
Path: `Peering Failure Due To Old Api Version`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PeeringFailureDueToOldApi | Table | https://nrp/ | mdsnrp | region, startTime, endTime |

### Put EncryptedVnet Request Traffic
Path: `Put EncryptedVnet Request Traffic`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | put vnet traffic | TimeSeries | https://nrp/ | mdsnrp | region, startTime, endTime |

### Put EncryptedVnet SuccessOrError
Path: `Put EncryptedVnet SuccessOrError`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IfPutVnetWithEncryptionSucceeded | Table | https://nrp | mdsnrp | region, startTime, endTime |

### Put Vnet Encryption Call Outside Supported Regions
Path: `Put Vnet Encryption Call Outside Supported Regions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | callOutsideSupportedRegions | Table | https://nrp | mdsnrp | startTime, endTime |

### Returned Clusters List when Encryption Capable Cluster is Required
Path: `Returned Clusters List when Encryption Capable Cluster is Required`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | clustersList | Table | https://nrp/ | mdsnrp | startTime, endTime |

### Runner Sub Failure in CRP logs
Path: `Runner Sub Failure in CRP logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | runnerErrorInCRP | Table | https://azcrp | crp_allprod | region, startTime, endTime |

### Runner Sub Failure in NRP logs
Path: `Runner Sub Failure in NRP logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | runner sub  | Table | https://nrp | mdsnrp | region, startTime, endTime |

### SupportVNetEncryptionFeature Setting
Path: `SupportVNetEncryptionFeature Setting`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SupportVNetEncryptionFeature | Table | https://nrp | mdsnrp | region |

### SupportVNetEncryptionOnRNMStack  Setting
Path: `SupportVNetEncryptionOnRNMStack  Setting`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SupportVNetEncryptionOnRNMStack  | Table | https://nrp | mdsnrp | region |

### ValidateEncryptionBasedOnVMSizeOnly Setting 
Path: `ValidateEncryptionBasedOnVMSizeOnly Setting `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ValidateEncryptionBasedOnVMSizeOnly | Table | https://nrp | mdsnrp | region |
