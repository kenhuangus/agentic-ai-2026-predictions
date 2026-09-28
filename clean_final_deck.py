# -*- coding: utf-8 -*-
"""Rewrite slide content: plain language, fewer points, no working notes."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build_slides.py"

SLIDES_EN = [
    {
        "number": 1,
        "raw_lines": [
            "Top 10 Predictions for Agentic AI in 2026",
            "Technology forecasts (Cloud Security Alliance, January 16, 2026)",
            "Evidence through September 27, 2026 · investment discussion · Not Investment Advice",
            "Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "Adjunct Professor, University of San Francisco: https://www.usfca.edu/faculty/ken-huang",
            "Regions: United States · China · European Union",
            "CSA article: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        ],
    },
    {
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
    },
    {
        "number": 3,
        "raw_lines": [
            "Original CSA Publication — January 16, 2026",
            "• Article: My Top 10 Predictions for Agentic AI in 2026",
            "• Technology and industry forecasts — not investment advice",
            "• Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "• Publisher: Cloud Security Alliance",
            "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "IMG:assets/images/csa-top-10-predictions-2026.png",
        ],
    },
    {
        "number": 4,
        "raw_lines": [
            "About This Deck",
            "• January 2026: ten technology predictions for Agentic AI (CSA)",
            "• This deck checks each prediction against public evidence in the US, China, and the EU",
            "• Short investment notes are for discussion only — Not Investment Advice",
            "• Ask: who pays, what product, and why now",
        ],
    },
    {
        "number": 5,
        "raw_lines": [
            "Where Capital Can Focus — Not Investment Advice",
            "| # | Trend | Focus / avoid |",
            "|---|---|---|",
            "| 1 | Self-improving agents | Private tests + human control / avoid open self-rewriting apps |",
            "| 2 | Agency over IQ | Long task agents / avoid chatbots labeled as agents |",
            "| 3 | MAESTRO benchmarks | Merge blockers in CI / avoid paper badges |",
            "| 4 | Agent risk | Live allow or deny on tools / avoid policy PDFs only |",
            "| 5 | Vibe coding security | Secure AI coding tools / avoid demo builders with open keys |",
            "| 6 | Browser agents | Approved actions + human approval / avoid pay-and-email bots |",
            "| 7 | Internal first | Internal platforms with KPIs / avoid public consumer first |",
            "| 8 | Agent CVEs | Secure MCP and patching / avoid unauthenticated tool servers |",
            "| 9 | MAESTRO v2 | Tools for today’s 7 layers / avoid fake v2 claims |",
            "| 10 | AIVSS | Scoring after v1 is final / avoid unmapped private scores |",
        ],
    },
    {
        "number": 6,
        "raw_lines": [
            "P1 — Self-Improving Agents",
            "Evidence: Early systems beat a fixed R&D budget baseline; production still needs private tests the agent cannot see, plus human control.",
            "• Opportunity — Test platforms and controls so self-improving agents cannot game the score; buyers are frontier labs and AI R&D teams",
            "• Avoid — Public apps sold as self-improving AGI that rewrite their own code with no private tests and no spend limit",
        ],
    },
    {
        "number": 7,
        "raw_lines": [
            "P2 — Agency Matters More Than IQ Scores",
            "Evidence: New benchmarks score multi-hour tool work, not quiz scores alone.",
            "• Opportunity — Agents that finish long tool workflows; sell planning and persistence scores into model selection and RFPs",
            "• Avoid — Chat products labeled as agents with no tools and no multi-hour tasks",
        ],
    },
    {
        "number": 8,
        "raw_lines": [
            "P3 — MAESTRO Security Benchmarks",
            "Evidence: MAESTRO is in playbooks and CI; shared public leaderboards are still thin.",
            "• Opportunity — Scanners that map a change to MAESTRO layers and block high-risk agent merges",
            "• Avoid — “MAESTRO compliant” badges with no layer tests and no scanner output",
        ],
    },
    {
        "number": 9,
        "raw_lines": [
            "P4 — Agentic Risk Management",
            "Evidence: US, China, and EU rules now treat agent risk as a compliance problem.",
            "• Opportunity — Runtime allow or deny on tool calls, plus one control pack mapped to NIST, the EU AI Act, and China filing",
            "• Avoid — Policy documents with no live control when an agent calls a tool",
        ],
    },
    {
        "number": 10,
        "raw_lines": [
            "P5 — Vibe Coding Security Hangover",
            "Evidence: About 91% of audited AI-generated apps had security holes (arXiv:2606.23130).",
            "• Opportunity — Security checks built into AI coding tools before deploy (login, secrets, access control)",
            "• Avoid — Builders that ship demos with hardcoded keys and APIs with no authentication",
        ],
    },
    {
        "number": 11,
        "raw_lines": [
            "P6 — Browser Agents Still Struggle",
            "Evidence: Browser-agent protocols still lose sync; desktop control remains easy to trick with prompt injection.",
            "• Opportunity — Agents limited to an approved action list, with human approval for payment and send-email",
            "• Avoid — Consumer bots that can pay or send email with no human check",
        ],
    },
    {
        "number": 12,
        "raw_lines": [
            "P7 — Enterprise: Internal First",
            "Evidence: Most enterprise programs start inside the company; many stall on content and data cleanup.",
            "• Opportunity — Internal agent platforms with ERP and IT connectors, and a KPI finance can audit",
            "• Avoid — Public consumer agents before an internal workflow has a measurable KPI",
        ],
    },
    {
        "number": 13,
        "raw_lines": [
            "P8 — More Agentic Ecosystem CVEs",
            "Evidence: LangChain, MCP, and coding-agent bugs are already scored like normal software CVEs.",
            "• Opportunity — Secure MCP gateways and fast patching of agent frameworks and plugins",
            "• Avoid — MCP servers with no login, and one shared token for every tool",
        ],
    },
    {
        "number": 14,
        "raw_lines": [
            "P9 — MAESTRO v2 Practical Adoption",
            "Evidence: MAESTRO v2 is not published. The model in use is still seven layers.",
            "• Opportunity — Implementation software and training for the current seven-layer model",
            "• Avoid — Products that claim “MAESTRO v2” or “ten layers” before CSA publishes v2",
        ],
    },
    {
        "number": 15,
        "raw_lines": [
            "P10 — OWASP AIVSS v1",
            "Evidence: v0.8 is live; v1.0 is in public review through October 1, 2026.",
            "• Opportunity — Scoring engines and release gates once v1 is final",
            "• Avoid — Private “AI risk scores” that refuse to map to AIVSS after v1 is the standard",
        ],
    },
    {
        "number": 16,
        "raw_lines": [
            "Regional Lens — United States · China · European Union",
            "| Theme | United States | China | European Union |",
            "|---|---|---|---|",
            "| Where demand is | Labs, CVE tools, enterprise buyers | Internal ops under local rules and filing | Compliance software and human oversight |",
            "| Self-improve / agency | Test vendors and vertical R&D agents | Regulated autonomy levels | Research ahead of open deploy |",
            "| Security | MAESTRO and AIVSS products, AppSec | Fast patching | Build and AI Act gates |",
            "| Browser agents | Reliable protocols and click defenses | Limited action lists in work apps | Standards plus easy human review |",
            "| Enterprise | Internal platforms first | Data-local agent platforms | Human-in-the-loop before going external |",
        ],
    },
    {
        "number": 17,
        "raw_lines": [
            "Open Questions — Not Investment Advice",
            "• Will AIVSS v1 create paid scoring products, or stay a free checklist?",
            "• Will browser-agent reliability become a product category, or stay a framework feature?",
            "• Do internal agent platforms win budget before public consumer agents earn trust?",
            "• Can security for AI-generated code become a default merge check?",
        ],
    },
    {
        "number": 18,
        "raw_lines": [
            "Primary Sources",
            "• CSA predictions: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• Self-improving agents (AIDE²): weco.ai blog (2026-07-14); arXiv:2609.26457",
            "• AgencyBench (ACL 2026); Autonomous Agency Scale arXiv 2607.17947",
            "• MAESTRO seven-layer analysis: CSA blog 2026-08-13 (Ken Huang)",
            "• CSA AICM v1.1; China agent regulation (enforceable 2026-07-15); EU AI Act",
            "• Vibe coding security study: arXiv:2606.23130",
            "• A2UI: a2ui.org · AIVSS: aivss.owasp.org · Contentstack Agentic Enterprise Report 2026",
        ],
    },
    {
        "number": 19,
        "raw_lines": [
            "Closing",
            "• These ten items began as technology predictions — investment notes are discussion only",
            "• Not Investment Advice — not a recommendation to buy or sell",
            "• Near-term themes: runtime agent controls, security for AI-generated code, MCP and gateway security",
            "• Watch: AIVSS v1, browser-agent reliability, MAESTRO v2 when CSA publishes it",
            "• kenhuangus.substack.com · aivss.owasp.org · DistributedApps.ai · linkedin.com/in/kenhuang8",
        ],
    },
    {
        "number": 20,
        "slide_type": "thanks",
        "raw_lines": [
            "Thank you",
            "Graph Engineering for Agentic AI Systems · Harness Engineering",
            "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM",
        ],
    },
]

SLIDES_ZH = {
    "1": [
        "2026 智能体 AI 十大预测",
        "技术预测（云安全联盟 CSA，2026 年 1 月 16 日）",
        "证据截至 2026 年 9 月 27 日 · 附投资讨论 · 不构成投资建议",
        "作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "旧金山大学（USF）客座教授：https://www.usfca.edu/faculty/ken-huang",
        "区域：美国 · 中国 · 欧盟",
        "CSA 原文：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
    ],
    "2": [
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
    ],
    "3": [
        "CSA 原文发布 — 2026 年 1 月 16 日",
        "• 文章：My Top 10 Predictions for Agentic AI in 2026",
        "• 技术与产业预测 — 不是投资建议",
        "• 作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "• 发布方：云安全联盟（CSA）",
        "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "IMG:assets/images/csa-top-10-predictions-2026.png",
    ],
    "4": [
        "关于本演示",
        "• 2026 年 1 月：CSA 发布十条智能体 AI 技术预测",
        "• 本演示对照美国、中国、欧盟的公开证据检查每条预测",
        "• 投资相关说明仅供讨论 — 不构成投资建议",
        "• 关注：谁付费、卖什么产品、为何是现在",
    ],
    "5": [
        "资本可关注的方向 — 不构成投资建议",
        "| # | 趋势 | 关注 / 回避 |",
        "|---|---|---|",
        "| 1 | 自我改进智能体 | 私有测试 + 人工控制 / 回避公网自行改代码应用 |",
        "| 2 | 自主性重于智商分 | 长任务智能体 / 回避聊天冒充智能体 |",
        "| 3 | MAESTRO 基准 | CI 合并阻断 / 回避纸面徽章 |",
        "| 4 | 智能体风险 | 工具调用实时放行拒绝 / 回避只有制度 PDF |",
        "| 5 | Vibe coding 安全 | 安全的 AI 编程工具 / 回避带明文密钥的演示生成器 |",
        "| 6 | 浏览器智能体 | 批准动作 + 人工审批 / 回避可支付发信机器人 |",
        "| 7 | 内部优先 | 有 KPI 的内部平台 / 回避先做公网消费级 |",
        "| 8 | 智能体 CVE | 安全 MCP 与补丁 / 回避无登录的工具服务器 |",
        "| 9 | MAESTRO v2 | 现行七层工具与培训 / 回避虚假 v2 宣称 |",
        "| 10 | AIVSS | v1 定稿后的评分 / 回避无法对照的私有分 |",
    ],
    "6": [
        "预测 1 — 自我改进智能体",
        "现有证据：早期系统已能在固定研发预算下超过人工基线；投产仍需要智能体看不见的私有测试，以及人工控制。",
        "• 机会 — 私有测试与防刷分控制，卖给前沿实验室和 AI 研发团队",
        "• 回避 — 面向公网、自称自我改进 AGI、无私有测试且无花费上限就自行改代码的应用",
    ],
    "7": [
        "预测 2 — 自主性比智商分数更重要",
        "现有证据：新基准主要打分「数小时工具任务」，而不是测验分数。",
        "• 机会 — 能完成长工具流程的智能体；把规划与持续执行分数卖进选型与招标",
        "• 回避 — 没有工具、也完不成数小时任务、却自称智能体的聊天产品",
    ],
    "8": [
        "预测 3 — MAESTRO 安全基准",
        "现有证据：MAESTRO 已进入操作手册和 CI；公开排行榜仍少。",
        "• 机会 — 按 MAESTRO 分层检查变更、并阻断高风险智能体合并的扫描器",
        "• 回避 — 没有分层测试、没有扫描输出的「MAESTRO 合规」徽章",
    ],
    "9": [
        "预测 4 — 智能体风险管理",
        "现有证据：美、中、欧规则已把智能体风险当作合规问题。",
        "• 机会 — 工具调用的实时允许或拒绝，外加一套映射 NIST、欧盟 AI 法案与中国备案的控制包",
        "• 回避 — 只有制度文档、不能在工具调用时做实时控制的产品",
    ],
    "10": [
        "预测 5 — Vibe Coding 安全后遗症",
        "现有证据：被审计的 AI 生成应用约 91% 有安全漏洞（arXiv:2606.23130）。",
        "• 机会 — 在 AI 编程工具里内置部署前安全检查（登录、密钥、访问控制）",
        "• 回避 — 交付演示时带硬编码密钥、且 API 无认证的生成器",
    ],
    "11": [
        "预测 6 — 浏览器智能体仍难落地",
        "现有证据：浏览器智能体协议仍易失同步；桌面操作仍容易被提示注入欺骗。",
        "• 机会 — 只允许批准动作清单，支付和发邮件需人工审批",
        "• 回避 — 可以支付或发邮件、却没有人工确认的消费级机器人",
    ],
    "12": [
        "预测 7 — 企业：内部优先",
        "现有证据：多数企业项目从公司内部起步；很多卡在内容和数据清理。",
        "• 机会 — 连接 ERP/IT 的内部智能体平台，并有财务可审计的 KPI",
        "• 回避 — 内部流程还没有可衡量 KPI 之前就做公网消费级智能体",
    ],
    "13": [
        "预测 8 — 智能体生态 CVE 增多",
        "现有证据：LangChain、MCP 和编程智能体漏洞已按普通软件 CVE 评级。",
        "• 机会 — 安全的 MCP 网关，以及对智能体框架与插件的快速补丁",
        "• 回避 — 无登录的 MCP 服务器，以及一把令牌调用全部工具",
    ],
    "14": [
        "预测 9 — MAESTRO v2 落地采用",
        "现有证据：MAESTRO v2 尚未发布。现行模型仍是七层。",
        "• 机会 — 面向现行七层模型的落地软件与培训",
        "• 回避 — 在 CSA 发布 v2 之前宣称「MAESTRO v2」或「十层」的产品",
    ],
    "15": [
        "预测 10 — OWASP AIVSS v1",
        "现有证据：v0.8 已上线；v1.0 公开评审至 2026 年 10 月 1 日。",
        "• 机会 — v1 定稿后的评分引擎与发布门禁",
        "• 回避 — v1 成为标准后仍拒绝对照 AIVSS 的私有「AI 风险分」",
    ],
    "16": [
        "区域视角 — 美国 · 中国 · 欧盟",
        "| 主题 | 美国 | 中国 | 欧盟 |",
        "|---|---|---|---|",
        "| 需求所在 | 实验室、CVE 工具、企业买方 | 本地规则与备案下的内部运营 | 合规软件与人工监督 |",
        "| 自我改进 / 自主性 | 测试厂商与垂直研发智能体 | 受监管的自主等级 | 研究先于开放部署 |",
        "| 安全 | MAESTRO 与 AIVSS 产品、应用安全 | 快速补丁 | 构建与 AI 法案门禁 |",
        "| 浏览器智能体 | 可靠协议与点击防护 | 办公应用中的有限动作清单 | 标准 + 便于人工复核 |",
        "| 企业 | 内部平台优先 | 数据本地智能体平台 | 对外前保留人工把关 |",
    ],
    "17": [
        "未决问题 — 不构成投资建议",
        "• AIVSS v1 会催生付费评分产品，还是停留在免费清单？",
        "• 浏览器智能体可靠性会成为独立产品，还是框架附带功能？",
        "• 内部智能体平台能否在公网消费级赢得信任之前拿到预算？",
        "• AI 生成代码的安全检查能否成为默认合并门禁？",
    ],
    "18": [
        "主要来源",
        "• CSA 预测：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• 自我改进智能体（AIDE²）：weco.ai 博客（2026-07-14）；arXiv:2609.26457",
        "• AgencyBench（ACL 2026）；自主性量表 arXiv 2607.17947",
        "• MAESTRO 七层分析：CSA 博客 2026-08-13（Ken Huang）",
        "• CSA AICM v1.1；中国智能体监管（2026-07-15 起施行）；欧盟 AI 法案",
        "• Vibe coding 安全研究：arXiv:2606.23130",
        "• A2UI：a2ui.org · AIVSS：aivss.owasp.org · Contentstack 2026 智能体企业报告",
    ],
    "19": [
        "结语",
        "• 这十条首先是技术预测 — 投资说明仅供讨论",
        "• 不构成投资建议 — 不是买卖推荐",
        "• 近期主题：智能体运行时控制、AI 生成代码安全、MCP 与网关安全",
        "• 可关注：AIVSS v1、浏览器智能体可靠性、以及 CSA 发布后的 MAESTRO v2",
        "• kenhuangus.substack.com · aivss.owasp.org · DistributedApps.ai · linkedin.com/in/kenhuang8",
    ],
    "20": [
        "谢谢",
        "《Graph Engineering for Agentic AI Systems》·《Harness Engineering》",
        "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM",
    ],
}


def to_py(obj: object) -> str:
    s = json.dumps(obj, ensure_ascii=False, indent=4)
    return s.replace(": true", ": True").replace(": false", ": False").replace(": null", ": None")


def main() -> None:
    for s in SLIDES_EN:
        n = str(s["number"])
        assert len(SLIDES_ZH[n]) == len(s["raw_lines"]), (n, len(SLIDES_ZH[n]), len(s["raw_lines"]))

    text = BUILD.read_text(encoding="utf-8")
    m_en = re.search(r"SLIDES_EN = (\[.*?\])\n\nSLIDES_ZH = ", text, re.S)
    m_zh = re.search(r"SLIDES_ZH = (\{.*?\})\n\nPHRASES = ", text, re.S)
    if not m_en or not m_zh:
        raise SystemExit("Could not locate SLIDES_EN / SLIDES_ZH in build_slides.py")

    text2 = (
        text[: m_en.start(1)]
        + to_py(SLIDES_EN)
        + text[m_en.end(1) : m_zh.start(1)]
        + to_py(SLIDES_ZH)
        + text[m_zh.end(1) :]
    )

    # Clean hero template strings for future rebuilds
    text2 = text2.replace(
        "'CSA 技术预测（2026-01-16），年中证据截至 2026-09-27；投资论点为今日新增的讨论框架，不构成投资建议。状态存档：标签 v1-midyear-scorecard。'",
        "'CSA 技术预测（2026-01-16），证据截至 2026-09-27；附投资讨论，不构成投资建议。'",
    )
    text2 = text2.replace(
        "'CSA technology predictions (2026-01-16), mid-year evidence through 2026-09-27, plus illustrative investment theses added today. Not Investment Advice. Status archive: tag v1-midyear-scorecard.'",
        "'CSA technology predictions (2026-01-16), evidence through 2026-09-27, with investment discussion. Not Investment Advice.'",
    )
    text2 = text2.replace(
        "'2026 智能体 AI 十大预测 · 年中成绩单'",
        "'2026 智能体 AI 十大预测'",
    )
    text2 = text2.replace(
        "'Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard'",
        "'Top 10 Predictions for Agentic AI in 2026'",
    )

    BUILD.write_text(text2, encoding="utf-8")

    r = subprocess.run([sys.executable, str(BUILD)], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)
    r = subprocess.run([sys.executable, str(ROOT / "cleanup_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)

    # Patch live hero text (build only replaces Packt originals)
    for path in (ROOT / "slides.html", ROOT / "docs" / "slides.html"):
        t = path.read_text(encoding="utf-8")
        replacements = [
            (
                "CSA technology predictions (2026-01-16), mid-year evidence through 2026-09-27, plus illustrative investment theses added today. Not Investment Advice. Status archive: tag v1-midyear-scorecard.",
                "CSA technology predictions (2026-01-16), evidence through 2026-09-27, with investment discussion. Not Investment Advice.",
            ),
            (
                "CSA 技术预测（2026-01-16），年中证据截至 2026-09-27；投资论点为今日新增的讨论框架，不构成投资建议。状态存档：标签 v1-midyear-scorecard。",
                "CSA 技术预测（2026-01-16），证据截至 2026-09-27；附投资讨论，不构成投资建议。",
            ),
            (
                "Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard",
                "Top 10 Predictions for Agentic AI in 2026",
            ),
            (
                "2026 智能体 AI 十大预测 · 年中成绩单",
                "2026 智能体 AI 十大预测",
            ),
        ]
        for old, new in replacements:
            t = t.replace(old, new)
        path.write_text(t, encoding="utf-8")

    # Landing page: strip archive chip / working notes
    for path in (ROOT / "index.html", ROOT / "docs" / "index.html"):
        if not path.exists():
            continue
        t = path.read_text(encoding="utf-8")
        t = t.replace(
            '<div class="eyebrow">Technology predictions · investment theses added 2026-09-27 · Not Investment Advice</div>',
            '<div class="eyebrow">Technology predictions · investment discussion · Not Investment Advice</div>',
        )
        t = t.replace(
            "<h2>CSA technology forecasts first — illustrative investment theses added today</h2>",
            "<h2>CSA technology forecasts, with a short investment discussion</h2>",
        )
        t = t.replace(
            "This site checks each prediction against public evidence through September 27, 2026, and adds an optional investment-discussion layer created on that same date.",
            "This site checks each prediction against public evidence through September 27, 2026, and adds a short investment discussion.",
        )
        t = t.replace(
            '<span class="chip">Investment layer added 2026-09-27</span>\n        <span class="chip">Not Investment Advice</span>\n        <span class="chip">Archive: v1-midyear-scorecard</span>',
            '<span class="chip">Not Investment Advice</span>',
        )
        t = t.replace(
            '<p style="margin-top:0.55rem;"><strong style="color:var(--ink);">Not Investment Advice.</strong> Original CSA content is technology prediction. Investment theses on this site were added 2026-09-27 for discussion only.</p>',
            '<p style="margin-top:0.55rem;"><strong style="color:var(--ink);">Not Investment Advice.</strong> Original CSA content is technology prediction. Investment notes are for discussion only.</p>',
        )
        t = t.replace("Weco AIDE² Level-1 RSI (Jul 2026)", "Early self-improving R&D agents (Jul 2026)")
        path.write_text(t, encoding="utf-8")

    # Final sanity: no archive tag, no hidden-eval wording
    blob = (ROOT / "slides.html").read_text(encoding="utf-8") + (ROOT / "slides-zh.js").read_text(encoding="utf-8")
    for bad in ("v1-midyear-scorecard", "hidden-eval", "hidden eval", "隐藏评测", "年中层", "Base layer", "Investment layer"):
        if bad in blob:
            raise SystemExit(f"Leftover working note or jargon: {bad}")
    print("CLEAN OK")


if __name__ == "__main__":
    main()
