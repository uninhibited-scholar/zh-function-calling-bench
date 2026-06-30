#!/usr/bin/env python3
"""Run an OpenAI-compatible chat model over zh-function-calling-bench -> predictions.jsonl.
Zero deps (urllib). Then score with scripts/score.py.

Usage:
  export OPENAI_API_KEY=sk-...
  python3 scripts/run_model.py --model gpt-4o [--base-url ...] [--limit N]
Output: predictions_<model>.jsonl  ({"id":..., "calls":[{"name","arguments"}]})
"""
import argparse, json, os, re, ssl, sys, urllib.request
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYS = ("你是函数调用助手。给定用户请求与可用工具列表，判断应调用哪些函数及参数。"
       "只输出一个 JSON 对象：{\"calls\":[{\"name\":\"函数名\",\"arguments\":{...}}]}。"
       "若没有合适的工具、或信息不足以调用，则输出 {\"calls\":[]}。不要解释。"
       "当前日期见用户消息中的 context_date，用于解析相对时间。")

def extract_obj(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m: text = m.group(1).strip()
    i = text.find("{")
    if i >= 0:
        try: return json.loads(text[i:text.rfind("}")+1])
        except Exception: pass
    return {"calls":[]}

def call(base, key, model, user):
    body = json.dumps({"model":model,"temperature":0,
        "messages":[{"role":"system","content":SYS},{"role":"user","content":user}]}).encode()
    req = urllib.request.Request(base.rstrip("/")+"/chat/completions", data=body,
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=120, context=_SSL_CTX) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL","https://api.openai.com/v1"))
    ap.add_argument("--key", default=os.environ.get("OPENAI_API_KEY",""))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    if not a.key: print("ERROR: set OPENAI_API_KEY or --key"); return 2
    out = a.out or os.path.join(ROOT, f"predictions_{re.sub(r'[^a-zA-Z0-9._-]','_',a.model)}.jsonl")
    rows = [json.loads(l) for l in open(os.path.join(ROOT,"data","bench.jsonl"),encoding="utf-8") if l.strip()]
    if a.limit: rows = rows[:a.limit]
    # 断点续跑：跳过已写的 id
    done=set()
    if os.path.exists(out):
        for l in open(out,encoding="utf-8"):
            if l.strip():
                try: done.add(json.loads(l)["id"])
                except Exception: pass
    todo=[o for o in rows if o["id"] not in done]
    print(f"resume: {len(done)} done, {len(todo)} todo")
    with open(out,"a",encoding="utf-8") as w:
        for i,o in enumerate(todo,1):
            user = (f"context_date: {o.get('context_date','')}\n"
                    f"可用工具:\n{json.dumps(o['tools'],ensure_ascii=False)}\n\n"
                    f"用户请求: {o['query']}")
            for _retry in range(3):
                try:
                    obj = extract_obj(call(a.base_url,a.key,a.model,user))
                    calls = obj.get("calls",[]) if isinstance(obj,dict) else []
                    break
                except Exception as e:
                    import time; time.sleep(2*(_retry+1))
                    if _retry==2: print(f"  [{i}] {o['id']} error: {e}"); calls=[]
            w.write(json.dumps({"id":o["id"],"calls":calls},ensure_ascii=False)+"\n"); w.flush()
            print(f"  [{i}/{len(todo)}] {o['id']} -> {len(calls)} call(s)")
    print(f"\nwrote {out}\n下一步: python3 scripts/score.py {out}")
    return 0
if __name__ == "__main__": sys.exit(main())
