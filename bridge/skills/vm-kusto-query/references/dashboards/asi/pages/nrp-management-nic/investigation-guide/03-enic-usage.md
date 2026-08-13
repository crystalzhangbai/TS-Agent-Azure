# Enic Usage

> Source: **NRP - Management Nic** dashboard, chapter **Enic Usage** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Enic Usage Customer Based

### Enic Usage per Customer

_Widget purpose:_ Enic Usage Customer Based

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Enic Usage > Enic Usage Customer Based`

```kusto
let d = datatable (SubscriptionId:string, Customer:string)
["640e2d9e-8d9a-40d1-b51a-d84db4969ee0", "Dell", 
"0629574c-1c80-4365-b0c6-3f5fdde6518e", "Dell", 
"ee920d60-90f3-4a92-b5e7-bb284c3a6ce2", "NGINX", 
"c1ce8002-e944-43ae-bbe2-33481e2c9928", "NGINX",
"8f4765e6-7c9f-4e06-a881-8b9e1aa5d646", "Palo Alto", 
"1adc902d-2621-40cb-8109-6ab72c2c26c8", "Palo Alto", 
"474240ee-c2a4-4373-bc0d-bd2e3dba4714", "Liftr", 
"af20b225-d632-4791-97a0-2b33fa486420", "Liftr"
];
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(90d)
| where OperationName == "PutNicOperation"
| where Request contains "\"nictype\": \"Elastic\""
| join kind = leftouter d on SubscriptionId
| where Customer != ""
| summarize uc = count() by ResourceName, Customer, bin(TIMESTAMP, 1d)
| summarize UpdateCount = sum(uc)/1.0 by Customer, bin(TIMESTAMP, 1d)
| project TIMESTAMP, UpdateCount, Customer
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## Enic Usage Region Based

### Enic Usage

_Widget purpose:_ Enic Usage Region Based

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Enic Usage > Enic Usage Region Based`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(30d)
| where OperationName == "PutNicOperation"
| where Request contains "\"nictype\": \"Elastic\""
| summarize uc = count() by ResourceName, Region, bin(TIMESTAMP, 1d)
| summarize UpdateCount = sum(uc)/1.0 by ResourceName, Region, bin(TIMESTAMP, 1d)
| project TIMESTAMP, UpdateCount, Region
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## Monthly Active Enic

### Monthly Active Enic

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Enic Usage > Monthly Active Enic`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(90d)
| where OperationName == "PutNicOperation"
| where Request contains "\"nictype\": \"Elastic\""
| summarize uc = count() by ResourceName, bin(TIMESTAMP, 30d)
| summarize ct = count() by bin(TIMESTAMP, 30d)
| summarize ActiveEnic = sum(ct)/1.0 by bin(TIMESTAMP, 30d)
| project TIMESTAMP, ActiveEnic
```

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---

## Pnic Usage

### Pnic Usage

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Enic Usage > Pnic Usage`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(30d)
| where OperationName == "PutNicOperation"
| where Request contains "\"elasticNetworkInterfaceLinks\""
| summarize uc = count() by ResourceName, Region, bin(TIMESTAMP, 1d)
| summarize UpdateCount = sum(uc)/1.0 by ResourceName, Region, bin(TIMESTAMP, 1d)
| project TIMESTAMP, UpdateCount, Region
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutNicOperation"` · `Request contains "\"`

---
