# AKS Troubleshooting Table Schemas

This directory contains JSON schema files for key AKS Kusto database tables used in troubleshooting.

## Storage Location
`table-schema/` (relative to the skill root directory)

## Database Coverage

### AKSmetrics (2 tables)
- **KubePodStatusReason** - Pod status reason metrics
- **KubePodContainerStatusReady** - Container ready status metrics

### AKSinfra (4 tables)
**IMPORTANT**: These tables track **AKS underlay infrastructure**, not customer worker nodes!

Underlay infrastructure consists of:
- Master nodes: Run underlay Kubernetes control plane
- Infra nodes: Run AKS infrastructure services  
- Agent nodes: Run customer control plane (CCP) pods

Tables:
- **ProcessInfo** - Container and process information from underlay nodes
- **UnderlayAuditLogs** - ⚠️ **DEPRECATED / UNAVAILABLE** — Table no longer exists in live AKSinfra database. Schema JSON retained for historical reference only. Do not query this table.
- **UnderlayNodeInfo** - Comprehensive underlay node information (CPU, memory, disk, network, etc.)
- **UnderlayNanny** - Underlay infrastructure remediation logs

### AKSccplogs (15 tables)
Control plane logs and events:
- **KubeAudit** - Kubernetes audit logs
- **KubeAPIServer** - (Note: Not yet fetched, marked as ControlPlaneEventsAll)
- **ControlPlaneEvents** - Shoebox control plane events
- **ControlPlaneEventsNonShoebox** - Non-shoebox control plane events
- **CloudControllerManager** - Cloud controller manager logs
- **ClusterAutoscaler** - Cluster autoscaler logs
- **Etcd** - Etcd logs
- **KubeSystemEvents** - Kube-system namespace events
- **AKSKubeEvents** - AKS Kubernetes events
- **CCPKonnectivityAgent** - CCP Konnectivity agent logs
- **CSIAzureBlobController** - Azure Blob CSI driver logs
- **CSIAzureDiskController** - Azure Disk CSI driver logs
- **CSIAzureFileController** - Azure File CSI driver logs
- **FleetAgentEvents** - Fleet agent events
- **Guard** - Guard (AAD) logs
- **KonnectivityServer** - Konnectivity server logs

### AKSprod (10 tables)
Production cluster management data:
- **FrontEndQoSEvents** - Frontend QoS events
- **AsyncQoSEvents** - Async operation QoS events
- **FrontEndContextActivity** - Frontend context activity with distributed tracing
- **AsyncContextActivity** - Async context activity
- **AutoUpgraderEvents** - Auto-upgrader events
- **AKSAlertmanager** - Alertmanager alerts
- **RemediatorEvent** - Remediator events
- **ManagedClusterSnapshot** - Managed cluster configuration snapshots
- **OutgoingRequestTrace** - Outgoing HTTP request traces
- **AgentPoolSnapshot** - Agent pool configuration snapshots

## Schema Format

Each schema file contains:
- **TableName**: Name of the table
- **Schema**: Comma-separated list of `column:type` pairs
- **DatabaseName**: Source database name
- **Folder**: Optional folder organization (usually null)
- **DocString**: Optional documentation (usually null)

## Usage

These schemas can be used to:
1. Understand available columns for KQL queries
2. Build query validation tools
3. Generate documentation
4. Create troubleshooting guides

## Notes

- All schemas retrieved from AKS Kusto MCP on 2026-01-28
- Schemas are filtered to include only the most relevant tables for troubleshooting
- Total: 31 tables across 4 databases
