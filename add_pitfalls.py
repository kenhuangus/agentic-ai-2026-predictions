#!/usr/bin/env python3
"""Add pitfall + do-not-invest lines to each P1–P10 investor slide (EN/ZH)."""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build_slides.py"
ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "DistributedApps.AI",
    "GIT_AUTHOR_EMAIL": "kenhuangus@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "DistributedApps.AI",
    "GIT_COMMITTER_EMAIL": "kenhuangus@users.noreply.github.com",
}

# Extra lines appended after Thesis 3 for each prediction number
EXTRA_EN = {
    1: [
        "• Pitfall — Treating Level-1 RSI demos as an intelligence explosion; ignition is unproven and eval gaming is common",
        "• Do not invest — Open-web “self-improving AGI” apps with no hidden evals, no kill-switch, and no budget ceiling",
    ],
    2: [
        "• Pitfall — Paying for IQ/MMLU wrapper startups while buyers already score agency (tools, persistence, correction)",
        "• Do not invest — Chatbots marketed as agents without durable goals, tool contracts, or Idle-Gap ambient behavior",
    ],
    3: [
        "• Pitfall — Funding another static PDF checklist; buyers need CI enforcement and evidence packs, not slideware",
        "• Do not invest — “MAESTRO-compliant” badges with no layer tests, no ATLAS mapping, and no scanner output",
    ],
    4: [
        "• Pitfall — Building US-only GRC that cannot export EU AI Act / CN filing evidence — multinationals will churn",
        "• Do not invest — Policy docs generators with no runtime control plane and no priced decision on tool calls",
    ],
    5: [
        "• Pitfall — Generic SAST rebranded as “AI security” without covering AI-specific failure modes (BAC/IDOR/secrets)",
        "• Do not invest — Vibe builders that optimize time-to-demo while shipping debug CORS, hardcoded keys, and no auth on APIs",
    ],
    6: [
        "• Pitfall — Betting on full open-DOM computer-use reliability before protocol resync and injection defense mature",
        "• Do not invest — Consumer browser agents with payments/email send and no human approval or session isolation",
    ],
    7: [
        "• Pitfall — Skipping data readiness; 78% of enterprises hit content/data blockers that kill agent ROI narratives",
        "• Do not invest — Open-web B2C agent plays that burn trust capital before internal ops has a measurable P&L win",
    ],
    8: [
        "• Pitfall — Assuming model vendors absorb framework/MCP CVE risk; blast radius sits in the app’s dependency tree",
        "• Do not invest — Unauthenticated MCP servers, god-token tool hosts, and agent stacks without SBOM/pinning discipline",
    ],
    9: [
        "• Pitfall — Consulting-only MAESTRO decks that never encode L1–L10 into tools — frameworks without software stall",
        "• Do not invest — “Trust plane” shells that rename IAM/observability without agency-specific identity or interrupt paths",
    ],
    10: [
        "• Pitfall — Shipping scoring UX before v1 freeze; methodology churn will force rework and buyer distrust",
        "• Do not invest — Proprietary “AI risk scores” that refuse AIVSS/AIUC-1/MAESTRO crosswalks once v1 is the standard",
    ],
}

EXTRA_ZH = {
    1: [
        "• 陷阱 — 把一级 RSI 演示当成智能爆炸；点火未证实，且评估作弊常见",
        "• 不宜投 — 无隐藏评估、无急停、无预算上限的开放网络「自我改进 AGI」应用",
    ],
    2: [
        "• 陷阱 — 为 IQ/MMLU 包装创业公司买单，而买方已在用自主性（工具、持续、纠错）打分",
        "• 不宜投 — 被宣传为智能体、却无耐久目标、无工具契约、无 Idle-Gap Ambient 行为的聊天机器人",
    ],
    3: [
        "• 陷阱 — 再投一份静态 PDF 清单；买方需要的是 CI 强制执行与证据包，而非幻灯片",
        "• 不宜投 — 无分层测试、无 ATLAS 映射、无扫描输出的「MAESTRO 合规」徽章",
    ],
    4: [
        "• 陷阱 — 只做美国 GRC、无法导出欧盟 AI 法案/中国备案证据 — 跨国客户会流失",
        "• 不宜投 — 只会生成政策文档、没有运行时控制平面、不对工具调用做计价决策的产品",
    ],
    5: [
        "• 陷阱 — 把通用 SAST 改名「AI 安全」，却不覆盖 AI 特有失败模式（访问控制/IDOR/密钥）",
        "• 不宜投 — 优化演示速度、却交付调试 CORS、硬编码密钥、API 无认证的氛围构建器",
    ],
    6: [
        "• 陷阱 — 在协议重同步与注入防御成熟前，押注开放 DOM 计算机使用的全面可靠",
        "• 不宜投 — 可支付/发信且无人审批、无会话隔离的消费级浏览器智能体",
    ],
    7: [
        "• 陷阱 — 跳过数据就绪；78% 企业卡在内容/数据阻断，会杀死智能体 ROI 叙事",
        "• 不宜投 — 在内部运营尚无可度量损益胜利前，就燃烧信任资本的开放网络 B2C 智能体",
    ],
    8: [
        "• 陷阱 — 认为模型厂商会吞下框架/MCP CVE 风险；爆炸半径在应用的依赖树里",
        "• 不宜投 — 无认证的 MCP 服务器、上帝令牌工具主机、以及无 SBOM/钉死纪律的智能体栈",
    ],
    9: [
        "• 陷阱 — 只有咨询式 MAESTRO 幻灯、从不把 L1–L10 编进工具 — 无软件的框架会停滞",
        "• 不宜投 — 只是改名 IAM/可观测性、却无智能体身份与中断路径的「信任平面」空壳",
    ],
    10: [
        "• 陷阱 — 在 v1 冻结前就上线评分 UX；方法变更会迫使返工并损害买方信任",
        "• 不宜投 — 在 v1 成为标准后仍拒绝 AIVSS/AIUC-1/MAESTRO 对照的专有「AI 风险分」",
    ],
}


def run(args, input_text=None, check=True):
    r = subprocess.run(args, cwd=ROOT, input=input_text, text=True, capture_output=True, env=ENV)
    if check and r.returncode:
        sys.stderr.write(r.stdout or "")
        sys.stderr.write(r.stderr or "")
        raise SystemExit(r.returncode)
    return r


def main() -> None:
    text = BUILD.read_text(encoding="utf-8")
    m_en = re.search(r"SLIDES_EN = (\[.*?\])\n\nSLIDES_ZH = ", text, re.S)
    m_zh = re.search(r"SLIDES_ZH = (\{.*?\})\n\nPHRASES = ", text, re.S)
    en = ast.literal_eval(m_en.group(1))
    zh = ast.literal_eval(m_zh.group(1))

    for s in en:
        title = s["raw_lines"][0]
        m = re.match(r"P(\d+)\s*—", title)
        if not m:
            continue
        pnum = int(m.group(1))
        n = str(s["number"])

        def strip_extra(lines):
            out = []
            for L in lines:
                core = L.lstrip().lstrip("•").lstrip()
                if core.startswith(("Pitfall", "Do not invest", "陷阱", "不宜投")):
                    continue
                out.append(L)
            return out

        en_base = strip_extra(s["raw_lines"])
        zh_base = strip_extra(zh[n])

        def split_head_theses(lines, thesis_re):
            theses = [L for L in lines if thesis_re.search(L)]
            head = [L for L in lines if L not in theses]
            return head[:2], theses[:3]

        en_head, en_theses = split_head_theses(en_base, re.compile(r"Thesis\s*[123]"))
        zh_head, zh_theses = split_head_theses(zh_base, re.compile(r"论点\s*[123]"))
        if len(en_theses) < 3 or len(zh_theses) < 3:
            raise SystemExit(f"P{pnum} thesis count en={len(en_theses)} zh={len(zh_theses)}")

        # If ZH title/evidence missing a line, pad from prior structure
        if len(zh_head) < 2:
            # recover: first line title, second evidence (non-thesis)
            zh_all = strip_extra(zh[n])
            zh_title = zh_all[0]
            zh_evidence = next((L for L in zh_all[1:] if not re.search(r"论点\s*[123]", L)), zh_all[1])
            zh_head = [zh_title, zh_evidence]

        s["raw_lines"] = en_head + en_theses + EXTRA_EN[pnum]
        zh[n] = zh_head + zh_theses + EXTRA_ZH[pnum]
        if len(s["raw_lines"]) != len(zh[n]):
            raise SystemExit(
                f"P{pnum} len mismatch en={len(s['raw_lines'])} zh={len(zh[n])} "
                f"en_head={len(en_head)} en_theses={len(en_theses)} "
                f"zh_head={len(zh_head)} zh_theses={len(zh_theses)}"
            )

    def to_py(obj):
        s = json.dumps(obj, ensure_ascii=False, indent=4)
        return s.replace(": true", ": True").replace(": false", ": False").replace(": null", ": None")

    text2 = text[: m_en.start(1)] + to_py(en) + text[m_en.end(1) : m_zh.start(1)] + to_py(zh) + text[m_zh.end(1) :]
    BUILD.write_text(text2, encoding="utf-8")

    # Light update to About / Closing to mention pitfalls
    text2 = BUILD.read_text(encoding="utf-8")
    text2 = text2.replace(
        "• Method: convert each prediction into ≤3 investable theses grounded in US/China/EU evidence through 2026-09-27",
        "• Method: ≤3 investable theses per trend, plus explicit pitfalls and do-not-invest anti-theses (US/China/EU evidence through 2026-09-27)",
    )
    text2 = text2.replace(
        "• 方法：将每条预测转化为 ≤3 条可投资论点，并锚定截至 2026-09-27 的美/中/欧证据",
        "• 方法：每个趋势 ≤3 条可投资论点，并列出陷阱与不宜投的反论点（美/中/欧证据截至 2026-09-27）",
    )
    text2 = text2.replace(
        "• Each of the 10 CSA trends maps to ≤3 theses with a payer and a product surface",
        "• Each of the 10 CSA trends maps to ≤3 theses plus pitfall / do-not-invest lines",
    )
    text2 = text2.replace(
        "• CSA 的 10 个趋势各自映射到 ≤3 条带付费方与产品表面的投资论点",
        "• CSA 的 10 个趋势各自映射到 ≤3 条投资论点，并附陷阱 / 不宜投",
    )
    BUILD.write_text(text2, encoding="utf-8")

    r = subprocess.run([sys.executable, str(ROOT / "build_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)
    r = subprocess.run([sys.executable, str(ROOT / "cleanup_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)

    shutil.copy2(ROOT / "slides.html", ROOT / "docs" / "slides.html")
    shutil.copy2(ROOT / "slides-zh.js", ROOT / "docs" / "slides-zh.js")

    # verify
    html = (ROOT / "slides.html").read_text(encoding="utf-8")
    data = json.loads(re.search(r"const slidesData = (\[.*?\]);", html, re.S).group(1))
    zhjs = json.loads((ROOT / "slides-zh.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    for s in data:
        n = str(s["number"])
        assert len(zhjs["lines"][n]) == len(s["raw_lines"]), n
        if re.match(r"P\d+\s*—", s["raw_lines"][0]):
            assert any("Pitfall" in L for L in s["raw_lines"]), s["raw_lines"][0]
            assert any("Do not invest" in L for L in s["raw_lines"]), s["raw_lines"][0]
            print(s["number"], "OK", len(s["raw_lines"]), "lines")

    # commit push
    run(["git", "add", "-A"])
    if run(["git", "status", "--porcelain"]).stdout.strip():
        tree = run(["git", "write-tree"]).stdout.strip()
        head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
        msg = (
            "Add pitfalls and do-not-invest anti-theses to each prediction slide.\n"
            "\n"
            "Each P1–P10 now lists ≤3 theses plus explicit pitfall and avoid lines (EN/ZH).\n"
        )
        new = run(["git", "commit-tree", tree, "-p", head], input_text=msg).stdout.strip()
        run(["git", "reset", "--soft", new])
        assert "Co-authored-by" not in run(["git", "log", "-1", "--format=%B"]).stdout
        run(["git", "push", "origin", "HEAD:main"])
        print("COMMIT", new)
    print("DONE")


if __name__ == "__main__":
    main()
