"""P4 · AITB-Bench 外部复现包（Assurance Instrument Test Bench / 试真台）

路径：从源码安装（PyPI 未发布，2026-11-26 实测 404），固定提交号。
断言要点（正向 + 负向必须成对）：
  1. aitb demo   → rc=0，PASS 3 / FAIL 0（正向：一个绿）
  2. aitb list   → 可列出预设（说明包数据 presets/*.json 装进去了）
  3. aitb selftest → rc=1 且 negctl_violations=0（负向：台子必须会红；README 明示 exit 1 是期望结果）
注意：selftest 的计数行会出现 "PASS 1 / FAIL 3"，这是负控被正确抓出的表现，不是缺陷；
      因此本包断言 rc=1 + negctl_violations=0，而不断言 "全 PASS"。
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Harness, src_dir  # noqa: E402

SRC = src_dir("aitb-bench", "AITB_SRC")
h = Harness("aitb-bench")
PY = h.python

git = h.run(["git", "--version"], cwd=SRC)
h.check("git 可用（记录环境用，不作为复现前提）", git["rc"] == 0, "rc=%s %s" % (git["rc"], (git["out"] + git["err"]).strip()[:120]))
commit = ""
head = os.path.join(SRC, ".git", "HEAD")
if os.path.exists(head):
    ref = open(head, encoding="utf-8").read().strip()
    if ref.startswith("ref:"):
        rp = os.path.join(SRC, ".git", ref.split(" ", 1)[1].strip())
        commit = open(rp, encoding="utf-8").read().strip() if os.path.exists(rp) else ref
    else:
        commit = ref

inst = h.pip_install(["-e", "."], cwd=SRC)
h.check("pip install -e .（源码安装）", inst["rc"] == 0, "rc=%s %s" % (inst["rc"], inst["err"][-300:]))

demo = h.run([PY, "-X", "utf8", "-m", "aitb_bench.core", "demo"], cwd=SRC, timeout=600)
h.expect_rc("aitb demo 退出码 0（正向）", demo, 0)
h.expect_contains("demo 三项全绿", demo, '{"PASS": 3, "FAIL": 0')

lst = h.run([PY, "-X", "utf8", "-m", "aitb_bench.core", "list"], cwd=SRC)
h.expect_rc("aitb list 可执行", lst, 0)
h.expect_contains("预设 demo 在场（包数据已安装）", lst, "demo")
h.expect_contains("预设 selftest 在场", lst, "selftest")

self_t = h.run([PY, "-X", "utf8", "-m", "aitb_bench.core", "selftest"], cwd=SRC, timeout=900)
h.expect_rc("aitb selftest 退出码 1（负向：台子会红）", self_t, 1)
h.expect_contains("负控违规数为 0（负控本身有效）", self_t, "negctl_violations=0")

h.finish({"pin": "source@" + commit, "route": "git+pip -e", "note": "PyPI 未发布，实测 404"})
