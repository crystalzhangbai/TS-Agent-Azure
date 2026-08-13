# Common Log Patterns Quick Reference

Fast pattern matching for log analysis — covers OS, network, middleware, and database scenarios.

---

## Severity filtering

Use these regex patterns for grep filtering:

```bash
# Critical errors (must fix)
grep -iE 'fatal|critical|panic|emergency|alert' <logfile>

# General errors
grep -iE 'error|fail(ed|ure)?|exception' <logfile>

# Warnings (potential precursors)
grep -iE 'warn(ing)?|deprecated|slow' <logfile>

# Performance / resource related
grep -iE 'timeout|timed out|refused|reset|killed|oom|out of memory' <logfile>
```

---

## Linux OS layer patterns

### Kernel panic signatures

| Pattern | Meaning | Severity |
|---------|---------|---------|
| `Kernel panic - not syncing` | Kernel halted, unrecoverable | Fatal |
| `general protection fault` | Memory protection violation | Critical |
| `Oops:` | Kernel exception (may recover) | Critical |
| `BUG: kernel NULL pointer dereference` | Driver bug | Critical |
| `RIP:` | Instruction pointer at crash | Critical |
| `Call Trace:` | Function call stack (used for analysis) | Critical |

### OOM Killer typical sequence

```
1. kernel: [<PID>] <UID> <user> <pid> total-vm:...
2. kernel: Out of memory: Kill process <PID> (<process>)
3. kernel: Killed process <PID>, UID xxx, (<process>) total-vm:xxx
```

**Key fields**: process name, RSS (actual memory used), oom_score_adj

### SSH brute-force / connection failure patterns

```
# Failed login (auth.log)
sshd[<pid>]: Failed password for <user> from <ip>
sshd[<pid>]: Invalid user <user> from <ip>

# Connection rejected (firewall / TCP wrapper)
sshd[<pid>]: refused connect from <ip>

# Authentication errors
sshd[<pid>]: error: PAM: Authentication failure
```

---

## Disk / storage layer patterns

### SCSI / SATA / NVMe error patterns

```
# Disk I/O timeout
sd <X:Y:Z:W>: [sdX] Sense Key : Hardware Error
ata<N>: SError: { ... }
ata<N>.<NN>: status: { DRDY ERR }

# Bad sectors
end_request: I/O error, dev sdX, sector NNNNNNN
Buffer I/O error on dev sdX1, logical block NNNN

# NVMe specific
nvme nvme0: I/O <N> QID <Q> timeout, reset controller
nvme0n1: Read failure
```

### File system errors

```
# EXT4
EXT4-fs error (device sdX): ext4_lookup:...
EXT4-fs (sdX): warning: mounting fs with errors

# XFS
XFS: Internal error xfs_trans_cancel at line ...
XFS: log mount/recovery failed

# Mount errors
mount: wrong fs type, bad option, bad superblock on /dev/sdX
```

---

## systemd / service patterns

```
# Service start failure
systemd[1]: Failed to start <service>.service.
systemd[1]: <service>.service: Main process exited, code=exited, status=<N>/<NAME>
systemd[1]: <service>.service: Failed with result 'exit-code'.

# Boot timeout
systemd[1]: Timed out waiting for device <dev>.
systemd[1]: Dependency failed for <target>.

# Repeated failures (entering failed state)
systemd[1]: <service>.service: Start request repeated too quickly.
```

---

## Network layer patterns

### NIC / link state

```
# Link state change
kernel: <iface>: link is not ready
kernel: <iface>: link up, 1000 Mbps, full duplex
kernel: <iface>: link down

# DHCP failure
dhclient[<pid>]: No DHCPOFFERS received.
NetworkManager[<pid>]: <warn> [ts] dhcp4 (<iface>): request timed out
```
