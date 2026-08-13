# (top-level)

> Source: **ARM Azure Recall Investigation Guide** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Kusto Query - Multi Row - Prod

_Widget purpose:_ Deleted resources in CSV

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `MultiRow` · Widget: `Table`

```kusto
let targetSubscriptionId = subId; //Subscription ID
let rg = rgName; //RG Name
let startTime = datetime_add('hour', -1, startDate);
let endTime = datetime_add('hour', 1, endDate);

macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpOutgoingRequests
    | where targetUri has rg
    | where PreciseTimeStamp between(startTime..endTime) 
    | where subscriptionId == targetSubscriptionId
    | where httpMethod == "DELETE"
    | where httpStatusCode > 199 and httpStatusCode < 300
    | extend resourceUri = strcat('/subscriptions/', split(tolower(split(targetUri, '/subscriptions/')[1]), '?')[0])
    | distinct PreciseTimeStamp, resourceUri, targetResourceProvider, targetResourceType
)
```

**Params:** `{subId}`, `{rgName}`, `{startDate}`, `{endDate}`

**Signal filters seen in KQL:** `httpMethod == "DELETE"`

---

### CSV Transformation - Prod

_Widget purpose:_ Deleted resources in CSV

Cluster: `?` · Database: `?` · Type: `Table`

```kusto
// Validate that 'kustoInput' exists and is an array
if (!data || !data.kustoInput || !Array.isArray(data.kustoInput)) {
  throw new Error("'kustoInput' parameter is missing or is not an array.");
}

// Add headers for the CSV
const headers = `"Resource id","Resource Provider","Resource Type"`;

// Escape values safely for CSV
const csvEscape = (v) => `"${String(v).replace(/"/g, '""')}"`;

// Normalize, validate, dedupe by resource id, and sort
const uniqueRows = Array.from(
  new Map(
    data.kustoInput.map((item) => {
      const resourceUri = item?.resourceUri ?? item?.Value;

      const targetResourceProvider =
        typeof item?.targetResourceProvider === "string"
          ? item.targetResourceProvider.toUpperCase().trim()
          : item?.targetResourceProvider;

      const targetResourceType =
        typeof item?.targetResourceType === "string"
          ? item.targetResourceType.toUpperCase().trim()
          : item?.targetResourceType;

      // Validate required properties
      if (
        typeof resourceUri !== "string" ||
        typeof targetResourceProvider !== "string" ||
        typeof targetResourceType !== "string"
      ) {
        throw new Error(
          `Invalid data: Expected 'resourceUri' (or 'Value'), 'targetResourceProvider', and 'targetResourceType' to be strings.`
        );
      }

      const normalizedResourceUri = resourceUri.trim();

      // Dedupe only by resource id
      return [
        normalizedResourceUri.toUpperCase(),
        {
          resourceUri: normalizedResourceUri,
          targetResourceProvider,
          targetResourceType
        }
      ];
    })
  ).values()
).sort((a, b) => {
  // Sort by Resource Type first, then Provider, then Resource id
  return (
    a.targetResourceType.localeCompare(b.targetResourceType) ||
    a.targetResourceProvider.localeCompare(b.targetResourceProvider) ||
    a.resourceUri.localeCompare(b.resourceUri)
  );
});

// Build CSV rows
const csvData = uniqueRows
  .map((item) =>
    [
      csvEscape(item.resourceUri),
      csvEscape(item.targetResourceProvider),
      csvEscape(item.targetResourceType)
    ].join(",")
  )
  .join("\r\n");

// Combine headers and data
const completeCsv = `${headers}\r\n${csvData}`;

// Return the data in a single cell
return [{ CSVFormat: completeCsv }];
```

**Params:** `{kustoInput}`

---

### Transform data per provider - Prod

_Widget purpose:_ Deleted Resources per resource provider

Cluster: `?` · Database: `?` · Type: `Table`

```kusto
/* ============================================================================
  Deleted Resource Grouper (Provider-Level View) — NEW SCHEMA
  Input schema (each item in data.kustoInput):
    - PreciseTimeStamp: string (ISO) or Date
    - resourceUri: string (Azure resource id)
    - targetResourceProvider: string (e.g., MICROSOFT.KEYVAULT)
    - targetResourceType: string (e.g., VAULTS)

  Output:
    One row per provider with:
      - latest timestamp seen for that provider
      - resources grouped by type (plain text, ASI-friendly)
      - SAP mapping
      - Notes populated with recovery links/instructions (provider-driven)
============================================================================ */

/* --------------------------- [1] SAP MAPPING ----------------------------- */
const sapMapping = {
  "MICROSOFT.WEB": "Azure/Web App",
  "MICROSOFT.STORAGE": "Azure/Storage Account Management/Deletion and Recovery/Recover deleted storage account",
  "MICROSOFT.SERVICEBUS": "Azure/Service Bus",
  "MICROSOFT.OPERATIONALINSIGHTS": "Azure/Log Analytics",
  "MICROSOFT.NETWORK": "Azure/Virtual Network",
  "MICROSOFT.DOCUMENTDB": "Azure/Cosmos DB",
  "MICROSOFT.ALERTSMANAGEMENT": "Azure/Application Insights",
  "MICROSOFT.SQL": "Azure/SQL Database/Connectivity: Configuration and How-To Questions/Private Link",
  "MICROSOFT.SYNAPSE": "Azure/Azure Synapse Analytics Workspace",
  "MICROSOFT.DATABRICKS": "Azure/Databricks/Workspace/Recover a deleted workspace",
  "MICROSOFT.LOGIC": "Azure/Logic App/Connectors/A Connector Not Listed",
  "MICROSOFT.MACHINELEARNINGSERVICES": "Azure/Machine Learning/Workspace Management, Configuration and Security/Issues to recover workspace and resources associated with workspace",
  "MICROSOFT.INSIGHTS": "Azure/Application Insights/Deploy, Configure or Manage Application Insights Resources/Recover a Deleted Application Insights resource",
  "MICROSOFT.DATAFACTORY": "Azure/Data Factory/Data Factory Administration (Factory Creation, Move, Limits, Backup or Restore, etc.)/How do I create a backup or restore an accidentally deleted Factory or Pipeline",
  "MICROSOFT.CONTAINERREGISTRY": "Azure/Container Registry/Registry Configuration/Recovering deleted image/repository",
  "MICROSOFT.CONTAINERSERVICE": "Azure/Container Instances/Management",
  "MICROSOFT.RELAY": "Azure/Relay/Performance and Latency",
  "MICROSOFT.KEYVAULT": "Azure/Key Vault/Key Vault Administration/Key Vault Recovery (Soft Delete & Purge Protection)",
  "MICROSOFT.COMPUTE": "Azure/Disk Storage/Disk Recovery",
  "MICROSOFT.OPERATIONSMANAGEMENT": "Azure/Log Analytics/Create and manage Log Analytics workspaces/Restore deleted workspace",
  "MICROSOFT.APIMANAGEMENT": "Azure/API Management Service/Configuration and Management/Backup or Restore Service",
  "MICROSOFT.APPPLATFORM": "Azure/Azure Spring Apps/Service/Failed to delete service",
  "MICROSOFT.AUTOMATION": "Azure/Azure Automation/Automation Account/I am trying to delete or unlink an Automation Account",
  "MICROSOFT.BOTSERVICE": "Azure/Bot Service/Manage a bot/Delete a bot",
  "MICROSOFT.CACHE": "Azure/Cache for Redis/Cache Management/Delete",
  "MICROSOFT.COGNITIVESERVICES": "Azure/Azure AI Foundry/Data and Indexes/Issues with Create, Read, Update, or Delete Indexes",
  "MICROSOFT.DEVICES": "Azure/IoT Hub/Unable to create or delete IoT hub",
  "MICROSOFT.EVENTHUBS": "Azure/Event Hubs/Create or Delete Operations",
  "MICROSOFT.NETAPP": "Azure/Azure NetApp Files/NFS volume - Create, delete or mount issues/Mount issues",
  "MICROSOFT.RECOVERYSERVICES": "Azure/Azure Backup/Vault delete and move",
  "MICROSOFT.SERVICEFABRIC": "Azure/Fabric Data Engineering/Create, update, or delete items/Lakehouse SQL Endpoint is not created"
};

/* ---------------------- [2] RECOVERY LINKS FOR NOTES --------------------- */
const recoveryMapping = {
  "MICROSOFT.KEYVAULT": [
    "[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/key-vault-recovery?tabs=azure-portal)",
    "[Azure Key Vault - PowerShell](https://learn.microsoft.com/en-us/powershell/module/az.keyvault/undo-azkeyvaultremoval?view=azps-9.7.1)"
  ],
  "MICROSOFT.OPERATIONALINSIGHTS": [
    "[OperationalInsights](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/delete-workspace?tabs=azure-portal#recover-workspace)"
  ],
  "MICROSOFT.STORAGE": [
    "[Storage Account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-recover)"
  ],
  "MICROSOFT.WEB": [
    "[WebApps](https://learn.microsoft.com/en-us/azure/app-service/app-service-undelete)"
  ],
  "MICROSOFT.AUTOMATION": [
    "[AutomationAccounts](https://learn.microsoft.com/en-in/azure/automation/delete-account?tabs=azure-portal#restore-a-deleted-automation-account)"
  ],
  "MICROSOFT.COGNITIVESERVICES": [
    "[Azure AI](https://learn.microsoft.com/en-us/azure/ai-services/recover-purge-resources?tabs=azure-portal)"
  ],
  "MICROSOFT.MACHINELEARNINGSERVICES": [
    "[Machine Learning Workspace](https://learn.microsoft.com/en-us/azure/machine-learning/concept-soft-delete?view=azureml-api-2)"
  ],
  "MICROSOFT.APIMANAGEMENT": [
    "APIM Service:",
    "List soft-deleted services (get name): [API](https://learn.microsoft.com/en-us/rest/api/resource-manager/apicenter/deleted-services/list-by-subscription?view=rest-resource-manager-apicenter-2024-03-15-preview&tabs=HTTP)",
    "Restore using [REST API](https://learn.microsoft.com/en-us/rest/api/resource-manager/apicenter/services/create-or-update?view=rest-resource-manager-apicenter-2024-03-15-preview&tabs=HTTP#request-body) with `properties.restore`"
  ]
};

/* ----------------------------- [3] SETTINGS ------------------------------ */
/*
  Keep this to protect the UI from huge cells.
  We will NOT print any "... (+N more)" line (copy/paste-friendly).
*/
const MAX_IDS_PER_TYPE = 300;

/* ------------------------------ [4] HELPERS ------------------------------ */
if (!data || !Array.isArray(data.kustoInput)) {
  throw new Error("'kustoInput' parameter is missing or is not an array.");
}

const asString = (x) => (x == null ? "" : String(x).trim());
const toUpper = (s) => asString(s).toUpperCase();
const toLower = (s) => asString(s).toLowerCase();
const cleanResourceId = (rid) => asString(rid).split("?")[0].split("#")[0];

const parseTs = (tsLike) => {
  if (tsLike instanceof Date) return isNaN(tsLike) ? null : tsLike;
  const s = asString(tsLike);
  if (!s) return null;
  const d = new Date(s);
  return isNaN(d) ? null : d;
};

/* ------------------------- [5] MAIN AGGREGATION -------------------------- */
const providerMap = Object.create(null);

for (let i = 0; i < data.kustoInput.length; i++) {
  const row = data.kustoInput[i] || {};

  const provider = toUpper(row.targetResourceProvider);
  const type = toLower(row.targetResourceType) || "(unknown-type)";
  if (!provider) continue;

  const rid = cleanResourceId(row.resourceUri);
  if (!rid) continue;

  if (!providerMap[provider]) {
    providerMap[provider] = {
      types: Object.create(null),
      totals: Object.create(null), // still tracked (may help later)
      latestTs: null
    };
  }
  const bucket = providerMap[provider];

  if (!bucket.types[type]) bucket.types[type] = new Set();

  bucket.totals[type] = (bucket.totals[type] || 0) + 1;

  // Print cap only (no truncation marker line)
  if (bucket.types[type].size < MAX_IDS_PER_TYPE) {
    bucket.types[type].add(rid);
  }

  const ts = parseTs(row.PreciseTimeStamp);
  if (ts && (!bucket.latestTs || ts > bucket.latestTs)) {
    bucket.latestTs = ts;
  }
}

/* ------------------------------ [6] OUTPUT ------------------------------- */
const rows = Object.keys(providerMap).sort().map((provider) => {
  const { types, totals, latestTs } = providerMap[provider];

  // Plain formatting (no bullets, no divider)
  const sections = Object.keys(types).sort().map((t) => {
  const ids = Array.from(types[t]).sort();

  // Count what you actually show: unique resource IDs
  const uniqueCount = ids.length;

  const header = `${t.toUpperCase()} (${uniqueCount})`;
  const body = ids.map((id) => `  ${id}`).join("\n");

  return body ? `${header}\n${body}` : header;
});


  const recoveryLines = recoveryMapping[provider] || [];
  const notes = recoveryLines.length
  ? Array.from(new Set(recoveryLines)).join("\n\n")
  : "";

  return {
    PreciseTimeStamp: latestTs ? latestTs.toISOString() : "",
    ResourceProvider: provider,
    DeletedResourcesPerProvider: sections.join("\n\n"),
    SAP: sapMapping[provider] || "",
    Notes: notes
  };
});

return rows;
```

**Params:** `{kustoInput}`

---
