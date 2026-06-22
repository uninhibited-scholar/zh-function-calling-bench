#!/usr/bin/env python3
"""Argument-value normalization for fair matching. Extend in docs/normalization.md."""
import re
CN_NUM = {"零":"0","一":"1","二":"2","两":"2","三":"3","四":"4","五":"5","六":"6","七":"7","八":"8","九":"9","十":"10"}
def norm(v):
    if isinstance(v, str):
        s = v.strip()
        s = re.sub(r"\s+", "", s)
        return s
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return str(v)
    return v
def norm_args(d):
    return {k: norm(v) for k, v in sorted((d or {}).items())}
