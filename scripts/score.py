#!/usr/bin/env python3
"""Score predictions for zh-function-calling-bench.
Usage: python3 scripts/score.py predictions.jsonl
predictions: {"id":..., "calls":[{"name":...,"arguments":{...}}]}"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm_args
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(path):
    d={}
    for line in open(path,encoding="utf-8"):
        line=line.strip()
        if line:
            o=json.loads(line); d[o["id"]]=o
    return d
def callset(calls):
    return sorted((c["name"], tuple(sorted(norm_args(c.get("arguments")).items()))) for c in (calls or []))
def main():
    if len(sys.argv)<2: print("usage: score.py predictions.jsonl"); return 2
    gold=load(os.path.join(ROOT,"data","bench.jsonl")); pred=load(sys.argv[1])
    n=name_ok=full_ok=missing=0
    irr_total=irr_ok=0
    for gid,g in gold.items():
        n+=1
        p=pred.get(gid)
        gcalls=(g.get("gold") or {}).get("calls") or []
        if p is None: missing+=1; pcalls=[]
        else: pcalls=p.get("calls") or []
        gnames=sorted(c["name"] for c in gcalls); pnames=sorted(c["name"] for c in pcalls)
        if gnames==pnames: name_ok+=1
        if callset(gcalls)==callset(pcalls): full_ok+=1
        if g.get("category")=="irrelevance":
            irr_total+=1
            if not pcalls: irr_ok+=1
    rep={"n":n,"missing_predictions":missing,
         "function_name_accuracy":round(name_ok/n,3),
         "full_call_accuracy":round(full_ok/n,3),
         "irrelevance_accuracy":round(irr_ok/irr_total,3) if irr_total else None}
    print(json.dumps(rep,ensure_ascii=False,indent=2))
    open(os.path.join(ROOT,"report.json"),"w",encoding="utf-8").write(json.dumps(rep,ensure_ascii=False,indent=2))
    return 0
if __name__=="__main__": sys.exit(main())
