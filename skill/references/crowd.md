# 众包协作拆书（crowd）

让社区贡献者用 bookverse 流水线拆书，产物经 PR 由维护者合并进宇宙。本文是全流程规范：贡献者怎么干、维护者怎么合、边界在哪。

**设计原则（防写冲突）**：贡献者只产出**天然无冲突的增量**——新书目录（corpus）、新书节点、新概念文件；一切**派生物**（edges.jsonl / LIBRARY / books-index / index.md）由维护者合并后统一 rebuild；**人格与涌现裁决**只在维护者侧（确认点 C 的默认入库制是维护者的人格，不吸收贡献者的人格信号）。

## 一、贡献者流程（七步）

### 0. 环境
```bash
git clone git@github.com:godlockin/bookverse.git && cp -r bookverse/skill/ ~/.agents/skills/bookverse/
git clone git@github.com:godlockin/bookcorpus.git   # 数据仓工作副本
git clone git@github.com:godlockin/bookverse.git bookverse-universe  # 宇宙工作副本（读参照 + 可能的宇宙 PR）
```
需要：支持 skills 的 coding agent（ZCode / Claude Code 等）+ 本地有目标书的电子文件。

### 1. 认领（防重复拆）
在 **bookcorpus** 仓库开 Issue（「拆书请求」模板）：书名 / 作者 / 为什么值得拆 / 建议分类。维护者核两件事后 assign 认领人：① `book_lookup.py <书名>` 查重（已拆过则转「重读」轨道或关闭）② 分类归属（书库两位数分类层级）。**认领后 7 天无提交自动释放**（维护者手动解 assign 并在 issue 注明）。

### 2. 本地拆解
```bash
cd bookcorpus && git checkout -b book/<slug>
```
对 agent 说「拆解这本书：<本地文件路径>」，分类/确认点按流程走（全自动模式亦可）。产物落 `corpus/<分类层级>/<slug>/`。拆解深度自选（全拆/轻拆/调研档，见 SKILL.md 拆解深度节）——issue 里建议过档位的按建议来。

### 3. 自检（PR 前必过）
```bash
python3 ~/.agents/skills/bookverse/scripts/validate.py <bookcorpus 根> <bookverse-universe>/universe
python3 ~/.agents/skills/bookverse/scripts/check_punctuation.py corpus/<分类>/<slug>/06-takeaway/*.md --fix
```
外加：review-log.md 三角色意见齐（内容质量 / 渠道 / 去AI味）；**生成 PR 包**（见第二节）。

### 4. 发 PR（可能两个）
- **主 PR → bookcorpus**（分支 `book/<slug>`）：新增 `corpus/<分类>/<slug>/` 全目录 + `PR-PACKAGE.md`；PR 描述用「拆书 PR」模板，关联认领 issue
- **副 PR → bookverse**（仅当宇宙增量非空）：新概念文件（`universe/concepts/<域>/…/<slug>.md`）+ 书节点（`universe/books/<分类>/<slug>.md`）。**禁止**改动：edges.jsonl、LIBRARY、books-index、index.md、persona/*、emergent 已裁决区——这些是维护者领地

### 5. 审查（PR 上的三层）
1. **机器层（CI）**：validate.py、标点检查、版权护栏（fulltext/PDF 零容忍）、rebuild 幂等
2. **抽验层**：PR 描述必须给 3-5 条抽验（论断 → [原文·行号] → 上下文引句）；有原书的审查者本地核对，没有的审逻辑与格式
3. **评审层**：review-log 中的 FIX 是否处置完整；去AI味是否达标

### 6. 合并（维护者，见第三节）

### 7. 收尾
merge 后维护者 rebuild 宇宙、裁决涌现候选、close issue；贡献者在 fork 同步主仓。

## 二、PR 包（`PR-PACKAGE.md`，拆书完成时由流程生成，放书目录根部）

```markdown
# PR 包 —《书名》
## 概要（slug / 分类 / 深度档 / teardown-version / 成本）
## bookcorpus 变更清单（新增文件树 + 行数）
## bookverse 宇宙增量
- 书节点 md 全文（ready-to-copy，frontmatter 十一字段齐）
- 新概念文件全文（每个：slug / 中文名 / 域 / emerged-from）
- 既有概念对照表追加行（若有：概念名 + 追加行内容）
## 涌现候选（供维护者裁决，不入格）
## 抽验材料（3-5 条：论断 → [原文·行号] → 上下文引句）
## 自检结果（validate / 标点 / review-log 三角色结论摘要）
```

## 三、维护者合并 checklist（六步）

1. CI 全绿（四项）
2. review-log 三角色齐、FIX 处置完整
3. 亲手抽验 ≥2 条（对照自有原书或公版来源；核不了的在 PR 标注「未核」并要求第二审查者）
4. `book_lookup.py` 终查重（版本冲突 → 重读轨道，teardown-version 递增而非覆盖）
5. 合并顺序：**先 merge bookcorpus PR，再 merge bookverse 副 PR** → 在 bookverse 跑 `universe_rebuild.py` → commit AUTO 产物（edges/LIBRARY/index 更新）
6. 人格侧：把 PR-PACKAGE 的涌现候选过确认点 C（默认入库/否决留痕）→ close 认领 issue → 必要时更新 frontier（外延书单去重）

## 四、边界与红线

| 域 | 贡献者 | 维护者 |
|---|---|---|
| corpus 书目录 | ✅ 新增（一书一 PR） | 审查合并 |
| universe 书节点 / 新概念 | ✅ 新增文件 | 审查合并 |
| 既有概念对照表 | ⚠️ 只许追加行，PR 里说明 | 审查 |
| edges / LIBRARY / index | ❌ 禁改（派生物） | rebuild 统一生成 |
| persona / 涌现裁决 | ❌ 禁改 | ✅ 独占 |
| skill 规范 | 走 bookverse 规范 PR | 先贤评审级门槛 |

**版权红线**：`00-source/fulltext.md` 与任何 PDF/EPUB 原件禁止提交（CI 检查，零容忍）；拆解产物中的原文摘录属评注引用，贡献者对自提交内容的版权边界自负。

**质量红线**：无 review-log 不合；行号抽验失败退回；去AI味不过退回——退回时在 PR 给出具体段落级意见，不做整体否决。
