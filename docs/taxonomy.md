# 任务类型 taxonomy
- single：单函数单次调用。
- parallel：一句话需并行多个调用。
- multi_turn：需结合 `history` 上下文确定调用（餐馆名、日程标题等）。
- irrelevance：**不应调用任何函数**（闲聊/信息不足应追问/无匹配工具）；`gold.calls=[]`。
- arg_hard：参数抽取难例（相对日期、中文数字、口语时间、枚举映射）。
难度 easy/medium/hard 按抽取与推断难度划分。
