#!/usr/bin/env python3
"""Argument value normalization shared by scorer & docs."""
import re
FW={c:chr(ord(c)-0xFEE0) for c in "０１２３４５６７８９"}
def normalize_value(v):
    s=str(v).strip().translate(str.maketrans(FW))
    s=s.replace("：",":").replace(" ","")
    return s
