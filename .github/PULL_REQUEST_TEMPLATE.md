<!-- bookverse（技能仓）PR 模板：规范 / 工具 / 宇宙数据三类通用 -->

## PR 类型

- [ ] 规范（skill/references…——需附实战依据与「最疼反例」自我攻击，见 CONTRIBUTING）
- [ ] 工具（scripts / mcp——py_compile + 冒烟 + rebuild 幂等）
- [ ] 宇宙数据（概念/书节点——须来自拆书 PR 的副 PR，关联 bookcorpus PR #<编号>）

## 改动摘要

## 验证

- [ ] `python3 skill/scripts/validate.py <corpus> universe` 通过
- [ ] 涉及 rebuild：连跑两遍无 diff
- [ ] CHANGELOG 已补条目（规范/工具类）

## 边界自查

- [ ] 未改 edges.jsonl / LIBRARY / books-index / index.md（维护者 rebuild 领地）
- [ ] 未改 universe/persona/*（维护者人格）
