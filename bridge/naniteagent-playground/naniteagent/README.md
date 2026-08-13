# NaniteAgent

Agentic AI for support engineering and technical assistance.

NaniteAgent packages a curated set of troubleshooting and knowledge-retrieval skills sourced from '[NaniteAgent](https://aka.ms/naniteagent)'. It combines natural-language interaction with structured skill content so engineers can move from a question to actionable diagnostics faster.

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [What This Plugin Includes](#what-this-plugin-includes)
- [Usage](#usage)
- [Skills & Reference](#skills--reference)
- [Installing the Plugin](#installing-the-plugin)
- [Contributing](#contributing)
- [Contacts](#contacts)

## Overview

NaniteAgent is designed to improve support-engineer productivity and make technical troubleshooting easier to navigate. It packages reusable Agent Skills that encode investigation workflows, Kusto-centric diagnostics, and progressive-disclosure guidance for complex technical topics.

**Key benefits:**
- Reduce troubleshooting time
- Streamline data exploration with natural language
- Capture and operationalize SME knowledge
- Reuse proven investigation workflows across scenarios

## The Problem

Support engineers often spend significant time searching documentation, writing queries, and correlating logs before they can reach a diagnosis. Static documentation is useful, but it is slow to navigate and difficult to apply during active investigations.

NaniteAgent turns that knowledge into skill-based workflows so the right guidance is easier to find and reuse.

### Included skill areas

| Skill | Purpose |
|------|---------|
| `aks` | AKS cluster troubleshooting, schema references, and investigation guides |
| `b01` | Azure networking Kusto query support across common networking scenarios |
| `confidence-score` | Confidence scoring framework for structured diagnostic assessments |
| `css` | Employee and support workflow queries, entitlement, ICM, and data-access workflows |
| `network-trace` | Network packet capture analysis and processing (pcap, pcapng, tcpdump) |
| `playwright-cli` | Browser automation for flows that need interactive retrieval |
| `wiki` | Progressive-disclosure guidance and documentation patterns for skill authoring |

### What it is built for

NaniteAgent is intended for support-engineering and technical-assistance workflows where users need:
- troubleshooting guidance
- Kusto query patterns
- quick access to curated reference material
- reusable skill-based investigation steps

## MCP Integration

Real-time access to essential data sources is configured in `.mcp.json`.

| Server | Purpose |
|--------|---------|
| `mslearn` | Microsoft Learn search for documentation and reference material |
| `eagleai` | EagleAI Kusto proxy for China-region accessible cluster queries |
| `enghub` | EngHub engineering documentation and service metadata |
| `csswiki` | CSS supportability wiki search for Azure and support workflows |
| `azurewiki` | Azure engineering wiki search for engineering guidance and docs |
| `azurefrontdoor` | Front Door-specific wiki and troubleshooting content |
| `azuremcp` | Azure MCP server for Kusto and Azure resource access |
| `workiq` | WorkIQ access for M365-related data and workflows |

## Usage

After installing the plugin, use the skills directly in Claude or Copilot to guide investigations.

### Example prompts

```text
Investigate AKS cluster health for a node-not-ready issue.
```

```text
Give me the B01 Kusto queries for ExpressRoute circuit troubleshooting.
```

```text
Help me find the right CSS workflow for CoreIdentity access renewal.
```

```text
Show me the progressive-disclosure pattern I should follow when writing a new skill.
```

## Installing the Plugin

### 1. Add the playground marketplace

From an interactive Agency session:

```text
/plugin marketplace add agency-microsoft/playground
```

### 2. Install NaniteAgent

```text
/plugin install naniteagent@agency-playground
```

### 3. Verify installation

```text
/plugin list
```

You should see `naniteagent` in the list of installed plugins.

### Uninstalling

```text
/plugin uninstall naniteagent
```

## Hooks

NaniteAgent includes a simple hook example in `hooks/hooks.json`.

- **PreToolUse** — emits a session-ready notice before each tool use
- **PostToolUse** — emits a completion notice after each tool use
- **SessionStart** — reminds users to start a new session for each topic

## Contributing

### Getting started

1. **Get contributor access** — join the [CoreIdentity group](https://coreidentity.microsoft.com/manage/Entitlement/entitlement/agencyopenco-adho) (Reader access, auto-approved for FTEs).
2. **Create a user branch** — use `users/<your-alias>/<feature-name>`.
3. **Keep the source scope focused** — this plugin currently packages only the seven approved skill areas listed above.

### Plugin directory structure

```text
plugins/naniteagent/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── agency.json
├── hooks/
│   ├── hooks.json
│   └── scripts/
├── README.md
└── skills/
    ├── aks/
    ├── b01/
    ├── confidence-score/
    ├── css/
    ├── network-trace/
    ├── playwright-cli/
    └── wiki/
```

### Adding or updating content

- Keep each skill’s structure intact when importing changes from the source repository.
- Preserve the skill markdown, references, and data files already present in each folder.
- Do not edit generated marketplace files directly.

### Submitting changes

1. Commit and push your user branch.
2. Open a PR to `main`.
3. Let the marketplace sync workflow regenerate the marketplace files.
4. Request review from a teammate with domain knowledge.

## Contacts

For issues or questions, use the repository’s normal contribution flow and PR review process.

If you need to change the skill source set, keep the scope limited to the approved folders listed in the overview.
