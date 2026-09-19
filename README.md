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

## 安装与上手

### 0. 前置条件

| 依赖 | 说明 |
|---|---|
| 支持 skills 的 coding agent | ZCode / Claude Code 等（需子 agent 派生 + 联网检索能力） |
| Python ≥ 3.8 | 脚本零第三方依赖，`python3 --version` 确认 |
| git | 拉取技能仓与数据仓 |
| 可选：本地书库 | 电子书 PDF/EPUB 分类目录；没有也能拆（联网调研模式，无原文降级） |
| macOS 专属 | 扫描版 PDF OCR 用 `skill/scripts/ocr.swift`（Vision 框架）；其他平台需自配 OCR |

### 1. 安装技能仓（两种方式）

**方式 A · 拷贝安装（使用者）**——装的是快照，更新需重新拷贝：
```bash
git clone git@github.com:godlockin/bookverse.git && cd bookverse
cp -r skill/ ~/.agents/skills/bookverse/
```

**方式 B · 符号链接（推荐，仓库 `git pull` 即生效）**：
```bash
git clone git@github.com:godlockin/bookverse.git ~/path/to/bookverse
ln -s ~/path/to/bookverse/skill ~/.agents/skills/bookverse
```
> Claude Code 等若用别的 skills 目录（如 `~/.claude/skills/`），把链接目标换成对应目录即可。

### 2. 准备数据仓（三选一）

```bash
# ① 用官方数据仓（含已拆书目，可直接续拆/对照）
git clone git@github.com:godlockin/bookcorpus.git ~/path/to/bookcorpus

# ② 自建空数据仓（从零开始自己的宇宙）
mkdir -p ~/path/to/my-corpus/corpus
python3 ~/.agents/skills/bookverse/scripts/universe_rebuild.py ~/path/to/my-corpus/universe --init

# ③ 先试用不落盘：跳过，首跑引导会替你处理
```

> 注意：官方数据仓的宇宙（universe）在**本仓库**内——用方式①时 `universe_root` 填本仓的 `universe/` 目录。

### 3. 初始化配置

**自动引导**：配置不存在时，第一次说「拆解《XX》」会触发三步引导（数据仓 clone/初始化 → `corpus_root` → `universe_root`，可选 `library_root`），答完写盘、当次任务不中断。

**手工配置**：创建 `~/.agents/skills/bookverse/config.yaml`（模板见 [skill/config.example.yaml](skill/config.example.yaml)）：
```yaml
library_root: /path/to/your/pdf-library     # 私有书库（可选，留空走联网调研模式）
corpus_root: /path/to/bookcorpus            # 数据仓根（corpus/ 的父目录）
universe_root: /path/to/bookverse/universe  # 宇宙目录（官方布局=本仓 universe/；自建仓指向自己的）
```

### 4. 验证安装（三条命令）

```bash
python3 ~/.agents/skills/bookverse/scripts/validate.py <corpus根> <universe目录>   # 结构校验，exit 0 即过
python3 ~/.agents/skills/bookverse/scripts/book_lookup.py --list                   # 列出已拆书目
python3 <bookverse仓>/mcp/test_client.py                                           # MCP 冒烟（装了 MCP 再跑）
```

### 5. 首次拆书

1. 准备一本电子书（PDF/EPUB/DOCX/TXT/MD；只有书名则走联网调研模式）
2. 对 agent 说「拆解这本书：<文件路径>」
3. 确认点 A 检查专家编排 → 之后按确认点推进（说「全自动」可跳过 A/C）
4. 拆完看 `universe/LIBRARY.md`：主题域分组书目树 + 产物齐缺 + 概念域索引
5. 不确定值不值得全拆？先说「轻拆」（digest+书评+核心产物，约一半成本）；三档深度判据见 SKILL.md

### 6. 更新与卸载

- 更新：方式 B 用户 `git pull` 即生效；方式 A 重新 `cp -r`；版本变化看 [CHANGELOG.md](CHANGELOG.md)
- 卸载：删 `~/.agents/skills/bookverse` 与本仓库即可——你的数据（corpus/universe/config）独立在数据仓，不受影响

### 7. 可选：阅读宇宙接进 MCP 客户端

在任意 MCP 客户端（ZCode / Claude Desktop / Cursor）注册 `reading-universe` 服务器，日常对话即可检索/引用你拆过的书——注册步骤见 [mcp/README.md](mcp/README.md)。

## 运行要求

- 支持 skills 的 coding agent（ZCode / Claude Code 等），需子 agent 派生与联网检索能力
- Python ≥ 3.8（零第三方依赖）；OCR 脚本为 macOS（Vision），其他平台扫描版需自配
- token 成本参考：一本 25 万字书全流程约 10-20M token（含子 agent；三档拆解深度见 SKILL.md）

## License

**CC BY-NC 4.0**（署名—非商业性使用 4.0，见 [LICENSE](LICENSE)）：

- ✅ 允许二创、改编、个人与非商业使用；**必须署名**——建议格式「基于 godlockin/bookverse（CC BY-NC 4.0）」并注明修改
- ❌ 商用（付费产品、培训、企业内部商业使用、变相收费等）默认禁止，**需另行取得作者书面授权**；不确定是否商用时默认视为需要授权
- 📤 **产出物署名**：用本 skill 生成的产物（书评/概念卡/digest/讲稿等）对外发布时，须声明「由 bookverse 生成」
- universe/persona 为维护者个人数据，请勿在 fork 中复用；拆书产物含原文摘录属评注引用范畴，使用边界由使用者自负
