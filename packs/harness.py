"""Phase 32 外部复现包通用执行器（无第三方依赖，仅标准库）。

设计原则：
1) 每条断言都有可打印的证据（rc、stdout 关键行、耗时）；
2) 断言失败不抛异常中断，全部跑完再汇总，便于外部验证者一次看到全部差异；
3) 结果写成 RESULT.json，含环境快照（平台/Python/包版本/Git 提交），便于审计比对。
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import time


def src_dir(name, env=None):
    """定位被测源码目录：优先环境变量，其次 <repo>/_src/<name>。缺失即明确报错退出 3。"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.environ.get(env) if env else None
    if not p:
        p = os.path.join(root, "_src", name)
    if not os.path.isdir(p):
        sys.stderr.write(
            "\n[missing source] %s\n"
            "  clone it first:  git clone --depth=1 <repo-url> _src/%s\n"
            "  or set %s to an existing checkout.\n" % (p, name, env or "the env var")
        )
        sys.exit(3)
    return p


class Harness:
    def __init__(self, name, python=None):
        self.name = name
        self.python = python or sys.executable
        self.rows = []
        self.t0 = time.time()

    # ---- 基础执行 ----
    def run(self, cmd, cwd=None, timeout=900, env=None):
        e = os.environ.copy()
        e.setdefault("PYTHONIOENCODING", "utf-8")
        if env:
            e.update(env)
        # Windows 上 git/npm 等是 .cmd 包装脚本，CreateProcess 不能直接执行，需经 cmd.exe
        resolved = list(cmd)
        if resolved and isinstance(resolved[0], str):
            path = shutil.which(resolved[0])
            if path and path.lower().endswith((".cmd", ".bat")):
                resolved = ["cmd.exe", "/c", path] + resolved[1:]
        started = time.time()
        try:
            p = subprocess.run(resolved, cwd=cwd, timeout=timeout, capture_output=True, text=True, env=e)
            rc, out, err = p.returncode, p.stdout or "", p.stderr or ""
        except subprocess.TimeoutExpired as ex:
            rc, out, err = "TIMEOUT", (ex.stdout or ""), (ex.stderr or "")
        return {"cmd": cmd, "cwd": cwd, "rc": rc, "out": out, "err": err,
                "seconds": round(time.time() - started, 1)}

    # ---- 断言 ----
    def check(self, label, cond, evidence):
        ok = bool(cond)
        self.rows.append({"label": label, "ok": ok, "evidence": str(evidence)[:600]})
        print(("[PASS] " if ok else "[FAIL] ") + label + " :: " + str(evidence)[:220].replace("\n", " | "))
        return ok

    def expect_rc(self, label, res, expected):
        return self.check(label, res["rc"] == expected,
                          "rc=%s (expected %s) %.1fs" % (res["rc"], expected, res["seconds"]))

    def expect_contains(self, label, res, needle):
        return self.check(label, needle in (res["out"] + res["err"]), "needle=%r" % needle)

    def expect_not_contains(self, label, res, needle):
        return self.check(label, needle not in (res["out"] + res["err"]), "absent=%r" % needle)

    # ---- 收尾 ----
    def finish(self, extra=None):
        snap = {
            "pack": self.name,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "python_path": self.python,
            "cwd": os.getcwd(),
            "when_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seconds_total": round(time.time() - self.t0, 1),
            "checks": self.rows,
            "passed": sum(1 for r in self.rows if r["ok"]),
            "failed": sum(1 for r in self.rows if not r["ok"]),
        }
        if extra:
            snap.update(extra)
        outdir = os.environ.get("REPRO_OUT") or os.getcwd()
        with open(os.path.join(outdir, "RESULT.json"), "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=2)
        print("\n=== %s: %d passed / %d failed in %.1fs ===" % (
            self.name, snap["passed"], snap["failed"], snap["seconds_total"]))
        sys.exit(0 if snap["failed"] == 0 else 1)

    # ---- 工具 ----
    @staticmethod
    def which(name):
        return shutil.which(name)

    def pip_install(self, args, cwd=None):
        return self.run([self.python, "-m", "pip", "install", "--disable-pip-version-check", "-q"] + args,
                        cwd=cwd, timeout=600)
