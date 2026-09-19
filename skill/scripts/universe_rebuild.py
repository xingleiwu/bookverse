#!/usr/bin/env python3
"""reading-universe · 阅读宇宙 MCP 服务器（零依赖，stdio 传输）

让任何 MCP 客户端（ZCode / Claude Desktop / Cursor 等）在日常对话中检索、
引用已拆书目的内容与概念——像真人一样旁征博引。

数据源（全部为 markdown 事实源，只读）：
  <UNIVERSE_PATH>/books/*.md           书节点（frontmatter + 连接）
  <UNIVERSE_PATH>/concepts/*.md        概念节点（各书论述对照表）
  <UNIVERSE_PATH>/graph/edges.jsonl    边表
  <UNIVERSE_PATH>/emergent.md          涌现台账
  <UNIVERSE_PATH>/persona/profile.md   读者人格
  <BOOKS_PATH>/*/03-synthesis/level1.md     泛化报告（取「一段话总结」）
  <BOOKS_PATH>/*/06-takeaway/*.md           传播物料（napkin 钩子 / brief 等）

环境变量：
  UNIVERSE_PATH  宇宙目录（默认读 ~/.agents/skills/bookverse/config.yaml 的 workspace_root/universe）
  BOOKS_PATH     拆书根目录（默认 UNIVERSE_PATH/../books）

工具：
  search_universe  全库检索（书/概念/涌现/金句）
  get_concept      概念详情（各书对照表——旁征博引的核心）
  get_book         书详情（一句话总结 + 核心主张 + 物料清单）
  neighbors        节点邻接（相关概念与书目）
  get_emergent     涌现观点台账
  get_persona      读者人格档案
  cite             组合引用：给定话题，返回可直接贴进对话的引用块
"""
import json
import os
import re
import sys
from pathlib import Path

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "reading-universe", "version": "0.1.0"}

HOME = Path.home()


def _cfg_from_file():
    """skill 零真实地址：从 config.yaml（skill 安装目录 > 本项目根）读键值。"""
    vals = {}
    for cfg in (HOME / ".agents" / "skills" / "bookverse" / "config.yaml",
                Path(__file__).resolve().parent.parent.parent / "config.yaml"):
        if cfg.exists():
            for line in cfg.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^(\w[\w-]*):\s*(.+?)\s*$", line)
                if m and not m.group(2).lstrip().startswith("<"):
                    vals[m.group(1)] = Path(m.group(2).strip().strip("'\"")).expanduser()
    return vals


_CFG = _cfg_from_config() if False else _cfg_from_file()


def _universe_from_config():
    return _CFG.get("universe_root") or (_CFG.get("workspace_root") / "universe" if _CFG.get("workspace_root") else None)


UNIVERSE = (Path(os.environ["UNIVERSE_PATH"]).expanduser()
            if os.environ.get("UNIVERSE_PATH") else _universe_from_config())
if not UNIVERSE or not UNIVERSE.exists():
    print("未找到宇宙目录：请设 UNIVERSE_PATH 环境变量，或在 ~/.agents/skills/bookverse/config.yaml 写入 "
          "workspace_root（模板见 bookverse/skill/config.example.yaml）", file=sys.stderr)
    raise SystemExit(2)
BOOKS = (Path(os.environ["BOOKS_PATH"]).expanduser() if os.environ.get("BOOKS_PATH") else
         (_CFG.get("corpus_root") or (_CFG.get("workspace_root") if _CFG.get("workspace_root") else UNIVERSE.parent / "corpus")))


# ---------- 极简 frontmatter / md 解析 ----------

def parse_frontmatter(text: str):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    fm, current = {}, None
    body_start = len(lines)
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = i + 1
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\S[^:]*):\s*(.*)$", line)
        if m and not line.startswith((" ", "-", "\t")):
            key, val = m.group(1).strip(), m.group(2).strip()
            if val == "":
                fm[key], current = [], key
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                fm[key] = [v.strip().strip("\"'") for v in inner.split(",")] if inner else []
                current = None
            else:
                fm[key] = val.strip("\"'")
                current = None
        elif line.lstrip().startswith("- ") and current is not None:
            if isinstance(fm.get(current), list):
                fm[current].append(line.lstrip()[2:].strip().strip("\"'"))
    return fm, "\n".join(lines[body_start:])


def read(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


# ---------- 语料加载 ----------

def load_corpus():
    corpus = {"books": {}, "concepts": {}, "edges": [], "takeaways": {}}
    if (UNIVERSE / "books").exists():
        for f in sorted((UNIVERSE / "books").rglob("*.md")):
            fm, body = parse_frontmatter(read(f))
            if fm:
                corpus["books"][f.stem] = {"slug": f.stem, "fm": fm, "body": body, "path": f}
    if (UNIVERSE / "concepts").exists():
        for f in sorted((UNIVERSE / "concepts").rglob("*.md")):
            fm, body = parse_frontmatter(read(f))
            if fm:
                name = fm.get("concept", f.stem)
                corpus["concepts"][f.stem] = {
                    "stem": f.stem, "name": name, "fm": fm, "body": body, "path": f,
                    "aliases": fm.get("aliases", []) if isinstance(fm.get("aliases"), list) else [],
                }
    ej = UNIVERSE / "graph" / "edges.jsonl"
    if ej.exists():
        for line in read(ej).splitlines():
            line = line.strip()
            if line:
                try:
                    corpus["edges"].append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if BOOKS.exists():
        for d in sorted(BOOKS.iterdir()):
            if not d.is_dir():
                continue
            takes = {}
            tdir = d / "06-takeaway"
            if tdir.exists():
                for f in sorted(tdir.glob("*.md")):
                    takes[f.stem] = read(f)
            l1 = d / "03-synthesis" / "level1.md"
            corpus["takeaways"][d.name] = {"takeaways": takes, "level1": read(l1) if l1.exists() else ""}
    return corpus


def one_liner(book_slug: str, corpus) -> str:
    l1 = corpus["takeaways"].get(book_slug, {}).get("level1", "")
    m = re.search(r"## 一段话总结\s*\n+(.+?)(?:\n\n|\n#)", l1, re.S)
    return m.group(1).strip() if m else ""


def find_concept(corpus, name: str):
    n = name.strip().lower()
    for node in corpus["concepts"].values():
        if n in (node["name"].lower(), node["stem"].lower(),
                 *[a.lower() for a in node["aliases"]]):
            return node
    for node in corpus["concepts"].values():
        if n in node["name"].lower() or any(n in a.lower() for a in node["aliases"]):
            return node
    return None


def find_book(corpus, key: str):
    k = key.strip().lower()
    for b in corpus["books"].values():
        if k in (b["slug"].lower(), str(b["fm"].get("title", "")).lower()):
            return b
    for b in corpus["books"].values():
        if k in b["slug"].lower() or k in str(b["fm"].get("title", "")).lower():
            return b
    return None


def tokenize(q: str):
    return [t for t in re.split(r"[\s，。,、；;：:！?？]+", q.strip()) if t]


def score_text(text: str, tokens):
    low = text.lower()
    return sum(low.count(t.lower()) for t in tokens if t)


# ---------- 工具实现 ----------

def tool_search_universe(args, corpus):
    q = str(args.get("query", "")).strip()
    limit = int(args.get("limit", 8))
    if not q:
        return "请给出检索词，如：交易费用 / 需求定律 / 涌现"
    tokens = tokenize(q)
    hits = []
    for node in corpus["concepts"].values():
        s = score_text(node["name"], tokens) * 3
        s += score_text(" ".join(node["aliases"]), tokens) * 3
        s += score_text(node["body"], tokens)
        if s:
            hits.append((s, "concept", node["name"], node["body"], str(node["path"])))
    for b in corpus["books"].values():
        s = score_text(f"{b['fm'].get('title','')} {b['fm'].get('author','')}", tokens) * 3
        s += score_text(" ".join(b["fm"].get("themes", []) or []), tokens) * 2
        s += score_text(b["body"], tokens)
        ol = one_liner(b["slug"], corpus)
        s += score_text(ol, tokens) * 2
        if s:
            hits.append((s, "book", str(b["fm"].get("title", b["slug"])),
                         ol or b["body"][:300], str(b["path"])))
    em = read(UNIVERSE / "emergent.md")
    for m in re.finditer(r"\d+\.\s*\*\*「([^」]+)」\*\*：(.+?)(?=\n\d+\.|\n##|$)", em, re.S):
        s = score_text(m.group(1) + m.group(2), tokens)
        if s:
            hits.append((s, "emergent", m.group(1), m.group(2).strip()[:300], str(UNIVERSE / "emergent.md")))
    hits.sort(key=lambda x: -x[0])
    if not hits:
        return f"宇宙中未检索到与「{q}」相关的内容（当前 {len(corpus['books'])} 本书 / {len(corpus['concepts'])} 个概念）。"
    out = [f"检索「{q}」— 命中 {len(hits[:limit])} 条：\n"]
    for s, kind, name, excerpt, path in hits[:limit]:
        excerpt = re.sub(r"\n+", " ", excerpt).strip()[:260]
        out.append(f"### [{kind}] {name}（相关度 {s}）\n{excerpt}\n→ {path}\n")
    return "\n".join(out)


def tool_get_concept(args, corpus):
    name = str(args.get("name", "")).strip()
    node = find_concept(corpus, name) if name else None
    if not node:
        return f"未找到概念「{name}」。现有概念：{'、'.join(c['name'] for c in corpus['concepts'].values())}"
    aliases = f"（别名：{'、'.join(node['aliases'])}）" if node["aliases"] else ""
    return f"# 概念：{node['name']}{aliases}\n\n{node['body']}\n\n→ {node['path']}"


def tool_get_book(args, corpus):
    key = str(args.get("slug_or_title", "")).strip()
    b = find_book(corpus, key) if key else None
    if not b:
        return f"未找到书「{key}」。已拆书目：{'、'.join(b['fm'].get('title', s) for s, b in corpus['books'].items())}"
    slug = b["slug"]
    ol = one_liner(slug, corpus)
    takes = corpus["takeaways"].get(slug, {}).get("takeaways", {})
    take_list = "、".join(takes.keys()) if takes else "无"
    brief = takes.get("brief", "")
    core = ""
    if brief:
        m = re.search(r"core-claim:\s*(.+)", brief)
        if m:
            core = f"\n\n**核心主张**：{m.group(1).strip()}"
    themes = "、".join(b["fm"].get("themes", []) or [])
    return (f"# {b['fm'].get('title', slug)}\n\n"
            f"- 作者：{b['fm'].get('author','')}\n- 类型：{b['fm'].get('type','')}\n"
            f"- 拆书日期：{b['fm'].get('date-torn','')}\n- 主题：{themes}\n"
            f"- 物料：{take_list}{core}\n\n## 一段话总结\n\n{ol or '（见 level1.md）'}\n\n"
            f"## 书节点原文\n\n{b['body']}\n\n→ {b['path']}")


def tool_neighbors(args, corpus):
    node = str(args.get("node", "")).strip()
    c = find_concept(corpus, node)
    b = find_book(corpus, node)
    slug = None
    if c:
        slug = c["stem"]
    elif b:
        slug = b["slug"]
    else:
        slug = node
    rel = [e for e in corpus["edges"]
           if slug in e.get("source", "") + "|" + e.get("target", "")
           or node in e.get("source", "") + "|" + e.get("target", "")]
    if not rel:
        return f"节点「{node}」暂无边。总边数 {len(corpus['edges'])}。"
    lines = [f"节点「{node}」的邻接（{len(rel)} 条边）："]
    for e in rel:
        arrow = "→" if e["source"].endswith(slug) or e["source"] == node else "←"
        lines.append(f"- {e['source']} {arrow} [{e['relation']}] {e['target']}")
    return "\n".join(lines)


def tool_get_emergent(args, corpus):
    em = read(UNIVERSE / "emergent.md")
    return em or "涌现台账为空。"


def tool_get_persona(args, corpus):
    p = read(UNIVERSE / "persona" / "profile.md")
    return p or "人格档案尚未创建。"


def tool_cite(args, corpus):
    topic = str(args.get("topic", "")).strip()
    tokens = tokenize(topic)
    if not tokens:
        return "请给出话题，如：机会成本 / 免疫结构"
    best = None
    best_s = 0
    for node in corpus["concepts"].values():
        s = score_text(node["name"] + " ".join(node["aliases"]), tokens) * 3
        s += score_text(node["body"], tokens)
        if s > best_s:
            best, best_s = node, s
    if not best:
        return f"宇宙中暂无可引用的内容匹配「{topic}」（已拆 {len(corpus['books'])} 本书）。"
    rows = re.findall(r"^\| (?!书 \|)(.+?) \| (.+?) \| (.+?) \| (.+?) \|$", best["body"], re.M)
    out = [f"**关于「{best['name']}」**（引用自阅读宇宙）："]
    for who, stance, point, loc in rows[:4]:
        out.append(f"- **{who.strip()}**（{stance.strip()}）：{point.strip()} {loc.strip()}")
    for slug, tk in corpus["takeaways"].items():
        nap = tk.get("takeaways", {}).get("napkin", "")
        for m in re.finditer(r"^- (.+)$", nap, re.M):
            if score_text(m.group(1), tokens) >= sum(len(t) for t in tokens):
                out.append(f"- 💬 {m.group(1).strip()}")
    out.append(f"\n（概念文件：{best['path']}）")
    return "\n".join(out)


TOOLS = [
    {
        "name": "search_universe",
        "description": "全库检索阅读宇宙：已拆书目、概念（含各书论述对照）、涌现观点。日常对话中想引用读过的书时先调这个。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索词，如：交易费用 / 需求定律"},
                "limit": {"type": "integer", "description": "返回条数上限，默认 8"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_concept",
        "description": "获取一个概念的完整节点：多本书对该概念的论述对照表（旁征博引的核心——同一个概念，不同书怎么说）。",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "概念名或别名，如：交易费用 / 科斯定律"}},
            "required": ["name"],
        },
    },
    {
        "name": "get_book",
        "description": "获取一本书的节点详情：一段话总结、核心主张、主题、物料清单。",
        "inputSchema": {
            "type": "object",
            "properties": {"slug_or_title": {"type": "string", "description": "书名或 slug"}},
            "required": ["slug_or_title"],
        },
    },
    {
        "name": "neighbors",
        "description": "获取节点（书或概念）的邻接关系：相关概念、相关书目、影响边。",
        "inputSchema": {
            "type": "object",
            "properties": {"node": {"type": "string", "description": "概念名或书 slug"}},
            "required": ["node"],
        },
    },
    {
        "name": "get_emergent",
        "description": "获取跨书涌现观点台账（书与书碰撞产生的合成判断）。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_persona",
        "description": "获取读者人格档案（品味画像、思想立场、表达特征）——对话时可参照此人格的立场与口味。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cite",
        "description": "组合引用：给定一个话题，返回可直接贴进对话的引用块（概念 + 各书观点对照 + 金句）。",
        "inputSchema": {
            "type": "object",
            "properties": {"topic": {"type": "string", "description": "话题关键词"}},
            "required": ["topic"],
        },
    },
]

TOOL_IMPLS = {
    "search_universe": tool_search_universe,
    "get_concept": tool_get_concept,
    "get_book": tool_get_book,
    "neighbors": tool_neighbors,
    "get_emergent": tool_get_emergent,
    "get_persona": tool_get_persona,
    "cite": tool_cite,
}


# ---------- MCP 协议层 ----------

def list_resources():
    res = []
    for base, scheme in ((UNIVERSE, "universe"), (BOOKS, "books")):
        if not base.exists():
            continue
        for f in sorted(base.rglob("*.md")):
            rel = f.relative_to(base)
            res.append({
                "uri": f"{scheme}:///{rel.as_posix()}",
                "name": f.name,
                "mimeType": "text/markdown",
            })
    return res


def read_resource(uri: str):
    for base, scheme in ((UNIVERSE, "universe"), (BOOKS, "books")):
        if uri.startswith(f"{scheme}:///"):
            rel = uri[len(f"{scheme}:///"):]
            p = (base / rel).resolve()
            if p.exists() and str(p).startswith(str(base)):
                return read(p)
    raise ValueError(f"未知资源：{uri}")


def handle(req, corpus):
    method = req.get("method", "")
    rid = req.get("id")
    is_notification = "id" not in req

    if method == "initialize":
        result = {
            "protocolVersion": req.get("params", {}).get("protocolVersion", PROTOCOL_VERSION),
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": SERVER_INFO,
        }
    elif method == "notifications/initialized":
        return None
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        impl = TOOL_IMPLS.get(name)
        if not impl:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": f"未知工具：{name}"}}
        try:
            text = impl(args, corpus)
            result = {"content": [{"type": "text", "text": text}]}
        except Exception as e:  # noqa: BLE001
            result = {"content": [{"type": "text", "text": f"工具执行出错：{e}"}], "isError": True}
    elif method == "resources/list":
        result = {"resources": list_resources()}
    elif method == "resources/read":
        uri = req.get("params", {}).get("uri", "")
        try:
            result = {"contents": [{"uri": uri, "mimeType": "text/markdown",
                                    "text": read_resource(uri)}]}
        except (ValueError, OSError) as e:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": str(e)}}
    elif rid is not None:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"未知方法：{method}"}}
    else:
        return None

    if is_notification:
        return None
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def main():
    corpus = load_corpus()
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except json.JSONDecodeError:
            continue
        resp = handle(req, corpus)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
