# mcp-reading-universe

把阅读宇宙（已拆书目 + 概念对照 + 涌现台账）暴露为 MCP 服务器，让任何 MCP 客户端在**日常对话**中检索并引用你读过的书——像真人一样旁征博引。

零依赖：纯 Python 标准库，无需安装任何包。

## 数据源

- `universe/books/*.md` 书节点 · `universe/concepts/*.md` 概念对照表 · `universe/graph/edges.jsonl` 边 · `universe/emergent.md` 涌现台账 · `universe/persona/profile.md` 读者人格
- `books/*/03-synthesis/level1.md`（一段话总结）· `books/*/06-takeaway/*.md`（napkin 钩子、brief 等）

新增拆书后**无需重启**相关工具即可被检索（每次调用实时扫描）；但长会话中的 MCP 客户端可能缓存，重启客户端可见最新数据。

## 工具（7 个）

| 工具 | 用途 | 示例问法 |
|---|---|---|
| `search_universe` | 全库检索 | "帮我找读过的书里关于 X 的内容" |
| `get_concept` | 概念的多书对照表 | "机会成本，我读过的书里分别怎么说？" |
| `get_book` | 书详情 + 一段话总结 | "那本讲需求定律的书讲了什么？" |
| `neighbors` | 节点邻接（相关概念/书目） | "科斯定律和什么概念相连？" |
| `get_emergent` | 涌现观点台账 | "我有哪些跨书涌现的想法？" |
| `get_persona` | 读者人格档案 | （对话参照用户立场与口味） |
| `cite` | 组合引用：话题 → 可直接贴进对话的引用块 | "用读过的书谈谈 X" |

## 注册到 ZCode

server.py 的宇宙目录解析顺序：`UNIVERSE_PATH` 环境变量 > `~/.agents/skills/bookverse/config.yaml` 的 `workspace_root/universe` > 本项目根的 `config.yaml`。先完成配置（模板见 `skill/config.example.yaml`），再注册：

```json
{
  "mcpServers": {
    "reading-universe": {
      "command": "python3",
      "args": ["<本项目 bookverse/mcp/server.py 的绝对路径>"]
    }
  }
}
```

本目录的 `.mcp.json` 是占位模板（路径需替换为真实绝对路径后才会生效）。

其他客户端（Claude Desktop / Cursor 等）同样把上面 `mcpServers` 块放进各自的配置文件即可。

## 测试

```bash
python3 test_client.py   # 9 项冒烟：握手/工具清单/全部工具/资源列表/错误处理
```

## 数据流

```
bookverse 拆书 → universe/*.md + books/*/06-takeaway/brief.md (frontmatter)
            → 本服务器实时扫描 → MCP 客户端对话引用
```

brief.md 的 YAML frontmatter（core-claim / themes / concepts）是专为 MCP 检索设计的机器可读层。
