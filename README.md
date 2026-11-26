# external-repro-kit

Executable, self-checking reproduction packs for five agent-trust tools. Run one command, get a `RESULT.json` that says **exactly which claims held and which did not** on *your* machine.

| Pack | Project | Route | Checks | Time |
|---|---|---|---|---|
| `p1_uibc_core` | UIBC Core | PyPI `uibc-core==0.5.5` | 11 | ~1 min |
| `p2_uibc_bench` | UIBC Bench | git `8395bcc` + subject repo | 9 | ~10 min (quick run 60 s) |
| `p3_lgd_eval` | LGD-Eval | git `3ac73d0` + pytest | 4 | ~3 min |
| `p4_aitb_bench` | Assurance Instrument Test Bench (AITB, 试真台) | source install | 9 | ~3 min |
| `p5_synomosai_mcp` | SynomosAI Governance MCP | git `dd3784f`, stdlib only | 21 | ~1 min |

## Quick start

```bash
git clone --depth=1 https://github.com/zhaoxinghua09-cell/external-repro-kit
cd external-repro-kit
bash packs/run_all.sh            # Linux/macOS
```
```powershell
.\packs\run_all.ps1             # Windows
```

One pack only:

```bash
bash packs/run_all.sh p1_uibc_core
```

Each pack writes `RESULT.json` next to `verify.py` with platform, architecture, Python version, **pin (version or commit)**, per-assertion evidence, and totals. A failing assertion makes the process exit non-zero — nothing turns green silently.

## What this kit proves — and what it does not

**Proves:** these five tools can be installed and run from public sources on a clean machine, and their advertised behaviours (including negative controls) hold or fail in ways you can see line by line.

**Does not prove:** that anyone independent has verified them. The `baseline/` folder holds the maintainers' own runs (Windows 11 / Python 3.13 and Linux / Python 3.12). Those are **E2 evidence** — same operator, affiliated with the projects. Independent reproduction (E3) requires *your* run, with *your* environment recorded.

> Verification level is stated explicitly in every pack. We do not convert "the maintainer ran it" into "externally validated".

## Known expected results (read before filing a bug)

| Pack | Looks like a failure, is actually expected |
|---|---|
| p1 | `[7/8]` key swap **passes** when the owner key is not pinned — by design: without pinning there is no identity binding |
| p2 | `FAIL 8` — 7 are platform-contract cases, 1 (`s11 J17.1`) is the repo's own stale receipt; `BLOCKED 4` disappear once `cryptography` is installed; PASS count differs by 1 between Windows and Linux (170 vs 171) |
| p3 | `npm view lgd-eval` returns 404 — the npm package genuinely does not exist (the repo's README says so) |
| p4 | `aitb selftest` exits 1 with `FAIL 3` — those are planted defects the bench must catch; the field `negctl_violations` only exists on commit `5cb5cba` and later, not on the older public `f2fa09d` |
| p5 | A clean, PII-free text **without** an `FP-[A-Za-z0-9]{8,}` fingerprint is rejected (`copyright_fingerprint_missing`, medium). The rule requires a fingerprint to be present |

## Layout

```
packs/
├─ harness.py              # stdlib-only runner: subprocess, assertions, RESULT.json
├─ expected_baseline.json  # assertion counts and key numbers (ranges allowed)
├─ run_all.ps1 / run_all.sh
└─ pN_*/verify.py
baseline/pN_*/RESULT.json  # maintainer runs (E2, paths sanitized)
REPRODUCTION_GUIDE.md      # per-pack install / expected output / failure modes
VERIFICATION_POLICY.md     # who counts as an independent validator; what evidence is accepted
```

## Source repos needed

Packs that test a repository expect it under `_src/` (or an env var):

```bash
mkdir -p _src && cd _src
git clone --depth=1 https://github.com/UIBC/uibc-bench
git clone --depth=1 https://github.com/zhaoxinghua09-cell/uibc-core
git clone --depth=1 https://github.com/LGD-Eval/LGD-Eval
git clone --depth=1 https://github.com/AITB-Bench/aitb-bench
git clone --depth=1 https://github.com/zhaoxinghua09-cell/synomosai-governance-mcp
```

Override with `BENCH_SRC`, `SUBJECT`, `LGD_EVAL_SRC`, `AITB_SRC`, `MCP_REPO`.

## Reporting a result

Open an issue with the `RESULT.json` attached plus your environment. See `VERIFICATION_POLICY.md` for the receipt template and independence declaration. Disagreement is more useful than agreement — record the delta, do not edit our baseline.

## 中文说明

这一套是"复现包"，不是"认证材料"。跑通只说明工具在你机器上能装能跑；**不代表任何第三方认可**。基准文件是我们自己跑的（E2），独立复现（E3）需要你的回执。已知的"预期失败"列在上表，先对照再报问题。

## License

MIT — see `LICENSE`.
