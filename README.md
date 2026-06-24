# zh-function-calling-bench

简体中文 · 原生「函数调用 / 工具调用」评测基准（可机器评分）。

[![CI](https://github.com/uninhibited-scholar/zh-function-calling-bench/actions/workflows/validate.yml/badge.svg)](https://github.com/uninhibited-scholar/zh-function-calling-bench/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)

评测 LLM 在**简体中文**语境下能否输出正确的**函数名 + 参数**。现有 function-calling 基准（BFCL / ToolLLM / ACEBench）为英文，中文仅有**繁中(ZHTW)翻译版**——本项目做**简体、原生编写、本土化场景**（车票/外卖/快递/日历等），非翻译。评分为 AST 式结构化匹配，零主观、CI 可担保。

> 现状诚实定位：**v0.4 种子集 103 条、单人编写、关键词基线**——能跑通、有论点、可复现的早期基准；规模化见 [PLAN.md](PLAN.md)。

## 数据
- `data/bench.jsonl`，共 **103 条**（目标 300+）。五类配比 `single 36 / parallel 17 / multi_turn 11 / arg_hard 19 / irrelevance 20`（**irrelevance 19.4% ≥15%**，防"逢问必调"刷分）。
- 字段：`id, category, difficulty, query, tools, gold, rationale, tags`（多轮含 `history`，相对日期含 `context_date`）。详见 [docs/taxonomy.md](docs/taxonomy.md) / [docs/normalization.md](docs/normalization.md)。

## 评测方法
让被测模型对每条 `query`（给定 `tools`）输出 `{id, calls:[{name,arguments}]}`，然后：
```bash
python3 scripts/score.py your_predictions.jsonl
```
指标：函数名准确率、**完整调用准确率**（name+required 参数，经归一化）、irrelevance 准确率、各类别分项。

## 关键词基线（自带论点）
朴素「关键词→函数」路由（`baselines/keyword_router.py`，总调首个工具、不抽参数）跑全集 76 条：

```json
{ "function_name_accuracy": 0.645, "full_call_accuracy": 0.0, "irrelevance_accuracy": 0.0 }
```

**看点**：朴素基线能蒙对约六成函数名，但**完整调用 0.0、irrelevance 0.0**——参数全填不对、该不调的也乱调。**选对工具 ≠ 会用工具**；真正难的是参数抽取与"该不该调"的判断，这正是本基准要测的。

## 跑真实模型（排行榜）
```bash
export OPENAI_API_KEY=sk-...     # 任意 OpenAI 兼容端点
python3 scripts/run_model.py --model <模型名> [--base-url <端点>]
python3 scripts/score.py predictions_<模型名>.jsonl
```

| 模型 | function_name_acc | full_call_acc | irrelevance_acc | 备注 |
|---|---:|---:|---:|---|
| naive baseline | 0.645 | 0.0 | 0.0 | 总调首个工具，作下限 |
| _待填_ | | | | |

## 质量保证
`scripts/check_bench.py` + CI 每次提交校验：schema 严格、gold 调用的函数与参数必须在 `tools` 中声明、required 齐全、enum 合法、`irrelevance` gold 为空、相对时间样本须带 `context_date`、`irrelevance` 占比 ≥15%、五类非空。**禁止靠删难例或放宽 gold 骗过校验。**

## 许可
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。

相关作品：[agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) · [attack-bench-zh](https://github.com/uninhibited-scholar/attack-bench-zh) · [defensive-refusal-bench-zh](https://github.com/uninhibited-scholar/defensive-refusal-bench-zh) · [cybersec-qa-dataset-zh](https://github.com/uninhibited-scholar/cybersec-qa-dataset-zh)
