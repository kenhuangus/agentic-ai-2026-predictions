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
            "Mid-Year Scorecard — as of September 27, 2026",
            "Original predictions: Cloud Security Alliance, January 16, 2026",
            "Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "Adjunct Professor, University of San Francisco: https://www.usfca.edu/faculty/ken-huang",
            "Regional lens: United States · China · European Union",
            "CSA article: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "Sources: CSA article + Substack; research cut-off 2026-09-27",
        ],
    },
    {
        "number": 2,
        "raw_lines": [
            "Original CSA Publication — January 16, 2026",
            "• Article: My Top 10 Predictions for Agentic AI in 2026",
            "• Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
            "• Publisher: Cloud Security Alliance (Industry Insights)",
            "• Open the original post:",
            "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• Screenshot below captures the published list of all 10 predictions",
            "IMG:assets/images/csa-top-10-predictions-2026.png",
        ],
    },
    {
        "number": 3,
        "raw_lines": [
            "About This Scorecard",
            "• Origin: Ken Huang — My Top 10 Predictions for Agentic AI in 2026 (CSA, 2026-01-16)",
            "• CSA URL: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• Method: map each prediction to public evidence in US, China, and EU through 2026-09-27",
            "• Evidence classes: peer-reviewed papers, CVE/NVD, CSA/OWASP/NIST artifacts, enterprise surveys, regulation",
            "• Verdict scale: Confirmed · Mostly confirmed · On track · Partial · In progress (toward year-end)",
            "• Not a forecast rewrite — a mid-year audit of what already happened vs what remains open",
        ],
    },
    {
        "number": 4,
        "raw_lines": [
            "Scorecard at a Glance — September 27, 2026",
            "| # | Prediction | Verdict |",
            "|---|---|---|",
            "| 1 | Self-improving / RSI agents | On track (research confirmed) |",
            "| 2 | Agency > Intelligence | On track |",
            "| 3 | MAESTRO-based security benchmarks | Partial → On track |",
            "| 4 | Agentic risk management center stage | Confirmed |",
            "| 5 | Vibe-coding security hangover | Confirmed |",
            "| 6 | Browser agents struggle | On track |",
            "| 7 | Enterprise: internal first | Mostly confirmed |",
            "| 8 | More CVEs in agentic ecosystem | Confirmed |",
            "| 9 | MAESTRO v2 practical release | Confirmed (2026-06-22) |",
            "| 10 | OWASP AIVSS v1 official release | In progress (review open) |",
        ],
    },
    {
        "number": 5,
        "raw_lines": [
            "P1 — The Self-Improving Agentic AI System",
            "Prediction (Jan 2026): move past static agents; more research and some real-world self-improving agents.",
            "• Verdict: On track — Level-1 recursive self-improvement (RSI) demonstrated in research; production still gated",
            "• United States: Weco AI AIDE² (2026-07-14) — 8-day outer loop, 7 successive harness upgrades; arXiv:2609.26457",
            "  • AIDE85 beat 2 years of hand-tuned AIDE-human on held-out MLE/ALE/WeatherBench under fixed $ budget",
            "  • Reward hacking on GPU-kernel task fell ~63% → ~34%; claims Level-1 net-positive RSI, not ignition",
            "• China: frontier agent regulation entered enforcement 2026-07-15 (CAC joint Implementation Opinions)",
            "  • Tiered authorization, auditable decision logs, human override for high-impact autonomous agents",
            "  • Self-modification loops face stronger filing/testing obligations than in open US labs",
            "• European Union: EU AI Act high-risk oversight + human-oversight duties slow open-web RSI deployment",
            "  • Research continues; production self-rewriting agents remain rare outside controlled sandboxes",
        ],
    },
    {
        "number": 6,
        "raw_lines": [
            "P2 — Agency > Intelligence",
            "Prediction: industry stops obsessing over raw intelligence scores; agency (plan, tools, persist) becomes primary.",
            "• Verdict: On track — agency metrics and benchmarks proliferated in 2026",
            "• United States: AgencyBench (ACL 2026) — 32 scenarios, ~90 tool calls / 1M tokens / hours of runtime",
            "  • Closed models 48.4% vs open 32.1%; emphasis on tool use, self-correction, resource efficiency",
            "  • Autonomous Agency Scale (AAS, Jul 2026) scores Active vs Ambient agency with Idle-Gap Test",
            "• China: agent products compete on task completion and tool chains more than MMLU-style leaderboards",
            "  • Regulatory framing treats agent decision authority as the control object, not model IQ",
            "• European Union: conformity and oversight discussions track autonomy level and impact, not raw capability scores",
            "  • Academic work (e.g. bipredictability / agency–intelligence theory, arXiv:2602.22519) separates the two constructs",
        ],
    },
    {
        "number": 7,
        "raw_lines": [
            "P3 — New Security Benchmarks via MAESTRO",
            "Prediction: new agent security benchmarks based on MAESTRO threat modeling get adopted.",
            "• Verdict: Partial → On track — MAESTRO is operationalized; universal benchmark suites still maturing",
            "• United States: CSA MAESTRO + ATLAS combined playbooks; TITO CI/CD threat modeling (CSA, 2026-02-11)",
            "  • Agentic red-team guides map tests to MAESTRO layers; STAR / AIUC-1 assurance paths emerging",
            "• China: MAESTRO cited in CSA guidance as a way to evidence engineered agent boundaries for regulators",
            "  • Domestic agent security evaluations increasingly require layer-wise threat coverage, not prompt-only tests",
            "• European Union: mappings into EU AI Act / ISO 42001 via CSA AICM; MAESTRO used as threat-generation front-end",
            "  • Gap: no single global numeric \"MAESTRO score\" yet — frameworks + scanners ahead of shared leaderboards",
        ],
    },
    {
        "number": 8,
        "raw_lines": [
            "P4 — Agentic AI Risk Management Takes Center Stage",
            "Prediction: organizations align with NIST AI RMF, CSA AICM, and OWASP AIVSS for agentic risk.",
            "• Verdict: Confirmed — risk management is the center of 2026 agentic governance",
            "• United States: NIST AI RMF remains the risk spine; CSA AICM v1.1 (Jun 23 / Jul Jul 2026) adds AIUC-1 mapping",
            "  • Five Eyes / CISA careful-adoption guidance for agentic services (May 2026); RSAC 2026 AIVSS panels",
            "• China: dedicated national AI-agent regulatory category enforceable from 2026-07-15",
            "  • Filing, testing, tiered decision authority, and mandatory human override for Level 2/3 agent decisions",
            "• European Union: EU AI Act obligations (transparency, risk assessment, human oversight) for high-risk systems",
            "  • AICM v1.1 supplies operational security controls the Act itself does not prescribe",
            "• Crosswalks: AIVSS ↔ AIUC-1 ↔ MAESTRO ↔ OWASP Agentic Top 10 now published and used in enterprise programs",
        ],
    },
    {
        "number": 9,
        "raw_lines": [
            "P5 — The \"Vibe Coding\" Security Hangover",
            "Prediction: vibe coding accelerates shipping; non-deterministic NL→code worsens DevSecOps risk.",
            "• Verdict: Confirmed — empirical studies show insecurity is the norm for vibe-coded apps",
            "• United States: arXiv:2606.23130 (v3 Sep 2026) — 9,041 OSS apps; audit of 200 deployed apps → 1,186 vulns",
            "  • 91.0% of audited apps had ≥1 vulnerability; 65.77% of findings Critical/High (BAC, injection, auth)",
            "  • Georgia Tech Vibe Security Radar: 74 CVEs traceable to AI coding tools by March 2026",
            "  • Tool CVEs: Cursor MCP (CVE-2025-54135), Claude Code (CVE-2025-55284 / CVE-2025-59536 class)",
            "• China: rapid adoption of AI coding assistants in startups; same failure modes (secrets, IDOR, missing auth)",
            "  • Domestic AppSec vendors shipping AI-code scanners into CI; regulators watch supply-chain leakage",
            "• European Union: NIS2 / CRA pressure pushes SBOM + build-time gates for AI-generated dependencies",
            "  • Shift-left DAST and fix-or-waive policies for AI-introduced CWE classes entering enterprise playbooks",
        ],
    },
    {
        "number": 10,
        "raw_lines": [
            "P6 — The Struggle of Browser Agents",
            "Prediction: browser agents struggle until AG-UI / A2UI interoperability and contractual gaps are fixed.",
            "• Verdict: On track — protocols advanced; production reliability still fragile",
            "• United States: AG-UI widely integrated (CopilotKit et al.) but STATE_DELTA silent drift documented (mid-2026)",
            "  • Main-thread stalls (20s+ structuredClone) and reconnect gap bugs filed on ag-ui-protocol/ag-ui",
            "  • Computer-use / GUI agents still fail under repeated prompt injection (Anthropic measurements: residual risk)",
            "• China: browser/desktop agents popular in productivity apps; reliability and permission UX remain pain points",
            "  • Domestic platforms prefer constrained action catalogs over open DOM control for consumer products",
            "• European Union: A2UI (Google + community) at v0.9.1 production; v1.0 release candidate (updated Jun 2026)",
            "  • Declarative UI catalogs improve safety vs arbitrary code; ordered delivery still required to avoid corruption",
            "• Bottom line: standards exist; \"widespread reliable adoption\" is not yet the default production posture",
        ],
    },
    {
        "number": 11,
        "raw_lines": [
            "P7 — Enterprise Deployment: Internal First",
            "Prediction: internal agent deployments widen; limited B2B/B2C agents on the open web due to caution.",
            "• Verdict: Mostly confirmed — internal still preferred; dual internal+external programs growing",
            "• United States: Contentstack Agentic Enterprise Report (May 2026, n=621)",
            "  • 37% primarily internal · 10% primarily external · 53% pursuing both",
            "  • 78% hit content/data readiness issues; 42% cite missing clear owner as a failure mode",
            "• China: large enterprises push internal ops agents (finance, IT, supply chain) under data-localization rules",
            "  • Consumer-facing agents exist but high-impact autonomy triggers July 2026 agent-regulation obligations",
            "• European Union: GDPR + AI Act push human-in-the-loop and DPIA before open-web autonomous agents",
            "  • Customer-service agents expand carefully; back-office automation remains the safer ROI path",
            "• Nuance vs Jan prediction: \"limited B2B/B2C\" is directionally right, but hybrid programs are now majority in US survey",
        ],
    },
    {
        "number": 12,
        "raw_lines": [
            "P8 — More CVEs for the Agentic Ecosystem",
            "Prediction: more CVEs for agent frameworks, browser/CUA agents, and vibe-coding tools — treated like classic vulns.",
            "• Verdict: Confirmed — 2026 CVE stream for agent stacks is sustained and severe",
            "• United States / global NVD:",
            "  • LangChain path traversal / sandbox escape — CVE-2026-55443 (fixed in 1.3.9; NVD Jun 2026)",
            "  • MCP Python SDK WebSocket Origin bypass — CVE-2026-59950 (HIGH); MCP Inspector RCE class continues",
            "  • Prior wave still active in ops: Claude Code RCE CVE-2025-59536; LangGrinch CVE-2025-68664; EchoLeak CVE-2025-32711",
            "• China: CNVD/CNNVD mirroring of agent-framework CVEs; domestic forks must patch MCP/tool hosts quickly",
            "• European Union: ENISA / national CERTs track agent supply-chain CVEs under product-security regimes",
            "  • Vendors increasingly issue advisories with CVSS and fixed versions — same severity culture as traditional software",
            "• Implication: SBOM + dependency pinning for LangChain/MCP/agent IDEs is now table stakes",
        ],
    },
    {
        "number": 13,
        "raw_lines": [
            "P9 — MAESTRO v2: Making It Practical",
            "Prediction: publish MAESTRO v2 with clear how-to guidance for vendor implementation.",
            "• Verdict: Confirmed — CSA released MAESTRO v2 on 2026-06-22",
            "• What shipped: expansion from 7 → 10 layers across three operational domains",
            "  • Domains: Infrastructure/Intelligence/Knowledge · Environment/Execution · Agency/Governance/Accountability",
            "  • Horizontal Trust Control Plane: governance, safety, monitoring, identity",
            "• Aligned with CSA AI Agent Reference Architecture + Agentic Control Plane / Agentic Trust Framework papers (same day)",
            "• United States: skills, playbooks, and CI tooling encode L1–L10 threat IDs for assessments",
            "• China / EU: v2 used as a practical bridge from architecture → controls (AICM) → regulatory evidence packs",
            "• Artifact: https://cloudsecurityalliance.org/artifacts/maestro-v2",
        ],
    },
    {
        "number": 14,
        "raw_lines": [
            "P10 — Official Release of OWASP AIVSS v1",
            "Prediction: publish AIVSS v1 at aivss.owasp.org as the definitive agentic scoring standard.",
            "• Verdict: In progress — on the stated 2026 path; v1.0 not final as of 2026-09-27",
            "• Milestone delivered: AIVSS Scoring System for OWASP Agentic AI Core Security Risks v0.8 (2026-03-19)",
            "  • Co-publication with AIUC-1, OWASP AI Exchange, Citizen Development Top 10",
            "  • Interactive AIUC-1 crosswalk live on aivss.owasp.org",
            "• Public review for v1.0 opened 2026-04-26; closes 2026-10-01; v1.0 slated before end of 2026",
            "• United States: RSAC 2026 sessions on measuring agentic risk with AIVSS; enterprise pilots on v0.8 scoring",
            "• China / EU: mappings to MAESTRO layers and AIUC-1 used in multinational risk programs ahead of v1 freeze",
            "• Status vs prediction: substance is live; \"official v1\" remains a Q4 2026 deliverable",
        ],
    },
    {
        "number": 15,
        "raw_lines": [
            "Regional Pattern — United States · China · European Union",
            "| Theme | United States | China | European Union |",
            "|---|---|---|---|",
            "| RSI / self-improve | Lab evidence (AIDE²) | Regulate frontier agents | Research > open deploy |",
            "| Agency metrics | AgencyBench, AAS | Task/tool KPIs + filing | Autonomy as risk object |",
            "| Risk mgmt | NIST RMF + AICM + AIVSS | Agent-specific law (Jul) | AI Act + AICM controls |",
            "| Vibe-code risk | Large empirical studies | Fast adoption + scanners | CRA/NIS2 build gates |",
            "| Browser agents | AG-UI scale + drift bugs | Constrained catalogs | A2UI std + oversight |",
            "| Enterprise posture | Internal-first, 53% both | Internal ops under localization | HITL before open web |",
            "| CVE culture | NVD-tracked agent CVEs | CNVD mirror + patch | CERT + product security |",
        ],
    },
    {
        "number": 16,
        "raw_lines": [
            "What Remains Open for Q4 2026",
            "• AIVSS v1.0: finish public review (closes 2026-10-01) and publish the frozen standard",
            "• Shared MAESTRO security leaderboards: move from playbooks/scanners to comparable public benchmarks",
            "• Browser-agent reliability: AG-UI sequence/resync defaults; A2UI v1.0 ratification and broader renderers",
            "• RSI beyond Level-1: independent replication of AIDE²; governance for self-modifying production agents",
            "• Open-web B2C agents: still the cautious minority — watch whether dual programs tip to external-primary",
            "• Vibe-coding controls: whether shift-left gates cut the 91% vulnerability baseline in production fleets",
        ],
    },
    {
        "number": 17,
        "raw_lines": [
            "Primary Sources (selected)",
            "• CSA predictions (2026-01-16): https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
            "• AIDE² RSI: weco.ai blog (2026-07-14); arXiv:2609.26457",
            "• AgencyBench: ACL 2026; Autonomous Agency Scale arXiv HTML 2607.17947",
            "• MAESTRO v2 artifact (2026-06-22): cloudsecurityalliance.org/artifacts/maestro-v2",
            "• CSA AICM v1.1 (2026-07-14 blog); China agent regulation CSA Labs note (enforcement 2026-07-15)",
            "• Vibe coding study: arXiv:2606.23130; OX Security / Georgia Tech CVE radar summaries",
            "• AG-UI production drift analyses (2026); A2UI a2ui.org v0.9.1 / v1.0-rc",
            "• Contentstack Agentic Enterprise Report 2026; NVD CVE-2026-55443; AIVSS aivss.owasp.org v0.8 + review",
        ],
    },
    {
        "number": 18,
        "raw_lines": [
            "Closing — Build Agentic AI Securely",
            "• 8 of 10 predictions are Confirmed, Mostly confirmed, or On track as of 2026-09-27",
            "• Two remain open by design: broader MAESTRO benchmark adoption (Partial) and AIVSS v1 freeze (In progress)",
            "• Security and risk management moved from slideware to CVEs, controls matrices, and regulatory filing",
            "• Next checkpoints: AIVSS v1 publication · A2UI v1.0 · independent RSI replication · open-web agent trust",
            "• Continue the conversation: kenhuangus.substack.com · aivss.owasp.org · CSA AI Safety working groups",
            "• Contact: DistributedApps.ai · LinkedIn linkedin.com/in/kenhuang8",
        ],
    },
]

SLIDES_ZH = {
    "1": [
        "2026 智能体 AI 十大预测",
        "年中成绩单 — 截至 2026 年 9 月 27 日",
        "原始预测：云安全联盟（CSA），2026 年 1 月 16 日",
        "作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "旧金山大学（USF）客座教授：https://www.usfca.edu/faculty/ken-huang",
        "区域视角：美国 · 中国 · 欧盟",
        "CSA 原文：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "来源：CSA 文章与 Substack；研究截止日期 2026-09-27",
    ],
    "2": [
        "CSA 原文发布 — 2026 年 1 月 16 日",
        "• 文章：My Top 10 Predictions for Agentic AI in 2026",
        "• 作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
        "• 发布方：云安全联盟（Industry Insights）",
        "• 打开原文：",
        "• https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• 下方截图展示已发布的全部 10 条预测",
        "IMG:assets/images/csa-top-10-predictions-2026.png",
    ],
    "3": [
        "关于本成绩单",
        "• 出处：Ken Huang —《My Top 10 Predictions for Agentic AI in 2026》（CSA，2026-01-16）",
        "• CSA 链接：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• 方法：将每条预测映射到截至 2026-09-27 的美、中、欧公开证据",
        "• 证据类型：同行评议论文、CVE/NVD、CSA/OWASP/NIST 产物、企业调研、监管文件",
        "• 判定等级：已证实 · 基本证实 · 进展符合预期 · 部分兑现 · 进行中（指向年末）",
        "• 不是改写预测，而是年中审计：已发生什么 vs 仍未关闭什么",
    ],
    "4": [
        "成绩单一览 — 2026 年 9 月 27 日",
        "| # | 预测 | 判定 |",
        "|---|---|---|",
        "| 1 | 自我改进 / RSI 智能体 | 进展符合预期（研究已证实） |",
        "| 2 | 自主性 > 智力 | 进展符合预期 |",
        "| 3 | 基于 MAESTRO 的安全基准 | 部分兑现 → 符合预期 |",
        "| 4 | 智能体风险管理成焦点 | 已证实 |",
        "| 5 | 「氛围编程」安全后遗症 | 已证实 |",
        "| 6 | 浏览器智能体仍艰难 | 进展符合预期 |",
        "| 7 | 企业：内部优先部署 | 基本证实 |",
        "| 8 | 智能体生态更多 CVE | 已证实 |",
        "| 9 | MAESTRO v2 实用版发布 | 已证实（2026-06-22） |",
        "| 10 | OWASP AIVSS v1 正式发布 | 进行中（公开评审中） |",
    ],
    "5": [
        "预测 1 — 自我改进的智能体 AI 系统",
        "预测（2026 年 1 月）：告别静态智能体；自我改进研究与部分落地增加。",
        "• 判定：进展符合预期 — 一级递归自我改进（RSI）已在研究中演示；生产部署仍受限",
        "• 美国：Weco AI AIDE²（2026-07-14）— 8 天外环、7 次连续 harness 升级；arXiv:2609.26457",
        "  • AIDE85 在固定美元预算下于留出基准上超过两年手调的 AIDE-human",
        "  • GPU 内核任务奖励作弊约 63%→34%；宣称一级净正 RSI，非点火级",
        "• 中国：前沿智能体监管自 2026-07-15 进入执法（网信办等联合实施意见）",
        "  • 分级授权、可审计决策日志、高影响自主智能体的人类否决",
        "  • 自我修改环比美国开放实验室面临更强备案与测试义务",
        "• 欧盟：AI 法案高风险义务与人类监督延缓开放网络上的 RSI 部署",
        "  • 研究持续；生产级自我改写智能体在受控沙箱外仍罕见",
    ],
    "6": [
        "预测 2 — 自主性 > 智力",
        "预测：业界不再痴迷原始智力分数；自主性（规划、工具、持续目标）成为主指标。",
        "• 判定：进展符合预期 — 2026 年自主性度量与基准大量出现",
        "• 美国：AgencyBench（ACL 2026）— 32 场景，约 90 次工具调用 / 100 万 token / 数小时运行",
        "  • 闭源 48.4% vs 开源 32.1%；强调工具使用、自我纠错与资源效率",
        "  • 自主代理量表（AAS，2026 年 7 月）区分 Active / Ambient，并用 Idle-Gap 检验",
        "• 中国：产品竞争更看重任务完成与工具链，而非 MMLU 类榜单",
        "  • 监管将智能体决策权限视为控制对象，而非模型智商",
        "• 欧盟：合规与监督讨论跟踪自主等级与影响，而非原始能力分",
        "  • 学术工作（如 arXiv:2602.22519）将自主性与智力区分为不同构念",
    ],
    "7": [
        "预测 3 — 基于 MAESTRO 的新安全基准",
        "预测：基于 MAESTRO 威胁建模的智能体安全基准得到采用。",
        "• 判定：部分兑现 → 符合预期 — MAESTRO 已工程化；统一基准套件仍在成熟",
        "• 美国：CSA MAESTRO + ATLAS 组合实践；TITO CI/CD 威胁建模（CSA，2026-02-11）",
        "  • 智能体红队指南按 MAESTRO 层映射测试；STAR / AIUC-1 保障路径出现",
        "• 中国：CSA 指南引用 MAESTRO，作为向监管证明智能体边界被工程化的方式",
        "  • 国内评估日益要求分层威胁覆盖，而非仅提示词测试",
        "• 欧盟：经 CSA AICM 映射到 AI 法案 / ISO 42001；MAESTRO 作为威胁生成前端",
        "  • 缺口：尚无全球统一的「MAESTRO 分数」— 框架与扫描器领先于公共排行榜",
    ],
    "8": [
        "预测 4 — 智能体 AI 风险管理成为焦点",
        "预测：组织对齐 NIST AI RMF、CSA AICM 与 OWASP AIVSS 以管理智能体风险。",
        "• 判定：已证实 — 风险管理是 2026 年智能体治理的中心议题",
        "• 美国：NIST AI RMF 仍是风险主轴；CSA AICM v1.1（2026 年 6/7 月）增加 AIUC-1 映射",
        "  • 五眼联盟 / CISA 对智能体服务的审慎采用指南（2026 年 5 月）；RSAC 2026 AIVSS 专场",
        "• 中国：国家级 AI 智能体专项监管类别自 2026-07-15 可执行",
        "  • 备案、测试、分级决策权限，以及对 2/3 级决策的强制人类否决",
        "• 欧盟：AI 法案对高风险系统的透明度、风险评估与人类监督义务",
        "  • AICM v1.1 补充法案本身未规定的运行安全控制",
        "• 交叉映射：AIVSS ↔ AIUC-1 ↔ MAESTRO ↔ OWASP 智能体 Top 10 已发布并进入企业项目",
    ],
    "9": [
        "预测 5 — 「氛围编程」安全后遗症",
        "预测：氛围编程加速交付；自然语言生成代码的非确定性加剧 DevSecOps 风险。",
        "• 判定：已证实 — 实证研究显示氛围编程应用不安全是常态",
        "• 美国：arXiv:2606.23130（v3，2026 年 9 月）— 9041 个开源应用；审计 200 个已部署应用 → 1186 个漏洞",
        "  • 91.0% 被审计应用至少 1 个漏洞；65.77% 为严重/高危（访问控制、注入、认证）",
        "  • 佐治亚理工 Vibe Security Radar：截至 2026 年 3 月可追溯到 AI 编程工具的 CVE 达 74 个",
        "  • 工具 CVE：Cursor MCP（CVE-2025-54135）、Claude Code（CVE-2025-55284 / CVE-2025-59536 类）",
        "• 中国：初创快速采用 AI 编程助手；同样失败模式（密钥、IDOR、缺失认证）",
        "  • 国内 AppSec 厂商将 AI 代码扫描纳入 CI；监管关注供应链泄露",
        "• 欧盟：NIS2 / CRA 压力推动对 AI 生成依赖的 SBOM 与构建期门禁",
        "  • 针对 AI 引入 CWE 的左移 DAST 与「修复或豁免」策略进入企业手册",
    ],
    "10": [
        "预测 6 — 浏览器智能体的艰难之路",
        "预测：在 AG-UI / A2UI 互操作与合同缺口修复前，浏览器智能体将继续艰难。",
        "• 判定：进展符合预期 — 协议前进；生产可靠性仍脆弱",
        "• 美国：AG-UI 广泛集成（CopilotKit 等），但 STATE_DELTA 静默漂移已有记录（2026 年中）",
        "  • ag-ui-protocol/ag-ui 上报告主线程卡顿（structuredClone 超 20 秒）与重连缺口",
        "  • 计算机使用 / GUI 智能体在反复提示注入下仍失败（Anthropic 测量：残留风险）",
        "• 中国：生产力应用中浏览器/桌面智能体流行；可靠性与权限体验仍是痛点",
        "  • 消费级产品更偏好受约束动作目录，而非开放 DOM 控制",
        "• 欧盟：A2UI（Google 与社区）生产版 v0.9.1；v1.0 为候选（2026 年 6 月更新）",
        "  • 声明式 UI 目录比任意代码更安全；仍需有序投递以免状态损坏",
        "• 结论：标准已在；「广泛可靠采用」尚未成为默认生产姿态",
    ],
    "11": [
        "预测 7 — 企业部署：内部优先",
        "预测：内部智能体部署显著扩大；因谨慎，面向开放网络的 B2B/B2C 仍有限。",
        "• 判定：基本证实 — 内部仍优先；内部+外部双线项目在增长",
        "• 美国：Contentstack 智能体企业报告（2026 年 5 月，n=621）",
        "  • 37% 以内部为主 · 10% 以外部为主 · 53% 同时推进",
        "  • 78% 遭遇内容/数据就绪问题；42% 将缺少明确负责人列为失败模式",
        "• 中国：大型企业在数据本地化规则下推进内部运营智能体（财务、IT、供应链）",
        "  • 消费向智能体存在，但高影响自主性触发 2026 年 7 月智能体监管义务",
        "• 欧盟：GDPR + AI 法案推动在开放网络自主智能体前完成 HITL 与 DPIA",
        "  • 客服智能体谨慎扩展；后台自动化仍是更稳妥的 ROI 路径",
        "• 相对 1 月预测的细微差别：「有限 B2B/B2C」方向正确，但美国调研中混合项目已成多数",
    ],
    "12": [
        "预测 8 — 智能体生态出现更多 CVE",
        "预测：智能体框架、浏览器/计算机使用智能体与氛围编程工具将出现更多 CVE，并按传统软件严重度对待。",
        "• 判定：已证实 — 2026 年智能体栈 CVE 持续且严重",
        "• 美国 / 全球 NVD：",
        "  • LangChain 路径穿越 / 沙箱逃逸 — CVE-2026-55443（1.3.9 修复；NVD 2026 年 6 月）",
        "  • MCP Python SDK WebSocket Origin 绕过 — CVE-2026-59950（高危）；MCP Inspector RCE 类持续",
        "  • 前一波仍在运维中：Claude Code RCE CVE-2025-59536；LangGrinch CVE-2025-68664；EchoLeak CVE-2025-32711",
        "• 中国：CNVD/CNNVD 镜像智能体框架 CVE；国内分支需快速修补 MCP/工具主机",
        "• 欧盟：ENISA / 国家 CERT 在产品安全制度下跟踪智能体供应链 CVE",
        "  • 厂商日益发布带 CVSS 与修复版本的公告 — 与传统软件同等严重度文化",
        "• 含义：对 LangChain/MCP/智能体 IDE 的 SBOM + 依赖锁定已成为基本要求",
    ],
    "13": [
        "预测 9 — MAESTRO v2：使之可落地",
        "预测：发布侧重实用说明的 MAESTRO v2，指导厂商如何落地。",
        "• 判定：已证实 — CSA 于 2026-06-22 发布 MAESTRO v2",
        "• 交付内容：由 7 层扩展为 10 层，分属三个运营域",
        "  • 域：基础设施/智能/知识 · 环境/执行 · 自主性/治理/问责",
        "  • 横向信任控制平面：治理、安全、监控、身份",
        "• 同日对齐 CSA AI 智能体参考架构 + 智能体控制平面 / 智能体信任框架论文",
        "• 美国：技能、手册与 CI 工具将 L1–L10 威胁 ID 编码进评估",
        "• 中国 / 欧盟：v2 作为从架构 → 控制（AICM）→ 监管证据包的实用桥梁",
        "• 产物：https://cloudsecurityalliance.org/artifacts/maestro-v2",
    ],
    "14": [
        "预测 10 — OWASP AIVSS v1 正式发布",
        "预测：在 aivss.owasp.org 发布 AIVSS v1，作为智能体评分的权威标准。",
        "• 判定：进行中 — 仍在 2026 年路径上；截至 2026-09-27 v1.0 尚未定稿",
        "• 已交付里程碑：面向 OWASP 智能体核心安全风险的 AIVSS 评分系统 v0.8（2026-03-19）",
        "  • 与 AIUC-1、OWASP AI Exchange、公民开发 Top 10 联合发布",
        "  • AIUC-1 交互式对照表已上线 aivss.owasp.org",
        "• v1.0 公开评审于 2026-04-26 开启；2026-10-01 截止；v1.0 计划 2026 年底前发布",
        "• 美国：RSAC 2026 以 AIVSS 度量智能体风险；企业在 v0.8 上试点评分",
        "• 中国 / 欧盟：在 v1 冻结前，跨国风险项目已使用到 MAESTRO 层与 AIUC-1 的映射",
        "• 相对预测：实质内容已可用；「正式 v1」仍是 2026 年第四季度交付物",
    ],
    "15": [
        "区域格局 — 美国 · 中国 · 欧盟",
        "| 主题 | 美国 | 中国 | 欧盟 |",
        "|---|---|---|---|",
        "| RSI / 自我改进 | 实验室证据（AIDE²） | 监管前沿智能体 | 研究 > 开放部署 |",
        "| 自主性度量 | AgencyBench、AAS | 任务/工具 KPI + 备案 | 自主性即风险对象 |",
        "| 风险管理 | NIST RMF + AICM + AIVSS | 智能体专项法（7 月） | AI 法案 + AICM 控制 |",
        "| 氛围编程风险 | 大型实证研究 | 快速采用 + 扫描 | CRA/NIS2 构建门禁 |",
        "| 浏览器智能体 | AG-UI 规模 + 漂移缺陷 | 受约束目录 | A2UI 标准 + 监督 |",
        "| 企业姿态 | 内部优先，53% 双线 | 本地化下的内部运营 | 开放网络前 HITL |",
        "| CVE 文化 | NVD 跟踪智能体 CVE | CNVD 镜像 + 补丁 | CERT + 产品安全 |",
    ],
    "16": [
        "2026 年第四季度仍待关闭的事项",
        "• AIVSS v1.0：完成公开评审（2026-10-01 截止）并发布冻结标准",
        "• 共享 MAESTRO 安全排行榜：从手册/扫描器走向可比较的公共基准",
        "• 浏览器智能体可靠性：AG-UI 默认序号/重同步；A2UI v1.0 批准与更广渲染器",
        "• 超越一级的 RSI：独立复现 AIDE²；自我修改生产智能体的治理",
        "• 开放网络 B2C 智能体：仍是谨慎少数 — 观察双线项目是否转向外部优先",
        "• 氛围编程控制：左移门禁能否压低生产环境中 91% 的漏洞基线",
    ],
    "17": [
        "主要来源（节选）",
        "• CSA 预测（2026-01-16）：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
        "• AIDE² RSI：weco.ai 博客（2026-07-14）；arXiv:2609.26457",
        "• AgencyBench：ACL 2026；自主代理量表 arXiv HTML 2607.17947",
        "• MAESTRO v2 产物（2026-06-22）：cloudsecurityalliance.org/artifacts/maestro-v2",
        "• CSA AICM v1.1（2026-07-14 博客）；中国智能体监管 CSA Labs 说明（执法 2026-07-15）",
        "• 氛围编程研究：arXiv:2606.23130；OX Security / 佐治亚理工 CVE 雷达摘要",
        "• AG-UI 生产漂移分析（2026）；A2UI a2ui.org v0.9.1 / v1.0-rc",
        "• Contentstack 2026 智能体企业报告；NVD CVE-2026-55443；AIVSS aivss.owasp.org v0.8 + 评审",
    ],
    "18": [
        "结语 — 安全地构建智能体 AI",
        "• 截至 2026-09-27，10 条预测中有 8 条为已证实、基本证实或进展符合预期",
        "• 两条按设计仍开放：更广的 MAESTRO 基准采用（部分）与 AIVSS v1 冻结（进行中）",
        "• 安全与风险管理已从幻灯片走向 CVE、控制矩阵与监管备案",
        "• 下一检查点：AIVSS v1 发布 · A2UI v1.0 · 独立 RSI 复现 · 开放网络智能体信任",
        "• 继续对话：kenhuangus.substack.com · aivss.owasp.org · CSA AI 安全工作组",
        "• 联系：DistributedApps.ai · LinkedIn linkedin.com/in/kenhuang8",
    ],
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
                  ? '原始预测发表于云安全联盟（2026-01-16）。本成绩单审计截至 2026-09-27 在美国、中国与欧盟的公开证据兑现情况。'
                  : 'Original predictions published by the Cloud Security Alliance (2026-01-16): https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026 — this scorecard audits US, China, and EU evidence through 2026-09-27.'}
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
