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
            "Investor thesis scorecard — as of September 27, 2026",
            "Original predictions: Cloud Security Alliance, January 16, 2026",
            "Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "Adjunct Professor, University of San Francisco: https://www.usfca.edu/faculty/ken-huang",
            "Lens: up to 3 investment theses per trend · US · China · EU evidence",
            "CSA article: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "Archive snapshot on GitHub tag: v1-midyear-scorecard"
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
            "• Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "• Publisher: Cloud Security Alliance (Industry Insights)",
            "• Open the original post:",
            "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• Screenshot below captures the published list of all 10 predictions",
            "IMG:assets/images/csa-top-10-predictions-2026.png"
        ]
    },
    {
        "number": 4,
        "raw_lines": [
            "About This Investor Scorecard",
            "• Origin: Ken Huang — My Top 10 Predictions for Agentic AI in 2026 (CSA, 2026-01-16)",
            "• CSA URL: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• Method: ≤3 investable theses per trend, plus explicit pitfalls and do-not-invest anti-theses (US/China/EU evidence through 2026-09-27)",
            "• Prior mid-year audit (status only) preserved as GitHub tag v1-midyear-scorecard / branch archive/v1-midyear-scorecard",
            "• Thesis bar: who pays, what product category, why now — not generic “AI will grow” claims",
            "• Regions still matter: US lab/CVE markets, China agent regulation, EU AI Act / CRA gates shape where capital can deploy"
        ]
    },
    {
        "number": 5,
        "raw_lines": [
            "Thesis Map at a Glance — September 27, 2026",
            "| # | Trend | Primary investable surface |",
            "|---|---|---|",
            "| 1 | Self-improving / RSI | Eval harnesses · governed self-mod · vertical RSI |",
            "| 2 | Agency > Intelligence | Agency scores · long-horizon agents · ambient agents |",
            "| 3 | MAESTRO benchmarks | CI threat modeling · red-team SaaS · assurance |",
            "| 4 | Agentic risk mgmt | Agent GRC · runtime policy · AI insurance tech |",
            "| 5 | Vibe-coding hangover | AI AppSec · secure builders · auto-remediation |",
            "| 6 | Browser agents | Protocol reliability · action catalogs · CUA defense |",
            "| 7 | Internal-first enterprise | Internal platforms · back-office ROI · controlled B2B |",
            "| 8 | Agentic CVEs | Agent SBOM · MCP gateways · secure vendors |",
            "| 9 | MAESTRO v2 | Implementation suites · trust plane · training |",
            "| 10 | AIVSS v1 | Scoring engines · crosswalks · release gates |"
        ]
    },
    {
        "number": 6,
        "raw_lines": [
            "P1 — Self-Improving / RSI Agents — Investor theses",
            "Evidence so far: Level-1 RSI demos (e.g. AIDE²); production still gated by eval + governance.",
            "• Thesis 1 — Evaluation infrastructure: bet on hidden-eval harnesses, reward-hacking detectors, and RSI regression suites sold to frontier labs and AI R&D teams",
            "• Thesis 2 — Governed self-modification: platforms that allow agents to rewrite tools/prompts only behind policy gates, audit logs, and human kill-switches (US labs + CN filing regimes)",
            "• Thesis 3 — Vertical RSI for code/ML ops: auto-research agents that improve training/inference pipelines under a fixed $ budget — not open-web general RSI",
            "• Pitfall — Treating Level-1 RSI demos as an intelligence explosion; ignition is unproven and eval gaming is common",
            "• Do not invest — Open-web “self-improving AGI” apps with no hidden evals, no kill-switch, and no budget ceiling"
        ]
    },
    {
        "number": 7,
        "raw_lines": [
            "P2 — Agency > Intelligence — Investor theses",
            "Evidence so far: AgencyBench, AAS, enterprise buyers scoring tool-use and persistence over raw IQ.",
            "• Thesis 1 — Agency measurement layer: startups that productize agency scores (plan/tool/persist) for model selection, vendor RFP, and insurance underwriting",
            "• Thesis 2 — Long-horizon task agents: invest in products that win on multi-hour tool workflows and self-correction, not chatbot leaderboard deltas",
            "• Thesis 3 — Ambient / always-on agents: scarce Ambient agency (Idle-Gap) is the next premium — companions and ops agents that act between user prompts under hard scopes",
            "• Pitfall — Paying for IQ/MMLU wrapper startups while buyers already score agency (tools, persistence, correction)",
            "• Do not invest — Chatbots marketed as agents without durable goals, tool contracts, or Idle-Gap ambient behavior"
        ]
    },
    {
        "number": 8,
        "raw_lines": [
            "P3 — MAESTRO Security Benchmarks — Investor theses",
            "Evidence so far: MAESTRO operationalized in playbooks/CI; shared public leaderboards still maturing.",
            "• Thesis 1 — Continuous threat modeling in CI: TITO-class scanners that map PRs to MAESTRO layers and block risky agent merges",
            "• Thesis 2 — Agent red-team as a service: recurring layer-mapped attack packs + ATLAS crosswalks sold to banks, SaaS, and AI platforms",
            "• Thesis 3 — Assurance products: STAR / AIUC-1 style attestations that package MAESTRO evidence for buyers, insurers, and regulators",
            "• Pitfall — Funding another static PDF checklist; buyers need CI enforcement and evidence packs, not slideware",
            "• Do not invest — “MAESTRO-compliant” badges with no layer tests, no ATLAS mapping, and no scanner output"
        ]
    },
    {
        "number": 9,
        "raw_lines": [
            "P4 — Agentic Risk Management — Investor theses",
            "Evidence so far: AICM v1.1, NIST AI RMF, China agent law, EU AI Act — risk is the buying center.",
            "• Thesis 1 — GRC for agents: control catalogs + questionnaires that map once to NIST / AICM / EU AI Act / CN filing and export auditor packs",
            "• Thesis 2 — Runtime risk engines: policy decision points on tool calls, autonomy tier, and human override — priced per agent-action",
            "• Thesis 3 — AI insurance & underwriting tech: AIUC-1 / AIVSS scoring feeds that let carriers price agent deployments",
            "• Pitfall — Building US-only GRC that cannot export EU AI Act / CN filing evidence — multinationals will churn",
            "• Do not invest — Policy docs generators with no runtime control plane and no priced decision on tool calls"
        ]
    },
    {
        "number": 10,
        "raw_lines": [
            "P5 — Vibe Coding Security Hangover — Investor theses",
            "Evidence so far: ~91% of audited vibe-coded apps vulnerable; tool CVEs and secrets sprawl rising.",
            "• Thesis 1 — AI-native AppSec for generated code: shift-left SAST/DAST tuned to AI failure modes (BAC, IDOR, hardcoded secrets)",
            "• Thesis 2 — Secure vibe platforms: IDEs/builders that ship with auth defaults, secret vaults, and fix-or-waive gates before deploy",
            "• Thesis 3 — Managed remediation: services/products that auto-patch AI-introduced CWE classes and prove exploitability pre-merge",
            "• Pitfall — Generic SAST rebranded as “AI security” without covering AI-specific failure modes (BAC/IDOR/secrets)",
            "• Do not invest — Vibe builders that optimize time-to-demo while shipping debug CORS, hardcoded keys, and no auth on APIs"
        ]
    },
    {
        "number": 11,
        "raw_lines": [
            "P6 — Browser Agents Struggle — Investor theses",
            "Evidence so far: AG-UI drift/perf issues; A2UI maturing; computer-use still injection-fragile.",
            "• Thesis 1 — Protocol reliability layer: sequence/resync, durable state, and snapshot-tax control for AG-UI / A2UI production stacks",
            "• Thesis 2 — Constrained action catalogs: browser/desktop agents that only call approved UI actions (safer than open DOM) for enterprise RPA replacement",
            "• Thesis 3 — Defense for computer-use: injection detection, session isolation, and human-in-the-loop for high-impact clicks (payments, email send)",
            "• Pitfall — Betting on full open-DOM computer-use reliability before protocol resync and injection defense mature",
            "• Do not invest — Consumer browser agents with payments/email send and no human approval or session isolation"
        ]
    },
    {
        "number": 12,
        "raw_lines": [
            "P7 — Enterprise Internal-First — Investor theses",
            "Evidence so far: internal ops preferred; dual programs growing; open-web B2C still cautious.",
            "• Thesis 1 — Internal agent platforms: secure connectors to ERP/ITSM/finance with data-ready pipelines (the 78% readiness gap)",
            "• Thesis 2 — Agentic back-office ROI: finance/ops automation with measurable P&L payback (fastest ROI categories in 2026 surveys)",
            "• Thesis 3 — Controlled externalization: products that graduate internal agents to B2B with DPIA, HITL, and tenant isolation — not consumer viral agents first",
            "• Pitfall — Skipping data readiness; 78% of enterprises hit content/data blockers that kill agent ROI narratives",
            "• Do not invest — Open-web B2C agent plays that burn trust capital before internal ops has a measurable P&L win"
        ]
    },
    {
        "number": 13,
        "raw_lines": [
            "P8 — Agentic Ecosystem CVEs — Investor theses",
            "Evidence so far: LangChain/MCP/coding-agent CVEs treated like classic software severity.",
            "• Thesis 1 — Agent SBOM + dependency firewall: pin/patch LangChain, MCP SDKs, IDE plugins with CVE streaming to SecOps",
            "• Thesis 2 — Secure MCP gateways: Host/Origin auth, least-privilege tool scopes, and sandbox escape prevention as infrastructure",
            "• Thesis 3 — Vendor security brands: agent-framework vendors that win enterprise on response time, CVSS clarity, and signed releases",
            "• Pitfall — Assuming model vendors absorb framework/MCP CVE risk; blast radius sits in the app’s dependency tree",
            "• Do not invest — Unauthenticated MCP servers, god-token tool hosts, and agent stacks without SBOM/pinning discipline"
        ]
    },
    {
        "number": 14,
        "raw_lines": [
            "P9 — MAESTRO v2 Practical Adoption — Investor theses",
            "Evidence so far: CSA MAESTRO v2 shipped 2026-06-22 (10 layers + Trust Control Plane).",
            "• Thesis 1 — MAESTRO implementation suites: templates, L1–L10 threat IDs, and SSRM ownership matrices sold as consulting + software",
            "• Thesis 2 — Trust Control Plane startups: identity, monitoring, and safety as horizontal control planes aligned to v2 domains",
            "• Thesis 3 — Training & certification: courses/cert paths that make MAESTRO the default hiring skill for agent security engineers",
            "• Pitfall — Consulting-only MAESTRO decks that never encode L1–L10 into tools — frameworks without software stall",
            "• Do not invest — “Trust plane” shells that rename IAM/observability without agency-specific identity or interrupt paths"
        ]
    },
    {
        "number": 15,
        "raw_lines": [
            "P10 — OWASP AIVSS v1 — Investor theses",
            "Evidence so far: v0.8 live; v1.0 public review through 2026-10-01; freeze targeted before year-end.",
            "• Thesis 1 — Scoring engines: products that compute AIVSS for agent releases and feed ticketing / SSVC prioritization",
            "• Thesis 2 — Crosswalk platforms: one risk graph across AIVSS ↔ AIUC-1 ↔ MAESTRO ↔ OWASP Agentic Top 10 for multinational buyers",
            "• Thesis 3 — Compliance acceleration: EU/US/CN programs that treat AIVSS scores as release gates and insurer inputs once v1 freezes",
            "• Pitfall — Shipping scoring UX before v1 freeze; methodology churn will force rework and buyer distrust",
            "• Do not invest — Proprietary “AI risk scores” that refuse AIVSS/AIUC-1/MAESTRO crosswalks once v1 is the standard"
        ]
    },
    {
        "number": 16,
        "raw_lines": [
            "Regional Capital Lens — United States · China · European Union",
            "| Theme | United States | China | European Union |",
            "|---|---|---|---|",
            "| Where $ pools | Labs, CVE tooling, enterprise surveys | Internal ops under localization + filing | Compliance software + human-oversight UX |",
            "| RSI / agency | Eval + vertical RSI startups | Regulated autonomy tiers | Research > open deploy; autonomy as risk object |",
            "| Security stack | MAESTRO/AIVSS productization, AppSec | Patch velocity + CNVD mirror | CRA/NIS2 build gates, AI Act mappings |",
            "| Browser agents | Protocol reliability + CUA defense | Constrained catalogs in productivity apps | A2UI std + oversight-friendly UX |",
            "| Enterprise | Internal platforms, dual programs | Data-local agent platforms | HITL-first externalization |"
        ]
    },
    {
        "number": 17,
        "raw_lines": [
            "Open Questions for Capital — Q4 2026",
            "• Does AIVSS v1 freeze create a scoring-engine category winner, or stay a free checklist?",
            "• Will AG-UI/A2UI reliability layers become infrastructure picks or stay framework features?",
            "• Is RSI investable beyond eval vendors before Level-2 ignition evidence?",
            "• Do internal-first platforms capture budget before open-web B2C agents clear trust?",
            "• Can AI AppSec vendors cut the ~91% vibe-coded vuln baseline enough to become default CI?",
            "• Watch regulation: CN agent filing costs vs US CVE velocity vs EU CRA/AI Act gates"
        ]
    },
    {
        "number": 18,
        "raw_lines": [
            "Primary Sources (selected)",
            "• CSA predictions (2026-01-16): https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• AIDE² RSI: weco.ai blog (2026-07-14); arXiv:2609.26457",
            "• AgencyBench: ACL 2026; Autonomous Agency Scale arXiv HTML 2607.17947",
            "• MAESTRO v2 artifact (2026-06-22): cloudsecurityalliance.org/artifacts/maestro-v2",
            "• CSA AICM v1.1 (2026-07-14 blog); China agent regulation CSA Labs note (enforcement 2026-07-15)",
            "• Vibe coding study: arXiv:2606.23130; OX Security / Georgia Tech CVE radar summaries",
            "• AG-UI production drift analyses (2026); A2UI a2ui.org v0.9.1 / v1.0-rc",
            "• Contentstack Agentic Enterprise Report 2026; NVD CVE-2026-55443; AIVSS aivss.owasp.org v0.8 + review"
        ]
    },
    {
        "number": 19,
        "raw_lines": [
            "Closing — Where capital meets agentic security",
            "• Each of the 10 CSA trends maps to ≤3 theses plus pitfall / do-not-invest lines",
            "• Strongest near-term wallets: enterprise GRC/runtime controls, AI AppSec for vibe coding, MCP/gateway security",
            "• Structural openers into Q4: AIVSS v1 freeze, A2UI reliability, independent RSI replication",
            "• Status-only archive remains at tag v1-midyear-scorecard for comparison",
            "• Continue: kenhuangus.substack.com · aivss.owasp.org · CSA AI Safety working groups",
            "• Contact: DistributedApps.ai · LinkedIn linkedin.com/in/kenhuang8"
        ]
    },
    {
        "number": 20,
        "slide_type": "thanks",
        "raw_lines": [
            "Thank you",
            "Graph Engineering for Agentic AI Systems · Harness Engineering",
            "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM"
        ]
    }
]

SLIDES_ZH = {
    "1": [
        "2026 智能体 AI 十大预测",
        "投资论点成绩单 — 截至 2026 年 9 月 27 日",
        "原始预测：云安全联盟（CSA），2026 年 1 月 16 日",
        "作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "旧金山大学（USF）客座教授：https://www.usfca.edu/faculty/ken-huang",
        "视角：每个趋势最多 3 条投资论点 · 美 · 中 · 欧证据",
        "CSA 原文：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "GitHub 存档标签：v1-midyear-scorecard"
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
        "• 作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "• 发布方：云安全联盟（Industry Insights）",
        "• 打开原文：",
        "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• 下方截图展示已发布的全部 10 条预测",
        "IMG:assets/images/csa-top-10-predictions-2026.png"
    ],
    "4": [
        "关于本投资成绩单",
        "• 出处：Ken Huang —《My Top 10 Predictions for Agentic AI in 2026》（CSA，2026-01-16）",
        "• CSA 链接：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• 方法：每个趋势 ≤3 条可投资论点，并列出陷阱与不宜投的反论点（美/中/欧证据截至 2026-09-27）",
        "• 先前年中审计（仅状态判定）保留为 GitHub 标签 v1-midyear-scorecard / 分支 archive/v1-midyear-scorecard",
        "• 论点标准：谁付费、什么产品类别、为何是现在 — 而非笼统的「AI 会增长」",
        "• 区域仍关键：美国实验室/CVE 市场、中国智能体监管、欧盟 AI 法案/CRA 门禁决定资本可部署之处"
    ],
    "5": [
        "投资论点地图一览 — 2026 年 9 月 27 日",
        "| # | 趋势 | 主要可投资表面 |",
        "|---|---|---|",
        "| 1 | 自我改进 / RSI | 评估 harness · 受治自我修改 · 垂直 RSI |",
        "| 2 | 自主性 > 智力 | 自主性分数 · 长时程智能体 · Ambient 智能体 |",
        "| 3 | MAESTRO 基准 | CI 威胁建模 · 红队 SaaS · 保障证明 |",
        "| 4 | 智能体风险管理 | 智能体 GRC · 运行时策略 · AI 保险科技 |",
        "| 5 | 氛围编程后遗症 | AI AppSec · 安全构建器 · 自动修复 |",
        "| 6 | 浏览器智能体 | 协议可靠性 · 动作目录 · 计算机使用防御 |",
        "| 7 | 企业内部优先 | 内部平台 · 后台 ROI · 受控 B2B |",
        "| 8 | 智能体 CVE | 智能体 SBOM · MCP 网关 · 安全厂商 |",
        "| 9 | MAESTRO v2 | 实施套件 · 信任平面 · 培训认证 |",
        "| 10 | AIVSS v1 | 评分引擎 · 交叉映射 · 发布门禁 |"
    ],
    "6": [
        "预测 1 — 自我改进 / RSI 智能体 — 投资论点",
        "现有证据：一级 RSI 演示（如 AIDE²）；生产仍受评估与治理约束。",
        "• 论点 1 — 评估基础设施：押注隐藏评估 harness、奖励作弊检测与 RSI 回归套件，卖给前沿实验室与 AI 研发团队",
        "• 论点 2 — 受治理的自我修改：仅在策略门禁、审计日志与人类急停之后允许智能体改写工具/提示（适配美国实验室与中国备案制度）",
        "• 论点 3 — 面向代码/ML Ops 的垂直 RSI：在固定美元预算下改进训练/推理管线的自动研究智能体 — 而非开放网络通用 RSI",
        "• 陷阱 — 把一级 RSI 演示当成智能爆炸；点火未证实，且评估作弊常见",
        "• 不宜投 — 无隐藏评估、无急停、无预算上限的开放网络「自我改进 AGI」应用"
    ],
    "7": [
        "预测 2 — 自主性 > 智力 — 投资论点",
        "现有证据：AgencyBench、AAS；企业买方更看重工具使用与持续执行，而非原始智商。",
        "• 论点 1 — 自主性度量层：将规划/工具/持续目标分数产品化，用于模型选型、供应商 RFP 与保险核保",
        "• 论点 2 — 长时程任务智能体：投资能赢多数小时工具工作流与自我纠错的产品，而非聊天机器人榜单分差",
        "• 论点 3 — Ambient / 常驻智能体：稀缺的 Ambient 自主性（Idle-Gap）将成为溢价 — 在硬范围下于用户提示之间行动的伙伴与运维智能体",
        "• 陷阱 — 为 IQ/MMLU 包装创业公司买单，而买方已在用自主性（工具、持续、纠错）打分",
        "• 不宜投 — 被宣传为智能体、却无耐久目标、无工具契约、无 Idle-Gap Ambient 行为的聊天机器人"
    ],
    "8": [
        "预测 3 — MAESTRO 安全基准 — 投资论点",
        "现有证据：MAESTRO 已进入手册/CI；共享公共排行榜仍在成熟。",
        "• 论点 1 — CI 中的持续威胁建模：将 PR 映射到 MAESTRO 层并阻断高风险智能体合并的 TITO 类扫描器",
        "• 论点 2 — 智能体红队即服务：面向银行、SaaS 与 AI 平台的分层攻击包 + ATLAS 对照，按周期订阅",
        "• 论点 3 — 保障产品：将 MAESTRO 证据打包给买方、保险公司与监管的 STAR / AIUC-1 类证明",
        "• 陷阱 — 再投一份静态 PDF 清单；买方需要的是 CI 强制执行与证据包，而非幻灯片",
        "• 不宜投 — 无分层测试、无 ATLAS 映射、无扫描输出的「MAESTRO 合规」徽章"
    ],
    "9": [
        "预测 4 — 智能体风险管理 — 投资论点",
        "现有证据：AICM v1.1、NIST AI RMF、中国智能体法规、欧盟 AI 法案 — 风险是采购中心。",
        "• 论点 1 — 面向智能体的 GRC：一次映射 NIST / AICM / 欧盟 AI 法案 / 中国备案并导出审计包的控制目录与问卷",
        "• 论点 2 — 运行时风险引擎：对工具调用、自主等级与人类否决的策略决策点 — 按智能体动作计费",
        "• 论点 3 — AI 保险与核保技术：让承保方为智能体部署定价的 AIUC-1 / AIVSS 评分供给",
        "• 陷阱 — 只做美国 GRC、无法导出欧盟 AI 法案/中国备案证据 — 跨国客户会流失",
        "• 不宜投 — 只会生成政策文档、没有运行时控制平面、不对工具调用做计价决策的产品"
    ],
    "10": [
        "预测 5 — 氛围编程安全后遗症 — 投资论点",
        "现有证据：约 91% 被审计的氛围编程应用存在漏洞；工具 CVE 与密钥扩散上升。",
        "• 论点 1 — 面向生成代码的 AI 原生 AppSec：针对 AI 失败模式（访问控制、IDOR、硬编码密钥）调优的左移 SAST/DAST",
        "• 论点 2 — 安全的氛围编程平台：默认认证、密钥保险库与部署前「修复或豁免」门禁的 IDE/构建器",
        "• 论点 3 — 托管修复：自动修补 AI 引入的 CWE 类别并在合并前证明可利用性的服务/产品",
        "• 陷阱 — 把通用 SAST 改名「AI 安全」，却不覆盖 AI 特有失败模式（访问控制/IDOR/密钥）",
        "• 不宜投 — 优化演示速度、却交付调试 CORS、硬编码密钥、API 无认证的氛围构建器"
    ],
    "11": [
        "预测 6 — 浏览器智能体艰难之路 — 投资论点",
        "现有证据：AG-UI 漂移/性能问题；A2UI 成熟中；计算机使用仍易受注入影响。",
        "• 论点 1 — 协议可靠性层：为 AG-UI / A2UI 生产栈提供序号/重同步、耐久状态与快照税控制",
        "• 论点 2 — 受约束动作目录：仅调用已批准 UI 动作的浏览器/桌面智能体（比开放 DOM 更安全），替代企业 RPA",
        "• 论点 3 — 计算机使用防御：注入检测、会话隔离，以及对高影响点击（支付、发信）的人类在环",
        "• 陷阱 — 在协议重同步与注入防御成熟前，押注开放 DOM 计算机使用的全面可靠",
        "• 不宜投 — 可支付/发信且无人审批、无会话隔离的消费级浏览器智能体"
    ],
    "12": [
        "预测 7 — 企业内部优先 — 投资论点",
        "现有证据：内部运营优先；双线项目增长；开放网络 B2C 仍谨慎。",
        "• 论点 1 — 内部智能体平台：通向 ERP/ITSM/财务的安全连接器与数据就绪管线（填补 78% 就绪缺口）",
        "• 论点 2 — 智能体后台 ROI：具有可度量损益回收的财务/运营自动化（2026 调研中最快回收类别）",
        "• 论点 3 — 受控外部化：以 DPIA、HITL 与租户隔离将内部智能体升级到 B2B 的产品 — 而非先做消费级病毒式智能体",
        "• 陷阱 — 跳过数据就绪；78% 企业卡在内容/数据阻断，会杀死智能体 ROI 叙事",
        "• 不宜投 — 在内部运营尚无可度量损益胜利前，就燃烧信任资本的开放网络 B2C 智能体"
    ],
    "13": [
        "预测 8 — 智能体生态 CVE — 投资论点",
        "现有证据：LangChain/MCP/编程智能体 CVE 已按传统软件严重度对待。",
        "• 论点 1 — 智能体 SBOM + 依赖防火墙：钉死/修补 LangChain、MCP SDK、IDE 插件，并向 SecOps 流式推送 CVE",
        "• 论点 2 — 安全 MCP 网关：Host/Origin 认证、最小权限工具范围与防沙箱逃逸，作为基础设施出售",
        "• 论点 3 — 厂商安全品牌：以响应速度、CVSS 清晰度与签名发布赢得企业的智能体框架厂商",
        "• 陷阱 — 认为模型厂商会吞下框架/MCP CVE 风险；爆炸半径在应用的依赖树里",
        "• 不宜投 — 无认证的 MCP 服务器、上帝令牌工具主机、以及无 SBOM/钉死纪律的智能体栈"
    ],
    "14": [
        "预测 9 — MAESTRO v2 落地采用 — 投资论点",
        "现有证据：CSA MAESTRO v2 已于 2026-06-22 发布（10 层 + 信任控制平面）。",
        "• 论点 1 — MAESTRO 实施套件：以咨询 + 软件形式出售的模板、L1–L10 威胁 ID 与 SSRM 责任矩阵",
        "• 论点 2 — 信任控制平面创业公司：对齐 v2 域的身份、监控与安全横向控制平面",
        "• 论点 3 — 培训与认证：使 MAESTRO 成为智能体安全工程师默认招聘技能的课程/认证路径",
        "• 陷阱 — 只有咨询式 MAESTRO 幻灯、从不把 L1–L10 编进工具 — 无软件的框架会停滞",
        "• 不宜投 — 只是改名 IAM/可观测性、却无智能体身份与中断路径的「信任平面」空壳"
    ],
    "15": [
        "预测 10 — OWASP AIVSS v1 — 投资论点",
        "现有证据：v0.8 已上线；v1.0 公开评审至 2026-10-01；计划年底前冻结。",
        "• 论点 1 — 评分引擎：为智能体发布计算 AIVSS 并馈入工单 / SSVC 优先级的产品",
        "• 论点 2 — 交叉映射平台：覆盖 AIVSS ↔ AIUC-1 ↔ MAESTRO ↔ OWASP 智能体 Top 10 的单一风险图，服务跨国买方",
        "• 论点 3 — 合规加速：一旦 v1 冻结，将 AIVSS 分数作为发布门禁与保险输入的美欧中项目",
        "• 陷阱 — 在 v1 冻结前就上线评分 UX；方法变更会迫使返工并损害买方信任",
        "• 不宜投 — 在 v1 成为标准后仍拒绝 AIVSS/AIUC-1/MAESTRO 对照的专有「AI 风险分」"
    ],
    "16": [
        "区域资本视角 — 美国 · 中国 · 欧盟",
        "| 主题 | 美国 | 中国 | 欧盟 |",
        "|---|---|---|---|",
        "| 资金池 | 实验室、CVE 工具、企业调研 | 本地化 + 备案下的内部运营 | 合规软件 + 人类监督体验 |",
        "| RSI / 自主性 | 评估 + 垂直 RSI 创业公司 | 受监管的自主等级 | 研究 > 开放部署；自主性即风险对象 |",
        "| 安全栈 | MAESTRO/AIVSS 产品化、AppSec | 补丁速度 + CNVD 镜像 | CRA/NIS2 构建门禁、AI 法案映射 |",
        "| 浏览器智能体 | 协议可靠性 + 计算机使用防御 | 生产力应用中的受约束目录 | A2UI 标准 + 便于监督的体验 |",
        "| 企业 | 内部平台、双线项目 | 数据本地智能体平台 | HITL 优先的外部化 |"
    ],
    "17": [
        "给资本的未决问题 — 2026 年第四季度",
        "• AIVSS v1 冻结会造就评分引擎类别赢家，还是停留在免费清单？",
        "• AG-UI/A2UI 可靠性层会成为基础设施标的，还是框架附带功能？",
        "• 在二级点火证据出现前，RSI 是否只在评估供应商层面可投资？",
        "• 内部优先平台能否在开放网络 B2C 智能体建立信任前拿下预算？",
        "• AI AppSec 厂商能否把约 91% 的氛围编程漏洞基线压到成为默认 CI？",
        "• 关注监管：中国智能体备案成本 vs 美国 CVE 速度 vs 欧盟 CRA/AI 法案门禁"
    ],
    "18": [
        "主要来源（节选）",
        "• CSA 预测（2026-01-16）：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• AIDE² RSI：weco.ai 博客（2026-07-14）；arXiv:2609.26457",
        "• AgencyBench：ACL 2026；自主代理量表 arXiv HTML 2607.17947",
        "• MAESTRO v2 产物（2026-06-22）：cloudsecurityalliance.org/artifacts/maestro-v2",
        "• CSA AICM v1.1（2026-07-14 博客）；中国智能体监管 CSA Labs 说明（执法 2026-07-15）",
        "• 氛围编程研究：arXiv:2606.23130；OX Security / 佐治亚理工 CVE 雷达摘要",
        "• AG-UI 生产漂移分析（2026）；A2UI a2ui.org v0.9.1 / v1.0-rc",
        "• Contentstack 2026 智能体企业报告；NVD CVE-2026-55443；AIVSS aivss.owasp.org v0.8 + 评审"
    ],
    "19": [
        "结语 — 资本与智能体安全交汇之处",
        "• CSA 的 10 个趋势各自映射到 ≤3 条投资论点，并附陷阱 / 不宜投",
        "• 近期最强钱包：企业 GRC/运行时控制、氛围编程 AI AppSec、MCP/网关安全",
        "• 进入第四季度的结构性窗口：AIVSS v1 冻结、A2UI 可靠性、独立 RSI 复现",
        "• 仅状态判定的存档仍在标签 v1-midyear-scorecard，便于对照",
        "• 继续对话：kenhuangus.substack.com · aivss.owasp.org · CSA AI 安全工作组",
        "• 联系：DistributedApps.ai · LinkedIn linkedin.com/in/kenhuang8"
    ],
    "20": [
        "谢谢",
        "《Graph Engineering for Agentic AI Systems》·《Harness Engineering》",
        "amazon.com/dp/B0HHZVDQQY · amazon.com/dp/B0HF3F86YM"
    ]
}

PHRASES = {
    "Harness Engineering Masterclass": "智能体 AI 2026 预测成绩单",
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
            "document.title = uiText(\n        'Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard',\n        '2026 智能体 AI 十大预测 — 年中成绩单'\n      );",
        ),
        (
            "brand.textContent = uiText('Harness Engineering Masterclass', '智能体驾驭工程大师课');",
            "brand.textContent = uiText('Agentic AI 2026 Predictions', '智能体 AI 2026 预测成绩单');",
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
                ${slideLang === 'zh' ? '2026 智能体 AI 十大预测 · 年中成绩单' : 'Top 10 Predictions for Agentic AI in 2026 — Mid-Year Scorecard'}
              </div>
              <div class="slide-1-hero-desc">
                ${slideLang === 'zh'
                  ? '基于 CSA 十大预测（2026-01-16）的投资论点成绩单。每个趋势最多 3 条可投资论点，锚定美 · 中 · 欧至 2026-09-27 的证据。状态审计存档：GitHub 标签 v1-midyear-scorecard。'
                  : 'Investor thesis scorecard from the CSA Top 10 (2026-01-16). Up to 3 investable theses per trend, grounded in US · China · EU evidence through 2026-09-27. Prior status audit: GitHub tag v1-midyear-scorecard.'}
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
                <div class="slide-1-pillar-title">${slideLang === 'zh' ? '📊 10 条判定' : '📊 10 Verdicts'}</div>
                <div class="slide-1-pillar-desc">${slideLang === 'zh' ? '截至 2026-09-27 的证据审计' : 'Evidence audit as of 2026-09-27'}</div>
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
            {"id": 9, "title": "MAESTRO v2", "verdict": "confirmed"},
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
