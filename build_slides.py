#!/usr/bin/env python3
"""Inject prediction slides + ZH pack into the packt-harness template."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Verdict labels used in scorecard tables
# ON_TRACK | CONFIRMED | PARTIAL | IN_PROGRESS | MOSTLY_CONFIRMED

SLIDES_EN = [
    {
        "number": 1,
        "raw_lines": [
            "Top 10 Predictions for Agentic AI in 2026",
            "Cloud Security Alliance · January 16, 2026",
            "United States · China · European Union",
            "Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "Adjunct Professor, University of San Francisco: https://www.usfca.edu/faculty/ken-huang",
            "Not Investment Advice",
            "https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026"
        ]
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
            "• Substack: kenhuangus.substack.com  ·  LinkedIn: linkedin.com/in/kenhuang8"
        ]
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
            "IMG:assets/images/csa-top-10-predictions-2026.png"
        ]
    },
    {
        "number": 4,
        "raw_lines": [
            "Not Investment Advice",
            "• Technology predictions first published with the Cloud Security Alliance in January 2026",
            "• Any investment comments here are for education only",
            "• Not a recommendation to buy, sell, or hold any security or company",
            "• Readers should do their own diligence"
        ]
    },
    {
        "number": 5,
        "raw_lines": [
            "Investment Map — Not Investment Advice",
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
            "| 10 | AIVSS | Scoring after v1 is final / avoid unmapped private scores |"
        ]
    },
    {
        "number": 6,
        "raw_lines": [
            "P1 — Self-Improving Agents",
            "Early systems beat a fixed R&D budget baseline. Production still needs private tests the agent cannot see, plus human control.",
            "• Opportunity — Private eval platforms and Reward Hacking controls for frontier labs and AI R&D teams",
            "• Avoid — Public apps sold as self-improving AGI that rewrite their own code with no private tests and no spend limit"
        ]
    },
    {
        "number": 7,
        "raw_lines": [
            "P2 — Agency Matters More Than IQ Scores",
            "New benchmarks score multi-hour tool work, not quiz scores alone.",
            "• Opportunity — Agents that finish long tool workflows; sell planning and persistence scores into model selection and RFPs",
            "• Avoid — Chat products labeled as agents with no tools and no multi-hour tasks"
        ]
    },
    {
        "number": 8,
        "raw_lines": [
            "P3 — MAESTRO Security Benchmarks",
            "MAESTRO is in playbooks and CI. Shared public leaderboards are still thin.",
            "• Opportunity — Scanners that map a change to MAESTRO layers and block high-risk agent merges",
            "• Avoid — “MAESTRO compliant” badges with no layer tests and no scanner output"
        ]
    },
    {
        "number": 9,
        "raw_lines": [
            "P4 — Agentic Risk Management",
            "US, China, and EU rules now treat agent risk as a compliance problem.",
            "• Opportunity — Runtime allow or deny on tool calls, plus one control pack mapped to NIST, the EU AI Act, and China filing",
            "• Avoid — Policy documents with no live control when an agent calls a tool"
        ]
    },
    {
        "number": 10,
        "raw_lines": [
            "P5 — Vibe Coding Security Hangover",
            "About 91% of audited AI-generated apps had security holes (arXiv:2606.23130).",
            "• Opportunity — Security checks built into AI coding tools before deploy (login, secrets, access control)",
            "• Avoid — Builders that ship demos with hardcoded keys and APIs with no authentication"
        ]
    },
    {
        "number": 11,
        "raw_lines": [
            "P6 — Browser Agents Still Struggle",
            "Browser-agent protocols still lose sync. Desktop control remains easy to trick with prompt injection.",
            "• Opportunity — Agents limited to an approved action list, with human approval for payment and send-email",
            "• Avoid — Consumer bots that can pay or send email with no human check"
        ]
    },
    {
        "number": 12,
        "raw_lines": [
            "P7 — Enterprise: Internal First",
            "Most enterprise programs start inside the company. Many stall on content and data cleanup.",
            "• Opportunity — Internal agent platforms with ERP and IT connectors, and a KPI finance can audit",
            "• Avoid — Public consumer agents before an internal workflow has a measurable KPI"
        ]
    },
    {
        "number": 13,
        "raw_lines": [
            "P8 — More Agentic Ecosystem CVEs",
            "LangChain, MCP, and coding-agent bugs are already scored like normal software CVEs.",
            "• Opportunity — Secure MCP gateways and fast patching of agent frameworks and plugins",
            "• Avoid — MCP servers with no login, and one shared token for every tool"
        ]
    },
    {
        "number": 14,
        "raw_lines": [
            "P9 — MAESTRO v2 Practical Adoption",
            "MAESTRO v2 is not published. The model in use is still seven layers.",
            "• Opportunity — Implementation software and training for the current seven-layer model",
            "• Avoid — Products that claim “MAESTRO v2” or “ten layers” before CSA publishes v2"
        ]
    },
    {
        "number": 15,
        "raw_lines": [
            "P10 — OWASP AIVSS v1",
            "v0.8 is live. v1.0 is in public review through October 1, 2026.",
            "• Opportunity — Scoring engines and release gates once v1 is final",
            "• Avoid — Private “AI risk scores” that refuse to map to AIVSS after v1 is the standard"
        ]
    },
    {
        "number": 16,
        "raw_lines": [
            "Primary Sources",
            "• CSA predictions: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• Self-improving agents (AIDE²): weco.ai blog (2026-07-14); arXiv:2609.26457",
            "• AgencyBench (ACL 2026); Autonomous Agency Scale arXiv 2607.17947",
            "• MAESTRO seven-layer analysis: CSA blog 2026-08-13 (Ken Huang)",
            "• CSA AICM v1.1; China agent regulation (enforceable 2026-07-15); EU AI Act",
            "• Vibe coding security study: arXiv:2606.23130",
            "• A2UI: a2ui.org · AIVSS: aivss.owasp.org · Contentstack Agentic Enterprise Report 2026"
        ]
    },
    {
        "number": 17,
        "raw_lines": [
            "Looking Ahead",
            "• RSI and agent swarms are becoming important",
            "• Physical AI and humanoid robots are still in an early stage",
            "• World models need much more work — GPT-6 and Astra give some hope",
            "• Agentic AI security will focus on the secure harness",
            "• Not Investment Advice",
            "• kenhuangus.substack.com · aivss.owasp.org · DistributedApps.ai · linkedin.com/in/kenhuang8"
        ]
    },
    {
        "number": 18,
        "slide_type": "thanks",
        "raw_lines": [
            "Recent Books",
            "Graph Engineering for Agentic AI Systems · Harness Engineering",
            "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM"
        ]
    }
]

SLIDES_ZH = {
    "1": [
        "2026 智能体 AI 十大预测",
        "云安全联盟（CSA）· 2026 年 1 月 16 日",
        "美国 · 中国 · 欧盟",
        "作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "旧金山大学（USF）客座教授：https://www.usfca.edu/faculty/ken-huang",
        "不构成投资建议",
        "https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026"
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
        "• Substack：kenhuangus.substack.com  ·  LinkedIn：linkedin.com/in/kenhuang8"
    ],
    "3": [
        "CSA 原文发布 — 2026 年 1 月 16 日",
        "• 文章：My Top 10 Predictions for Agentic AI in 2026",
        "• 技术与产业预测 — 不是投资建议",
        "• 作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "• 发布方：云安全联盟（CSA）",
        "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "IMG:assets/images/csa-top-10-predictions-2026.png"
    ],
    "4": [
        "不构成投资建议",
        "• 技术预测最初于 2026 年 1 月与云安全联盟（CSA）发布",
        "• 文中投资相关评论仅供教育与讨论",
        "• 不是买卖或持有任何证券或公司的建议",
        "• 请读者自行尽职调查"
    ],
    "5": [
        "投资地图 — 不构成投资建议 (Not Investment Advice)",
        "| # | 趋势 | 关注 / 回避 |",
        "|---|---|---|",
        "| 1 | 自我改进智能体 (Self-Improving / RSI) | 私有测试 (Private Eval) + 人工控制 / 回避公网自行改代码 |",
        "| 2 | 自主性重于智商分 (Agency > IQ) | 长任务智能体 / 回避聊天冒充智能体 |",
        "| 3 | MAESTRO 基准 (Benchmarks) | CI 合并阻断 / 回避纸面徽章 |",
        "| 4 | 智能体风险 (Agentic Risk) | 工具调用实时放行/拒绝 (Allow/Deny) / 回避只有制度 PDF |",
        "| 5 | Vibe Coding 安全 | 安全的 AI 编程工具 / 回避带明文密钥的演示生成器 |",
        "| 6 | 浏览器智能体 (Browser Agents) | 批准动作清单 (Approved Actions) + 人工审批 / 回避可支付发信机器人 |",
        "| 7 | 内部优先 (Internal First) | 有 KPI 的内部平台 / 回避先做公网消费级 |",
        "| 8 | 智能体 CVE | 安全 MCP 与补丁 / 回避无登录的工具服务器 |",
        "| 9 | MAESTRO v2 | 现行七层 (7 Layers) 工具与培训 / 回避虚假 v2 宣称 |",
        "| 10 | AIVSS | v1 定稿后的评分 / 回避无法对照的私有分 |"
    ],
    "6": [
        "预测 1 — 自我改进智能体 (Self-Improving / RSI)",
        "早期系统已能在固定研发预算下超过人工基线 (Human Baseline)。投产仍需要智能体看不见的私有测试 (Private Eval)，以及人工控制。",
        "• 机会 — 私有测试 (Private Eval) 平台与防刷分 (Reward Hacking) 控制，卖给前沿实验室和 AI 研发团队",
        "• 回避 — 面向公网、自称自我改进 AGI、无 Private Eval 且无花费上限就自行改代码的应用"
    ],
    "7": [
        "预测 2 — 自主性 (Agency) 比智商分数 (IQ Scores) 更重要",
        "新基准主要打分「数小时工具任务 (Multi-hour Tool Tasks)」，而不是测验分数。",
        "• 机会 — 能完成长工具流程的智能体；把规划 (Planning) 与持续执行 (Persistence) 分数卖进选型与招标 (RFP)",
        "• 回避 — 没有工具、也完不成数小时任务、却自称智能体 (Agent) 的聊天产品"
    ],
    "8": [
        "预测 3 — MAESTRO 安全基准 (Security Benchmarks)",
        "MAESTRO 已进入操作手册 (Playbooks) 和 CI。公开排行榜 (Leaderboards) 仍少。",
        "• 机会 — 按 MAESTRO 分层检查变更、并阻断高风险智能体合并 (Merge) 的扫描器",
        "• 回避 — 没有分层测试、没有扫描输出的「MAESTRO 合规」徽章"
    ],
    "9": [
        "预测 4 — 智能体风险管理 (Agentic Risk Management)",
        "美、中、欧规则已把智能体风险当作合规 (Compliance) 问题。",
        "• 机会 — 工具调用的实时允许或拒绝 (Allow/Deny)，外加一套映射 NIST、欧盟 AI 法案与中国备案的控制包 (Control Pack)",
        "• 回避 — 只有制度文档、不能在工具调用时做实时控制 (Runtime Control) 的产品"
    ],
    "10": [
        "预测 5 — Vibe Coding 安全后遗症 (Security Hangover)",
        "被审计的 AI 生成应用约 91% 有安全漏洞（arXiv:2606.23130）。",
        "• 机会 — 在 AI 编程工具里内置部署前安全检查：登录、密钥 (Secrets)、访问控制 (Access Control)",
        "• 回避 — 交付演示时带硬编码密钥 (Hardcoded Secrets)、且 API 无认证 (No Auth) 的生成器"
    ],
    "11": [
        "预测 6 — 浏览器智能体 (Browser Agents) 仍难落地",
        "浏览器智能体协议仍易失同步 (Desync / Drift)。桌面操作仍容易被提示注入 (Prompt Injection) 欺骗。",
        "• 机会 — 只允许批准动作清单 (Approved Action Catalog)，支付和发邮件需人工审批",
        "• 回避 — 可以支付或发邮件、却没有人工确认的消费级机器人"
    ],
    "12": [
        "预测 7 — 企业：内部优先 (Internal First)",
        "多数企业项目从公司内部起步。很多卡在内容与数据清理 (Content / Data Cleanup)。",
        "• 机会 — 连接 ERP/IT 的内部智能体平台，并有财务可审计的 KPI",
        "• 回避 — 内部流程还没有可衡量 KPI 之前就做公网消费级 (B2C) 智能体"
    ],
    "13": [
        "预测 8 — 智能体生态 CVE 增多",
        "LangChain、MCP 和编程智能体漏洞已按普通软件 CVE 评级。",
        "• 机会 — 安全的 MCP 网关 (MCP Gateway)，以及对智能体框架与插件的快速补丁 (Patching)",
        "• 回避 — 无登录的 MCP 服务器，以及一把令牌调用全部工具 (Shared / God Token)"
    ],
    "14": [
        "预测 9 — MAESTRO v2 落地采用 (Practical Adoption)",
        "MAESTRO v2 尚未发布。现行模型仍是七层 (7 Layers)。",
        "• 机会 — 面向现行七层模型的落地软件与培训",
        "• 回避 — 在 CSA 发布 v2 之前宣称「MAESTRO v2」或「十层 (10 Layers)」的产品"
    ],
    "15": [
        "预测 10 — OWASP AIVSS v1",
        "v0.8 已上线。v1.0 公开评审 (Public Review) 至 2026 年 10 月 1 日。",
        "• 机会 — v1 定稿后的评分引擎 (Scoring Engine) 与发布门禁 (Release Gate)",
        "• 回避 — v1 成为标准后仍拒绝对照 (Crosswalk) AIVSS 的私有「AI 风险分」"
    ],
    "16": [
        "主要来源 (Primary Sources)",
        "• CSA 预测：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• 自我改进智能体 / RSI（AIDE²）：weco.ai 博客（2026-07-14）；arXiv:2609.26457",
        "• AgencyBench（ACL 2026）；自主性量表 (Autonomous Agency Scale) arXiv 2607.17947",
        "• MAESTRO 七层分析：CSA 博客 2026-08-13（Ken Huang）",
        "• CSA AICM v1.1；中国智能体监管（2026-07-15 起施行）；欧盟 AI 法案 (EU AI Act)",
        "• Vibe Coding 安全研究：arXiv:2606.23130",
        "• A2UI：a2ui.org · AIVSS：aivss.owasp.org · Contentstack 2026 智能体企业报告"
    ],
    "17": [
        "展望 (Looking Ahead)",
        "• RSI 与智能体集群 (Agent Swarm) 正变得越来越重要",
        "• 具身智能 (Physical AI) 与人形机器人 (Humanoid Robot) 仍处早期阶段",
        "• 世界模型 (World Model) 仍需大量工作 — GPT-6 与 Astra 带来一些希望",
        "• 智能体 AI 安全将聚焦安全驾驭层 (Secure Harness)",
        "• 不构成投资建议 (Not Investment Advice)",
        "• kenhuangus.substack.com · aivss.owasp.org · DistributedApps.ai · linkedin.com/in/kenhuang8"
    ],
    "18": [
        "近期图书",
        "《Graph Engineering for Agentic AI Systems》·《Harness Engineering》",
        "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM"
    ]
}

PHRASES = {
    "Harness Engineering Masterclass": "智能体 AI 2026 预测",
    "🏠 Home Site": "🏠 站点主页",
    "Presentation Mode": "放映模式",
    "Grid View": "网格视图",
    "❮ Prev": "❮ 上一页",
    "Next ❯": "下一页 ❯",
    "Go ➔": "跳转 ➔",
    "⛶ Fullscreen": "⛶ 全屏",
}


def main() -> None:
    html_path = ROOT / "slides.html"
    text = html_path.read_text(encoding="utf-8")

    # Replace slidesData
    pattern = r"const slidesData = \[.*?\];\n"
    replacement = "const slidesData = " + json.dumps(SLIDES_EN, ensure_ascii=False) + ";\n"
    text2, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"Failed to replace slidesData (matches={n})")

    # Branding / titles
    replacements = [
        (
            "Packt Masterclass Presentation: 85 Interactive Code, Architecture & Skill Slides",
            "Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard",
        ),
        ("Harness Engineering Masterclass", "Agentic AI 2026 Predictions"),
        ("packt-slides-lang", "predictions-slides-lang"),
        (
            "Packt Masterclass Presentation: 85 Interactive Code, Architecture & Skill Slides",
            "Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard",
        ),
        (
            "document.title = uiText(\n        'Packt Masterclass Presentation: 85 Interactive Code, Architecture & Skill Slides',\n        'Packt 大师课演示：85 页交互式代码、架构与技能幻灯片'\n      );",
            "document.title = uiText(\n        'Top 10 Predictions for Agentic AI in 2026',\n        '2026 智能体 AI 十大预测'\n      );",
        ),
        (
            "brand.textContent = uiText('Harness Engineering Masterclass', '智能体驾驭工程大师课');",
            "brand.textContent = uiText('Agentic AI 2026 Predictions', '智能体 AI 2026 预测');",
        ),
        (
            "home.textContent = uiText('🏠 Home Site', '🏠 课程主页');",
            "home.textContent = uiText('🏠 Home Site', '🏠 站点主页');",
        ),
        (
            'href="https://kenhuangus.github.io/packt-harness/"',
            'href="./index.html"',
        ),
        (
            "github.com/kenhuangus/packt-harness",
            "github.com/kenhuangus/agentic-ai-2026-predictions",
        ),
    ]
    for old, new in replacements:
        text2 = text2.replace(old, new)

    # Title slide hero / pillars — only replace if still on the Packt originals
    old_hero = """          <div id="slide-content-wrap" class="slide-1-container">
            <div class="slide-1-hero-card">
              <div class="slide-1-hero-tagline">
                Architecting Deterministic Control Systems for Non-Deterministic AI Agents
              </div>
              <div class="slide-1-hero-desc">
                A comprehensive masterclass in engineering reliable, observable, and secure production agent harnesses with Claude, memory architectures, AST guardrails, TDA self-healing loops, and compound multi-agent teams.
              </div>
            </div>"""

    new_hero = """          <div id="slide-content-wrap" class="slide-1-container">
            <div class="slide-1-hero-card">
              <div class="slide-1-hero-tagline">
                ${slideLang === 'zh' ? '2026 智能体 AI 十大预测' : 'Top 10 Predictions for Agentic AI in 2026'}
              </div>
              <div class="slide-1-hero-desc">
                ${slideLang === 'zh'
                  ? '云安全联盟（CSA）2026 年 1 月技术预测。美国 · 中国 · 欧盟。不构成投资建议。'
                  : 'Cloud Security Alliance technology predictions, January 2026. United States · China · European Union. Not Investment Advice.'}
              </div>
            </div>"""

    if old_hero in text2:
        text2 = text2.replace(old_hero, new_hero)

    # Pillars on title slide
    old_pillars = """            <div class="slide-1-pillars-row">
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">🛡️ Deterministic Harness</div>
                <div class="slide-1-pillar-desc">Memory, scoped sandboxing &amp; AST hooks</div>
              </div>
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">🧪 Test-Driven Reliability</div>
                <div class="slide-1-pillar-desc">Pytest feedback &amp; anti-regression suites</div>
              </div>
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">🤖 Multi-Agent Systems</div>
                <div class="slide-1-pillar-desc">Planner, implementer &amp; reviewer worktrees</div>
              </div>
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">📜 5-Gate Scorecard</div>
                <div class="slide-1-pillar-desc">Production readiness audit</div>
              </div>
            </div>"""

    new_pillars = """            <div class="slide-1-pillars-row">
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">${slideLang === 'zh' ? '🇺🇸 美国' : '🇺🇸 United States'}</div>
                <div class="slide-1-pillar-desc">${slideLang === 'zh' ? '实验室 RSI、CVE、企业调研' : 'Lab RSI, CVEs, enterprise surveys'}</div>
              </div>
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">${slideLang === 'zh' ? '🇨🇳 中国' : '🇨🇳 China'}</div>
                <div class="slide-1-pillar-desc">${slideLang === 'zh' ? '智能体专项监管与落地' : 'Agent-specific regulation &amp; deployment'}</div>
              </div>
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">${slideLang === 'zh' ? '🇪🇺 欧盟' : '🇪🇺 European Union'}</div>
                <div class="slide-1-pillar-desc">${slideLang === 'zh' ? 'AI 法案、A2UI、控制映射' : 'AI Act, A2UI, control mappings'}</div>
              </div>
              <div class="slide-1-pillar-pill">
                <div class="slide-1-pillar-title">${slideLang === 'zh' ? '📊 投资讨论' : '📊 Investment Notes'}</div>
                <div class="slide-1-pillar-desc">${slideLang === 'zh' ? '不构成投资建议' : 'Not Investment Advice'}</div>
              </div>
            </div>"""

    if old_pillars in text2:
        text2 = text2.replace(old_pillars, new_pillars)

    # Hide packt logo badge if present — keep structure, point away from packt
    text2 = text2.replace(
        'style="display: (slide.number === 1) ? \'inline-flex\' : \'none\'"',
        'style="display: none"',
    )

    # Course instructor badge label
    text2 = text2.replace(
        "<span>🎓 Course Instructor</span>",
        "<span>${slideLang === 'zh' ? '🎓 作者' : '🎓 Author'}</span>",
    )

    html_path.write_text(text2, encoding="utf-8")

    zh_payload = {"lines": SLIDES_ZH, "phrases": PHRASES}
    (ROOT / "slides-zh.js").write_text(
        "window.SLIDES_ZH = " + json.dumps(zh_payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    # Persist research JSON for the landing page / README
    research = {
        "as_of": "2026-09-27",
        "source_article": "https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "predictions": [
            {"id": 1, "title": "Self-Improving Agentic AI", "verdict": "on_track"},
            {"id": 2, "title": "Agency > Intelligence", "verdict": "on_track"},
            {"id": 3, "title": "MAESTRO Security Benchmarks", "verdict": "partial"},
            {"id": 4, "title": "Agentic Risk Management", "verdict": "confirmed"},
            {"id": 5, "title": "Vibe Coding Security Hangover", "verdict": "confirmed"},
            {"id": 6, "title": "Browser Agents Struggle", "verdict": "on_track"},
            {"id": 7, "title": "Enterprise Internal First", "verdict": "mostly_confirmed"},
            {"id": 8, "title": "More Agentic CVEs", "verdict": "confirmed"},
            {"id": 9, "title": "MAESTRO v2", "verdict": "in_progress"},
            {"id": 10, "title": "OWASP AIVSS v1", "verdict": "in_progress"},
        ],
    }
    (ROOT / "research" / "scorecard.json").write_text(
        json.dumps(research, indent=2) + "\n", encoding="utf-8"
    )

    # Copy to docs/ for GitHub Pages option
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "slides.html").write_text(text2, encoding="utf-8")
    (docs / "slides-zh.js").write_bytes((ROOT / "slides-zh.js").read_bytes())

    print(f"Wrote {len(SLIDES_EN)} EN slides and ZH pack.")
    print("Updated slides.html, slides-zh.js, research/scorecard.json, docs/")


if __name__ == "__main__":
    main()
