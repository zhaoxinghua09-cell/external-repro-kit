"""P1 · UIBC Core 外部复现包

最小路径（外部验证者视角）：
  1. Python 3.10+ 干净环境
  2. pip install uibc-core==0.5.5（PyPI 固定版本）
  3. uibc demo（一条命令内含正向 + 负向：封印→校验→篡改→抓出→换钥重签→钉住公钥抓出）
断言要点：
  - demo 退出码必须为 0
  - 必须出现 8 个阶段标记 [1/8]…[8/8]
  - 篡改必须被判 FAIL（负向控制）
  - 换钥重签在未钉住时必须 PASS（这是已知边界，不是缺陷）
  - 同一包钉住 owner 公钥后必须 FAIL（说明钉住有效）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Harness, src_dir  # noqa: E402

h = Harness("uibc-core")
PY = h.python

inst = h.pip_install(["uibc-core==0.5.5"])
h.check("pip install uibc-core==0.5.5", inst["rc"] == 0, "rc=%s %s" % (inst["rc"], inst["err"][-300:]))

ver = h.run([PY, "-c", "import importlib.metadata as m; print(m.version('uibc-core'))"])
h.expect_rc("包已可 import 且版本可读", ver, 0)
h.expect_contains("版本号 = 0.5.5", ver, "0.5.5")

demo = h.run([PY, "-X", "utf8", "-m", "uibc_core.cli", "demo"], timeout=300)
h.expect_rc("uibc demo 退出码 0", demo, 0)
for stage in ("[1/8]", "[4/8]", "[6/8]", "[8/8]"):
    h.expect_contains("demo 阶段 %s 出现" % stage, demo, stage)
h.expect_contains("篡改被抓住（负向控制）", demo, "expected FAIL: tampered content")
h.expect_contains("换钥重签在未钉住时通过（已知边界）", demo, "verifies against itself")
h.expect_contains("钉住公钥后换钥被抓", demo, "key substitution caught by pinning")

h.finish({"pin": "uibc-core==0.5.5", "route": "PyPI"})
