# Windows BSOD Bugcheck Codes Reference

> Quick lookup for BSOD analysis — common BugCheck codes and their typical causes.

## Memory-related

| Code | Name | Typical Cause |
|------|------|--------------|
| `0x0A` | IRQL_NOT_LESS_OR_EQUAL | Driver attempted to access pageable memory at high IRQL |
| `0x1A` | MEMORY_MANAGEMENT | Memory management subsystem error |
| `0x50` | PAGE_FAULT_IN_NONPAGED_AREA | Referenced unallocated memory in nonpaged area |
| `0x7F` | UNEXPECTED_KERNEL_MODE_TRAP | Kernel mode received an unexpected trap |

## Driver-related

| Code | Name | Typical Cause |
|------|------|--------------|
| `0xC2` | BAD_POOL_CALLER | Driver allocated/freed pool memory incorrectly |
| `0xD1` | DRIVER_IRQL_NOT_LESS_OR_EQUAL | Driver accessed pageable memory at high IRQL |
| `0x9F` | DRIVER_POWER_STATE_FAILURE | Driver did not respond correctly to power state change |
| `0xC4` | DRIVER_VERIFIER_DETECTED_VIOLATION | Driver Verifier flagged a driver fault |

## Boot / storage

| Code | Name | Typical Cause |
|------|------|--------------|
| `0x7B` | INACCESSIBLE_BOOT_DEVICE | Cannot read boot device — storage driver missing or HBA changed |
| `0xED` | UNMOUNTABLE_BOOT_VOLUME | Boot volume cannot be mounted — filesystem corrupted |
| `0xF4` | CRITICAL_OBJECT_TERMINATION | Critical kernel process terminated unexpectedly |

## System / process

| Code | Name | Typical Cause |
|------|------|--------------|
| `0xEF` | CRITICAL_PROCESS_DIED | Critical OS process (csrss/winlogon/services) crashed |
| `0xC000021A` | STATUS_SYSTEM_PROCESS_TERMINATED | Critical user-mode process exited |
| `0x9E` | USER_MODE_HEALTH_MONITOR | Cluster service detected hang |

## DLL / system file

| Code | Name | Typical Cause |
|------|------|--------------|
| `0xC0000218` | STATUS_CANNOT_LOAD_REGISTRY_FILE | Registry hive corrupted |
| `0xC0000034` | STATUS_OBJECT_NAME_NOT_FOUND | Missing system file or registry key |

---

## Analysis tips

### 1. Note the parameters

Every BugCheck has 4 parameters (Param 1–4). Different codes use them differently — look them up in Microsoft Docs.

Example — `0x7E SYSTEM_THREAD_EXCEPTION_NOT_HANDLED`:
- Param 1 = exception code (e.g. `0xC0000005` = access violation)
- Param 2 = exception address (in faulting module)
- Param 3 = exception record
- Param 4 = context record

### 2. Locate the faulting module

Microsoft modules end in `ms`, `nt`, `win`; third-party usually end with the vendor name. Common faulting modules:
- `nvlddmkm.sys` — NVIDIA display driver
- `igdkmd64.sys` — Intel graphics driver
- `aksdf.sys` — security software
- `klif.sys` — Kaspersky
- `eamonm.sys` — ESET

### 3. Check dump files

```powershell
# Default dump file locations
C:\Windows\Minidump\*.dmp           # Mini dump (small)
C:\Windows\MEMORY.DMP               # Kernel/complete dump

# Analyze with WinDbg
!analyze -v
!process 0 0
!thread
```

### 4. Common combinations

| Pattern | Possible Cause |
|---------|--------------|
| Repeated 0x7B after VM size change | NVMe / SCSI driver missing (e.g. Lsv2 series) |
| 0xEF + csrss.exe | System file corruption — run `sfc /scannow` |
| Multiple 0xD1 with same module | Specific driver bug — update or remove |
| 0x9F during shutdown | A driver did not respond to power state change |

---

## Reference

- [Microsoft Docs: Bug Check Code Reference](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-code-reference2)
- csswiki: search "BSOD analysis" / "memory dump"
- TSG: Azure VM BSOD Investigation Guide
