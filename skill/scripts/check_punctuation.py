#!/usr/bin/env python3
"""bookverse · 半角标点检查（润色规范硬性要求）

规则：成稿必须中文全角标点（，。、；：！？（）～）。
转换采用「CJK 邻接」保守策略：仅当半角标点前或后紧邻中文字符时才判为违规并转换，
避免破坏英文、代码、数字（小数 3.5、列表编号 "1. "、网址等）。
保护区域：YAML frontmatter、``` 代码块、行内代码 `...`、URL、Markdown 表格分隔行。

用法：
  python3 check_punctuation.py FILE...            # 只报告
  python3 check_punctuation.py FILE... --fix      # 报告并自动转换为全角

书籍信息中的 "/" 分隔符本就不在检查范围（规范明确豁免）。
退出码：0 = 干净；1 = 发现问题（--fix 后已修完则仍返回 1 以提示曾有改动？否——修复后返回 0）。
"""
import sys
import re
from pathlib import Path

HALF2FULL = {
    ",": "，", ".": "。", ";": "；", ":": "：",
    "!": "！", "?": "？", "(": "（", ")": "）", "~": "～",
}
HALF_CHARS = set(HALF2FULL)

URL_RE = re.compile(r"https?://\S+")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def is_cjk(ch: str) -> bool:
    if not ch:
        return False
    cp = ord(ch)
    return (
        0x3400 <= cp <= 0x9FFF      # CJK 扩展A + 基本区
        or 0xF900 <= cp <= 0xFAFF   # 兼容表意文字
        or 0x3000 <= cp <= 0x303F   # CJK 标点（全角环境）
        or 0xFF00 <= cp <= 0xFFEF   # 全角形式
    )


def split_frontmatter(text: str):
    """返回 (frontmatter行集合, 正文行列表)。frontmatter 按行号标记跳过。"""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return set(range(0, i + 1)), lines
    return set(), lines


def scan_line(line: str, line_no: int):
    """扫描一行，返回 [(col, half_char)]。保护行内代码与 URL；保守 CJK 邻接判定。"""
    # 用占位符保护行内代码与 URL
    protects = []

    def stash(m):
        protects.append(m.group(0))
        return f"\x00{len(protects) - 1}\x00"

    work = INLINE_CODE_RE.sub(stash, line)
    work = URL_RE.sub(stash, work)

    issues = []
    chars = list(work)
    for i, ch in enumerate(chars):
        if ch not in HALF_CHARS:
            continue
        # 前一个非空格字符
        prev = next((chars[j] for j in range(i - 1, -1, -1)
                     if not chars[j].isspace() and chars[j] != "\x00"), "")
        # 后一个非空格字符
        nxt = next((chars[j] for j in range(i + 1, len(chars))
                    if not chars[j].isspace() and chars[j] != "\x00"), "")
        if ch == ".":
            # 小数（3.5）与列表编号（1. ）保护
            p_raw = chars[i - 1] if i > 0 else ""
            n_raw = chars[i + 1] if i + 1 < len(chars) else ""
            if p_raw.isdigit() and (n_raw.isdigit() or n_raw == "" or n_raw == " "):
                continue
        if is_cjk(prev) or is_cjk(nxt):
            issues.append((i, ch))

    # 还原保护段
    def unstash(s):
        return re.sub(r"\x00(\d+)\x00", lambda m: protects[int(m.group(1))], s)

    return issues, unstash(work)


def process(path: Path, fix: bool):
    text = path.read_text(encoding="utf-8")
    fm_lines, lines = split_frontmatter(text)
    all_issues = []
    fixed_lines = list(lines)

    in_fence = False
    for ln, raw in enumerate(lines):
        stripped = raw.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or ln in fm_lines:
            continue
        # 表格分隔行 |---|---| 跳过
        if re.fullmatch(r"[\s|:\-]+", raw):
            continue
        issues, unstashed = scan_line(raw, ln + 1)
        if issues:
            all_issues.extend((ln + 1, col, ch) for col, ch in issues)
            if fix:
                chars = list(unstashed)
                for col, ch in issues:
                    chars[col] = HALF2FULL[ch]
                fixed_lines[ln] = "".join(chars)

    if fix and all_issues:
        path.write_text("\n".join(fixed_lines) + ("\n" if text.endswith("\n") else ""),
                        encoding="utf-8")

    # 报告
    by_line = {}
    for ln, col, ch in all_issues:
        by_line.setdefault(ln, []).append((col, ch))
    for ln in sorted(by_line):
        col, ch = by_line[ln][0]
        snippet = lines[ln - 1][max(0, col - 10):col + 10].strip()
        extra = f"（共{len(by_line[ln])}处）" if len(by_line[ln]) > 1 else ""
        print(f"  {path.name}:{ln}: 半角 '{ch}'{extra}  …{snippet}…")
    return len(all_issues)


def main():
    args = [a for a in sys.argv[1:] if a != "--fix"]
    fix = "--fix" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    total = 0
    for arg in args:
        p = Path(arg)
        if not p.exists():
            print(f"跳过（不存在）：{p}")
            continue
        files = [p] if p.is_file() else sorted(p.glob("*.md"))
        for f in files:
            total += process(f, fix)
    if total == 0:
        print("✓ 标点检查通过：无半角标点问题")
        sys.exit(0)
    print(f"{'已修复' if fix else '发现'} {total} 处半角标点" + ("（已写入全角）" if fix else "（用 --fix 自动转换）"))
    sys.exit(0 if fix else 1)


if __name__ == "__main__":
    main()
