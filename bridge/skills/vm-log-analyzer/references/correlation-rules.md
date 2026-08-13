# Cross-layer Correlation Rules

Rule library for identifying cross-layer causal chains during multi-file analysis.

---

## Rule format

```
Trigger event (source layer) → Expected effect (target layer)
Match conditions + time window
```

---

## OS layer → Middleware layer

### Rule 1: OOM → process termination
- **Trigger**: `Out of memory: Kill process` in syslog
- **Expected effect**: in the same time window, middleware/database logs show `connection refused` / `connection reset` / service restart records
- **Time window**: ±30 seconds
- **Notes**: after the kernel OOM killer terminates a process, services that depend on it immediately observe broken connections

### Rule 2: Disk I/O error → database write failure
- **Trigger**: `I/O error, dev` / `Buffer I/O error` in `kern.log` / `dmesg`
- **Expected effect**: database errorlog shows `write error` / `disk full` / `tablespace` errors
- **Time window**: ±60 seconds
- **Notes**: underlying disk failures propagate directly into the database I/O layer

### Rule 3: System clock jump → cluster split-brain
- **Trigger**: `time jump` / `ntpd: time stepped` in syslog
- **Expected effect**: Pacemaker/Corosync shows node timeouts and resource failovers
- **Time window**: ±120 seconds
- **Notes**: cluster heartbeat timeout thresholds are based on system time; NTP jumps can falsely trigger fencing

---

## OS layer → Network layer

### Rule 4: Network interface down → connection timeout
- **Trigger**: `link down` / `NIC link is Down` / `eth0: renamed` in syslog/dmesg
- **Expected effect**: in the same window, pcap shows TCP retransmissions/RST/DNS failures, or application/middleware logs show heavy `connection timeout` / `connection reset by peer` / DNS resolution failures
- **Time window**: ±10 seconds
- **Notes**: NIC state changes break TCP sessions directly

### Rule 5: Firewall rule change → connection refused
- **Trigger**: `iptables` / `firewalld` rule change in auth.log/syslog
- **Expected effect**: pcap shows TCP RST or ICMP type 3 (port unreachable), or application logs show `connection refused` / `no route to host` / TCP connection failures
- **Time window**: ±30 seconds

---

## Middleware layer → Application layer

### Rule 6: Database connection-pool exhaustion → application 500 errors
- **Trigger**: database logs show `max_connections reached` / `too many connections`
- **Expected effect**: Nginx/Apache error.log shows `upstream timed out` / HTTP 502/503
- **Time window**: ±30 seconds

### Rule 7: SAP HANA service restart → SAP application errors
- **Trigger**: HANA trace shows `System stopped` / `emergency shutdown` / indexserver or nameserver service stop
- **Expected effect**: SAP SM21 system log shows `Database connection broken`, or `dev_w*` trace shows `Reconnect failed` / `DBSL error`
- **Time window**: ±120 seconds
- **Notes**: HANA restarts often surface first as NetWeaver work process database reconnect failures; prove with both HANA and SAP app-layer timestamps.

---

## Cluster-layer correlation rules

### Rule 8: Fencing triggered → resource failover
- **Trigger**: Pacemaker shows `will be fenced` / `stonith` action
- **Expected effect**: the other node takes over the resource, logs show resource `start` actions, brief application outage
- **Time window**: 0–300 seconds after fencing

### Rule 9: Cluster split-brain
- **Trigger**: Corosync shows two partitions both believing themselves to be the DC
- **Signature**: both nodes' Pacemaker logs contain `I am the DC` with overlapping timestamps
- **Impact**: most severe cluster failure; data-consistency risk

---

## Time-correlation algorithm notes

When you need to do multi-file correlation manually (the model itself, no helper script), apply this logic:

1. **Timestamp normalization**: convert all file events to UTC at second precision (watch for `+0800` / `EDT` / local-time discrepancies)
2. **Sliding-window matching**: for each trigger event, search for related events in target files within the time window declared by each rule above (±30s / ±60s / etc.)
3. **Confidence scoring**:
   - Hit inside window + keyword match → high confidence (clear causality)
   - Hit inside window without keyword → medium confidence (suspected correlation)
   - Time proximity only → low confidence (time coincidence; needs human judgement)
4. **Causal-chain output**: sorted by confidence, high-confidence chains shown first

For larger multi-file bundles, prefer bundled helpers: `scripts\log_normalizer.py --merge` to build a UTC event list, then `scripts\correlator.py <files...>` to apply tagged cross-layer rules. For tiny scoped questions, an inline Python snippet is still enough.
