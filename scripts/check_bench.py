#!/usr/bin/env python3
"""Validation for zh-function-calling-bench. Exit 0=clean,1=problems."""
import json, os, re, sys
from collections import Counter
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ={"id","category","difficulty","query","tools","gold","rationale","tags"}
OPT={"history","context_date"}
CATS={"single","parallel","multi_turn","irrelevance","arg_hard"}
REL=re.compile(r"明天|后天|大后天|今天|下周|本周|下下周")
def main():
    probs=[]; seen_id=set(); seen_q=set(); n=0; cat=Counter()
    for ln,line in enumerate(open(os.path.join(ROOT,"data/bench.jsonl"),encoding="utf-8"),1):
        line=line.strip()
        if not line: continue
        n+=1
        try: o=json.loads(line)
        except Exception as e: probs.append(f"L{ln} bad JSON {e}"); continue
        ks=set(o)
        if not REQ<=ks or not ks<=(REQ|OPT): probs.append(f"L{ln} keys={sorted(ks)}"); continue
        if o["id"] in seen_id: probs.append(f"L{ln} dup id")
        seen_id.add(o["id"])
        if o["query"] in seen_q: probs.append(f"L{ln} dup query")
        seen_q.add(o["query"])
        if o["category"] not in CATS: probs.append(f"L{ln} bad category")
        cat[o["category"]]+=1
        if o["difficulty"] not in {"easy","medium","hard"}: probs.append(f"L{ln} bad difficulty")
        if not str(o.get("rationale","")).strip(): probs.append(f"L{ln} empty rationale")
        toolnames={t["name"] for t in o["tools"]}
        toolprops={t["name"]:t["parameters"] for t in o["tools"]}
        calls=o["gold"]["calls"]
        if o["category"]=="irrelevance" and calls: probs.append(f"L{ln} irrelevance must have empty gold")
        if o["category"]!="irrelevance" and not calls: probs.append(f"L{ln} non-irrelevance needs gold calls")
        for c in calls:
            if c["name"] not in toolnames: probs.append(f"L{ln} call {c['name']} not in tools"); continue
            pp=toolprops[c["name"]]; props=pp.get("properties",{}); req=pp.get("required",[])
            for k in c.get("arguments",{}):
                if k not in props: probs.append(f"L{ln} arg {k} not in {c['name']} schema")
            for k in req:
                if k not in c.get("arguments",{}): probs.append(f"L{ln} missing required {k} in {c['name']}")
            for k,v in c.get("arguments",{}).items():
                pr=props.get(k,{})
                if "enum" in pr and v and v not in pr["enum"]: probs.append(f"L{ln} {k}={v!r} not in enum")
        # samples that RESOLVE a relative date into a YYYY-MM-DD arg must carry context_date
        has_resolved_date=any(re.match(r"^\\d{4}-\\d{2}-\\d{2}$",str(v))
                              for c in calls for v in c.get("arguments",{}).values())
        if has_resolved_date and REL.search(o["query"]) and "context_date" not in o:
            probs.append(f"L{ln} resolved date arg from relative time but no context_date")
    irr_ratio=cat["irrelevance"]/n if n else 0
    if irr_ratio<0.15: probs.append(f"irrelevance ratio {irr_ratio:.2f} < 0.15")
    for c in CATS:
        if cat[c]==0: probs.append(f"category {c} is empty")
    print(f"checked {n} samples | categories {dict(cat)}")
    if probs:
        print(f"FAIL — {len(probs)} issue(s):")
        for x in probs[:40]: print("  -",x)
        return 1
    print("PASS — schema/tools/args/enum/irrelevance/balance all clean.")
    return 0
sys.exit(main())
