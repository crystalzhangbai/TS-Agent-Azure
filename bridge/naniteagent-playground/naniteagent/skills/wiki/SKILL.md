---
name: wiki
version: 1.0.0
description: Skills Documentation for Progressive Disclosure in csswiki, azurewiki, seektheway, arr, this document outlines best practices for creating Agent Skills with progressive disclosure patterns for csswiki integration. Progressive disclosure helps users access information gradually, revealing complexity only when needed.
---

## What are Agent Skills?
Agent Skills are reusable, LLM-callable capabilities that encapsulate:
- Troubleshooting workflows
- Diagnostic procedures
- Best practices and guidance
- Kusto queries and data exploration patterns
- Integration with MCP (Model Context Protocol) tools

## Progressive Disclosure Principles

### 1. Layer Information by Complexity
Structure content from simple to complex:
- **Level 1**: Quick answer or common solution for how to, 
- **Level 2**: Detailed explanation with context and step-by-step guidance
- **Level 3**: Advanced troubleshooting or edge cases

### 2. Start with Actionable Summaries
Begin each skill with:
- **What**: Brief description (1-5 sentences)
- **When to Use**: Clear trigger conditions
- **Quick Action**: Immediate next step

## Quick Summary
**Purpose**: [One sentence describing what this skill does]
**Use When**: [Specific conditions or symptoms]
**Quick Action**: [Immediate first step]

## Basic Troubleshooting
[Common scenarios and solutions - 3-5 bullet points]

## Detailed Investigation
<details>
<summary>Expand for detailed steps</summary>

### Step 1: [Action]
- Description
- Expected outcome
- What to do if it fails

### Step 2: [Action]
- Description
- Expected outcome
- What to do if it fails

</details>

## Data Queries
<details>
<summary>Kusto Queries</summary>

### Query 1: [Purpose]
```kusto
[Query here]
```
**What it shows**: [Explanation]
**Look for**: [Key indicators]

</details>

## Advanced Scenarios
<details>
<summary>Edge Cases and Complex Issues</summary>

[Advanced content here]

</details>

## Related Resources
- [Link to wiki page]
- [Related work items]
- [Related skills]

## Metadata
- **Last Updated**: [Date]
- **SME Contact**: [Name/Team]
- **Tags**: [tag1, tag2, tag3]
```

## Best Practices for CSSWiki Integration

### 1. Use Clear Navigation Cues
```markdown
### 🔍 Quick Check
[Simple verification steps]

### 🛠️ Resolution Steps
[Common fixes]

### 📊 Data Analysis
[Queries and logs]

### 🚨 Escalation Criteria
[When to escalate]
```

### 2. Link Strategically
- Link to wiki pages for deep documentation
- Link to related skills for alternative approaches
- Link to work items for examples
- Keep links contextual, not overwhelming

### 3. Optimize for LLM Parsing
- Use clear headers (##, ###)
- Keep paragraphs short (2-3 sentences)
- Use lists for sequences and options
- Add semantic markers (IMPORTANT, NOTE, WARNING)

### 4. Progressive Query Disclosure
Start with simple queries, hide complex ones:

```markdown
## Quick Status Check
```kusto
// Simple query for immediate insight
ResourceType
| where TimeGenerated > ago(1h)
| summarize count() by ResultType
```

<details>
<summary>Advanced Diagnostic Query</summary>

```kusto
// Complex multi-table join for deep analysis
[Complex query]
```
</details>
```

## Skill Categories for CSSWiki

### Diagnostic Skills
- Network connectivity issues
- Authentication failures
- Performance degradation
- Configuration errors

### Query Skills
- Log analysis patterns
- Metric exploration
- Event correlation
- Trend analysis

### Workflow Skills
- Case triage procedures
- Escalation pathways
- Customer communication templates
- Documentation updates

## Integration with MCP Tools

### Azure MCP Integration
Skills should reference Kusto clusters:
```markdown
**Required Connection**: [Cluster name]
**Database**: [Database name]
**Required Permissions**: [Permission level]
```

### DevOps MCP Integration
Skills should link work items and wiki:
```markdown
**Wiki Page**: [Organization/Project/Wiki/Page]
**Related Work Items**: #12345, #67890
**Pipelines**: [Link to relevant pipeline]
**WorkItem** : [Link to related work item]
```

### DriDash - Host Networking DRI Dashboard

**DriDash** (aka.ms/dridash) is a dashboard maintained by Host Networking's Datapath Operations team (wanetdpop@microsoft.com). It contains Kusto queries, dashboard links, and other supplemental information for debugging host networking issues.

**Dashboard URL Format**:
```
https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=1hours&p-_endTime=now&p-_NodeId=<GUID or all>&p-_ContainerId=<GUID or all>&p-_ICMId=<number>
```

**URL Parameters**:
| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `p-_startTime` | Start time for data query | `1hours`, `24hours`, `7days` |
| `p-_endTime` | End time for data query | `now`, specific timestamp |
| `p-_NodeId` | Node GUID to investigate | `37880214-9dfe-ab2e-6d81-3c17e0ba3b05` or `all` |
| `p-_ContainerId` | Container GUID to filter | GUID or `all` |
| `p-_ICMId` | ICM incident number | Numeric ICM ID |

**When to Use DriDash**:
- Investigating host networking issues on specific nodes
- Analyzing VFP, GFT, or SoC-related problems
- Debugging datapath connectivity issues
- Correlating network events with ICM incidents

**Example Usage**:
```markdown
For NodeId: 37880214-9dfe-ab2e-6d81-3c17e0ba3b05
URL: https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=1hours&p-_endTime=now&p-_NodeId=37880214-9dfe-ab2e-6d81-3c17e0ba3b05&p-_ContainerId=all&p-_ICMId=
```

**Contact**: wanetdpop@microsoft.com (Host Networking Datapath Operations)

### Azure DevOps MCP Servers (Multi-Organization Support)

The NaniteAgent integrates with multiple Azure DevOps MCP servers, each providing access to different knowledge bases and organizational content:

#### 1. **azurewiki** - Azure Engineering Team Knowledge
- **Coverage**: Comprehensive Azure engineering team documentation and knowledge base
- **Content**: All Azure engineer team wikis, technical documentation, and best practices
- **Use Cases**: General Azure engineering guidance, product documentation, architectural patterns
- **Organizations**: Multiple Azure engineering orgs
- **Language**: English

#### 2. **csswiki** - CSS Production Knowledge Base
- **Coverage**: CSS (Customer Service & Support) production content spanning multiple Azure services
- **Project Mapping in csswiki**:
  - AzureIaaSVM : Azure Compute (VMs, VM Scale Sets)  
  - AzureNetworking :  Azure Networking (VNet, Load Balancer, Application Gateway, ExpressRoute, VPN Gateway) 
  - AzureContainers : Azure Kubernetes Service (AKS)
  - AzureDBMySQL : Azure Database Services (PostgreSQL, MySQL)
  - AzureAD: Azure Active Directory (AAD)
  - Azure Backup and Recovery Services (ABRS)
- **Use Cases**: Production support scenarios, troubleshooting guides, customer-facing documentation
- **Organizations**: Multiple CSS production orgs
- **Language**: English

##### Special Project: AzureNetworking
The **AzureNetworking** project in csswiki is uniquely structured for Azure Network troubleshooting:

**Organization Structure**:
- Wiki pages organized by product (per Azure Network service)
- Each product has dedicated troubleshooting guides
- Standardized "Log Source for <Product Name>" wiki pages

**Log Source Wiki Pages**:
Each Azure Network product maintains a dedicated log source page containing:
- Product-specific Kusto queries
- Query parameters and customization points
- Common log patterns and signatures
- Data source references (tables, clusters, databases)

**Available Product Log Sources**:
- Log Source for VNet
- Log Source for Load Balancer
- Log Source for Application Gateway
- Log Source for ExpressRoute
- Log Source for VPN Gateway
- Log Source for Azure Firewall
- Log Source for Network Watcher
- Log Source for Virtual WAN
- Log Source for Traffic Manager
- And more...

#### 3. **seektheway** - Deep Dive Chinese Language Knowledge
- **Coverage**: Subject Matter Expert (SME) content with L400 (advanced) deep dive topics
- **Content Areas**:
  - Azure Networking (Advanced scenarios and configurations)
  - Azure Kubernetes Service (AKS) (Deep architectural and operational topics)
- **Unique Value**: Chinese language content with expert-level technical depth
- **Use Cases**: Advanced troubleshooting, architectural deep dives, Chinese-speaking customer support
- **Organizations**: SME-focused Azure orgs
- **Language**: Chinese (中文)

#### 4. **arr** - Azure DevOps Multi-Org Resource Repository
- **Coverage**: Cross-organizational Azure DevOps resources and workflows
- **Content**: Shared pipelines, work item templates, common workflows, collaboration patterns
- **Use Cases**: DevOps automation, cross-team workflows, standardized processes
- **Organizations**: Multiple Azure DevOps organizations
- **Language**: English

#### Best Practices for Multi-MCP Integration

**Querying Across MCP Servers**:
```markdown
**Knowledge Sources**:
- azurewiki: [Link to Azure engineering docs]
- csswiki: [Link to CSS production guide]
- seektheway: [Link to Chinese deep dive - 中文深度技术文档]
- arr: [Link to related work items and pipelines]
```

**Language Considerations**:
- Default to English content from azurewiki, csswiki, and arr
- Use seektheway for Chinese language support or L400 deep dives
- Tag skills with language indicators when applicable

**Service Coverage Matrix**:
| Service Area | azurewiki | csswiki | seektheway | arr |
|--------------|-----------|---------|------------|-----|
| General Azure Engineering | ✓ | - | - | - |
| Azure Compute | ✓ | ✓ | - | - |
| Azure Networking | ✓ | ✓ | ✓ (L400) | - |
| Azure AKS | ✓ | ✓ | ✓ (L400) | - |
| Azure Databases | ✓ | ✓ | - | - |
| Backup & Recovery | ✓ | ✓ | - | - |
| DevOps Workflows | - | - | - | ✓ |

**Skill Routing Recommendations**:
- **General inquiries**: Start with azurewiki
- **Customer support cases**: Use csswiki for production scenarios
- **Advanced/complex issues**: Check seektheway for L400 deep dives
- **Chinese language support**: Prioritize seektheway
- **DevOps automation**: Reference arr for workflows and pipelines

### Azure Network Troubleshooting Workflow (csswiki AzureNetworking Project)

When troubleshooting Azure Network issues, follow this systematic workflow:

#### Step 1: Search for Known Issues
**Priority Order**:
1. **Search Work Items**: Check if the issue has been reported and resolved
   - Search csswiki work items by product name, error message, or symptom
   - Review related work items, comments, and resolutions
   - Look for patterns in similar cases

2. **Search Wiki Pages**: Find existing troubleshooting guides
   - Search AzureNetworking project wiki by product and symptom
   - Look for Common Issues, FAQ, or Known Problems pages
   - Review product-specific troubleshooting sections

#### Step 2: Access Log Source Documentation
If no known issue found, locate the product-specific log source:

```markdown
**Example**: For ExpressRoute issues
- Navigate to: csswiki > AzureNetworking Project > Wiki
- Find: "Log Source for ExpressRoute" page
- Review available Kusto queries and parameters
```

**Log Source Page Structure**:
- **Overview**: Data sources and table references
- **Common Queries**: Pre-built Kusto queries with parameters
- **Query Parameters**: Required inputs (subscription ID, resource name, time range, etc.)
- **Log Patterns**: Known signatures and correlation IDs
- **Troubleshooting Guides**: Links to step-by-step guides

#### Step 3: Execute Kusto Queries with Azure MCP

**Workflow**:
1. **Identify Relevant Query**: Select appropriate Kusto query from Log Source wiki or workitem 
2. **Extract Parameters**: Identify required parameters (e.g., `{subscriptionId}`, `{resourceName}`, `{timeRange}`)
3. **Replace with Customer Data**: Substitute parameters with actual customer input data
4. **Execute via Azure MCP**: Use Azure MCP Kusto integration to run the query
5. **Analyze Results**: Review query output for anomalies, errors, or patterns

**IMPORTANT - Kusto Query Format**:
When returning Kusto queries to users, **always** use the fully qualified format:
```kusto
cluster("<clustername>").database("<dbname>").<tablename>
| where ...
```

Example:
```kusto
cluster("hawkeyedataexplorer.westus2").database("HawkeyeLogs").HawkeyeRCAEvents
| where PreciseTimeStamp > ago(30d)
| where NodeId == "your-node-id"
```

This ensures queries are immediately executable and properly scoped.

**CRITICAL - Schema Validation Before Building Queries**:
When building Kusto queries WITHOUT an existing example (i.e., creating new queries from scratch):
1. **ALWAYS retrieve the table schema first** using Azure MCP Kusto integration
2. **Verify actual column names** before writing WHERE clauses or projections
3. **Never guess field names** - wrong column names cause query failures

Example workflow:
```markdown
Step 1: Get schema
- Use Azure MCP to fetch table schema for the target table
- Review available columns, data types, and naming conventions

Step 2: Build query with validated columns
- Use EXACT column names from schema (case-sensitive)
- Reference schema for proper filter syntax
- Validate timestamp column names (PreciseTimeStamp vs TimeGenerated vs Timestamp)
```

**Why This Matters**:
- Prevents query failures from typos or incorrect column names
- Reduces investigation time by avoiding trial-and-error
- Ensures queries work on first execution

#### Step 4: Leverage Troubleshooting Guides

**If query reveals issues**:
1. **Return to Wiki**: Navigate to product-specific troubleshooting guide
2. **Match Symptoms**: Find guide section matching query results
3. **Follow Resolution Steps**: Execute recommended fixes
4. **Document Outcome**: Update work item with findings

**If query is inconclusive**:
1. **Review Related Queries**: Check other queries in Log Source page
2. **Escalate to L400**: Consider seektheway for advanced scenarios
3. **Create New Guide**: Document new issue pattern for future reference

#### Step 5: Integration Pattern

**Complete Troubleshooting Flow as an sample**:
```markdown
1. User reports: "ExpressRoute circuit not connecting"

2. Agent searches:
   - csswiki work items: "ExpressRoute connection failure"
   - AzureNetworking wiki: "ExpressRoute troubleshooting"
   - mslearn articles for ExpressRoute

3. Once content return agent need read those content and determin the best response and move to next repeat action, for example agent navigates to:
   - Wiki page: "Log Source for ExpressRoute"

4. Agent identifies query:
   - "BGP Session Status Check"
   - Parameters: {circuitName}, {subscriptionId}, {timeRange}

5. Agent replaces parameters:
   - circuitName: customer's circuit name
   - subscriptionId: customer's subscription
   - timeRange: last 24 hours

6. Agent executes via Azure MCP:
   - Kusto cluster: [configured cluster]
   - Database: AzureDiagnostics
   - Query: [substituted query]

7. Agent analyzes results:
   - BGP status = "Down" detected
   - Navigate to wiki: "ExpressRoute BGP Session Failure Guide"
   - Follow resolution steps

8. Agent provides customer:
   - Root cause: BGP session down
   - Resolution: [from guide]
   - Reference: Work item #XXXXX
```

#### Best Practices for Azure Network Troubleshooting

**DO**:
- ✅ Always search mcp learn and mcp csswiki , azurewiki, type of work items and wiki first (avoid duplicate investigation)
- ✅ Use product names when searching Log Source pages
- ✅ Replace ALL query parameters with actual customer data if Log Source page query is kusto
- ✅ Document query results in work items for future reference
- ✅ Link to Log Source wiki page in case documentation
- ✅ Update troubleshooting guides when new patterns emerge

**DON'T**:
- ❌ Skip work item search 
- ❌ Run queries with placeholder parameters (produces no results)
- ❌ Ignore query errors or empty results (may indicate wrong parameters)
- ❌ Skip documentation when resolving novel issues
- ❌ Forget to validate query time ranges (may miss recent events)

## Versioning and Maintenance

### Version Control
```markdown
## Change Log
- **v1.2** (2026-01-10): Added ExpressRoute gateway scenarios as sample
- **v1.1** (2025-12-15): Enhanced query performance
- **v1.0** (2025-11-20): Initial release
```

### Review Schedule
- **Monthly**: Update statistics and common patterns
- **Quarterly**: Review with SMEs for accuracy
- **As Needed**: Update after major product changes

## Examples

### Example 1: Simple Diagnostic Skill
```markdown
# ExpressRoute Connection Failure

## Quick Summary
**Purpose**: Diagnose ExpressRoute circuit connection failures
**Use When**: Customer reports "cannot connect" or "circuit down"
**Quick Action**: Check circuit provisioning state

## Basic Checks
- Verify circuit ProvisioningState is "Succeeded"
- Confirm ServiceProvider status is "Provisioned"
- Check both primary and secondary links

<details>
<summary>Detailed Investigation Steps</summary>

[Detailed content...]
</details>
```

### Example 2: Query Skill
```markdown
# ExpressRoute BGP Session Analysis

## Quick Summary
**Purpose**: Analyze BGP session stability and routes
**Use When**: Routing issues or intermittent connectivity
**Quick Action**: Check BGP session state

## Quick Query
```kusto
AzureDiagnostics
| where ResourceType == "EXPRESSROUTECIRCUITS"
| where bgpStatus_s == "Down"
| project TimeGenerated, circuit_s, peer_s
```

<details>
<summary>Advanced Route Analysis</summary>

[Complex queries...]
</details>
```

## Tips for Skill Authors

1. **Write for scanning**: Users should grasp the skill in 10 seconds
2. **Test with real cases**: Validate against actual customer scenarios
3. **Get SME review**: Have experts validate technical accuracy
4. **Update regularly**: Skills decay without maintenance
5. **Link generously**: Connect to related content
6. **Tag appropriately**: Use consistent taxonomy
7. **Think workflows**: Chain skills together for complex scenarios

## Feedback Loop

Skills improve through use. Capture:
- **What worked**: Successful resolutions
- **What didn't**: Dead ends or confusion
- **What's missing**: Gaps in coverage
- **What's outdated**: Changed product behavior

Submit feedback via:
- Work item: [Link to feedback template]
- Teams channel: [Link]
- Direct to SME: [Contact info]

## Getting Started

1. Review existing skills in the repository
2. Choose a troubleshooting scenario
3. Create skill using template above
4. Test with 2-3 recent cases
5. Get SME review
6. Submit for inclusion in skill library

---

*For questions or contributions, contact the NaniteAgent team.*
