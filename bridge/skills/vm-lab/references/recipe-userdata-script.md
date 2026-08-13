# Recipe — Did the VM's user-data / init script actually run?

A worked example, not a fixed scenario. Use it as the template for any "the customer's
init automation behaves differently depending on **how the VM was built**" question.

## When to reach for this
A customer reports their **user-data / cloud-init / custom-script didn't execute**, or
runs in one build path but not another (marketplace/gallery image vs. restore-point/disk).

Real case — session `60e4550a` ("Verify VM Creation Methods"): user-data worked when the
VM was built from an **Azure Compute Gallery image**, but the *same* user-data "didn't run"
when the VM was built from a **VM restore point → OS disk**. IMDS could still serve the
`userData`, yet the script never executed.

## What the lab proves
*Whether* the script runs, and *why the build path changes the answer* — by reproducing
both paths side by side and reading a marker the script itself writes (no guessing).

## Experiment design — two variants, one RG, identical user-data
- **Variant A (control)** — fresh VM provisioned from an image + the user-data. Script *should* run.
- **Variant B (repro)** — take a restore point of a source VM → materialize an OS disk →
  build a new VM with `--attach-os-disk` + the *same* user-data. This is the customer's path.

Each user-data script stamps a **marker** so the path that executed is self-identifying
(gotchas.md §9):
```bash
echo "RAN=B iid=$(curl -s -H Metadata:true 'http://169.254.169.254/metadata/instance/compute/userData?api-version=2021-01-01&format=text') host=$(hostname) $(date -u)" | sudo tee -a /var/lab/history.log
```

## Steps — exact commands live in gotchas.md; don't re-handcraft them
1. Build RG → source VM → restore point → new disk → new VM per **gotchas.md §6**
   (the precise restore-point → disk → VM sequence).
2. Pass every script as an **LF-normalized file** with `--scripts "@file"` /
   `--user-data "@file"` (gotchas.md §1–2). Inline quoting silently corrupts the script —
   which itself *looks like* "the script didn't run", a false lead worth ruling out first.
3. Read the marker back with `az vm run-command` (runs as root, no SSH — gotchas.md §5):
   `cat /var/lab/history.log; grep -i customdata /var/lib/waagent/ovf-env.xml`.

## Reading the result — the actual root cause
The decider is **what's on the disk, not what you pass at create time** (gotchas.md §7):
- `--attach-os-disk` (specialized disk) **rejects `--custom-data`** but **accepts `--user-data`**.
- cloud-init precedence: a **stale `<CustomData>` baked into the reused disk short-circuits
  IMDS userData** (`if not ovf custom_data: fetch IMDS userData`). A restore-point disk that
  still carries the source's customData will *ignore* the new userData → "script didn't run".
- Confirm the fix in lab: clear `<CustomData>` from `/var/lib/waagent/ovf-env.xml` on the
  source **before** taking the restore point (snippet in gotchas.md §7), rebuild Variant B →
  userData now runs and the marker proves it.

## What to tell the customer
- `userData` is served **fresh per VM** (IMDS only, never persisted); `customData` is **baked
  into the disk** and travels with restore-point / disk reuse.
- If they build VMs from restore points/disks and rely on `userData`, make sure the **source
  disk carries no leftover `customData`** masking it — or standardize on `userData` and clear
  stale `customData` before snapshotting.

## Cleanup
One RG, kept by default for hands-on inspection. Teardown only on explicit confirmation:
`az group delete -n rg-userdata-lab --yes --no-wait`.
