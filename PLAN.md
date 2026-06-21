# 计划书：zh-function-calling-bench
## 简体中文 · 原生「函数调用 / 工具调用」评测基准（可机器评分）

> 交付给执行 agent 的自包含规格书，冷启动可执行。出品人 GitHub: uninhibited-scholar。
> 立场：通用能力评测（**非安全领域**）。评分纯 exact / 结构化匹配，零主观、CI 可担保。

## 0. 目标
评测一个 LLM 在**简体中文**语境下的函数调用能力：给定用户中文请求 + 一组可用工具(JSON Schema)，模型须输出**正确的函数名 + 正确的参数**。
产出：标注数据 + 自动评分器 + 基线 + 排行榜，发布 GitHub / HF / 魔搭。
**差异化**：目前 BFCL/ToolLLM/ACEBench 为英文；中文侧仅有**繁中(ZHTW)翻译版**——本项目做**简体、原生编写、本土化场景**（中文 App / 国内 API 风格），非翻译。

## 第 0 步（必做）：prior-art 核实
检索 BFCL(v3)、ToolLLM、ACEBench、Nexus、ZHTW function-calling leaderboard、ToolRM、2026 新 function-calling 基准。
产出 `docs/prior-art.md`：列同类语言/任务/评分法/是否简体原生/差异。确认"简体原生 + 本土化场景"是真缝；撞车则停、报告出品人。

## 1. v0 范围（目标 2 周）
- 规模：300–500 条（v0），可扩 1000+。
- 五类任务（参考 BFCL 但原生重写）：
  1. `single`：单函数单次调用。
  2. `parallel`：一句话需并行多个调用。
  3. `multi_turn`：多轮对话中按上下文选调用。
  4. `irrelevance`：**不该调用任何函数**（信息不足该追问 / 工具不匹配）——防"逢问必调"刷分。
  5. `arg_hard`：参数抽取难例（中文数字、日期"下周三"、单位、枚举值映射）。
- 场景本土化：外卖/12306 购票/快递/日历/天气/记账等中文常见场景，工具描述用中文。

## 2. 数据 schema（严格）
```json
{
  "id": "fc-0042",
  "category": "single",
  "difficulty": "easy",
  "query": "帮我查下从北京到上海明天上午的高铁。",
  "tools": [
    {"name": "search_train", "description": "查询火车票",
     "parameters": {"type": "object",
       "properties": {"from": {"type": "string"}, "to": {"type": "string"},
                      "date": {"type": "string", "description": "YYYY-MM-DD"},
                      "period": {"type": "string", "enum": ["上午","下午","晚上"]}},
       "required": ["from", "to", "date"]}}
  ],
  "gold": {"calls": [{"name": "search_train",
            "arguments": {"from": "北京", "to": "上海", "date": "2026-06-22", "period": "上午"}}]},
  "rationale": "明确的单次车票查询；'明天'按对话基准日解析为具体日期。",
  "tags": ["travel", "date-resolution"]
}
```
- 顶层键严格：`id, category, difficulty, query, tools, gold, rationale, tags`。
- `irrelevance` 类的 `gold.calls` 为 `[]`（空 = 不应调用）。
- 凡需相对日期解析，样本须给一个 `context_date` 字段作基准日，保证可判定。

## 3. 评分器 `score.py`（灵魂，参考 BFCL 的 AST 匹配）
让被测模型对每条输出 `{id, calls:[{name,arguments}]}`，评分：
- **函数名准确率**：调用的函数名集合是否正确。
- **完整调用准确率**：name + 全部 required 参数值都对（值做归一化：去空格、中文数字→阿拉伯、日期标准化、枚举同义词映射）。
- **irrelevance 准确率**：该空调用却调用了 = 误调用率；该调用却空 = 漏调用。
- **parallel / multi_turn 分项准确率**。
纯标准库、零依赖、确定性、CI 可跑；输出 `report.json`。归一化规则集中在 `scripts/normalize.py` 并写进 docs。

## 4. 校验 `check_bench.py` + CI（反 Goodhart）
- 每条合法 JSON、schema 严格、键完整；
- `gold.calls` 里每个 `name` 必须在该样本 `tools` 中有定义；
- 每个 argument 的键必须是该工具 parameters 里声明的；required 参数齐全；枚举值在 enum 内；
- `irrelevance` 类 gold 必须为空调用；
- 无重复 id、无重复 query；五类与难度分布非空；
- 相对时间样本必须带 `context_date`。
任一不过 → 红灯。**禁止靠删难例或放宽 gold 骗过校验。**

## 5. 基线（自带论点）
- **朴素基线**：关键词→函数的规则路由器（`baselines/keyword_router.py`），跑全集报告准确率。
- 预期：single 还行，但 `irrelevance` 和 `arg_hard` 崩 → 证明"光靠关键词路由做不了真函数调用"，即本基准价值。
- 可选：留 prompt 模板让出品人后续用任意模型刷分。

## 6. 仓库结构
```
zh-function-calling-bench/
  README.md  PLAN.md  LICENSE(CC BY 4.0)
  data/bench.jsonl
  scripts/score.py  scripts/normalize.py  scripts/check_bench.py
  baselines/keyword_router.py  baselines/predictions_keyword.jsonl
  docs/prior-art.md  docs/taxonomy.md  docs/normalization.md
  .github/workflows/validate.yml
```

## 7. 验收标准（机器可判定的"完成"）
1. `data/bench.jsonl` ≥ 300 条，`check_bench.py` 全绿；
2. `score.py` 能对示例预测产出完整 `report.json`（含上述各分项）；
3. 关键词基线结果写入 README（≥4 个指标，含 irrelevance）；
4. `docs/prior-art.md` + `docs/normalization.md` 完成；
5. CI 绿；README 含一键 `load_dataset` + 诚实来源说明（LLM 生成 vs 人工校验、归一化规则口径）。

## 8. 给执行 agent 的红线
- 工具与场景**原生中文编写**，不得直接翻译 BFCL 样本（避免污染与版权）。
- `irrelevance` 类必须占有足够比例（建议 ≥15%），这是区分真假能力的关键。
- 归一化规则一旦定下写进 docs，不得为了让某模型好看而临时改口径。
- 不确定某条 gold → 记 `docs/open-questions.md`，交出品人裁决。
- 每个里程碑跑 CI，红灯先修。

## 9. 里程碑
M1 prior-art + taxonomy + 归一化规则定稿。
M2 schema + check_bench + score + normalize + 30 条种子（端到端跑通，含 irrelevance）。
M3 扩到 300+、关键词基线、CI 绿。
M4 README/排行榜/诚实声明，发布 HF + 魔搭。
