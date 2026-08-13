# (top-level)

> Source: **Azure Compute Gallery - Copy Statistics** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Copy Speed

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`

```kusto
PirCasBlobCopyManagerEvent
| where TIMESTAMP > ago(30d) and artifactCategory == "SIGImage"
| where copyStatus == "Success" and isnotempty(replicationMetadata) and sourceBlobUri !contains "http://fake.blobvalidation/" and occupiedBlobSizeInBytes != 0
| extend replicateMetadataObj=parse_json(replicationMetadata)
| extend physicalSizeInGb = round(todouble(occupiedBlobSizeInBytes) / 1024 / 1024 /1024),timeSpent=totimespan(blobCopyDuration)/time(1s) 
| where physicalSizeInGb > 0
| sort by physicalSizeInGb desc
| project PreciseTimeStamp, physicalSizeInGb, blobCopyDuration, copyFlags, copyStaysAt0ByteDuration, timeSpent, speed=physicalSizeInGb*1024/timeSpent 
| summarize FastCopy=avgif(speed, copyFlags contains "SystemPriorityCopy"), 
            None=avgif(speed, copyFlags contains "None"), 
            CopyV2=avgif(speed, copyFlags == "CopyV2"), 
            min(PreciseTimeStamp), max(PreciseTimeStamp) by bin(PreciseTimeStamp, 1d)
| project PreciseTimeStamp, FastCopy, None, CopyV2
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `copyStatus == "Success"`

---
