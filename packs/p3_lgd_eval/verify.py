"""P3 · LGD-Eval 外部复现包

两件事必验：
  1. 测试集能跑（正向）：pytest tests → 13 passed；
  2. npm 分发不存在（负向事实）：`npm view lgd-eval version` 返回非 0（README 自己承认 npx 会 404）。
     —— 这条不是为了"证明有 bug"，而是把维护者自述与 registry 实况对齐。
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Harness, src_dir  # noqa: E402

REPO = src_dir("lgd-eval", "LGD_EVAL_SRC")
h = Harness("lgd-eval")
PY = h.python

commit = ""
head = os.path.join(REPO, ".git", "HEAD")
if os.path.exists(head):
    ref = open(head, encoding="utf-8").read().strip()
    if ref.startswith("ref:"):
        rp = os.path.join(REPO, ".git", ref.split(" ", 1)[1].strip())
        commit = open(rp, encoding="utf-8").read().strip() if os.path.exists(rp) else ref

inst = h.pip_install(["pytest"])
h.check("安装 pytest", inst["rc"] == 0, "rc=%s" % inst["rc"])

t = h.run([PY, "-X", "utf8", "-m", "pytest", "tests", "-q"], cwd=REPO, timeout=600)
h.expect_rc("pytest tests rc=0", t, 0)
h.expect_contains("13 个用例通过", t, "13 passed")

npm = shutil.which("npm") or shutil.which("npm.cmd")
if npm:
    cmd = ["cmd.exe", "/c", npm, "view", "lgd-eval", "version"] if npm.lower().endswith(".cmd") else [npm, "view", "lgd-eval", "version"]
    v = h.run(cmd, cwd=REPO, timeout=180)
    h.check("npm registry 无 lgd-eval（README 自述 404 属实）", v["rc"] != 0 and "404" in (v["out"] + v["err"]),
            "rc=%s %s" % (v["rc"], (v["out"] + v["err"]).strip()[:180]))
else:
    h.check("npm 可用（用于验证分发状态）", False, "npm 不存在")

h.finish({"pin": "git@" + (commit[:12] or "unknown"), "route": "git clone + pytest"})
