# Preflight Operations

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **Preflight Operations** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Correlation ID - Preflight Ops

_Widget purpose:_ Preflight Operations

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Preflight Operations`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Deployments').PreflightEvents
    | where TIMESTAMP between ((queryFrom - 12h)..(queryTo + 12h))
    | where correlationId == queryCorrelationId and isnotempty(queryCorrelationId)
    | where operationName == "ProviderPreflightStatus"
    | extend PreflightStatus = parse_json(tostring(split(message, ": ")[1]))
    | project TIMESTAMP, ActivityId, duration = durationInMilliseconds * 1ms, validationStatus, 
      resourceType = strcat(PreflightStatus["providerNamespace"], "/", PreflightStatus["resourceType"]),
      resourceLocation = PreflightStatus["location"],
      reason = PreflightStatus["reason"],
      scope = PreflightStatus["scope"],
      resourceCount = PreflightStatus["resourceCount"]
    | extend formatted_ts = format_datetime(TIMESTAMP, 'yyyy-MM-dd [HH:mm:ss]')
    | extend short_activity = substring(ActivityId, 0, 13)
)
| order by TIMESTAMP asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCorrelationId}`

**Signal filters seen in KQL:** `operationName == "ProviderPreflightStatus"`

---
