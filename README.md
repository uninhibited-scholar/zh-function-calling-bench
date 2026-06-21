# zh-function-calling-bench

简体中文 · 原生「函数调用 / 工具调用」评测基准（可机器评分）。

> 🚧 规划中。完整规格见 [PLAN.md](PLAN.md)。
> 评测 LLM 在简体中文语境下能否输出正确的函数名 + 参数。五类任务（单调用 / 并行 / 多轮 / 不该调用 / 参数难例），评分为 AST 式结构化匹配，零主观、CI 可担保。
> 现有 function-calling 基准（BFCL / ToolLLM / ACEBench）为英文，中文仅繁中翻译版——本项目做**简体、原生编写、本土化场景**。

相关作品：[agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) · [attack-bench-zh](https://github.com/uninhibited-scholar/attack-bench-zh) · [cybersec-qa-dataset-zh](https://github.com/uninhibited-scholar/cybersec-qa-dataset-zh)
