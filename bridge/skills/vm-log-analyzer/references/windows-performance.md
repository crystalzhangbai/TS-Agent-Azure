# Windows Performance Analysis Reference

> Domain knowledge for Windows VM performance analysis — CPU / memory / disk performance anomalies, memory pool exhaustion, resource-exhaustion detection, PerfInsights tool usage.
> Pull this together with `branch-windows.md` when Windows perf-related Event IDs appear (e.g. 2004 / 2019 / 2020 / 153 / 129 / 51 / 333).

---

## Performance Event Patterns

| Event ID | Source | Meaning | Fix |
|---|---|---|---|
| 2004 | Resource-Exhaustion-Detector | Low virtual memory (system commit nearing exhaustion) | Increase pagefile or expand VM memory |
| 1001 | Resource-Exhaustion-Detector | System commit memory exceeded the limit | Look for leaking processes; add RAM |
| 333 | Application Popup | I/O operation failed due to hardware / disk error | Check disk health (VM_Graph_Reader) |
| 153 | disk | Disk I/O retry (storage latency) | Check platform disk latency (VM_Graph_Reader); consider upgrading disk SKU |
| 129 | storahci / storport | Storage device reset (timeout) | Platform storage timeout — check VM_Kusto_Query |
| 11 | disk | Disk controller error | Disk hardware issue — check ASI |
| 51 | disk | Disk error during paging operation | Check disk health and the partition hosting the pagefile |
| 2019 | Srv | Nonpaged Pool exhaustion | Driver memory leak — use `poolmon` to identify the tag |
| 2020 | Srv | Paged Pool exhaustion | Driver memory leak — use `poolmon` to identify the tag |
| 7031 | Service Control Manager | Service terminated unexpectedly (crash) | Inspect Application log Event 1000 / 1001 for the process |
| 7034 | Service Control Manager | Service repeatedly terminating unexpectedly | Same as above; also inspect the service dependency chain |

---

## Performance Collection Commands

### System overview

```powershell
# Top 20 CPU processes
Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 Name, CPU, WS

# Real-time performance counters (CPU / available memory / disk queue)
Get-Counter '\Processor(_Total)\% Processor Time', '\Memory\Available MBytes', '\PhysicalDisk(_Total)\Avg. Disk Queue Length'

# Memory summary
systeminfo | findstr "Memory"
```

### Disk performance

```powershell
# Disk read / write latency
Get-Counter '\PhysicalDisk(*)\Avg. Disk sec/Read', '\PhysicalDisk(*)\Avg. Disk sec/Write'

# Disk queue depth
Get-Counter '\PhysicalDisk(*)\Current Disk Queue Length'
```

### Memory details

```powershell
# Kernel pools and committed memory
Get-Counter '\Memory\Pool Nonpaged Bytes', '\Memory\Pool Paged Bytes', '\Memory\Committed Bytes'

# Sort processes by memory consumption
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 20 Name, @{N='WS(MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}}
```

### Network

```powershell
# Active connections
netstat -an | findstr ESTABLISHED | Measure-Object
Get-Counter '\Network Interface(*)\Bytes Total/sec'
```

---

## PerfInsights Tool

Azure-provided automated performance analysis tool. Collects counters + event logs and generates an analysis report.

### How to use

1. Azure Portal → VM → **Diagnose and solve problems** → **Windows Perf Insights**
2. Select an analysis scenario: Quick / Performance / Advanced
3. The tool automatically collects CPU, memory, disk, network counters + event logs
4. It produces an automated analysis report flagging abnormal metrics

### Reading the output

| Report section | What to look for |
|----------------|------------------|
| **Findings** | Performance anomalies marked Critical / Warning |
| **CPU** | Processes sustained > 80%, kernel-mode CPU share |
| **Memory** | Available MB < 100, pool exhaustion, top working-set process |
| **Disk** | Average latency > 20 ms, queue depth > 2, I/O errors |
| **Network** | Retransmit rate, packet loss, bandwidth utilization |

> **Wiki reference**: `/Tools/Windows Perf Insights_Tool`

---

## Performance Analysis Decision Tree

```
Windows performance issue
├── Sustained high CPU
│   ├── Get-Process sorted by CPU → identify the offending process
│   ├── High kernel-mode CPU → driver / interrupt issue (check Event 129/153)
│   └── High user-mode CPU → application issue (check Application log)
│
├── Memory pressure
│   ├── Event 2004 / 1001 → Resource Exhaustion
│   ├── Available MB < 100 → identify the largest WS process
│   ├── Pool exhaustion (Event 2019 / 2020) → driver memory leak
│   └── Action: expand VM, increase pagefile, investigate the leak
│
├── High disk latency
│   ├── Repeated Event 153 → storage I/O retries
│   ├── Event 129 → storage timeout reset
│   ├── Avg. Disk sec/Read > 20 ms → disk performance bottleneck
│   └── Action: upgrade disk SKU (Standard → Premium SSD); review platform events
│
└── Service crash
    ├── Event 7031 / 7034 → service terminated unexpectedly
    ├── Application log Event 1000 → faulting module
    └── Action: update application / driver; check dependent services
```

---

## Cross-Skill References

| Skill | Purpose |
|-------|---------|
| **VM_Kusto_Query** | Query platform throttling events, host CPU / disk latency, ASI events |
| **VM_Graph_Reader** | View VM disk latency metrics, CPU utilization history, network bandwidth |
| **PerfInsights** | Automated performance data collection and analysis (see above) |

---

## AzureIaaSVM Wiki TSG References

- `/SME Topics/Performance` — performance troubleshooting home page
- `/Tools/Windows Perf Insights_Tool` — PerfInsights user guide
- `/Tools/VM assist for Windows_Tools` — automated diagnostics
