# Verification Pack — V4: Command / Step Feasibility

> **V-type:** V4 — *are the commands/steps we're about to hand a customer syntactically valid,
> correctly targeted, applicable to their environment, and is anything destructive flagged?*
> **Used by:** `vm-lab` (provides the pack) — typically loaded by **V5** when a customer email
> contains commands, or standalone when steps are about to be sent.
> **Contract:** [`_shared/verifier/verifier-subagent.md`](../../_shared/verifier/verifier-subagent.md) ·
> [`_shared/verifier/evidence-ledger.md`](../../_shared/verifier/evidence-ledger.md)

**V4 is STATIC BY DEFAULT.** It checks commands on paper — syntax, target mode, doc match,
applicability, destructive-op flag — **without executing anything**. Actually running a command in
the lab happens **only when the user explicitly asks** ("validate in lab / 在 lab 验证"). This keeps
`vm-lab`'s explicit-trigger iron rule intact: the verifier never auto-fires a lab run.

```
command in an artifact
      │
      ▼  (default — automatic at the gate)
STATIC checks: syntax · target mode · doc/known-good match · applicability · destructive flag
      │
      ▼  (ONLY if user explicitly says "validate in lab")
vm-lab actual execution against the fixed lab VMs  ← the gold truth, explicit-trigger only
```

---

## 1. Truth source

| Layer | Truth source |
|---|---|
| Syntax & target mode | `references/command-classification.md` (Mode A/B/C/D/E decision tree) |
| Destructive / disruptive classification | `vm-lab/SKILL.md` Step 3.3 Safety Review + Safety Rules |
| Doc / known-good match | the cited TSG/KB (hand the doc-faithfulness sub-check to **V1**) |
| Behavioral truth (only on explicit request) | **real lab execution** — the gold standard, never auto-run |

---

## 2. 命门 (load-bearing commands) for V4

| Is命门 | Is NOT命门 |
|---|---|
| A command whose **wrong target/syntax would break the customer's box** (destructive: `rm -rf`, `az vm delete`, `az disk delete`, registry/BCD/GRUB edits). | A read-only inspection command (`az vm show`, `Get-Service`, `cat`, `systemctl status`). |
| A command whose **applicability gates correctness** (Linux command sent to a Windows VM; Gen2-only step). | Generic context. |
| A **multi-line script** handed to the customer (user-data / cloud-init / CSE). | A one-off read command. |

---

## 3. Static checklist (default — no execution)

| # | Check | Fail → class |
|---|---|---|
| 1 | **Syntax valid** — flags, quoting, cmdlet/parameter names are real (per the mode's pattern). | Invalid syntax → `CONTRADICTED` (won't run). |
| 2 | **Correct target mode** — command routed to the right target per `command-classification.md` (Linux→Mode B, Windows→Mode C, `az`→Mode A, Portal→Mode D, ARM→Mode E). | Wrong target → `CONTRADICTED`. |
| 3 | **Applicability** — matches the customer's OS/VM-gen/SKU (no Linux command for a Windows VM, no Gen2-only step on Gen1). | Mismatch → `CONTRADICTED`; precondition omitted → `UNSUPPORTED`. |
| 4 | **Doc / known-good match** — the command matches the cited TSG/known-good template (not improvised). | Diverges from doc → `INFERRED` (route the cite to V1). |
| 5 | **Destructive-op flag** — any 🔴 destructive / 🟡 disruptive command is explicitly flagged with a warning + confirmation note before it reaches the customer. | Unflagged destructive op → **critical issue** → FAIL. |
| 6 | **No production-subscription / customer-resource execution baked in** — the step never tells us to run against the customer's live subscription as "verification". | Present → critical issue (violates the no-customer-subscription rule). |

### Destructive/disruptive classes (from Step 3.3)

| Pattern | Class |
|---|---|
| `rm -rf`, `del /s`, `Remove-AzResource`, `az vm delete`, `az disk delete` | 🔴 Destructive — must be flagged + confirmed |
| `az vm restart`, `Stop-AzVM`, `az vm deallocate` | 🟡 Disruptive — warn impact |
| `az vm create`, `New-AzVM` | 🟡 Cost — warn |
| `az vm show`, `Get-AzVM`, `cat`, `systemctl status` | 🟢 Safe |

---

## 4. Explicit-trigger lab run (the only path to actual execution)

The static checklist is the gate's **default**. The verifier does **not** run anything in the lab on
its own — doing so would break the `vm-lab` iron rule. Real execution happens only when the user
explicitly says "validate in lab", at which point control hands to `vm-lab` proper (parse →
classify → pre-flight → execute → report), against the **fixed lab VMs**, never the customer's
subscription.

> This is exactly the gap V4 closes: the lab was the gold truth but was only ever explicit-trigger
> and never wired as a verifier. V4 makes the **static** check a default gate while leaving the
> **execution** explicit.

---

## 5. Verifier procedure (V4)

1. Extract the commands/steps from the artifact; identify the destructive/applicability命门.
2. For each: classify the target mode (`command-classification.md`), check syntax, check
   applicability against the customer environment, match against the cited doc (V1), and flag
   destructive/disruptive ops (Step 3.3 table).
3. Classify, score, emit the verdict JSON
   ([`verifier-subagent.md` §7](../../_shared/verifier/verifier-subagent.md)).
   - 🟢 PASS → present + badge ("static-validated; lab run available on request").
   - 🟡 CONCERNS → divergence from doc / missing precondition → qualify or add caveat.
   - 🔴 FAIL → invalid syntax, wrong target, or unflagged destructive op → block; ask the human (and
     offer an explicit lab run if behavioral truth is needed).

> Default static, explicit-only execution, lab VMs only — never the customer's subscription.
