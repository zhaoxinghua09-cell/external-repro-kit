# Reproduction Guide — per-pack details

Every pack follows the same contract: install → run → observe → compare with `packs/expected_baseline.json` → keep `RESULT.json`.
Exit code `0` means every assertion held; non-zero means at least one did not and the `[FAIL]` line says which.

Environment used for our baseline runs: Windows 11 (AMD64, Python 3.13.18) and Linux (x86_64, Python 3.12). Both recorded in `baseline/`.

---

## P1 · UIBC Core — `packs/p1_uibc_core`

**Install**
```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install uibc-core==0.5.5
```
`verify.py` creates its own `.venv` if missing; base install has **no third-party runtime dependency** (extras `verify`/`conformance`/`interop` are optional).

**Minimal run**
```bash
python -m uibc_core.cli demo
```
**Expected**
- exit 0, phases `[1/8]` … `[8/8]`, ~4 s
- `[5/8]` self-verification `PASS`
- `[6/8]` tamper → `expected FAIL: tampered content`
- `[8/8]` key swap → `key substitution caught by pinning`

**Positive control:** `[5/8]` PASS.
**Negative control (2):** tamper caught; key swap caught *only when pinned*.
**Known failure mode (by design):** `[7/8]` key swap **passes** unpinned — `verifies against itself`; read that line, it states the boundary.
**Pin:** `uibc-core==0.5.5`, Python ≥ 3.10.

---

## P2 · UIBC Bench — `packs/p2_uibc_bench`

**Install**
```bash
git clone --depth=1 https://github.com/UIBC/uibc-bench   _src/uibc-bench     # HEAD 8395bcc
git clone --depth=1 https://github.com/zhaoxinghua09-cell/uibc-core _src/uibc-core
pip install "uibc-core==0.5.0" cryptography
```
The bench's README claims "no dependencies beyond the standard library"; in practice **`cryptography` is required** or `s02`/`s02b`/`s09` come back BLOCKED.

**Minimal run**
```bash
cd _src/uibc-bench && python run.py --quick --subject ../uibc-core
```
**Expected**
- exit 0, final line states the bench is healthy (all groups produced artefacts, no timeouts, no regression vs baseline)
- totals: **PASS 170 (Windows) / 171 (Linux), FAIL 8, BLOCKED 4, REFERENCE 1**
- artefacts under `runs/<timestamp>/summary.json`

**Negative control:** `python run.py --quick` **without** `--subject` → exit **2** with three ways to supply a subject. A preflight refusal, not a crash.
**Known failure modes:**
1. missing `cryptography` → 3 groups BLOCKED;
2. `s11 J17.1` FAIL "receipt still describes this tree" is the repo's own stale receipt, not your environment;
3. PASS differs by 1 across OSes — assert a range, never equality.
**Pin:** bench `8395bcc`, subject `uibc-core==0.5.0`.

---

## P3 · LGD-Eval — `packs/p3_lgd_eval`

**Install**
```bash
git clone --depth=1 https://github.com/LGD-Eval/LGD-Eval _src/LGD-Eval   # HEAD 3ac73d0
pip install pytest
```
**Minimal run**
```bash
cd _src/LGD-Eval && python -m pytest tests -q
```
**Expected:** exit 0, `13 passed` (4.1 s on Windows, 1.4 s on Linux).
**Negative control (distribution):** `npm view lgd-eval version` → `E404` — the npm package does not exist; the repo's own README says `npx lgd-eval` will fail.
**Known failure mode:** pytest not installed (the repo does not declare a test extra); no `node` → distribution check cannot run, the rest still works.
**Pin:** `3ac73d0`.

---

## P4 · Assurance Instrument Test Bench（AITB · 试真台）— `packs/p4_aitb_bench`

**Install** (not on PyPI)
```bash
git clone --depth=1 https://github.com/AITB-Bench/aitb-bench _src/aitb-bench
cd _src/aitb-bench && pip install -e .
```
**Minimal run**
```bash
aitb demo        # or: python -m aitb_bench.core demo
aitb list
aitb selftest
```
**Expected**
- `demo` exit **0**, `PASS 3 / FAIL 0 / SKIP 0 / BLOCKED 0`, artefacts in `runs/<ts>_demo/` (`run.json`, `verdicts.json`, `report.md`, `snapshot.html`, `manifest.json`, `progress.log`)
- `selftest` exit **1**, `PASS 1 / FAIL 3`, `negctl_violations=0`

**Positive control:** `demo` all green.
**Negative control:** the 3 `[NEG-CTRL] FAIL` lines are the bench catching planted defects. Assert `rc=1 and negctl_violations=0`, **never** "all passed".
**Known failure mode (version split):** on the older public commit `f2fa09d` the field `negctl_violations` **does not exist** (string `negctl` appears 0 times in the source). It exists from `5cb5cba` onward. `demo` and `selftest` exit codes are the same on both; only the negctl assertion differs.
**Pin:** `5cb5cba` (preferred) or `f2fa09d` — say which in your receipt.

---

## P5 · SynomosAI Governance MCP — `packs/p5_synomosai_mcp`

**Install** (zero dependencies, single file)
```bash
git clone --depth=1 https://github.com/zhaoxinghua09-cell/synomosai-governance-mcp _src/synomosai-governance-mcp
# stdio: python governance_mcp_server.py
# http:  python governance_mcp_server.py --http --port 9000
```
**Minimal run:** `python verify.py` — the pack speaks JSON-RPC over stdio itself (no official SDK, so protocol defects are not masked).
**Expected**
- `initialize` → `protocolVersion: 2025-03-26`, `serverInfo.version: 1.2.2`
- `tools/list` → **6 tools**: `audit_evidence_chain`, `a3_assess`, `passport_lookup`, `compliance_checklist`, `gov_scan`, `lgd_knowledge`
- `gov_scan` on a dirty sample (email + `ghp_` token + local path + phone) → `clean=false`, rejected, 5 categories hit
- `gov_scan` on a clean sample carrying `FP-6999EE1111DE` → `clean=true`, accepted

**Negative control:** dirty sample must be rejected.
**Known failure mode:** clean text **without** an `FP-[A-Za-z0-9]{8,}` fingerprint is also rejected (`copyright_fingerprint_missing`, medium). Judge success by `result.clean`, not by process exit code.
**Pin:** `dd3784f` (server 1.2.2).

---

## Receipt template

```markdown
### Reproduction receipt · <pack> · <name or org>
- Validator class: A (technical) / B (application) / C (theory/standards)
- Affiliation with maintainers: none / declared (explain)
- Timestamp (UTC):
- OS / arch:
- Python / Node:
- Install method and pin:
- Commands executed (verbatim):
- Exit code:
- Matches expected baseline: yes / no
- Deltas (if any), item by item:
- Evidence location (log / RESULT.json):
- Statement: this receipt covers the run above only; it is not a certification.
```
