#!/usr/bin/env python3
"""Naive keyword->function router (no real arg extraction). Emits predictions."""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW=[("高铁","search_train"),("火车","search_train"),("快递","query_express"),("天气","get_weather"),
 ("闹钟","set_alarm"),("换","currency_convert"),("日元","currency_convert"),("美元","currency_convert"),
 ("消息","send_message"),("酒店","book_hotel"),("外卖","order_food"),("点","order_food"),
 ("日程","add_event"),("音乐","play_music")]
out=[]
for line in open(os.path.join(ROOT,"data/bench.jsonl"),encoding="utf-8"):
    line=line.strip()
    if not line: continue
    o=json.loads(line); q=o["query"]; names={t["name"] for t in o["tools"]}
    calls=[]
    for kw,fn in KW:
        if kw in q and fn in names and fn not in [c["name"] for c in calls]:
            calls.append({"name":fn,"arguments":{}})  # naive: no args
    out.append({"id":o["id"],"calls":calls})
with open(os.path.join(ROOT,"baselines/predictions_keyword.jsonl"),"w") as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print("wrote",len(out))
