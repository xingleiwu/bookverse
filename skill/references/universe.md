# 阅读宇宙（universe）· 记忆层规范

跨书知识网络。每拆一本书，宇宙生长一次；书与书的连接随积累自然涌现。

## 目录结构

```
universe/
├── index.md  books-index.md  LIBRARY.md   # 索引三件套（后两者 AUTO 维护）
├── books/<书库分类层级>/<slug>.md          # 书节点——镜像 corpus/ 目录结构
├── concepts/<域>[/<子域>]/<概念slug>.md    # 概念节点按域分层（如 经济学/价格理论/；含时空背景节点）
├── graph/edges.jsonl   # 机器可读边表（派生自 frontmatter，可重建；note=证据指针）
├── frontier.md         # 待拆清单（step 4 外延书单自动进入）
├── persona/            # 人格层（见 persona.md）
└── records/            # 追加型记录 <type>-<yyyy-MM-dd>[-标题].md：dreams/ retros/ reviews/ roi/ proposals/[applied/] batch/
```

## 节点格式

**命名铁律（实战踩坑：中文名文件与英文 slug 文件曾并行产生孤儿节点）**：文件名一律用英文 slug（kebab-case）；节点的中文名只写在 frontmatter `concept:`/`title:` 字段。universe_rebuild.py 按 frontmatter 中文名→文件 slug 建映射，边表 target 永远用文件 slug。

**书目 frontmatter 字段表**（`universe/books/*.md`——LIBRARY.md 与 books-index.md 的数据源，缺字段即索引缺口）：

| 字段 | 必填 | 用途 |
|---|---|---|
| title / author / type | ✅ | 书目表展示；type 首词为主类型（决定 handbook 是否属默认产物） |
| year-published / date-torn | ✅ | 出版年 / 拆书日期 |
| domain | ✅ | 主题域——LIBRARY.md 书目树分组用，须与 index.md 域子图命名一致（Dream 拆域后同步改名） |
| cost | ✅ | 子 agent token 成本，无数据写「未计量」（RETRO-001 问题 2 的制度化偿还） |
| teardown-version | ✅ | 拆解版本号（整数，首拆 v1；重读仪式递增，第二版产物 -v2 后缀并存）——查重见 scripts/book_lookup.py |
| themes / concepts / related | ✅ | 主题词 / 概念中文名列表（须与概念文件 frontmatter `concept` 对齐）/ 书际关系（`关系:slug`） |
| rating | 可选 | 用户评分 |

**书节点** `books/<slug>.md`（slug 用拼音/英文短横线）：

```markdown
---
title: 活着
author: 余华
type: fiction (严肃文学)
year-published: 1993
date-torn: 2026-09-15
themes: [苦难, 生存, 家庭]
concepts: [苦难叙事, 命运与承受]
related: ["similar_to:song-of-youth", "opposes:wolf-hall"]
rating:  # 用户主观分，可空
---
## 一句话
## 核心概念（链接 universe/concepts/）
## 与宇宙的连接（边列表 + 说明）
```

**概念节点** `concepts/<概念slug>.md`——宇宙最有价值的产物，**同一概念在不同书中的论述对照表**：

```markdown
---
concept: 黑暗森林
aliases: [黑暗森林法则]
domains: [科幻, 战略]
emerged-from: three-body-problem
---
# 黑暗森林
## 各书论述对照
| 书 | 立场 | 论述要点 | 位置 |
|---|---|---|---|
| 三体 | 提出 | … | [原文·第二部] |
| 人类简史 | 间接呼应 | … | [推断·依据] |
## 对照结论
（它们在哪里一致、哪里冲突；冲突是否可裁决）
```

- 时空背景节点 = concepts/ 下带 `domains: [时空背景]` 的节点（如"安史之乱"），由时空坐标卡沉淀，天然跨书（传记、历史小说、诗集都可能连到它）
- **引用节点**（可选扩展）= `quotes/<slug>.md`：书中关键金句/原文段，供 takeaway 与跨书引用对照

## 边（受控词表）

书↔书：`similar_to` `opposes` `influenced_by` `sequel_of` `cross_validate`（互证）`same_event`（共享时空背景）
书↔概念：`proposes`（提出）`elaborates`（阐述）`critiques`（批判）
概念↔概念：`broader_than` `similar_to` `opposes` `evolved_from`

## 碰撞机制（何时读写宇宙）

- **Step 1 读**：index.md 找相关节点 → 确认点 A 呈现
- **Step 2/3 读**：专家对照已有概念节点（prompt 里附相关节点内容），产出"本书 X vs 《Y》的 Z"对照
- **Step 4 写**：新增本书节点；概念命中已有节点 → 在其对照表加一行；新概念 → 建节点；补边到 frontmatter；外延书单写 frontier.md；**同义概念归一**（已有一词之差的概念 → 用 alias 合并，不新建）

**内联边纪律（防强行连线）**：书↔书内联边仅在满足至少一条时建立——
1. 共享概念节点（两书都阐发同一个已有概念）
2. 主题域重叠（themes 有实质交集，非泛化大词）
3. 有证据的影响/引用关系（一方明确引用或批判另一方）
4. 用户在确认点 A/C 指定

主题距离很远时：**只入库、不连线**——书节点 + 自己的概念节点照常创建，但不造书↔书边。孤岛节点不是缺陷：它们等待未来某本新书同时够到两座岛时自然成桥，这正是涌现机制的工作方式。宁缺毋滥——垃圾边会让图谱失去可信度。

**边权与挂靠原则（用户裁决 2026-09-18）**：边的建立与强弱只看**语义相关性**（概念/观点的实际关联强度），不看出书先后——早期书的概念节点因「后来者默认挂靠」而积累度数优势，是图谱的结构性偏差（**先拆优势**：不能因为薛的书拆得最早就让它在宇宙里权重最大）。后书遇到语义更贴切的概念时，**建新节点再连旧节点**，不为省事挂靠旧名；Dream 合并审计专门检查「挂靠偏早」并提案修正。

## Dream（定期整理 / 睡眠整合）

触发：手动 `/bookverse dream`；或 books-index 每满 5 本，step 7 结束时提示"宇宙该做梦了"；或人格提案/涌现累计至阈值（约 20/50/100 条）时一并整理（用户裁决 2026-09-18）。

六步（产出 `universe/records/dreams/dream-<日期>.md`）：
0. **重读仪式（每次最多 1 本；用户裁决 2026-09-18 同意）**：挑一本旧书重读——人格版本差 ≥4 或书后出现新证据者优先；测绘图/书内图谱复用，step 3/5 重走，产出第二版 digest 与书评，新旧对照入 journal（同一本书对变了的人是另一本书）；**书节点 `teardown-version` 递增**（v1→v2），第二版产物以 `-v2` 后缀并存不覆盖
1. **合并审计**：扫描概念名/别名的语义重叠。机械同义（一词多译、显而易见的重复）→ 直接合并 + 记 journal；语义性重叠（如"租值消散"vs"寻租"是否该合）→ 出合并提案待用户裁决；同时检查「挂靠偏早」（见边权与挂靠原则）
2. **内化**：通读各概念节点的对照表与涌现台账，提炼**跨书模式**（≥3 本书反复出现的张力/共性）→ 生成 persona 内化提案（默认入库制，见 persona.md）；同时把 ≥5 行的对照表压缩出"小结行"附于表尾
3. **修剪**：被拒绝超 30 天的涌现候选 → 归档区（不再主动提议）；无任何对照行的孤立概念 → 标记"待连接"（不删除）；**思想立场表只做触达标记不删除**（用户裁决 2026-09-18：知识、技能、观点都有触发场景与条件，长期未触发≠应淘汰——逐行标注最近触发场景/时间即可，反驳与合并提案由合议生成、用户裁决）
4. **重组**：按最新 themes 重新聚类 index.md 的主题域子图（每图 ≤12 节点规则复查）
5. **报告**：合并/内化/修剪/重组/重读清单 + 宇宙健康度（孤岛数、平均度数、最热概念及其先拆优势检查）+ ROI 节（口径见 references/roi.md）——按域盘点投入产出与边际回报

Discipline：机械操作可自动执行（留痕），凡触及 persona 或删除性操作必须用户裁决。
- **只有主 agent 写宇宙**（子 agent 只产文件），避免写冲突

## 冷启动

宇宙不存在时（首拆），step 4 创建骨架：`index.md`（空表 + 说明）、`books/`、`concepts/`、`graph/`、`frontier.md`。

## index.md 结构

```markdown
# 阅读宇宙
## 书目（| 书 | 作者 | 类型 | 拆书日期 | 概念数 | ）
## 主题域子图
### <域1>（按 themes 聚类，每图 ≤12 节点，超了就拆分域）
```mermaid
graph ...（书为方节点，概念为圆节点，边带标签）
```
## 最近涌现（最新跨书连接清单）
```

## 存储演进路线（v1 不实现，到达条件再做）

- **现状**：markdown + YAML frontmatter 是**唯一事实源**；`edges.jsonl` 是派生缓存
- **涌现台账** `universe/emergent.md`：跨书涌现连接与合成观点的专门记录（含被用户**拒绝**的候选——拒绝留痕，避免重复提议）。frontmatter 边记确定性关系，emergent.md 记假设性连接
- **升级触发**：概念节点 > 150 个（按每本新增 10-12 个算，约 12 本书到达），或用户需要语义检索（"哪些书讲过反脆弱"）
- **升级方式**：SQLite（FTS5 全文 / sqlite-vec 向量）作查询缓存层；`scripts/universe_rebuild.py` 保证 md → DB 全量重建，DB 可随时删除重建，md 永不失真

## 重建脚本

```bash
python3 <skill目录>/scripts/universe_rebuild.py <root>/universe [--init]
```

**层级可加深规则（用户 2026-09-19）**：书库分类与概念域层级可按需加深，整体结构不变——只约束首段（书库两位数编号分类 / 概念一级域）与末段（英文 slug），中间层任意深度。硬校验入口：`python3 <skill目录>/scripts/validate.py`（目录结构/frontmatter/records 命名/边表完整性，CI 用，违规 exit≠0）；查重入口：`book_lookup.py <关键词>`。

扫 universe/books/ 与 universe/concepts/ 的 frontmatter（**递归**，支持层级子目录）→ 重建 edges.jsonl、index.md 书目表、universe/books-index.md 与 universe/LIBRARY.md；**corpus 根从 config 的 corpus_root 解析**（与宇宙分属两仓时必需；旧版 workspace_root 单根布局仍兼容：主题域分组书目树，按书目 frontmatter `domain:` 分组；每本书扫描 00-06 实际产物对照当前规范默认菜单打 ✓✗——规范升级后旧书的 ✗ 即回审/补建提示；附概念域索引与总览统计）。手改 md 后跑一次即可恢复一致性。脚本已支持 **note 持久化**：重建时按 `source+relation+target` 匹配保留旧 note，人工/流程填写的证据不会丢失。

**边表 note 证据指针纪律**（2026-09-17 起执行，存量 49 条已回填）：每条边的 note 是最短证据指针（≤50 字）——优先 `[原文·L行号]`，其次讲次/审计文件出处（`[原文·第0xx讲]`、`[时空审计…]`），确无行号的书-书边写 `[推断·<一句依据>]`。不得留空，不得编造行号。step 4 建边时同步填写；机器层消费者（MCP/脚本）据此按图索骥。
