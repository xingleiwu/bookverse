#!/usr/bin/env python3
"""MCP 服务器冒烟测试：spawn server.py，走一遍协议握手 + 全部工具调用。

数据依赖项的夹具全部从被测书库动态采集（get_book / get_concept 的空参回退
会列出全部书名/概念名），测试不绑定任何具体书库；空书库（新装/CI）自动跳过。
"""
import json
import re
import subprocess
import sys

SERVER = str(__import__("pathlib").Path(__file__).parent / "server.py")


def main():
    proc = subprocess.Popen([sys.executable, SERVER], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    failures = []

    def send(req):
        proc.stdin.write(json.dumps(req, ensure_ascii=False) + "\n")
        proc.stdin.flush()

    def recv(rid):
        for _ in range(50):
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            resp = json.loads(line)
            if resp.get("id") == rid:
                return resp
        return None

    def call(rid, name, args):
        send({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
              "params": {"name": name, "arguments": args}})
        r = recv(rid)
        return r["result"]["content"][0]["text"] if r else ""

    def check(name, cond, detail=""):
        print(("  PASS " if cond else "  FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    # 1. initialize
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test"}}})
    r = recv(1)
    check("initialize", r and r["result"]["serverInfo"]["name"] == "reading-universe", str(r))

    # 2. initialized 通知（不应有响应，后续 id 正常返回即证明未堵管道）
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # 3. tools/list
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    r = recv(2)
    tools = [t["name"] for t in r["result"]["tools"]] if r else []
    check("tools/list", set(tools) == {"search_universe", "get_concept", "get_book",
                                       "neighbors", "get_emergent", "get_persona", "cite"}, str(tools))

    # 4. 动态采集夹具：get_book 空参 → 「未找到书「」。已拆书目：A、B、C」
    listing = call(3, "get_book", {"slug_or_title": ""})
    m = re.search(r"已拆书目：(.+)$", listing)
    titles = [t.strip() for t in m.group(1).split("、")] if m and m.group(1).strip() else []
    check("get_book 空参列举", m is not None, listing[:120])

    first_concept = ""
    if titles:
        # 5. get_concept 空参 → 现有概念清单
        clisting = call(4, "get_concept", {"name": ""})
        m2 = re.search(r"现有概念：(.+)$", clisting)
        concepts = [c.strip() for c in m2.group(1).split("、")] if m2 and m2.group(1).strip() else []
        first_concept = concepts[0] if concepts else ""
        check("get_concept 空参列举", bool(first_concept), clisting[:120])

        # 6. get_book 正常路径（动态首个书名）
        detail = call(5, "get_book", {"slug_or_title": titles[0]})
        check("get_book 详情", titles[0] in detail, detail[:150])

    if first_concept:
        # 7. cite / 8. neighbors / 9. search（动态首个概念）
        cited = call(6, "cite", {"topic": first_concept})
        check("cite 动态概念", first_concept in cited or "→" in cited, cited[:150])
        nb = call(7, "neighbors", {"node": first_concept})
        check("neighbors 动态概念", first_concept in nb or "→" in nb, nb[:150])
        se = call(8, "search_universe", {"query": first_concept})
        check("search 动态概念", first_concept in se or "命中" in se, se[:150])

    if titles:
        # 10. get_emergent（返回非空即可，不绑定具体观点）
        em = call(9, "get_emergent", {})
        check("get_emergent", len(em.strip()) > 0, em[:100])

    if not titles:
        print("  SKIP 数据依赖项（空书库：新装/CI 环境，仅验证协议层）")

    # 11. resources/list
    send({"jsonrpc": "2.0", "id": 10, "method": "resources/list"})
    r = recv(10)
    check("resources/list", r is not None and isinstance(r.get("result", {}).get("resources"), list))

    # 12. 未知方法错误
    send({"jsonrpc": "2.0", "id": 11, "method": "no/such"})
    r = recv(11)
    check("unknown method → -32601", r and r.get("error", {}).get("code") == -32601)

    proc.stdin.close()
    proc.terminate()
    print()
    if failures:
        print(f"✗ {len(failures)} 项失败：{failures}")
        sys.exit(1)
    print("✓ 全部通过")


if __name__ == "__main__":
    main()
