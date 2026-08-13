# Verification Pack — V6: Scope / Route Decision

> **V-type:** V6 — *is the scope verdict correct and does the recommended SAP actually map to this
> problem?*
> **Used by:** `vm-case-triage` (Stage R), invoked before the
> closing action: the user changes the Support Area Path in DFM and clicks **Transfer**.
> **Contract:** [`_shared/verifier/verifier-subagent.md`](../../_shared/verifier/verifier-subagent.md) ·
> [`_shared/verifier/evidence-ledger.md`](../../_shared/verifier/evidence-ledger.md)

V6 settles by **table lookup, not re-run** — the truth lives in local catalogs, not a Kusto
cluster. The verifier re-queries `sap-tree-full.json` to confirm the recommended path **exists**
and re-applies `scope-decision-tree.md` / `support-boundary-rules.md` to confirm the verdict. The
mechanical question: *does the recommended SAP path literally exist in the tree, and does the
keyword chain that selected it match this case's problem domain?*

---

## 1. Truth source — local catalogs (look up; do NOT trust the maker's recall)

| Decision | Truth source | Lookup |
|---|---|---|
| Does the SAP path exist? | `references/sap-tree-full.json` (53k+ paths) | re-query by keyword; the recommended `path` must be a real node, not a plausible-looking string. |
| In/out of VM-Storage scope? | `references/scope-decision-tree.md` + `references/support-area-path-catalog.md` | re-apply the decision tree to the case keywords. |
| Borderline ownership? | `references/support-boundary-rules.md` (29 scenarios) | the verdict must cite the specific scenario # that governs. |
| Owning-team name | `support-area-path-map.md` | cross-check the team for VM-adjacent paths. |

```python
# Re-query the tree (run from the skill dir; UTF-8 mandatory or cp1252 crashes)
python -c "import json; [print(n['path']) for n in json.load(open('references/sap-tree-full.json', encoding='utf-8')) if '<kw>' in n['path']]"
```

> ⚠ **`sap-tree-full.json` is a ~14 MB machine-local artifact, NOT in git.** If it is missing, the
> verifier **cannot** mechanically confirm the path exists → return `UNSUPPORTED` honestly (do not
> guess the path is valid). Fall back to the online SAP Tree tool
> (`references/sap-tree-tool-guide.md`); a fresh clone / CI will not have the file.

---

## 2. 命门 (load-bearing claims) for V6

| Is命门 | Is NOT命门 |
|---|---|
| The **SAP hit that drives the owning team** — the exact path the case will be transferred to. | General domain discussion. |
| The **in/out-of-scope verdict** that drives the transfer-vs-keep decision. | Background restating of the symptom. |
| For a disputed case, the **boundary scenario** that settles ownership. | Non-controlling boundary commentary. |

This is settle-by-lookup, so "re-run" = re-query the JSON + re-read the rule. No 2–3 cap pressure —
usually one path + one scope verdict.

---

## 3. Checklist

| # | Check | Fail → class |
|---|---|---|
| 1 | **Path exists** — the recommended SAP path is a literal node in `sap-tree-full.json`. | Not found → `CONTRADICTED` (fabricated path). Tree missing → `UNSUPPORTED`. |
| 2 | **Path matches the problem domain** — the keyword chain that selected it actually corresponds to the case symptom (not an adjacent product, e.g. Blob→CSS Storage not AzureStorageDevices). | Wrong domain → `CONTRADICTED`. |
| 3 | **Scope verdict matches the tree** — in/out verdict follows `scope-decision-tree.md` for the case keywords. | Contradicts tree → `CONTRADICTED`. |
| 4 | **Borderline cited** — a disputed-ownership verdict names the governing `support-boundary-rules.md` scenario #. | Asserted without citing a scenario → `INFERRED` (boundary interpretation carries judgment) — surface it. |
| 5 | **Team name matches the path** — the owning team (if named) is the one mapped to that path. | Mismatch → `UNSUPPORTED`. |

---

## 4. Why borderline = INFERRED, not GROUNDED

Path existence and scope-tree match are mechanical (string lookup) → `GROUNDED`/`CONTRADICTED`.
But **boundary-ownership** calls (SQL-on-VM, Bastion, Managed Identity, ASR, Key Vault…) involve
reading a scenario rule against fuzzy case facts — that is `INFERRED` unless the scenario is an
exact, unambiguous match. Flag these so the human eyeballs the ownership call before transferring;
a wrong transfer ping-pongs the case.

---

## 5. Verifier procedure (V6)

1. Pull the recommended SAP path + scope verdict from the artifact/ledger.
2. **Re-query** `sap-tree-full.json` for the path; confirm it exists verbatim (or `UNSUPPORTED` if
   the file is absent).
3. **Re-apply** `scope-decision-tree.md` to the case keywords; confirm the in/out verdict.
4. For disputed ownership, confirm the cited `support-boundary-rules.md` scenario governs.
5. Classify, score, emit the verdict JSON
   ([`verifier-subagent.md` §7](../../_shared/verifier/verifier-subagent.md)).
   - 🟢 PASS → present the path + a one-line "confirmed in tree" badge; the **user** changes the SAP
     in DFM and clicks Transfer.
   - 🟡 CONCERNS → borderline ownership uncited → surface the scenario for human judgement.
   - 🔴 FAIL → fabricated/wrong path → block; show the actual tree matches, ask the human.

> Pure local-catalog lookup — no customer subscription, no Kusto. The user always performs the SAP
> change + Transfer manually (assistant rule).
