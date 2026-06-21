#!/usr/bin/env python3
"""Score predictions for zh-function-calling-bench.
Predictions: JSONL of {"id":..., "calls":[{"name":..,"arguments":{..}}]}."""
import json, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from normalize import normalize_value
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    d={}
    for line in open(p,encoding="utf-8"):
        line=line.strip()
        if line: o=json.loads(line); d[o["id"]]=o
    return d
def reqkeys(sample,name):
    for t in sample["tools"]:
        if t["name"]==name: return t["parameters"].get("required",[])
    return []
def call_sig(sample,call):
    req=reqkeys(sample,call["name"])
    args=call.get("arguments",{})
    return (call["name"], frozenset((k,normalize_value(args.get(k,""))) for k in req))
def name_set(calls): return frozenset(c["name"] for c in calls)
def full_set(sample,calls): return frozenset(call_sig(sample,c) for c in calls)
def main():
    if len(sys.argv)<2: print("usage: score.py preds.jsonl"); return 2
    gold=load(os.path.join(ROOT,"data/bench.jsonl")); pred=load(sys.argv[1])
    from collections import defaultdict
    miss=[i for i in gold if i not in pred]
    name_ok=full_ok=0
    cat_tot=defaultdict(int); cat_full=defaultdict(int)
    irr_gold=irr_false=irr_miss=0
    for i,g in gold.items():
        G=g["gold"]["calls"]; P=pred.get(i,{}).get("calls",[])
        cat=g["category"]; cat_tot[cat]+=1
        if name_set(G)==name_set(P): name_ok+=1
        full=(full_set(g,G)==full_set(g,P))
        if full: full_ok+=1; cat_full[cat]+=1
        if not G:  # irrelevance
            irr_gold+=1
            if P: irr_false+=1
        elif not P:
            irr_miss+=1
    n=len(gold)
    out={"n_scored":n,"missing_predictions":len(miss),
         "name_accuracy":round(name_ok/n,3),"full_call_accuracy":round(full_ok/n,3),
         "false_call_rate_on_irrelevance":round(irr_false/irr_gold,3) if irr_gold else None,
         "miss_rate_on_actionable":round(irr_miss/(n-irr_gold),3) if n-irr_gold else None,
         "by_category_full_accuracy":{c:round(cat_full[c]/cat_tot[c],3) for c in sorted(cat_tot)}}
    json.dump(out,open(os.path.join(ROOT,"report.json"),"w"),ensure_ascii=False,indent=2)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0
sys.exit(main())
