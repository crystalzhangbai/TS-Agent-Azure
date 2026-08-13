# AKS CSS Troubleshooting Skills

A [GitHub Copilot CLI skill](https://docs.github.com/en/copilot) for investigating and troubleshooting **Azure Kubernetes Service (AKS)** cluster issues. It combines **Azure DevOps wiki search** with **Kusto (KQL) database queries** to accelerate root-cause analysis for CSS (Customer Service & Support) engineers.

## Features

- **Guided troubleshooting workflow** — step-by-step investigation from symptom to root cause
- **Kusto query templates** — pre-built KQL queries for AKSprod, AKSccplogs, AKSinfra, and AKSmetrics databases
- **Wiki integration** — searches AKS PG and Supportability wikis for known issues and TSGs
- **Schema-aware** — includes table schema references to avoid common query pitfalls
- **Modular guides** — dedicated troubleshooting guides for nodes, cluster operations, and audit logs

## Repository Structure

This skill follows the [agentskills.io specification](https://agentskills.io/specification) with **progressive disclosure**:
- **Tier 1** — `name` + `description` in SKILL.md frontmatter (loaded at startup)
- **Tier 2** — Workflow instructions in SKILL.md body (loaded on activation)
- **Tier 3** — Detailed queries and references in `references/` and `guides/` (loaded on demand)

```
├── SKILL.md                         # Main skill definition (< 500 lines, progressive hub)
├── README.md                        # Human-facing documentation (this file)
├── LICENSE                          # MIT License
├── references/                      # Tier 3: Detailed reference material (loaded on demand)
│   ├── ARCHITECTURE.md              # AKS architecture, databases, components
│   ├── TABLE_SCHEMA_REFERENCE.md    # Quick-reference for Kusto table schemas
│   ├── TSG_REFERENCE.md             # Patterns from official AKS TSG repository
│   ├── cluster-info-queries.md      # Steps 4.1–4.7: Cluster info KQL queries
│   ├── cluster-health-checks.md     # Step 5: Health check KQL queries
│   ├── database-guide.md            # Database overview, common patterns, gotchas
│   └── query-best-practices.md      # Query errors, performance tips, presentation
├── guides/                          # Tier 3: Issue-specific troubleshooting guides
│   ├── node-troubleshooting.md      # Node lifecycle, CNI, networking issues
│   ├── cluster-operations.md        # Cluster CRUD, upgrades, autoscaler
│   └── audit-logs.md                # Kubernetes API audit log analysis
└── table-schema/                    # Full JSON schemas per database/table
    ├── AKSprod/
    ├── AKSccplogs/
    ├── AKSinfra/
    ├── AKSmetrics/
    └── README.md
```

## Prerequisites

| Tool | Purpose |
|------|---------|
| **ado-msazure-mcp** | Search AKS PG wiki |
| **ado-supportability-mcp** | Search AKS Supportability wiki |
| **aks-kusto-rti-mcp** | Execute KQL queries against AKS Kusto databases |

You also need read access to: **AKSprod**, **AKSccplogs**, **AKSinfra**, and **AKSmetrics** Kusto databases.

## Usage

1. Install as a [Copilot CLI skill](https://docs.github.com/en/copilot) by pointing to the `SKILL.md` file.
2. Start a troubleshooting session by describing the issue, providing the cluster resource ID and time range.
3. The skill will guide you through wiki search → cluster snapshot → Kusto queries → analysis.

## Covered Scenarios

- **Node issues** — NotReady, unregistered nodes, CNI failures, node provisioning
- **Cluster operations** — create/update/delete failures, upgrade issues
- **Control plane** — API server, etcd, controller-manager, scheduler logs
- **Networking** — Azure CNI (Classic/Overlay), BYO CNI, Kubenet
- **Autoscaler** — scale-up/down failures, capacity issues
- **Audit logs** — Kubernetes API audit analysis, RBAC investigation

## Contributing

Contributions are welcome! Feel free to:
- Add new troubleshooting guides under `guides/`
- Improve KQL query templates in `references/`
- Add table schemas for new databases under `table-schema/`
- Share TSG patterns in `references/TSG_REFERENCE.md`

## License

This project is licensed under the [MIT License](LICENSE).
