# zh-function-calling-bench

简体中文 · 原生「函数调用 / 工具调用」评测基准（可机器评分）。

[![CI](https://github.com/uninhibited-scholar/zh-function-calling-bench/actions/workflows/validate.yml/badge.svg)](https://github.com/uninhibited-scholar/zh-function-calling-bench/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)

评测 LLM 在**简体中文**语境下能否输出正确的**函数名 + 参数**。现有 function-calling 基准（BFCL / ToolLLM / ACEBench）为英文，中文仅有**繁中(ZHTW)翻译版**——本项目做**简体、原生编写、本土化场景**（车票/外卖/快递/日历等），非翻译。评分为 AST 式结构化匹配，零主观、CI 可担保。

> 现状诚实定位：**v0 种子集 34 条、单人编写、关键词基线**——能跑通、有论点、可复现的早期基准；规模化见 [PLAN.md](PLAN.md)。

## 数据
- `data/bench.jsonl`，v0 共 **34 条**（目标 300+）。五类：`single / parallel / multi_turn / irrelevance / arg_hard`，`irrelevance` 占 21%（≥15%，防"逢问必调"刷分）。
- 字段：`id, category, difficulty, query, tools, gold, rationale, tags`（多轮含 `history`，相对日期含 `context_date`）。详见 [docs/taxonomy.md](docs/taxonomy.md) / [docs/normalization.md](docs/normalization.md)。

## 评测方法
让被测模型对每条 `query`（给定 `tools`）输出 `{id, calls:[{name,arguments}]}`，然后：
```bash
python3 scripts/score.py your_predictions.jsonl
```
指标：函数名准确率、**完整调用准确率**（name+required 参数，经归一化）、irrelevance 误调用率、各类别分项准确率。

## 关键词基线（自带论点）
朴素「关键词→函数」路由（`baselines/keyword_router.py`，不抽参数）跑全集：

```json
{
  "name_accuracy": 0.676,
  "full_call_accuracy": 0.176,
  "false_call_rate_on_irrelevance": 0.143,
  "by_category_full_accuracy": {"single":0.0,"parallel":0.0,"multi_turn":0.0,"arg_hard":0.0,"irrelevance":0.857}
}
```

**看点**：关键词路由能挑对函数（name 78%），但**完整调用只有 18%**——它**根本不会抽参数**（single/parallel/arg_hard 全 0），还在 **1/4 的"不该调用"样本上误调**。一句话——**选对工具 ≠ 会用工具**；真正难的是参数抽取与"该不该调"的判断，这正是本基准要测的。

## 质量保证
`scripts/check_bench.py` + CI 每次提交校验：schema 严格、gold 调用的函数与参数必须在 `tools` 中声明、required 齐全、enum 合法、`irrelevance` gold 为空、相对时间样本须带 `context_date`、`irrelevance` 占比 ≥15%、五类非空。**禁止靠删难例或放宽 gold 骗过校验。**

## 许可
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。


## 数据与基线（v0.4）

- `data/bench.jsonl`：**v0.4 种子集 76 条**（单人编写、本土化场景、可复现；目标扩至 300+）。五类配比 single 21 / parallel 13 / multi_turn 8 / arg_hard 12 / **irrelevance 14（18.4%）**。
- 字段：`id, category, difficulty, context_date, query, tools, gold, rationale, tags`。

**朴素基线**（`baselines/keyword_router.py`，总调首个工具、空参）跑全集：

```json
{ "function_name_accuracy": 0.643, "full_call_accuracy": 0.0, "irrelevance_accuracy": 0.0 }
```

**看点**：朴素基线**完整调用准确率 0.0、irrelevance 0.0**——蒙对函数名没用，参数填不对、该不调的也乱调。**这正是"函数名对 ≠ 会调用、必须评参数与 irrelevance"的理由。**

> 诚实定位：v0.4、76 条、单人编写、朴素基线——能跑通、有论点、可复现的早期基准；尚非大规模权威基准。

相关作品：[agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) · [attack-bench-zh](https://github.com/uninhibited-scholar/attack-bench-zh) · [defensive-refusal-bench-zh](https://github.com/uninhibited-scholar/defensive-refusal-bench-zh) · [cybersec-qa-dataset-zh](https://github.com/uninhibited-scholar/cybersec-qa-dataset-zh)

---

## 🤝 执行 agent 交接清单（干到全勾即 v0 完成）

- [ ] **M1** `docs/prior-art.md` 填完（对比 BFCL/ToolLLM/ACEBench/ZHTW，确认"简体原生"是真缝）
- [ ] **M2** `scripts/normalize.py` 补全中文数字/相对日期/枚举同义词解析
- [ ] `data/bench.jsonl` ≥ 300 条，其中 `irrelevance` ≥ 15%，`python3 scripts/check_bench.py` 全绿
- [ ] `python3 scripts/score.py <pred>` 产出完整 `report.json`（含 irrelevance 准确率）
- [ ] 关键词基线结果写入 README（≥4 个指标，含 irrelevance）
- [ ] CI 绿；README 增 `load_dataset` + 诚实来源说明 + 归一化口径
- [ ] 红线：工具与场景**原生中文编写，不得翻译 BFCL 样本**；拿不准的记入 `docs/open-questions.md`

> `irrelevance`（不该调用）类是区分"真能力"与"逢问必调刷分"的关键，务必占够比例。
