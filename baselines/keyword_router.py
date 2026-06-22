#!/usr/bin/env python3
"""Naive baseline: always call the first tool with no args (or empty for irrelevance-blind)."""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def main():
    out=open(os.path.join(ROOT,"baselines","predictions_keyword.jsonl"),"w",encoding="utf-8")
    for line in open(os.path.join(ROOT,"data","bench.jsonl"),encoding="utf-8"):
        line=line.strip()
        if not line: continue
        o=json.loads(line); tools=o.get("tools",[])
        calls=[{"name":tools[0]["name"],"arguments":{}}] if tools else []
        out.write(json.dumps({"id":o["id"],"calls":calls},ensure_ascii=False)+"\n")
    print("wrote baselines/predictions_keyword.jsonl")
if __name__=="__main__": main()
