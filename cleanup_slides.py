#!/usr/bin/env python3
"""Clean packt-specific hard-coded slide branches from the predictions deck."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
path = ROOT / "slides.html"
t = path.read_text(encoding="utf-8")

# Always hide Packt badge
t = t.replace(
    """      const packtBadge = document.getElementById('slide-packt-badge');
      if (packtBadge) {
        packtBadge.style.display = (slide.number === 1) ? 'inline-flex' : 'none';
      }""",
    """      const packtBadge = document.getElementById('slide-packt-badge');
      if (packtBadge) {
        packtBadge.style.display = 'none';
      }""",
)

# Fix document.title leftover
t = t.replace(
    """      document.title = uiText(
        'Packt Masterclass Presentation: Hands-On Harness Engineering',
        'Packt 大师课：智能体驾驭工程（中英切换）'
      );""",
    """      document.title = uiText(
        'Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard',
        '2026 智能体 AI 十大预测 — 年中成绩单'
      );""",
)

# Empty svgMap
t2, n = re.subn(r"const svgMap = \{.*?\};", "const svgMap = {};", t, count=1, flags=re.S)
print("svgMap replacements", n)
t = t2

# Header logo
t = t.replace("assets/images/harness_app_icon.png", "assets/images/ken-head-shot.png")
t = t.replace('alt="Harness Engineering Logo"', 'alt="Ken Huang"')

# Simplify: keep slide 1 branch, drop slide 2+ special cases, default to bullets
start = t.find("} else if (slide.number === 1) {")
if start < 0:
    raise SystemExit("slide 1 branch not found")
end_marker = "bodyEl.innerHTML = bodyHtml;"
end = t.find(end_marker, start)
if end < 0:
    raise SystemExit("slide-body assignment not found")

s2 = t.find("} else if (slide.number === 2) {", start)
if s2 < 0:
    raise SystemExit("slide 2 branch not found")

# Truncate slide 1 content: keep only through pillars row closing, drop books / thesis leftovers
slide1 = t[start:s2]
pillars_end = slide1.find("</div>\n            </div>\n")
# Find end of pillars-row more reliably
marker = "slide-1-pillars-row"
pi = slide1.find(marker)
if pi < 0:
    raise SystemExit("pillars not in slide 1")
# Find the closing of slide-1-container after pillars
# Look for last occurrence pattern after pillars: closing divs before template end
# Strategy: cut slide1 at the end of pillars-row block
# Find `<div class="slide-1-pillars-row">` ... matching close
p_start = slide1.find('<div class="slide-1-pillars-row">')
if p_start < 0:
    raise SystemExit("pillars div missing")

# Walk from p_start to find matching closing for pillars-row then container
rest = slide1[p_start:]
# Simple: find `</div>\n          `;` that ends the template literal for slide 1
# The original ends bodyHtml += ` ... `;
tmpl_end = slide1.rfind("`;")
if tmpl_end < 0:
    raise SystemExit("template end not found in slide1")

# Rebuild a tight slide 1: keep from start through pillars inclusive
# Extract from bodyHtml += ` through pillars-row end
hero_start = slide1.find("bodyHtml += `")
if hero_start < 0:
    raise SystemExit("bodyHtml template missing")

# Find pillars-row closing: after pillars content there are nested divs
# Use regex to capture from bodyHtml through end of pillars-row
m = re.search(
    r"(bodyHtml \+= `\s*<div id=\"slide-content-wrap\" class=\"slide-1-container\">.*?class=\"slide-1-pillars-row\">.*?</div>\s*</div>)",
    slide1,
    flags=re.S,
)
if not m:
    raise SystemExit("could not extract compact slide 1 hero")

compact_slide1 = (
    "} else if (slide.number === 1) {\n"
    "        "
    + m.group(1)
    + "\n          </div>\n        `;\n      "
)

new_tail = (
    compact_slide1
    + """} else {
        bodyHtml += '<div id="slide-content-wrap" class="slide-content-wrapper">' + formatBullets(restLines) + '</div>';
      }

      """
)

t = t[:start] + new_tail + t[end:]
print("Simplified renderSlide; compact slide 1 length", len(compact_slide1))

path.write_text(t, encoding="utf-8")

# Sync docs/
docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
(docs / "slides.html").write_text(t, encoding="utf-8")
zh = ROOT / "slides-zh.js"
if zh.exists():
    (docs / "slides-zh.js").write_bytes(zh.read_bytes())

print("Saved slides.html and docs/slides.html")
