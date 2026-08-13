# Timeline Chart

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Timeline Chart** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AIR-BP (Reads, Writes, Flush)

### Azure Host Subscription Disk AIR-BP Timeline

_Widget purpose:_ AIR-BP (Reads, Writes, Flush)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Timeline Chart > AIR-BP (Reads, Writes, Flush)`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
        and IsNewDisk == 0 
        and Type in (0, 4) 
        and ArmId contains subId
        and HistogramTypeEnum in (1, 3, 4)
| summarize TotalIOsGt1s = sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
                TotalIOsGt2s = sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
                TotalIOsGt5s = sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256), 
                TotalIOsGt10s = sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
                TotalIOsGt15s = sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
                TotalIOsGt30s = sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256)
by bin(PreciseTimeStamp, 5m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`

---
