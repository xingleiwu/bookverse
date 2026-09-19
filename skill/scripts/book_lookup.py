#!/usr/bin/env python3
"""bookverse · 书籍查重与定位：这本书处理过吗？第几版？在哪？

用法：
  python3 book_lookup.py <书名或作者或slug关键词> [...]   # 模糊匹配，多词 AND
  python3 book_lookup.py --list                          # 全部已处理书目
exit 0 = 有命中；1 = 无命中（可放心新拆）；2 = 配置错误。零第三方依赖。
"""
import re
import sys
from pathlib import Path


def parse_fm(text):
    if not text.startswith("---"):
        return {}
    fm = {}
    for ln in text.splitlines()[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"^(\S[^:]*):\s*(.*)$", ln)
        if m and not ln.startswith((" ", "-", "\t")):
            fm[m.group(1).strip()] = m.group(2).strip()
    return fm


def norm(s):
    return re.sub(r"[\s：:，,。·\-_'’“”（）()]", "", str(s)).lower()


def main():
    cfg = Path(__file__).resolve().parent.parent / "config.yaml"
    vals = {}
    if cfg.exists():
        for ln in cfg.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(\w[\w-]*):\s*(.+?)\s*$", ln)
            if m and not m.group(2).lstrip().startswith("<"):
                vals[m.group(1)] = Path(m.group(2).strip())
    corpus = vals.get("corpus_root") or vals.get("workspace_root")
    if (corpus / "corpus").is_dir():
        corpus = corpus / "corpus"
    universe = vals.get("universe_root") or (vals.get("workspace_root") / "universe" if vals.get("workspace_root") else None)
    if not corpus or not universe:
        print("未找到 corpus/universe 配置（config.yaml）")
        sys.exit(2)

    books = []
    for f in sorted((universe / "books").rglob("*.md")) if (universe / "books").exists() else []:
        fm = parse_fm(f.read_text(encoding="utf-8"))
        rel = f.relative_to(universe / "books").with_suffix("")
        bdir = corpus / rel
        n_take = len(list((bdir / "06-takeaway").glob("*.md"))) if (bdir / "06-takeaway").exists() else 0
        books.append({
            "slug": f.stem, "title": fm.get("title", ""), "author": fm.get("author", ""),
            "date": fm.get("date-torn", ""), "ver": fm.get("teardown-version", "?"),
            "domain": fm.get("domain", ""), "corpus": rel, "takeaways": n_take,
        })

    args = [a for a in sys.argv[1:] if a != "--list"]
    if args:
        keys = [norm(a) for a in args]
        hits = [b for b in books if all(any(k in norm(v) for v in (b["title"], b["author"], b["slug"], b["domain"])) for k in keys)]
    else:
        hits = books

    if not hits:
        print("✗ 未处理过（无匹配书节点）——可按新书拆解；若疑重名，用 --list 核对全表")
        sys.exit(1)
    print(f"✓ 已处理 {len(hits)} 本：")
    for b in hits:
        print(f"  v{b['ver']} · {b['date']} · 《{b['title']}》 {b['author']} · {b['domain']}")
        print(f"     corpus/{b['corpus']} · takeaway×{b['takeaways']} · slug={b['slug']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
