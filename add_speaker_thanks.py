#!/usr/bin/env python3
"""Insert speaker intro (#2) and thanks/books closing slide from graph-engineer deck."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path(r"C:\Users\kenhu\packt\graph-engineer")
BUILD = ROOT / "build_slides.py"

SPEAKER_EN = {
    "number": 2,
    "slide_type": "speaker",
    "raw_lines": [
        "About the Speaker: Ken Huang, CISSP",
        "• AI book author and speaker (Harness Engineering, MAESTRO)",
        "• Adjunct Professor, University of San Francisco",
        "• OWASP AIVSS Project Lead",
        "• Fellow and co-chair of two CSA AI Safety working groups",
        "• Core member, OWASP Top 10 for LLM Applications",
        "• AIUC-1 Consortium Member",
        "• Grant reviewer, Schmidt Sciences",
        "• EC-Council instructor — Generative AI for Cyber Security",
        "• CEO of DistributedApps.ai: https://distributedapps.ai/",
        "• Substack: kenhuangus.substack.com  ·  LinkedIn: linkedin.com/in/kenhuang8",
    ],
}
SPEAKER_ZH = [
    "关于演讲者：Ken Huang，CISSP",
    "• AI 图书作者与演讲者（《Harness Engineering》《MAESTRO》）",
    "• 旧金山大学（USF）客座教授",
    "• OWASP AIVSS 项目负责人",
    "• CSA 院士，并担任两个 CSA AI 安全工作组联合主席",
    "• OWASP Top 10 for LLM Applications 核心成员",
    "• AIUC-1 联盟成员",
    "• Schmidt Sciences 基金评审成员",
    "• EC-Council 讲师 — 面向网络安全的生成式 AI",
    "• DistributedApps.ai 首席执行官：https://distributedapps.ai/",
    "• Substack：kenhuangus.substack.com  ·  LinkedIn：linkedin.com/in/kenhuang8",
]

THANKS_EN = {
    "number": 99,  # renumbered later
    "slide_type": "thanks",
    "raw_lines": [
        "Thank you",
        "Graph Engineering for Agentic AI Systems · Harness Engineering",
        "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM",
    ],
}
THANKS_ZH = [
    "谢谢",
    "《Graph Engineering for Agentic AI Systems》·《Harness Engineering》",
    "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM",
]

CSS_BLOCK = r"""
    /* Speaker + books gallery (from graph-engineer) */
    .instructor-slide-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.02fr) minmax(0, 1.25fr);
      gap: 1.25rem;
      height: 100%;
      align-items: start;
    }
    @media (max-width: 1040px) {
      .instructor-slide-grid { grid-template-columns: 1fr; height: auto; }
    }
    .instructor-info-col {
      display: flex; flex-direction: column; gap: 0.60rem; min-width: 0;
    }
    .instructor-info-col .main-bullets,
    .instructor-info-col .main-bullets.dense-columns,
    .instructor-info-col .bullet-list {
      columns: 1 !important; column-gap: 0 !important;
      display: flex; flex-direction: column; gap: 0.45rem; font-size: 0.98rem;
    }
    .instructor-info-col .primary-bullet { line-height: 1.50; margin-bottom: 0.25rem; }
    .author-books-card {
      background: var(--surface); border: 1.5px solid var(--rule); border-radius: 10px;
      overflow: hidden; display: flex; flex-direction: column;
      box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }
    .author-books-header {
      background: var(--accent-sf); color: var(--ink); font-family: var(--font-display);
      font-weight: 750; font-size: 0.88rem; padding: 0.45rem 0.80rem;
      border-bottom: 1.5px solid var(--rule); display: flex; justify-content: space-between;
      align-items: center; gap: 0.50rem; white-space: nowrap;
    }
    .author-books-header a {
      font-family: var(--font-body); font-size: 0.76rem; font-weight: 750;
      color: var(--accent-dk); text-decoration: underline; white-space: nowrap; flex-shrink: 0;
    }
    .books-gallery-grid {
      display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.40rem;
      padding: 0.50rem; background: #FAF8F2;
    }
    .book-item-card {
      display: flex; flex-direction: column; align-items: center; background: var(--surface);
      border: 1px solid var(--rule); border-radius: 6px; padding: 0.25rem 0.20rem;
      text-decoration: none; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      transition: transform 0.16s, border-color 0.16s, box-shadow 0.16s;
    }
    .book-item-card:hover {
      transform: translateY(-2px); border-color: var(--accent);
      box-shadow: 0 4px 12px rgba(217, 119, 87, 0.18);
    }
    .book-cover-img {
      width: 100%; height: clamp(80px, 11.5vh, 115px); object-fit: contain;
      border-radius: 4px; border: 0.5px solid var(--rule);
    }
    .book-item-title {
      font-size: 0.58rem; font-weight: 700; color: var(--ink); text-align: center;
      line-height: 1.15; margin-top: 0.20rem; white-space: nowrap; overflow: hidden;
      text-overflow: ellipsis; width: 100%; display: block;
    }
    .book-publisher-tag {
      font-size: 0.52rem; font-weight: 800; letter-spacing: 0.04em; color: var(--accent-dk);
      margin-top: 0.10rem;
    }

    /* Thanks / two recent books */
    .thanks-wrap {
      width: 100%; height: 100%; display: flex; flex-direction: column;
      gap: 0.55rem; min-height: 0;
    }
    .thanks-header { text-align: center; flex: 0 0 auto; }
    .thanks-kicker {
      font-family: var(--font-code); font-size: 0.72em; font-weight: 750;
      letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent-dk);
    }
    .thanks-lede {
      font-family: var(--font-display); font-size: 1.15em; font-weight: 750;
      color: var(--ink); margin-top: 0.20rem; line-height: 1.25;
    }
    .thanks-books {
      display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;
      flex: 1 1 auto; min-height: 0; align-items: stretch; overflow: hidden;
    }
    .thanks-book-card {
      background: var(--surface); border: 1.5px solid var(--rule); border-radius: 12px;
      padding: 0.55rem 0.65rem 0.65rem; box-shadow: 0 6px 18px rgba(0,0,0,0.05);
      display: flex; flex-direction: column; align-items: center; text-align: center;
      gap: 0.30rem; text-decoration: none; color: inherit;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      min-height: 0; overflow: hidden;
    }
    .thanks-book-card:hover {
      border-color: var(--accent); box-shadow: 0 8px 22px rgba(0,0,0,0.08);
    }
    .thanks-book-cover {
      flex: 1 1 auto; min-height: 0; width: 100%;
      display: flex; align-items: center; justify-content: center; overflow: hidden;
    }
    .thanks-book-cover img {
      width: auto; height: auto; max-width: 100%; max-height: 100%;
      object-fit: contain; border-radius: 5px; box-shadow: 0 3px 10px rgba(0,0,0,0.10);
    }
    .thanks-book-tag {
      font-family: var(--font-code); font-size: 0.62em; font-weight: 750;
      letter-spacing: 0.05em; text-transform: uppercase; color: var(--accent-dk);
      background: var(--accent-sf); border: 1px solid var(--rule); border-radius: 999px;
      padding: 0.12rem 0.45rem; flex: 0 0 auto;
    }
    .thanks-book-title {
      font-family: var(--font-display); font-size: 0.88em; font-weight: 750;
      line-height: 1.15; color: var(--ink); max-width: 17rem; flex: 0 0 auto;
    }
    .thanks-book-asin {
      font-family: var(--font-code); font-size: 0.62em; font-weight: 650;
      color: var(--ink-muted); line-height: 1.2; flex: 0 0 auto;
    }
    .thanks-book-asin span { color: var(--accent-dk); font-weight: 750; }
    .thanks-footer { text-align: center; flex: 0 0 auto; }
    .thanks-link a {
      color: var(--accent-dk); font-weight: 700; font-family: var(--font-code); font-size: 0.82em;
    }
    .slide-body:has(.thanks-wrap) { overflow: hidden; }
"""

RENDER_FUNCS = r"""
    function renderSpeaker(slide) {
      const rest = (slide.raw_lines || []).slice(1);
      const booksLabel = uiText(
        '📚 AI Books & Academic Publications (Springer · Cambridge · Wiley · Packt)',
        '📚 AI 图书与学术出版（Springer · Cambridge · Wiley · Packt）'
      );
      const amazonLabel = uiText('Amazon Author Page ➔', 'Amazon 作者页 ➔');
      return `
        <div id="slide-content-wrap" class="instructor-slide-grid">
          <div class="instructor-info-col">
            ${formatBullets(rest)}
          </div>
          <div class="author-books-card">
            <div class="author-books-header">
              <span>${booksLabel}</span>
              <a href="https://www.amazon.com/stores/author/B0D3J7L7GN" target="_blank" rel="noopener noreferrer">${amazonLabel}</a>
            </div>
            <div class="books-gallery-grid">
              <a href="https://www.amazon.com/dp/3031900251" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Agentic AI: Theories and Practices (Springer)">
                <img src="assets/images/books/springer_agentic_ai.jpg" alt="Agentic AI (Springer)" class="book-cover-img" />
                <div class="book-item-title">Agentic AI</div>
                <div class="book-publisher-tag">SPRINGER</div>
              </a>
              <a href="https://www.amazon.com/dp/3031448839" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Beyond AI (Springer)">
                <img src="assets/images/books/springer_beyond_ai.jpg" alt="Beyond AI (Springer)" class="book-cover-img" />
                <div class="book-item-title">Beyond AI</div>
                <div class="book-publisher-tag">SPRINGER</div>
              </a>
              <a href="https://www.amazon.com/dp/3031542517" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Generative AI Security (Springer)">
                <img src="assets/images/books/springer_generative_ai_security.jpg" alt="GenAI Security (Springer)" class="book-cover-img" />
                <div class="book-item-title">GenAI Security</div>
                <div class="book-publisher-tag">SPRINGER</div>
              </a>
              <a href="https://www.amazon.com/dp/3031901002" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Securing AI Agents (Springer)">
                <img src="assets/images/books/springer_securing_ai_agents.jpg" alt="Securing AI Agents" class="book-cover-img" />
                <div class="book-item-title">Securing Agents</div>
                <div class="book-publisher-tag">SPRINGER</div>
              </a>
              <a href="https://www.amazon.com/dp/1009384467" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Web3 (Cambridge)">
                <img src="assets/images/books/cambridge_web3.jpg" alt="Web3 (Cambridge UP)" class="book-cover-img" />
                <div class="book-item-title">Web3 &amp; Economy</div>
                <div class="book-publisher-tag">CAMBRIDGE</div>
              </a>
              <a href="https://www.amazon.com/dp/1394186524" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Blockchain and Web3 (Wiley)">
                <img src="assets/images/books/wiley_blockchain_web3.jpg" alt="Blockchain & Web3 (Wiley)" class="book-cover-img" />
                <div class="book-item-title">Blockchain Web3</div>
                <div class="book-publisher-tag">WILEY</div>
              </a>
              <a href="https://www.amazon.com/dp/B0HF3F86YM" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Harness Engineering">
                <img src="assets/images/books/harness_engineering.jpg" alt="Harness Engineering" class="book-cover-img" />
                <div class="book-item-title">Harness Eng.</div>
                <div class="book-publisher-tag">BEST SELLER</div>
              </a>
              <a href="https://www.amazon.com/dp/1807785017" target="_blank" rel="noopener noreferrer" class="book-item-card" title="OpenClaw AI in Production">
                <img src="assets/images/books/openclaw_ai_in_production.jpg" alt="OpenClaw AI in Production" class="book-cover-img" />
                <div class="book-item-title">OpenClaw AI</div>
                <div class="book-publisher-tag">PACKT</div>
              </a>
              <a href="https://www.amazon.com/dp/B0H8JW9XFN" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Engineering Agentic AI with Claude">
                <img src="assets/images/books/engineering_agentic_ai_claude.jpg" alt="Engineering Agentic AI with Claude" class="book-cover-img" />
                <div class="book-item-title">Agentic Claude</div>
                <div class="book-publisher-tag">CLAUDE AI</div>
              </a>
              <a href="https://www.amazon.com/dp/1836207034" target="_blank" rel="noopener noreferrer" class="book-item-card" title="LLM Design Patterns">
                <img src="assets/images/books/llm_design_patterns.jpg" alt="LLM Design Patterns" class="book-cover-img" />
                <div class="book-item-title">LLM Patterns</div>
                <div class="book-publisher-tag">PACKT</div>
              </a>
              <a href="https://www.amazon.com/dp/B0H13XWS8W" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Agentic AI Harness Pattern">
                <img src="assets/images/books/agentic_ai_harness_pattern.jpg" alt="Agentic AI Harness Pattern" class="book-cover-img" />
                <div class="book-item-title">AI Harness</div>
                <div class="book-publisher-tag">PATTERNS</div>
              </a>
              <a href="https://www.amazon.com/dp/B0HHZVDQQY" target="_blank" rel="noopener noreferrer" class="book-item-card" title="Graph Engineering for Agentic AI Systems">
                <img src="assets/images/graph_engineering_book.jpg" alt="Graph Engineering" class="book-cover-img" />
                <div class="book-item-title">Graph Eng.</div>
                <div class="book-publisher-tag">PACKT</div>
              </a>
            </div>
          </div>
        </div>`;
    }

    function renderThanks(slide) {
      const kicker = uiText('Further reading · Recent books', '延伸阅读 · 新近著作');
      const lede = uiText('Two companion Kindle books by Ken Huang', 'Ken Huang 两本配套 Kindle 著作');
      return `
        <div id="slide-content-wrap" class="thanks-wrap idea-slide">
          <div class="thanks-header">
            <div class="thanks-kicker">${kicker}</div>
            <div class="thanks-lede">${lede}</div>
          </div>
          <div class="thanks-books">
            <a class="thanks-book-card" href="https://www.amazon.com/dp/B0HHZVDQQY" target="_blank" rel="noopener noreferrer" title="Graph Engineering for Agentic AI Systems on Amazon">
              <div class="thanks-book-cover">
                <img src="assets/images/graph_engineering_book.jpg" alt="Graph Engineering for Agentic AI Systems book cover" />
              </div>
              <div class="thanks-book-tag">Kindle · B0HHZVDQQY</div>
              <div class="thanks-book-title">Graph Engineering for Agentic AI Systems</div>
              <div class="thanks-book-asin"><span>Amazon ↗</span></div>
            </a>
            <a class="thanks-book-card" href="https://www.amazon.com/dp/B0HF3F86YM" target="_blank" rel="noopener noreferrer" title="Harness Engineering on Amazon">
              <div class="thanks-book-cover">
                <img src="assets/images/harness_engineering_book.jpg" alt="Harness Engineering book cover" />
              </div>
              <div class="thanks-book-tag">Kindle · B0HF3F86YM</div>
              <div class="thanks-book-title">Harness Engineering</div>
              <div class="thanks-book-asin"><span>Amazon ↗</span></div>
            </a>
          </div>
          <div class="thanks-footer thanks-link">
            <a href="https://distributedapps.ai/" target="_blank" rel="noopener noreferrer">distributedapps.ai ↗</a>
            &nbsp;·&nbsp;
            <a href="https://kenhuangus.substack.com/" target="_blank" rel="noopener noreferrer">kenhuangus.substack.com ↗</a>
          </div>
        </div>`;
    }

"""


def copy_assets() -> None:
    books_dst = ROOT / "assets" / "images" / "books"
    books_dst.mkdir(parents=True, exist_ok=True)
    src_books = SRC / "assets" / "images" / "books"
    for name in src_books.iterdir():
        if name.suffix.lower() in {".jpg", ".png", ".jpeg", ".webp"}:
            shutil.copy2(name, books_dst / name.name)
    for name in ["graph_engineering_book.jpg", "harness_engineering_book.jpg", "harness_engineering_book.png"]:
        src = SRC / "assets" / "images" / name
        if src.exists():
            shutil.copy2(src, ROOT / "assets" / "images" / name)
    print("Copied book assets")


def patch_html_shell() -> None:
    path = ROOT / "slides.html"
    t = path.read_text(encoding="utf-8")

    if ".thanks-wrap" not in t:
        t = t.replace("</style>", CSS_BLOCK + "\n  </style>", 1)

    if "function renderSpeaker(slide)" not in t:
        # Insert before function renderSlide
        marker = "    function renderSlide(idx) {"
        if marker not in t:
            raise SystemExit("renderSlide not found")
        t = t.replace(marker, RENDER_FUNCS + "\n" + marker, 1)

    # Wire speaker/thanks into renderSlide body selection
    old = """      if (isSkill) {
        bodyHtml += renderSkillSlide(slide);
      } else if (isCode && slide.highlighted_code) {"""
    new = """      if (slide.slide_type === 'speaker') {
        bodyHtml += renderSpeaker(slide);
      } else if (slide.slide_type === 'thanks') {
        bodyHtml += renderThanks(slide);
      } else if (isSkill) {
        bodyHtml += renderSkillSlide(slide);
      } else if (isCode && slide.highlighted_code) {"""
    if "slide.slide_type === 'speaker'" not in t:
        if old not in t:
            raise SystemExit("renderSlide branch marker not found")
        t = t.replace(old, new, 1)

    path.write_text(t, encoding="utf-8")
    print("Patched slides.html shell")


def patch_build_slides() -> None:
    text = BUILD.read_text(encoding="utf-8")
    # Exec to get current data structures is hard; rewrite SLIDES_EN/ZH via regex insertion.

    # Load current EN list by eval of the assignment
    ns: dict = {}
    # Extract only the data portion safely
    m_en = re.search(r"SLIDES_EN = (\[.*?\])\n\nSLIDES_ZH = ", text, re.S)
    m_zh = re.search(r"SLIDES_ZH = (\{.*?\})\n\nPHRASES = ", text, re.S)
    if not m_en or not m_zh:
        raise SystemExit("Could not parse SLIDES_EN/SLIDES_ZH from build_slides.py")
    slides_en = json.loads(
        m_en.group(1)
        .replace("True", "true")
        .replace("False", "false")
        .replace("None", "null")
    ) if False else None

    # Use ast.literal_eval on Python source
    import ast

    slides_en = ast.literal_eval(m_en.group(1))
    slides_zh = ast.literal_eval(m_zh.group(1))

    # Remove prior speaker/thanks if re-running
    slides_en = [s for s in slides_en if s.get("slide_type") not in {"speaker", "thanks"}]
    # Also drop old "About the Speaker" title if present
    slides_en = [s for s in slides_en if not str(s.get("raw_lines", [""])[0]).startswith("About the Speaker")]
    slides_en = [s for s in slides_en if not str(s.get("raw_lines", [""])[0]).startswith("Thank you")]

    # Insert speaker after title (index 0)
    slides_en.insert(1, dict(SPEAKER_EN))
    # Append thanks as last (keep closing content before thanks? User said last slides = books)
    # Keep closing slide, then thanks as final
    slides_en.append(dict(THANKS_EN))

    # Renumber sequentially
    for i, s in enumerate(slides_en, start=1):
        s["number"] = i

    # Rebuild ZH dict
    # Shift: rebuild from EN numbers using old zh where titles match, else new packs
    old_zh = {str(k): v for k, v in slides_zh.items()}
    # Map old content by first line EN-> we rebuild carefully
    # Keep zh for non-speaker/thanks by matching EN first lines via previous build order.
    # Simpler: regenerate zh keys from current ZH file content in slides-zh.js after rebuild,
    # here construct from old_zh by title heuristics + new packs.

    # Load previous EN titles from before mutation via slides.html current data
    prev_html = (ROOT / "slides.html").read_text(encoding="utf-8")
    prev_en = json.loads(re.search(r"const slidesData = (\[.*?\]);", prev_html, re.S).group(1))
    prev_zh_js = (ROOT / "slides-zh.js").read_text(encoding="utf-8")
    prev_zh = json.loads(prev_zh_js[prev_zh_js.find("{") :].rstrip().rstrip(";"))["lines"]
    title_to_zh = {}
    for s in prev_en:
        n = str(s["number"])
        if n in prev_zh:
            title_to_zh[s["raw_lines"][0]] = prev_zh[n]

    new_zh = {}
    for s in slides_en:
        n = str(s["number"])
        title = s["raw_lines"][0]
        if s.get("slide_type") == "speaker":
            new_zh[n] = SPEAKER_ZH
        elif s.get("slide_type") == "thanks":
            new_zh[n] = THANKS_ZH
        elif title in title_to_zh and len(title_to_zh[title]) == len(s["raw_lines"]):
            new_zh[n] = title_to_zh[title]
        else:
            # fallback: keep EN (should not happen)
            print("WARN missing ZH for", n, title)
            new_zh[n] = s["raw_lines"][:]

    # Write back into build_slides.py
    en_py = json.dumps(slides_en, ensure_ascii=False, indent=4)
    # json uses true/false/null - convert to Python
    en_py = (
        en_py.replace(": true", ": True")
        .replace(": false", ": False")
        .replace(": null", ": None")
    )
    zh_py = json.dumps(new_zh, ensure_ascii=False, indent=4)
    zh_py = (
        zh_py.replace(": true", ": True")
        .replace(": false", ": False")
        .replace(": null", ": None")
    )

    text2 = text[: m_en.start(1)] + en_py + text[m_en.end(1) : m_zh.start(1)] + zh_py + text[m_zh.end(1) :]
    BUILD.write_text(text2, encoding="utf-8")
    print(f"build_slides.py now has {len(slides_en)} slides")


def main() -> None:
    copy_assets()
    patch_html_shell()
    patch_build_slides()
    r = subprocess.run([sys.executable, str(ROOT / "build_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)
    r = subprocess.run([sys.executable, str(ROOT / "cleanup_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)

    # Re-ensure speaker/thanks wiring survived rebuild (build only swaps slidesData)
    patch_html_shell()

    # Sync docs + assets
    docs = ROOT / "docs"
    shutil.copy2(ROOT / "slides.html", docs / "slides.html")
    shutil.copy2(ROOT / "slides-zh.js", docs / "slides-zh.js")
    img_root = ROOT / "assets" / "images"
    docs_img = docs / "assets" / "images"
    docs_img.mkdir(parents=True, exist_ok=True)
    for p in img_root.rglob("*"):
        if p.is_file():
            dest = docs_img / p.relative_to(img_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)

    # Verify
    t = (ROOT / "slides.html").read_text(encoding="utf-8")
    data = json.loads(re.search(r"const slidesData = (\[.*?\]);", t, re.S).group(1))
    print("total", len(data))
    print("slide2", data[1].get("slide_type"), data[1]["raw_lines"][0])
    print("last", data[-1].get("slide_type"), data[-1]["raw_lines"][0])
    assert data[1].get("slide_type") == "speaker"
    assert data[-1].get("slide_type") == "thanks"
    assert "function renderSpeaker" in t and "function renderThanks" in t
    zh = json.loads((ROOT / "slides-zh.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    for s in data:
        n = str(s["number"])
        assert n in zh["lines"], n
        assert len(zh["lines"][n]) == len(s["raw_lines"]), (n, len(zh["lines"][n]), len(s["raw_lines"]))
    print("PASS")


if __name__ == "__main__":
    main()
