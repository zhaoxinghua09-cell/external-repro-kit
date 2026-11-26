"""P2 · UIBC Bench 外部复现包

关键事实（先说清，避免外部验证者误判）：
  - 该仓未发布到 PyPI（实测 404），只能按提交号克隆；
  - 依赖 `cryptography` 未在 README 声明（不装则 s02/s02b/s09 三组 BLOCKED）；
  - 被测对象（subject）需自带 `uibc-core`，且 `vectors` 经验要求 0.5.0 才 8/8 对齐。

断言：
  1. 无 --subject 时 rc=2（预检拒绝，诚实负向行为）
  2. --quick 跑完 rc=0，自报"台子正常 / 无回归"
  3. 总账出现 PASS ≥ 170、FAIL = 8（8 条为基线已知项，非本次新增）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Harness, src_dir  # noqa: E402

BENCH = src_dir("uibc-bench", "BENCH_SRC")
SUBJECT = src_dir("uibc-core", "SUBJECT")
h = Harness("uibc-bench")
PY = h.python

commit = ""
head = os.path.join(BENCH, ".git", "HEAD")
if os.path.exists(head):
    ref = open(head, encoding="utf-8").read().strip()
    if ref.startswith("ref:"):
        rp = os.path.join(BENCH, ".git", ref.split(" ", 1)[1].strip())
        commit = open(rp, encoding="utf-8").read().strip() if os.path.exists(rp) else ref

inst = h.pip_install(["uibc-core==0.5.0", "cryptography"])
h.check("依赖安装（uibc-core==0.5.0 + cryptography）", inst["rc"] == 0, "rc=%s %s" % (inst["rc"], inst["err"][-200:]))

neg = h.run([PY, "-X", "utf8", "run.py", "--quick"], cwd=BENCH, timeout=120)
h.expect_rc("无 --subject 时预检拒绝 rc=2（负向）", neg, 2)
h.expect_contains("拒绝理由提到 subject 补全方式", neg, "subject")

pos = h.run([PY, "-X", "utf8", "run.py", "--quick", "--subject", SUBJECT], cwd=BENCH, timeout=900)
h.expect_rc("--quick 跑完 rc=0", pos, 0)
h.expect_contains("自报无回归", pos, "无回归")
h.expect_contains("不出现超时", pos, "无超时")

# 从最新一次 summary.json 读机器可读总账（比字符串匹配可靠）
import json, glob  # noqa: E402
sums = sorted(glob.glob(os.path.join(BENCH, "runs", "*", "summary.json")), key=os.path.getmtime)
totals = {}
if sums:
    d = json.load(open(sums[-1], encoding="utf-8"))
    totals = d.get("totals", {})
    h.check("总账 PASS ≥ 170", totals.get("PASS", 0) >= 170, totals)
    h.check("总账 FAIL = 8（基线已知项）", totals.get("FAIL") == 8, totals)
    h.check("总账 BLOCKED ≤ 4（缺前置，非缺陷）", totals.get("BLOCKED", 0) <= 4, totals)
else:
    h.check("找到 summary.json", False, "runs/*/summary.json 未生成")

h.finish({"pin": "git@" + (commit[:12] or "unknown"), "route": "git clone + pip 依赖",
          "subject": SUBJECT, "totals": totals})
