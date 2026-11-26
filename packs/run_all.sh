#!/usr/bin/env bash
# Run all reproduction packs (Linux / macOS)
#   bash run_all.sh              run all
#   bash run_all.sh p1_uibc_core run one
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"

if [ $# -ge 1 ]; then PACKS=("$1"); else PACKS=(p1_uibc_core p2_uibc_bench p3_lgd_eval p4_aitb_bench p5_synomosai_mcp); fi

FAILED=0
for p in "${PACKS[@]}"; do
    DIR="$ROOT/$p"
    EXE="$PY"
    if [ "$p" = "p1_uibc_core" ] && [ -x "$DIR/.venv/bin/python" ]; then EXE="$DIR/.venv/bin/python"; fi
    echo "==> $p"
    ( cd "$DIR" && "$EXE" -X utf8 verify.py )
    RC=$?
    if [ -f "$DIR/RESULT.json" ]; then
        "$PY" - "$DIR/RESULT.json" <<'EOF'
import json,sys
j=json.load(open(sys.argv[1],encoding="utf-8"))
print(f"    passed={j['passed']} failed={j['failed']} pin={j['pin']} -> {j['seconds_total']}s")
EOF
    fi
    [ $RC -ne 0 ] && FAILED=$((FAILED+1))
done

if [ $FAILED -gt 0 ]; then echo "FAILED: $FAILED pack(s)"; exit 1; fi
echo "ALL PACKS PASS"
