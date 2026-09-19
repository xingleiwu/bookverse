<div align="center">

<img src="assets/logo.svg" width="160" alt="bookverse logo"/>

# bookverse · 书宙

**拆书流水线 · 个人阅读宇宙 · 读者人格**

每读一本书，宇宙大一圈。

</div>

## 愿景

大多数阅读工具记住你**读过什么**；书宙想留下的是你**因为阅读变成了什么**。

- 每本书 → 一份可追溯的知识档案：每个论断带原文坐标，每条批判给证据，每件产物过三角色评审（内容质量 + 渠道专家 + 去AI味）
- 跨书 → 一张持续生长的阅读宇宙：概念多书对照、带证据指针的知识连边、跨书涌现的观点台账
- 长期 → 一个只属于你、随每次阅读进化的读者人格——品味、立场、思维与表达，逐版本留痕

书越读越多，宇宙越连越密；那面照出你思考方式的镜子，越来越清。

## 仓库体系（三仓模型）

| 仓库 | 内容 | 可见性 |
|---|---|---|
| **bookverse（本仓库·技能仓）** | skill/（方法论与脚本）+ mcp/（阅读宇宙服务器）+ assets/ + universe/（阅读宇宙、人格、records） | 开源，接受 PR |
| bookverse-data（数据仓，独立 git，仅 corpus/） | 拆书产物，镜像私有书库分类层级；`00-source/fulltext.md` 版权红线不入库 | 可开源可私有，按数据主人意愿 |
| 私有书库 | PDF 原件分类树 | **永不公开**（版权） |

首次使用时 skill 会**引导下载/初始化数据仓并配置本地路径**（数据仓 clone/init → corpus_root；universe_root 默认技能仓内；library_root 可选），全部落在 `config.yaml`，随时可改。

**协作方式见 [CONTRIBUTING.md](CONTRIBUTING.md)**——规范 PR、工具 PR、数据 PR（一书一 PR）各有验收门槛。

## 安装与快速上手

```bash
git clone <repo> bookverse && cd bookverse
cp -r skill/ ~/.agents/skills/bookverse/     # ZCode；兼容 skills 目录约定的 agent 通用
```

首次运行任意拆书指令（如「拆解《XX》」）会自动引导配置书库与结果目录。可选：把阅读宇宙接进 MCP 客户端（见 [mcp/README.md](mcp/README.md)）。

1. 准备一本电子书（PDF/EPUB/DOCX/TXT/MD；只有书名则走联网调研模式）
2. 对 agent 说「拆解这本书：<文件路径>」
3. 确认点 A 检查专家编排 → 之后按确认点推进（说「全自动」可跳过 A/C）
4. 拆完看数据仓的 `universe/LIBRARY.md`：主题域分组书目树 + 产物齐缺 + 概念域索引

## 运行要求

- 支持 skills 的 coding agent（ZCode / Claude Code 等），需子 agent 派生与联网检索能力
- Python ≥ 3.8（零第三方依赖）；OCR 脚本为 macOS（Vision），其他平台扫描版需自配
- token 成本参考：一本 25 万字书全流程约 10-20M token（含子 agent；三档拆解深度见 SKILL.md）

## License

**CC BY-NC 4.0**（署名—非商业性使用 4.0，见 [LICENSE](LICENSE)）：

- ✅ 允许二创、改编、个人与非商业使用；**必须署名**——建议格式「基于 godlockin/bookverse（CC BY-NC 4.0）」并注明修改
- ❌ 商用（付费产品、培训、企业内部商业使用等）默认禁止，**需另行取得作者书面授权**
- universe/persona 为维护者个人数据，请勿在 fork 中复用；拆书产物含原文摘录属评注引用范畴，使用边界由使用者自负
