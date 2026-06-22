# 参数归一化口径（评分用，定稿后不得为某模型临时改）
- 字符串：去首尾与内部空白。
- 中文数字/日期：相对日期按样本 context_date 解析为 YYYY-MM-DD；时间归一化为 HH:MM。
- 枚举：同义词映射到 enum 值。
- 详见 scripts/normalize.py（执行 agent 在 M2 补全数字/日期解析）。
