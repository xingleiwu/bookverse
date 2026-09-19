---
name: bookverse
description: 拆书流水线与个人阅读宇宙：对任意一本书（本地 PDF/EPUB/DOCX/TXT/MD 文件，或只有书名）做主题分类、MoE 专家深度拆解（叙事/论证/知识体系/时空考证/红队批判）、延伸阅读图谱、书评、社交媒体物料，并把每次拆书沉淀进跨书的「阅读宇宙」与持续进化的「读者人格」。当用户说「拆书」「拆解这本书」「分析《XX》」「这本书讲了什么」「帮我读这本书」「写《XX》的书评/读书笔记」「这本书和《YY》什么关系」「更新我的阅读宇宙」等时使用；用户只给一个书名或一个电子书文件路径时也应该用。
---

# bookverse · 书宙 · 拆书流水线与个人阅读宇宙

把一本书拆成结构化知识，沉淀为跨书的「阅读宇宙」，并让「读者人格」随每次交互进化。

**三层架构**

- **代谢层**：本流水线（提取 → 调研 → 专家深析 → 泛化 → 全书总结 → 延伸 → 书评 → 物料（评审组把关）→ 人格进化）
- **记忆层**：阅读宇宙（`universe/`，跨书知识网络，规范见 references/universe.md）
- **人格层**：读者人格（`universe/persona/`，随交互进化，规范见 references/persona.md）

**铁律**

1. AI 只提议，不擅自定调。人格属于用户，AI 是镜子不是主人。
2. 每条关键论断标注信源：`[原文·章节]` `[网络·来源]` `[推断·依据]`。无原文依据时不得伪造引文。
3. 批判必须给依据（原文定位或具体事实），不为批判而编造缺陷。
4. **主 agent 给子 agent 的 prompt 中只引用已核实文献**——从记忆写出的具体文献名/年份是未核实引用（实战：「Megrabyan 2019」查无此文），不确定的一律让子 agent 自行核实，不得作为前提写入 prompt。

**自主权契约**

免确认数据域：工作区下的 `books/`、`universe/`、`mcp-reading-universe/`、`books-index.md`、`HANDOFF*.md`，以及 `~/.agents/skills/bookverse/`（skill 自身迭代，含 config.yaml 配置读写）——流水线中间产物（00-source 至 06-takeaway、book-map、signals）全部直接创建/修改，不停下询问。仍需确认：工作区之外的任何文件（用户 shell 配置等）、删除整本书目录、对外发布内容、确认点 A/B/C 的流程裁决。配套项目权限白名单见 `<workspace>/.zcode/settings.json`；若工具权限仍弹窗，请用户选"总是允许"或切 accept-edits 模式。

## 配置（config.yaml · skill 正文零真实地址）

所有本机路径只存配置文件：`~/.agents/skills/bookverse/config.yaml`（skill 安装目录，机器本地；模板见 skill 源码 `config.example.yaml`）。

```yaml
library_root: <书库根目录>        # 私有书库 PDF 分类树（可留空走联网调研模式）
corpus_root: <数据仓根目录>       # 独立 git 仓库，仅含 corpus/（拆书产物，镜像书库分类层级）
universe_root: <宇宙目录>         # 默认 <技能仓>/universe；也可指向自建
```

- **首次使用**（读不到 config.yaml）：AskUserQuestion 三步引导，写盘后继续本次任务，不因配置阻塞：
  1. **数据仓**：给出仓库地址让用户 `git clone`（官方数据仓或用户自建空仓）；不 clone 则本地新建目录并 `python3 <skill目录>/scripts/universe_rebuild.py <目录>/universe --init` 初始化空宇宙骨架
  2. **workspace_root** ← 指向该数据仓根
  3. **library_root**（可选）：私有书库 PDF 分类树；暂无则留空，走联网调研模式
- **解析顺序**：① CWD 已是初始化数据仓（有 `universe/` 或 `corpus/`）→ 用 CWD，与 workspace_root 不一致时提醒用户是否回写配置；② 否则用 workspace_root（无 universe/ 则按首跑引导初始化）；③ 配置缺失 → 走首跑引导。
- **后期可改**：用户说「改配置 / 换书库 / 换结果目录」→ 读现值展示，按答复更新写盘。`universe_rebuild.py` 与 MCP 服务器同读此文件（MCP 另支持 UNIVERSE_PATH 环境变量覆盖）。

## 用法

```
/bookverse <书名 | 文件路径> [--to N] [--type 类型] [--no-persona] [--takeaway 清单] [--formula add|mul|auto]
```

- 输入：文件优先（PDF/EPUB/DOCX/TXT/MD），只有书名则联网调研
- `--to N`：只跑到第 N 步（1-7）
- `--type`：跳过自动分类（类型名见 references/taxonomy.md）
- `--no-persona`：本次不读写人格档案
- `--takeaway`：step 6 产出菜单（napkin,brief,principles,xhs,moments,talk,handbook，见 references/stage6-takeaway.md；minimal = napkin+xhs）
- `--formula`：餐巾纸公式风格（auto 默认：fiction→乘法，其余→加法）

### 拆解深度

决策依据一句话：看「这本书与宇宙悬案的关系 × 阅读目的」——不是所有书都值得全拆。三档决策表：

| 档位 | 做什么 | 成本 | 定档判据 |
|---|---|---|---|
| **全拆** | 七步全套 | 10-20M token/本 | 回应宇宙悬案 / 域主力建设 / 用户点名 |
| **轻拆**（`--to 5`） | digest + 书评 + 核心 takeaway | 约一半成本 | 同域补充读物 / 试探性兴趣 / 时效性内容 |
| **调研入库** | 无原文模式：联网书目调研 + 宇宙占位节点 + frontier 📚 标记 | 成本极低 | 原文未到手 / 买前评估 / 试水 |

默认全拆；批量模式按上表逐本定档并记入 BATCH-PROGRESS（队列项标注 [全拆/轻拆/调研]）。

**批量拆解模式**（用户说「按 XX 顺序逐个拆/逐本拆/继续拆」时启用）：跳过确认点 A（决定记入工作区 universe/records/batch/batch-<日期>.md）与 C（人格提案**默认入库**：经 `universe/records/proposals/proposal-<日期>-v<N>-<slug>.md` 起草后写入 profile 并归档 applied/，注明「默认入库——批量模式无交互信号」）；书评初稿即定稿但**并入评审组做事实核对**（见 review-panel.md）；评审组静默执行；每本完成后在 universe/records/batch/batch-<日期>.md 追加一行并汇报「本轮默认入格条数」。用 universe/records/batch/batch-<日期>.md 做跨上下文压缩的批次状态锚。**step 4 产物一件不跳**（含 04-network/related.md）——批量提速只省交互不省产物，跳过的产物会在 LIBRARY.md 留 ✗（2026-09-18 教训：批量四本全部缺书单）。

## 输出目录约定

根目录：按「配置」节解析（config.yaml 的 workspace_root；CWD 已初始化时优先并提醒回写）。skill 正文与脚本不写死任何真实地址。仓库根只保留 README/LICENSE/CHANGELOG/CONTRIBUTING 等基础文档。

```
<数据仓根>/（独立 git 仓库，仅 corpus）  # corpus/<书库分类层级>/<slug>/；首跑引导下载或初始化
├── skill/  mcp/  assets/  universe/ # skill 本体 / MCP 服务器 / 资源 / 阅读宇宙（含 persona 与 records）
├── corpus/<书库分类层级>/<书名slug>/   # 拆书中间文件（数据仓）——镜像私有书库目录结构
│   ├── 00-source/        # fulltext.md（原文提取，**不入库**·版权）、metadata.md
│   ├── 01-meta/ … 06-takeaway/      # 其余同前
├── universe/
│   ├── index.md  books-index.md  LIBRARY.md  frontier.md  emergent.md   # 索引三件套（AUTO）
│   ├── books/<书库分类层级>/<slug>.md
│   ├── concepts/<域>[/<子域>]/<概念slug>.md   # 按域分层（经济学/价格理论/…）
│   ├── graph/edges.jsonl  persona/（profile.md journal.md）
│   └── records/           # 追加型记录，统一命名 <type>-<yyyy-MM-dd>[-标题].md
│       ├── dreams/  retros/  reviews/  roi/  proposals/[applied/]  batch/
└── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md  .gitignore
```

## 流水线（7 步）

**Step 1 提取 + 并行调研** —— 读 references/stage1-research.md、references/taxonomy.md、references/universe.md（宇宙碰撞初查）、references/persona.md（读人格档案，`--no-persona` 时跳过）。
**取书前置查重**：`python3 <skill目录>/scripts/book_lookup.py <书名/作者关键词>`——已处理过则显示版本与路径（重复拆解=重读仪式场景，teardown-version 递增；同名不同书用 --list 核对）。解析输入并提取全文与元数据（**合集/套装先拆成独立书目各自走完整流水线；>30 万字超长书按章级单元分卷执行后汇总 merge，分卷全程维护书内知识图谱 book-graph——强关联章不拆散、专家可实时检索跨单元引用——规范见 references/stage1-research.md §1**）→ 主题分类（主/副类型 + 权重）→ **全书测绘官**（文件模式下派 1 个子 agent 通读全文产出测绘图：逐讲摘要 + 绝对化论断全量清单 + 概念密度 + 金句表，规范见 references/experts/router.md 覆盖策略）→ 并行 4 个调研子 agent（作者谱系 / 同类书目 / 立场对话书目 / 背景争议）→ MoE 门控生成专家激活清单（规则见 references/experts/router.md）。

⏸ **确认点 A**：呈现分类 + 权重 + 专家清单 + 召唤预算 + 宇宙相关节点，用户可增删改，确认后继续。

**Step 2 专家深析** —— 读 references/experts/&lt;主类型&gt;.md（副类型权重 ≥0.3 时加读其档案）和 references/experts/auditor.md。
按激活清单并行派常驻专家子 agent；运行中按 router.md 触发器动态召唤微专家（知识点卡）。产出 `02-analysis/`。阶段末汇报召唤记录。

**Step 3 综合泛化 → 全书总结** —— 先按类型档案的 level1 模板整合：正向解析 + 批判对照 + 时空坐标 + 宇宙碰撞；产出涌现「合成观点」候选（标注来源书目组合），产出 `03-synthesis/level1.md`（分析工作台）。**再读 references/stage3-digest.md**，把 level1 梳理、思考成全书总结 `03-synthesis/digest.md`（十碗水煎成一碗水：全书重要内容全覆盖的叙述版精炼）——digest 是书评与全部 takeaway 的共同基础，此步不可跳过。

**Step 4 延伸阅读** —— 按 references/universe.md：关联书单分两类——外延（联网搜索的未读书，进 `04-network/related.md` 并同步 `universe/frontier.md`）/ 内联（宇宙已有书——**内联边须满足语义条件：共享概念/主题重叠/有证据的影响关系/用户指定，见 universe.md 内联边纪律；主题过远时只入库不连线，留作孤岛节点**）。更新宇宙节点与边。**选书四象限（用户裁决 2026-09-18）**：外延书单持续覆盖「相同、相近、相反、完全不相干」四象限——兼听则明，不相干域是跨域联想与涌现的来源。

**Step 5 书评** —— 读 references/stage5-review.md。
以人格档案为底色、以 digest 为叙事底稿写初稿：全貌 digest 已承担，书评只从最重要、经典、有影响力、有价值的部分**选点深打**（装帧/正文/读后感三块结构 + 红队「值得商榷」块）→ ⏸ **确认点 B**：进入润色 spec 的逐段确认流程（文字对比，不用弹窗），过程中采集偏好信号到 `05-review/signals.md`。定稿后跑 `scripts/check_punctuation.py`。

**Step 6 Take away** —— 读 references/stage6-takeaway.md（类型菜单：`--takeaway` 可选）与 references/review-panel.md。
默认产出：餐巾纸压缩 + **brief 主旨总结（带 frontmatter，供 MCP 引用）** + **principles 指导方针** + 小红书版 + 朋友圈版 + 讲书脚本；knowledge 类加 handbook 学习手册。产物素材以 digest 为基础（细节回 level1/02-analysis 查证）。**每个产物初稿后必须过评审组（见 review-panel.md）：内容质量专家 + 对应渠道/产物专家 + 去AI味专家三重评审，全 PASS 才算完成**，意见落盘 `06-takeaway/review-log.md`；「全自动」模式下评审不省略只静默。交付前必须跑 `python3 <skill目录>/scripts/check_punctuation.py <交付文件> --fix`。

**Step 7 人格进化** —— 读 references/persona.md。
汇总本次信号（吸收的概念、书评交互偏好、被采纳的涌现观点）→ 生成人格更新提案（diff + 依据），**附一条「转变候选」（先贤评审 2026-09-18 补）：这次阅读可能改变了读者的哪个判断或行为——偏好信号只度量口味，此条专记转化；候选须含反问形式（这本书会问读者什么），用户可拒答** → 提案**默认入库**（用户裁决 2026-09-18：直接写入 profile 并标「默认入库」，proposals/ 起草后归档 applied/，用户保留事后否决权）→ ⏸ **确认点 C（汇报制）**：汇报本轮入格内容供事后否决，可跳过。

全部完成后跑 `python3 <skill目录>/scripts/universe_rebuild.py <root>/universe`——`books-index.md`、`universe/index.md` 书目表与 `LIBRARY.md`（书库总索引）由脚本 AUTO 区块自动维护，**不要手写**。书目 frontmatter 需含 `domain:`（主题域，LIBRARY.md 分组用）与 `cost:`（子 agent token 成本，无数据写「未计量」）。向用户汇报：本次产物清单 + 宇宙增长（新增节点/边）+ 人格变化 + token 成本（从子 agent usage 汇总，无数据标"未计量"）。若已满 4 的倍数本**或任一主题域超 12 节点**，提示"宇宙该做梦了"（`/bookverse dream`，规范见 references/universe.md 的 Dream 节）——判据以 rebuild 输出与 LIBRARY.md 为准：书目 4 的倍数看重建行数，域超限看 LIBRARY.md 概念域索引的标签计数 >12（2026-09-18 教训：经济学域 13 个概念靠人工盘点才发现批量期漏报）。

**Dream 模式**：`/bookverse dream`——不拆书，对宇宙做睡眠整合：合并审计、对照表内化、过期候选修剪、主题域重组（超限域拆分），产出 dream-report。防僭越纪律照常适用。

**复盘模式**：`/bookverse retro`——多本之后的经验总结：产出 universe/records/retros/retro-<yyyy-MM-dd>[-标题].md（现状盘点/验证了什么/暴露什么问题/成本质量基准/Dream 清单），并将可固化教训回写 skill。历史复盘存于 universe/records/retros/（时间戳命名）。**先贤评审常设化**：重大 skill 升级或 retro 时召唤先贤评审团——3-6 位先贤，按改动主题从名单池轮换（苏格拉底/庄子/尼采/伽达默尔/博尔赫斯/孔子/波普尔/奥威尔/图灵/芒格/凯恩斯），攻击对象是**改动本身与系统盲区**。纪律：每人只攻一个最疼的点、必须点名具体机制、不得泛泛而谈；主审合议三档裁决——指中（→修复或立提案）、部分被防御（→记录防御依据）、不采纳（→记录理由）。实战先例：2026-09-18 六先贤评审（苏格拉底/庄子/尼采/伽达默尔/博尔赫斯/孔子）指中 4 条盲区，产出缺席清单、缓存默认化、共同体外反方、转变候选四项升级。

**ROI 模式**：`/bookverse roi`——阅读投入产出报表：按主题域盘点成本与回报（概念/边/涌现/立场/物料/被引用度），给出边际回报与投入建议；口径与产出见 references/roi.md。

**回审模式**：闸门/规范升级后对存量书目的回审——按现行 review-panel.md 三角色逐产物审查（FIX 带原文证据落盘各书 `06-takeaway/review-log.md`），产出 universe/records/reviews/review-<yyyy-MM-dd>[-标题].md（逐书裁决/共性病灶/修复清单/修复记录），修复完成后存量与新标准对齐。先例：REVIEW-001（2026-09-17，digest 与评审组上线后的六本回审）。

## 确认点协议

- A：可用 AskUserQuestion 或对话文字，选项精简，给推荐项；C：汇报制——默认入库后汇报，接受事后否决。
- B：必须遵循润色 spec——直接在对话给「原句 → 改后」对比，等用户文字回复，**禁止**用弹窗/选择题工具。
- 用户说「全自动」「别停」时：跳过 A/C，B 仍保留（润色 spec 的核心交互），除非用户明说书评也不要确认。

## MoE 门控摘要（详见 references/experts/router.md）

专家不是固定名单，按门控激活：输入 = 类型权重 + 正文内容信号 + 宇宙碰撞结果，输出 = 激活清单（谁上场、聚焦什么、深度）。两层专家：常驻专家组（step 2 并行深析）+ 动态召唤微专家（任意阶段触达未覆盖知识点时现场召唤，做「搜索核实 → 对照共识 → 评价 → 补充」，产出知识点卡）。每阶段召唤上限默认 3-5 个，相似知识点合并。

## 子 agent 纪律

- **本机环境纪律**：本机 shell 为 zsh 且 `ls`/`grep`/`find` 被包装为函数（eza 等）——管道里用 `command ls` / `/bin/ls` / `/usr/bin/grep` 取原版行为；禁用 bashism（`declare -A` 等 zsh 不支持的语法）；若 Bash 报 `spawn /bin/zsh ENOENT`，属用户 shell 快照与沙箱管道冲突，不要反复重试，改用不依赖 shell 的工具（Read/Write/WebSearch）继续能做的部分，并提醒用户调整 ZCode shell 快照设置。
- 调研与专家任务用 general-purpose 子 agent，单消息多调用并行。
- **小批派单纪律（2026-09-17 实战教训）**：单消息并行派单 ≤3 个——当日两轮大批次（13 派、4 派）均因「600 秒不活跃」超时大量折损（13 派只成 3）。大批量任务分多轮派发；若整批全灭，**主 agent 顺序执行兜底**，不要原样重派第三次。骨架先写纪律的价值在同日得到验证：被超时杀掉的 digest 子 agent 仍留下了完整可用的成果文件。
- 子 agent prompt 必须自带完整上下文（书名、类型、输入文件路径、输出文件路径、信源规则），不依赖会话记忆。
- **防卡死纪律（必写进每个读长文子 agent 的 prompt）**：先立即写出带小节骨架的输出文件，再逐步用 Edit 充实；单次 Read 不超过 300 行；优先 Grep 定位、不通读全文。实战依据：首拆 7 名专家中 4 名因超时被杀（沉没约 25-33% 专家预算），加此纪律重派后全部成功。
- **同文件读写禁令（2026-09-19 实战教训：子 agent 拼装临时件时 `cat 分片* >> 汇总` 的汇总文件落入输入 glob，自我喂入膨胀至 51GB，幸而及时终止）**：shell 重定向的输出文件名**不得落入输入通配符范围**——`x >> x` 会以磁盘写入速度无限增长直到盘满。大批量文本拼接/过滤一律用 python（读入内存→处理→写新文件）；确需 shell 拼装时，输出写到输入 glob 匹配不到的名字，完成后 mv。命令异常缓慢时第一反应查文件体积（`ls -lh`），不要等它自己结束。
- 每个子 agent 只写自己的输出文件，不改宇宙（宇宙更新统一由主 agent 在 step 4/7 执行，避免写冲突）。

## 渐进加载索引

| 时机 | 读什么 |
|---|---|
| step 1 | stage1-research.md、taxonomy.md、universe.md、persona.md、experts/router.md |
| step 2 | experts/&lt;主类型&gt;.md（副类型≥0.3 加读）、experts/auditor.md |
| step 3 | stage3-digest.md（level1 完成后） |
| step 4 | universe.md（已在上下文则免） |
| step 5 | stage5-review.md |
| step 6 | stage6-takeaway.md、review-panel.md |
| step 7 | persona.md（已在上下文则免） |
