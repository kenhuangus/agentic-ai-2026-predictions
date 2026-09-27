#!/usr/bin/env python3
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
t = (root / "slides.html").read_text(encoding="utf-8")
en = json.loads(re.search(r"const slidesData = (\[.*?\]);", t, re.S).group(1))
zh_js = (root / "slides-zh.js").read_text(encoding="utf-8")
zh = json.loads(zh_js[zh_js.find("{") :].rstrip().rstrip(";"))
print("EN", len(en))
print("ZH", sorted(zh["lines"].keys(), key=int))
ok = True
for s in en:
    n = str(s["number"])
    lines = zh["lines"].get(n)
    if not lines:
        print("MISSING", n)
        ok = False
        continue
    if len(lines) != len(s["raw_lines"]):
        print("LEN", n, len(s["raw_lines"]), len(lines))
        ok = False
    else:
        print(n, "OK")
print("script", "slides-zh.js" in t)
print("buttons", 'setLang(' in t or "lang-btn" in t)
print("PASS" if ok else "FAIL")
