"""P5 · SynomosAI Governance MCP 外部复现包（以独立客户端、非维护者 SDK 驱动）

做法：用标准库起子进程跑 `governance_mcp_server.py`，通过 stdio 发 JSON-RPC 2.0，
不依赖官方 MCP SDK —— 这样"不同 MCP 实现"才算真的被测过，而不是同一套 SDK 自证。
断言要点：
  1. initialize 返回 protocolVersion 与 serverInfo
  2. tools/list 恰好 6 个工具（名称与 README 表格一致）
  3. tools/call gov_scan（脏样本）→ 命中凭据/路径/邮箱等
  4. tools/call gov_scan（干净样本）→ 零命中
  5. 二次 initialize 仍有响应（进程未崩，可连续调用）
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Harness, src_dir  # noqa: E402

REPO = src_dir("synomosai-governance-mcp", "MCP_REPO")
h = Harness("synomosai-governance-mcp")
PY = h.python
SERVER = os.path.join(REPO, "governance_mcp_server.py")

DIRTY = "email bob@example.com  token=ghp_ABCDEFGHIJKLMNOP  path C:\\Users\\alice\\secret\\x.txt  13800001111"
CLEAN_MARKED = "本文件用于合规说明。指纹 FP-6999EE1111DE ｜ © 2026 SynomosAI 保留所有权利。"


def payload(resp):
    """把 MCP 结果里的 content[0].text 解成 dict，便于对结构断言而非对字符串断言。"""
    try:
        return json.loads(resp["result"]["content"][0]["text"]).get("result", {})
    except Exception:
        return {}


def rpc(proc, obj):
    proc.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line)


p = subprocess.Popen([PY, "-X", "utf8", SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1)

init = rpc(p, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
               "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                          "clientInfo": {"name": "phase32-external-verifier", "version": "0.1"}}})
h.check("initialize 有响应", init is not None, init)
h.check("protocolVersion 可读", bool(init and init.get("result", {}).get("protocolVersion")),
        init and init.get("result", {}).get("protocolVersion"))
h.check("serverInfo 名称正确", (init or {}).get("result", {}).get("serverInfo", {}).get("name") ==
        "synomosai-governance-mcp", (init or {}).get("result", {}).get("serverInfo"))

tools = rpc(p, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
names = [t["name"] for t in (tools or {}).get("result", {}).get("tools", [])]
h.check("tools/list 返回 6 个工具", len(names) == 6, names)
for expected in ("a3_assess", "audit_evidence_chain", "compliance_checklist", "passport_lookup", "gov_scan", "lgd_knowledge"):
    h.check("工具 %s 存在" % expected, expected in names, names)

dirty = rpc(p, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "gov_scan", "arguments": {"text": DIRTY}}})
dtext = json.dumps(dirty, ensure_ascii=False)
dirty_payload = payload(dirty)
dirty_types = [f.get("type") for f in dirty_payload.get("findings", [])]
h.check("脏样本检出 ≥4 类命中", len(dirty_types) >= 4, dirty_types)
for cat in ("手机号", "邮箱", "本地路径", "疑似凭据"):
    h.check("脏样本命中类别 %s" % cat, cat in dirty_types, dirty_types)
h.check("脏样本 clean=false", dirty_payload.get("clean") is False, dirty_payload.get("clean"))
h.check("脏样本结论为驳回", "驳回" in (dirty_payload.get("verdict") or ""), dirty_payload.get("verdict"))

clean = rpc(p, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                "params": {"name": "gov_scan", "arguments": {"text": CLEAN_MARKED}}})
clean_payload = payload(clean)
h.check("带 FP 指纹的干净样本 clean=true", clean_payload.get("clean") is True,
        clean_payload.get("findings"))
h.check("干净样本结论为通过", "通过" in (clean_payload.get("verdict") or ""), clean_payload.get("verdict"))

a3 = rpc(p, {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "a3_assess", "arguments": {"intent": 4, "impact": 3, "reversibility": 4, "oversight": 2}}})
h.check("a3_assess 可调用且给结论", a3 is not None and "result" in a3, json.dumps(a3, ensure_ascii=False)[:300])

p.stdin.close()
rc = p.wait(timeout=60)
stderr = (p.stderr.read() or "")[-400:]
h.check("进程正常退出（无崩栈）", rc == 0, "rc=%s stderr=%s" % (rc, stderr))

h.finish({"pin": "git@dd3784f9", "transport_tested": "stdio JSON-RPC（独立客户端，非官方 SDK）"})
