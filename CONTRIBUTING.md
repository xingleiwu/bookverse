# 贡献指南（CONTRIBUTING）

本仓库是单体仓库：方法论（skill/）、工具（scripts、mcp/）、数据（books/、universe/）同库演进。三类内容的改动方式与验收门槛不同，请对号入座。

## 仓库模型

- **本仓库（bookverse）**：开源，接受 PR
- **书库仓库（私有）**：PDF 原件，版权原因**永不公开**，不参与协作；本仓库 books/ 的层级结构镜像书库分类（如 `books/03_经济与投资/经济理论/<slug>/`）

## 分支与提交

- `main` 受保护，只接受 PR 合入（维护者本人也走 PR，保留评审痕迹）
- 分支命名：`feat/<范围>`（规范/工具）、`book/<slug>`（一书一 PR）、`data/<范围>`（宇宙数据）、`fix/<范围>`
- Commit 前缀：`feat` / `fix` / `docs` / `data` / `refactor` / `chore`
- 一 PR 一主题：规范改动不要混工具改动，数据 PR 不要混规范改动

## 三类 PR 与验收门槛

### 1. 规范 PR（skill/SKILL.md、skill/references/）

改的是「拆书方法论」本身，门槛最高：

- 说明**动机与实战依据**（哪本书的拆解暴露了这个问题），纯理论优化默认不加——本仓库的规范全部由实战复盘固化
- 涉及流程变更的，建议附「先贤评审」式的自我攻击（这个改动最疼的反例是什么）
- `CHANGELOG.md` 补条目
- 收敛性：优先删规则而非加规则；新增纪律须附触发条件与失效条件

### 2. 工具 PR（skill/scripts/、mcp/）

- `python3 -m py_compile` 通过；mcp 改动跑 `python3 mcp/test_client.py`（空书库自动跳数据项）
- 涉及 universe_rebuild 的改动：**幂等性验证**（连续跑两遍，第二遍无 diff）
- 不引入第三方依赖（零依赖是既定约束）

### 3. 数据 PR（众包拆书——完整流程见 skill/references/crowd.md：认领 issue → 本地拆 → PR-PACKAGE → 主 PR 发 bookcorpus、宇宙增量副 PR 发本仓）

拆书产物与宇宙数据，**一书一 PR**：

- 必须包含 `06-takeaway/review-log.md`（三角色评审记录：内容质量 / 渠道专家 / 去AI味）
- 承重论断附 `[原文·行号]` 信源，抽验说明写在 PR 描述（哪几条回查了 fulltext）
- 书目 frontmatter 字段齐全（title/author/type/domain/cost/concepts/related，见 universe.md 字段表）
- **`00-source/fulltext.md` 与任何 PDF 禁止提交**（版权；CI 会检查）
- 合入前维护者重跑 `universe_rebuild.py` 校验 LIBRARY/edges 一致性
- `universe/`（阅读宇宙/人格/records）位于技能仓：persona 为维护者个人数据外部不改；概念卡与 edges 的修正类 PR 允许，须附证据指针

## CI（建议配置，GitHub Actions）

1. `py_compile` 全部脚本
2. `check_punctuation.py` 对 PR 涉及的 `books/**/06-takeaway/*.md`
3. rebuild 幂等：跑两遍 universe_rebuild，第二遍输出无变化
4. 版权护栏：`git ls-files | grep -E 'fulltext\.md|\.pdf$'` 必须为空

## Issue

三类轻量模板：**拆书请求**（想看某本被拆）、**规范提案**（方法论改动讨论，先议后 PR）、**bug**。

## 行为边界

拆书产物含原文摘录，属评注引用；贡献者对自己提交内容的版权边界自负。讨论书与观点时对事不对人——本仓库的红队纪律（批判必须给依据）同样适用于人与人的讨论。
