#!/usr/bin/env python3
"""CI gate for zh-function-calling-bench."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = {"id","category","difficulty","context_date","query","tools","gold","rationale","tags"}
CATS = {"single","parallel","multi_turn","irrelevance","arg_hard"}
REL = re.compile(r"(明天|后天|下周|下个?月|昨天|今天|本周)")
def main():
    f = os.path.join(ROOT,"data","bench.jsonl")
    problems, ids, queries, n, ncat = [], set(), set(), 0, {}
    for ln,line in enumerate(open(f,encoding="utf-8"),1):
        line=line.strip()
        if not line: continue
        n+=1
        try: o=json.loads(line)
        except Exception as e: problems.append(f"L{ln} bad JSON: {e}"); continue
        if set(o)!=KEYS: problems.append(f"L{ln} keys={sorted(o)}")
        if o.get("category") not in CATS: problems.append(f"L{ln} bad category {o.get('category')}")
        ncat[o.get("category")] = ncat.get(o.get("category"),0)+1
        if o.get("id") in ids: problems.append(f"L{ln} dup id")
        ids.add(o.get("id"))
        q=o.get("query","").strip()
        if q in queries: problems.append(f"L{ln} dup query")
        queries.add(q)
        toolnames={t["name"] for t in o.get("tools",[])}
        toolparams={t["name"]:set((t.get("parameters",{}).get("properties") or {}).keys()) for t in o.get("tools",[])}
        toolreq={t["name"]:set(t.get("parameters",{}).get("required",[])) for t in o.get("tools",[])}
        calls=(o.get("gold") or {}).get("calls")
        if calls is None: problems.append(f"L{ln} missing gold.calls"); calls=[]
        if o.get("category")=="irrelevance" and calls:
            problems.append(f"L{ln} irrelevance must have empty gold.calls")
        for c in calls:
            if c.get("name") not in toolnames:
                problems.append(f"L{ln} call name {c.get('name')} not in tools"); continue
            args=set((c.get("arguments") or {}).keys())
            extra=args-toolparams[c["name"]]
            if extra: problems.append(f"L{ln} undeclared args {extra}")
            miss=toolreq[c["name"]]-args
            if miss: problems.append(f"L{ln} missing required {miss}")
        if REL.search(q) and not o.get("context_date"):
            problems.append(f"L{ln} relative time but no context_date")
    print(f"checked {n} records; categories={ncat}")
    if problems:
        print(f"FAIL — {len(problems)} issue(s):")
        for p in problems[:50]: print("  -",p)
        return 1
    print("PASS — schema/tools/args/irrelevance/dupes all clean.")
    return 0
if __name__=="__main__": sys.exit(main())
