#!/usr/bin/env python3
"""Argument-value normalization for fair matching. See docs/normalization.md."""
import re, unicodedata
_CN={"零":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
def _cn2int(s):
    if s in _CN: return str(_CN[s])
    if s=="十": return "10"
    m=re.fullmatch(r"([一二两三四五六七八九]?)十([一二三四五六七八九]?)",s)
    if m:
        t=_CN.get(m.group(1),1) if m.group(1) else 1
        u=_CN.get(m.group(2),0) if m.group(2) else 0
        return str(t*10+u)
    return None
def norm(v):
    if isinstance(v,bool): return v
    if isinstance(v,(int,float)): return str(v)
    if isinstance(v,str):
        s=unicodedata.normalize("NFKC",v).strip()
        s=re.sub(r"\s+","",s)
        c=_cn2int(s)
        return c if c is not None else s
    if isinstance(v,list): return [norm(x) for x in v]
    return v
def norm_args(d): return {k:norm(v) for k,v in sorted((d or {}).items())}
