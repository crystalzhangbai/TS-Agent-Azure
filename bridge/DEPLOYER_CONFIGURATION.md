# Deployer Configuration Checklist

This file lists configuration that changes by deployer, tenant, Azure resource, customer, or local machine. Keep real values only in local files such as `.env`, `customers.json`, and `session_environments.json`.

| File and location | How to configure |
|---|---|
| `bridge/.env.example` line 7, `bridge/config.py` lines 17-20 | Set Bot Framework identity. Copy `bridge/.env.example` to `bridge/.env`; keep `MicrosoftAppType=MultiTenant` unless the Azure Bot/App Registration is single-tenant. Find `MicrosoftAppId` from the Azure Bot resource or App Registration client id. Create `MicrosoftAppPassword` from App Registration > Certificates & secrets. Set `MicrosoftAppTenantId` only for single-tenant bots. |
| `bridge/teams-app/manifest.json` lines 5 and 27 | Replace both placeholder GUIDs with the same `MicrosoftAppId` / bot app client id before packaging the Teams app. |
| `bridge/teams-app/manifest.json` lines 6-18 and 31-44 | Customize app publisher metadata, display name, descriptions, and command examples. These are not secrets, but they should match the new owner/team and avoid customer-specific names in public source. |
| `bridge/teams-app/manifest.json` line 53 | Keep only domains that can host the bot messaging endpoint, for example `*.devtunnels.ms`, your App Service domain, or an approved tunnel domain. |
| `bridge/.env.example` lines 14-18, `bridge/config.py` lines 23-26 | Set Azure OpenAI/model values. Use the endpoint shown in Azure OpenAI or Azure AI Foundry for the model resource, set `AZURE_OPENAI_MODEL` to the deployment name, keep the API version supported by that resource, and set `AZURE_OPENAI_API_KEY` only if the resource uses key auth. |
| `bridge/.env.example` lines 22-26, `bridge/config.py` lines 29-32, `bridge/brain_maf.py` lines 33 and 235-240 | Set Foundry project access. Get `FOUNDRY_PROJECT_ENDPOINT` from Azure AI Foundry project overview. Create or reuse a service principal with the needed Foundry/project role, then fill tenant id, client id, and client secret. The app fails fast if these are missing. |
| `bridge/.env.example` line 30, `bridge/launch-bridge.ps1` line 452 | Set `BOT_RESOURCE_ID` to the full Azure Bot Service resource id. Find it in Azure Portal > Bot resource > JSON View, or use `az bot show --resource-group <rg> --name <bot-name> --query id -o tsv`. |
| `bridge/.env.example` line 32, `bridge/launch-bridge.ps1` lines 340-347 | Optionally set `DEVTUNNEL_NAME` to reuse a named dev tunnel. Create or list tunnels with Dev Tunnel CLI, then make sure the running user has access to host it. Leave empty to create/use an unnamed tunnel. |
| `bridge/.env.example` lines 34-36, `bridge/launch-bridge.ps1` lines 455-457 | Optionally set `MGMT_SP_*` for endpoint auto-update. Create a service principal and grant it permission to update the Bot Service resource, then store its tenant id, client id, and secret in local `.env`. |
| `bridge/.env.example` lines 40-42, `bridge/tools/azure_vm.py` lines 23-25 | Optionally set Azure data-plane fallback identity. Use this when local `az login` / `DefaultAzureCredential` is not enough. Grant the SP Reader access to target subscriptions/resources. |
| `bridge/customers.example.json` line 2, `bridge/credentials.py` lines 20 and 41-46 | Copy to `bridge/customers.json` for customer-specific SP access. For each customer environment fill `name`, `tenant_id`, `client_id`, `client_secret`, and `subscriptions`. Create the SP in the customer tenant and grant at least Reader on the listed subscriptions. Never commit `customers.json`. |
| `bridge/session_environments.example.json` lines 2-15, `bridge/session_environment.py` lines 14-15 and 67-93 | Copy to `bridge/session_environments.json` to add selectable `/env` profiles. Use `auth_mode=sp` when backed by `customers.json`; use `auth_mode=delegated` when the Teams user must complete device-code login. Fill tenant/subscription and delegated client fields as needed. Never commit `session_environments.json`. |
| `bridge/session_environment.py` lines 18-22 | Customize optional `/env` aliases. Keep customer-specific aliases out of public source; add them only in private documentation or local forks. |
| `bridge/delegated_auth.py` lines 17 and 78 | Optionally replace the delegated auth public client id. The default is a public Azure CLI-style client id and is not a secret, but some tenants require a first-party or tenant-approved app registration. |
| `bridge/.env.example` lines 46-53, `bridge/tools/kusto.py` lines 24-26 and 168-170 | Configure Kusto/ADX defaults. Set cluster URL and database if tools should have defaults. Use `KUSTO_TENANT_ID`, `KUSTO_CLIENT_ID`, and `KUSTO_CLIENT_SECRET` for unattended SP auth; otherwise run `az login` for the bot runtime user. |
| `bridge/preflight_todo.py` lines 84 and 138-139 | Optionally set `KUSTO_AZ_TENANT_ID` in `.env` to control which tenant Azure CLI uses for Kusto tokens. If unset, the preflight code has a built-in default tenant hint. |
| `bridge/.env.example` lines 55-60 | Configure local runtime behavior. `PORT` must match the Bot endpoint tunnel port. `NANITE_DEEP_MODE_ENABLED`, `DELEGATED_AUTH_TTL_MINUTES`, `SHOW_TRACE`, and `RUN_LOG_ENABLED` are operational toggles. |
| `.gitignore` lines 2-7 and 20 | Keep local secret/config/runtime files out of Git: `.env`, `customers.json`, `session_environments.json`, and `bridge/runtime/`. If you add new local config files, add them here before putting real values in them. |

## Public Repository Rules

- Commit templates and documentation, not real deployment values.
- Local-only files: `bridge/.env`, `bridge/customers.json`, `bridge/session_environments.json`, and everything under `bridge/runtime/`.
- Secret values include any password, client secret, API key, access token, private tunnel URL, or customer-specific service principal secret.
- Resource identifiers such as subscription ids, tenant ids, bot resource ids, Foundry endpoints, and customer names are not always cryptographic secrets, but they still identify your environment. Keep them out of public templates unless they are intentionally generic examples.
- If any real secret was ever committed, rotate it first, then clean Git history with a tool such as `git-filter-repo` or BFG before making the repository public.
