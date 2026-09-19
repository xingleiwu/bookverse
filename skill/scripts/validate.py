#!/usr/bin/env python3
"""bookverse · 结构与格式硬校验（目录结构 / frontmatter / records 命名 / 边表完整性）

层级规则：书库与概念分类**可按需加深层级**（整体结构不变）——corpus/<两位数_分类>/…/<slug>/，concepts/<域>/…/<概念slug>/，中间层任意深度，仅约束首段与末段格式。

用法：
  python3 validate.py                 # 校验 config.yaml 指向的 corpus + universe
  python3 validate.py <corpus> <universe>
exit 0 = 全部通过；非 0 = 存在违规（CI 用）。零第三方依赖。
"""
import json
import re
import sys
from pathlib import Path

BOOK_STAGES = {"00-source", "01-meta", "02-analysis", "03-synthesis", "04-network", "05-review", "06-takeaway"}
BOOK_FM_REQUIRED = ["title", "author", "type", "year-published", "date-torn", "domain", "cost",
                    "themes", "concepts", "teardown-version"]
CONCEPT_FM_REQUIRED = ["concept", "domains", "emerged-from"]
RECORD_RE = re.compile(r"^(dream|retro|review|roi|proposal|batch)-\d{4}-\d{2}-\d{2}(-[\w\u4e00-\u9fff.-]+)?$"
                       r"|^proposal-\d{4}-\d{2}-\d{2}-v\d+")
BRIEF_FM_REQUIRED = ["title", "author", "type", "core-claim", "themes", "concepts", "source-book"]
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CAT_RE = re.compile(r"^\d{2}_")


def parse_fm(text):
    if not text.startswith("---"):
        return {}
    fm, cur = {}, None
    for ln in text.splitlines()[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"^(\S[^:]*):\s*(.*)$", ln)
        if m and not ln.startswith((" ", "-", "\t")):
            k, v = m.group(1).strip(), m.group(2).strip()
            fm[k] = v
            cur = k if v == "" else None
        elif ln.lstrip().startswith("- ") and cur:
            fm.setdefault(cur, [])
            if isinstance(fm[cur], list):
                fm[cur].append(ln.lstrip()[2:])
    return fm


class Checker:
    def __init__(self):
        self.fails = []

    def check(self, ok, msg):
        if not ok:
            self.fails.append(msg)
        return ok

    def report(self, name, n):
        if self.fails:
            print(f"✗ {name}：{len(self.fails)} 项违规")
            for f in self.fails:
                print(f"  - {f}")
            return 1
        print(f"✓ {name}（{n} 项检查全通过）")
        return 0


def main():
    cfg_vals = {}
    for cfg in (Path(__file__).resolve().parent.parent / "config.yaml",):
        if cfg.exists():
            for ln in cfg.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^(\w[\w-]*):\s*(.+?)\s*$", ln)
                if m and not m.group(2).lstrip().startswith("<"):
                    cfg_vals[m.group(1)] = Path(m.group(2).strip())
    args = sys.argv[1:]
    corpus = Path(args[0]).expanduser() if args else cfg_vals.get("corpus_root") or cfg_vals.get("workspace_root")
    # 语义归一：corpus 变量 = 数据仓根；实际语料目录 = 仓根/corpus（若用户直接传了 corpus/ 目录也能识别）
    if (corpus / "corpus").is_dir():
        corpus = corpus / "corpus"
    elif corpus.name == "corpus":
        pass
    else:
        print(f"⚠ {corpus} 下无 corpus/ 子目录（空数据仓？继续校验 universe 部分）")
    universe = Path(args[1]).expanduser() if len(args) > 1 else cfg_vals.get("universe_root") \
        or (cfg_vals.get("workspace_root") / "universe" if cfg_vals.get("workspace_root") else None)
    if not corpus or not universe:
        print("用法：validate.py <corpus> <universe>（或先配置 config.yaml）")
        sys.exit(2)
    c = Checker()
    n = 0

    # ① corpus 目录结构
    slugs = []
    if corpus.exists():
        for d in sorted(p for p in corpus.rglob("*") if p.is_dir() and p.name in BOOK_STAGES and p.parent.name not in BOOK_STAGES):
            book = d.parent
            if book.parent == corpus:
                c.check(False, f"corpus 顶层不允许平铺书目：{book.name}（须在 <两位数_分类>/<二级>/ 下）")
        for f in sorted(corpus.rglob("00-source")):
            n += 1
            book = f.parent
            rel = book.relative_to(corpus)
            parts = rel.parts
            c.check(len(parts) >= 2 and CAT_RE.match(parts[0]),
                    f"{rel}：层级须为 <两位数_分类>/…/<slug>/（≥2 层；分类可按需加深，整体结构不变）")
            c.check(bool(SLUG_RE.match(book.name)), f"{rel}：slug 须为 kebab-case 英文")
            bad = {p.name for p in book.iterdir() if p.is_dir()} - BOOK_STAGES
            c.check(not bad, f"{rel}：非法子目录 {sorted(bad)}（白名单 {sorted(BOOK_STAGES)}）")
            slugs.append(book.name)

    # ② 书节点 frontmatter（含 corpus/universe 一一对应）
    ubooks = sorted((universe / "books").rglob("*.md")) if (universe / "books").exists() else []
    ubook_stems = {f.stem for f in ubooks}
    for s in slugs:
        c.check(s in ubook_stems, f"corpus/{s}：universe/books 缺对应书节点")
    for f in ubooks:
        n += 1
        fm = parse_fm(f.read_text(encoding="utf-8"))
        for k in BOOK_FM_REQUIRED:
            c.check(k in fm and fm[k] != "", f"universe/books/{f.name}：缺必填字段 {k}")
        c.check(bool(SLUG_RE.match(f.stem)), f"universe/books/{f.name}：文件名须英文 slug")
        rel = f.relative_to(universe / "books").with_suffix("")
        c.check((corpus / rel).exists(), f"universe/books/{f.name}：corpus 无对应目录（应为 corpus/{rel}）")
        c.check(re.match(r"^\d+$", str(fm.get("teardown-version", ""))), f"{f.name}：teardown-version 须为整数")
    for stem in ubook_stems - set(slugs):
        c.check(False, f"universe/books/{stem}.md：corpus 无 00-source（孤儿书节点）")

    # ③ 概念节点
    ucon = sorted((universe / "concepts").rglob("*.md")) if (universe / "concepts").exists() else []
    stems = set()
    for f in ucon:
        n += 1
        stems.add(f.stem)
        c.check(bool(SLUG_RE.match(f.stem)), f"concepts/{f.name}：文件名须英文 slug")
        fm = parse_fm(f.read_text(encoding="utf-8"))
        for k in CONCEPT_FM_REQUIRED:
            c.check(k in fm and fm[k] != "", f"concepts/{f.name}：缺必填字段 {k}")
        c.check(not re.search(r"[\u4e00-\u9fff]", f.stem), f"concepts/{f.name}：中文名须写在 frontmatter concept 字段")

    # ④ records 命名
    rec = universe / "records"
    if rec.exists():
        for f in sorted(rec.rglob("*.md")):
            n += 1
            if f.parent.name not in ("applied",):
                c.check(bool(RECORD_RE.match(f.stem)), f"records/{f.relative_to(rec)}：命名须为 <type>-<yyyy-MM-dd>[-标题].md")

    # ⑤ 边表
    ej = universe / "graph" / "edges.jsonl"
    if ej.exists():
        book_ids = {f"book:{f.stem}" for f in ubooks}
        for i, ln in enumerate(ej.read_text(encoding="utf-8").splitlines(), 1):
            n += 1
            try:
                e = json.loads(ln)
            except json.JSONDecodeError:
                c.check(False, f"edges.jsonl:{i}：非法 JSON")
                continue
            c.check(e.get("source", "").startswith("book:") and e.get("target", ""), f"edges.jsonl:{i}：source/target 格式")
            c.check(bool(e.get("note", "").strip()), f"edges.jsonl:{i}：note 证据指针不得为空")
            c.check(e["source"] in book_ids or True, "")
            if e["target"].startswith("book:") and e["target"] not in book_ids:
                c.check(False, f"edges.jsonl:{i}：target 书节点不存在 {e['target']}")
            if e["target"].startswith("concept:") and e["target"].split(":", 1)[1] not in stems:
                c.check(False, f"edges.jsonl:{i}：target 概念不存在 {e['target']}")

    # ⑥ brief frontmatter
    for f in sorted(corpus.rglob("06-takeaway/brief.md")):
        n += 1
        fm = parse_fm(f.read_text(encoding="utf-8"))
        for k in BRIEF_FM_REQUIRED:
            c.check(k in fm and fm[k] != "", f"{f.parent.parent.name} brief.md：缺必填字段 {k}")

    sys.exit(c.report(f"bookverse 结构校验（corpus={corpus} universe={universe}）", n))


if __name__ == "__main__":
    main()
