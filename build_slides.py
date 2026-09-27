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
            "| # | Trend | Invest / avoid snapshot |",
            "|---|---|---|",
            "| 1 | RSI | Eval + governed self-mod + ML-ops RSI / avoid public AGI self-rewrite |",
            "| 2 | Agency | Procurement scores + long-horizon agents / avoid chat labeled as agents |",
            "| 3 | MAESTRO bench | CI checks + red-team sub + assurance reports / avoid PDF badges |",
            "| 4 | Risk mgmt | Agent GRC + runtime allow-deny + insurer workbench / avoid doc-only GRC |",
            "| 5 | Vibe coding | AppSec + secure builders + remediation / avoid demo-first builders |",
            "| 6 | Browser agents | Protocol reliability + action catalogs + CUA controls / avoid pay-send bots |",
            "| 7 | Internal-first | Internal platforms + KPI back-office + controlled B2B / avoid premature B2C |",
            "| 8 | Agentic CVEs | SBOM firewall + MCP gateway + patchable vendors / avoid unauth MCP |",
            "| 9 | MAESTRO v2 | Implementation software + trust plane + listed training / avoid renamed IAM |",
            "| 10 | AIVSS v1 | Scoring + crosswalk + release gates / avoid proprietary unmapped scores |"
        ]
    },
    {
        "number": 6,
        "raw_lines": [
            "P1 — Self-Improving / RSI Agents — Investor theses",
            "Evidence so far: AIDE² is Level-1 RSI (net-positive R&D under a fixed budget); production still needs hidden evals and governance.",
            "• Thesis 1 — Evaluation infrastructure: hidden-eval harnesses, reward-hacking detectors, and RSI regression suites sold to frontier labs and AI R&D teams",
            "• Thesis 2 — Governed self-modification: agents may rewrite tools or prompts only after policy approval, audit logs, and a human stop (US labs; China filing plus human override)",
            "• Thesis 3 — Vertical RSI for ML ops: auto-research agents that improve a training or inference pipeline under a fixed dollar budget; buyer is the AI infrastructure team",
            "• Pitfall — Treating Level-1 (faster than a human baseline on a fixed budget) as Level-2 (the improver gets better at improving); Level-2 is not shown, and reward hacking is common",
            "• Do not invest — Public-web apps marketed as self-improving AGI that rewrite their own code with no hidden eval and no dollar cap"
        ]
    },
    {
        "number": 7,
        "raw_lines": [
            "P2 — Agency > Intelligence — Investor theses",
            "Evidence so far: AgencyBench (multi-hour tool tasks, ACL 2026) and AAS (Active vs Ambient bands).",
            "• Thesis 1 — Agency scores for procurement: plan, tool-use, and persistence scores sold into model selection and vendor RFPs",
            "• Thesis 2 — Long-horizon task agents: software that finishes multi-hour tool workflows and self-corrects; buyer is ops or engineering, not a chat leaderboard",
            "• Thesis 3 — Scoped idle-period agents: enterprise ops agents that act between user prompts only inside a written permission boundary (high AAS Ambient scores remain uncommon)",
            "• Pitfall — Paying for MMLU or IQ-score wrappers while buyers already score tools, persistence, and correction",
            "• Do not invest — Chat products labeled as agents with no cross-session goal, no tool contract, and no multi-hour task completion"
        ]
    },
    {
        "number": 8,
        "raw_lines": [
            "P3 — MAESTRO Security Benchmarks — Investor theses",
            "Evidence so far: MAESTRO is in playbooks and CI; shared public leaderboards are still maturing.",
            "• Thesis 1 — CI layer checks: scanners that map a pull request to MAESTRO layers and block high-risk agent merges; buyer is the platform security team",
            "• Thesis 2 — Agent red-team subscription: recurring attack packs mapped to layers, plus a MITRE ATLAS crosswalk, sold to banks, SaaS, and AI platforms",
            "• Thesis 3 — Assurance reports: third-party reports that package MAESTRO layer evidence for procurement and regulators (same buyers as CSA STAR and AIUC-1)",
            "• Pitfall — Paying for another static PDF checklist; buyers pay for a CI block and an evidence pack",
            "• Do not invest — \"MAESTRO-compliant\" badges with no layer tests, no ATLAS mapping, and no scanner output"
        ]
    },
    {
        "number": 9,
        "raw_lines": [
            "P4 — Agentic Risk Management — Investor theses",
            "Evidence so far: AICM v1.1, NIST AI RMF, China agent regulation (enforceable 2026-07-15), EU AI Act — risk and compliance teams are the buyer.",
            "• Thesis 1 — Agent GRC: one control catalog and questionnaire mapped to NIST, AICM, the EU AI Act, and China filing, exported as an auditor pack for the compliance team",
            "• Thesis 2 — Runtime risk engines: allow or deny on tool calls, autonomy tier, and human override, priced per agent action",
            "• Thesis 3 — Insurance underwriting workbenches: carrier tools that turn an AIUC-1 control result and an AIVSS score into a premium and an exclusion",
            "• Pitfall — US-only GRC that cannot export EU AI Act or China filing evidence; multinational buyers will leave",
            "• Do not invest — Policy-document generators with no runtime allow or deny on tool calls"
        ]
    },
    {
        "number": 10,
        "raw_lines": [
            "P5 — Vibe Coding Security Hangover — Investor theses",
            "Evidence so far: about 91% of audited vibe-coded apps had vulnerabilities (arXiv:2606.23130); tool CVEs and exposed secrets continue to increase.",
            "• Thesis 1 — AppSec for generated code: pre-merge SAST/DAST sold to AppSec teams, tuned for flaws these apps ship (broken access control, IDOR, hardcoded secrets)",
            "• Thesis 2 — Secure vibe platforms: IDEs and app builders with default authentication, a secrets store, and a fix-or-waive gate before deploy",
            "• Thesis 3 — Managed remediation: a service that patches those CWE classes and attaches a proof of exploitability before merge",
            "• Pitfall — Generic SAST renamed \"AI security\" that does not test broken access control, IDOR, or hardcoded secrets",
            "• Do not invest — Vibe builders that optimize demo speed and ship debug CORS, hardcoded keys, and APIs with no authentication"
        ]
    },
    {
        "number": 11,
        "raw_lines": [
            "P6 — Browser Agents Struggle — Investor theses",
            "Evidence so far: AG-UI drift and performance issues; A2UI at v0.9.1 / v1.0-rc; computer-use is still exposed to prompt injection.",
            "• Thesis 1 — Protocol reliability: sequence numbers, resync, persistent session state, and limits on full-UI snapshot size and frequency for AG-UI / A2UI production stacks",
            "• Thesis 2 — Approved action catalogs: browser and desktop agents that call only an approved action list, not an open DOM, sold as an enterprise RPA replacement",
            "• Thesis 3 — Computer-use controls: injection detection, session isolation, and human approval for payment and email-send clicks",
            "• Pitfall — Funding open-DOM computer-use as production-ready before resync and injection checks exist",
            "• Do not invest — Consumer browser agents that can pay or send email with no human approval and no session isolation"
        ]
    },
    {
        "number": 12,
        "raw_lines": [
            "P7 — Enterprise Internal-First — Investor theses",
            "Evidence so far: Contentstack 2026 — 37% internal-primary, 10% external-primary, 53% both; 78% of leaders with a production program hit content or data rework.",
            "• Thesis 1 — Internal agent platforms: secure ERP, ITSM, and finance connectors plus content and data pipelines; buyer is central IT",
            "• Thesis 2 — Back-office workflow agents: approvals and routing for ops leaders who track a finance-audited KPI (Contentstack: 94% of KPI-measured internal programs reported a positive return)",
            "• Thesis 3 — Controlled B2B release: software that publishes an internal agent to a business customer only with a DPIA, human approval, and tenant isolation",
            "• Pitfall — Deploying agents before content and data are ready; that rework is what delayed production programs in the same survey",
            "• Do not invest — Public-web consumer agents funded before an internal workflow has a KPI finance can audit"
        ]
    },
    {
        "number": 13,
        "raw_lines": [
            "P8 — Agentic Ecosystem CVEs — Investor theses",
            "Evidence so far: LangChain CVE-2026-55443, MCP CVE-2026-59950, and coding-agent RCEs are scored like other software CVEs.",
            "• Thesis 1 — Agent SBOM and dependency firewall: version-pin and patch LangChain, MCP SDKs, and IDE plugins, and stream CVEs to the security operations team",
            "• Thesis 2 — Secure MCP gateways: Host and Origin authentication, least-privilege tool scopes, and sandbox-escape controls, sold as infrastructure",
            "• Thesis 3 — Framework vendors that pass procurement: publish time-to-patch, CVSS, and signed releases; buyer is enterprise security",
            "• Pitfall — Assuming the model vendor covers framework and MCP CVEs; the vulnerable code is in the application dependency tree",
            "• Do not invest — MCP servers with no authentication, tool hosts that use one token for every tool, and agent stacks with no SBOM or version pin"
        ]
    },
    {
        "number": 14,
        "raw_lines": [
            "P9 — MAESTRO v2 Practical Adoption — Investor theses",
            "Evidence so far: CSA MAESTRO v2 shipped 2026-06-22 (10 layers + Trust Control Plane).",
            "• Thesis 1 — Implementation software: layer templates, L1–L10 threat IDs, and a matrix of who owns each layer, sold to the security engineering team",
            "• Thesis 2 — Trust Control Plane products: agent identity, action monitoring, and an interrupt path mapped to v2 domains; buyer is the agent-platform owner",
            "• Thesis 3 — Training and certification: paid courses that security hiring managers can list for agent-security roles",
            "• Pitfall — Workshops that never put L1–L10 checks into a tool the customer runs",
            "• Do not invest — Products that rename IAM or observability \"trust plane\" and omit agent identity and an interrupt path"
        ]
    },
    {
        "number": 15,
        "raw_lines": [
            "P10 — OWASP AIVSS v1 — Investor theses",
            "Evidence so far: v0.8 live; v1.0 public review through 2026-10-01; freeze targeted before year-end.",
            "• Thesis 1 — Scoring engines: products that compute AIVSS for an agent release and send the score to ticketing and SSVC priority queues",
            "• Thesis 2 — Crosswalk software: one mapping across AIVSS, AIUC-1, MAESTRO, and OWASP Agentic Top 10 for multinational security buyers",
            "• Thesis 3 — Release gates: after the v1 freeze, block a release when the AIVSS score crosses a set threshold; buyer is the release owner in US, EU, and China programs",
            "• Pitfall — Shipping a scoring interface before the v1 freeze; method changes force rework, and buyers will not trust the number",
            "• Do not invest — Proprietary \"AI risk scores\" that, after v1 is the published standard, still refuse a mapping to AIVSS, AIUC-1, and MAESTRO"
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
        "| # | 趋势 | 宜投 / 不宜投速览 |",
        "|---|---|---|",
        "| 1 | RSI | 评测 + 受控自改 + ML 运维 RSI / 不宜投公网自称 AGI 自改 |",
        "| 2 | 自主性 | 采购分数 + 长时程智能体 / 不宜投聊天冒充智能体 |",
        "| 3 | MAESTRO 基准 | CI 检查 + 红队订阅 + 鉴证报告 / 不宜投 PDF 徽章 |",
        "| 4 | 风险管理 | 智能体 GRC + 运行时放行拒绝 + 核保工作台 / 不宜投纯文档 GRC |",
        "| 5 | Vibe coding | 应用安全 + 安全构建器 + 托管修复 / 不宜投演示优先构建器 |",
        "| 6 | 浏览器智能体 | 协议可靠 + 动作目录 + 计算机操作控制 / 不宜投可支付发信机器人 |",
        "| 7 | 内部优先 | 内部平台 + KPI 后台 + 受控 B2B / 不宜投过早消费级 |",
        "| 8 | 智能体 CVE | SBOM 防火墙 + MCP 网关 + 能过采购厂商 / 不宜投无认证 MCP |",
        "| 9 | MAESTRO v2 | 落地软件 + 信任平面 + 可写进 JD 的培训 / 不宜投改名 IAM |",
        "| 10 | AIVSS v1 | 评分 + 对照 + 发布门禁 / 不宜投拒绝对照的专有分 |"
    ],
    "6": [
        "预测 1 — 自我改进 / RSI 智能体 — 投资论点",
        "现有证据：AIDE² 属于一级 RSI（固定预算下研发效率高于人工基线）；生产仍需要隐藏评测与治理。",
        "• 论点 1 — 评测基础设施：向前沿实验室和 AI 研发团队销售隐藏评测框架、奖励作弊检测和 RSI 回归测试套件",
        "• 论点 2 — 受控自我修改：智能体只有在策略审批、审计日志和人工急停之后才能改写工具或提示词（美国实验室；中国备案加人工接管）",
        "• 论点 3 — ML 运维的垂直 RSI：在固定美元预算内改进训练或推理管线的自动研究智能体；买方是 AI 基础设施团队",
        "• 陷阱 — 把一级（固定预算下高于人工基线）当成二级（改进者自己变得更会改进）；二级尚未被实验证实，奖励作弊常见",
        "• 不宜投 — 面向公网、宣传「自我改进 AGI」、且在无隐藏评测、无美元上限下自行改代码的应用"
    ],
    "7": [
        "预测 2 — 自主性 > 智力 — 投资论点",
        "现有证据：AgencyBench（数小时工具任务，ACL 2026）与 AAS（任务执行带 vs 空闲带）。",
        "• 论点 1 — 用于采购的自主性分数：把规划、工具使用和持续执行分数卖进模型选型和供应商招标",
        "• 论点 2 — 长时程任务智能体：能完成数小时工具流程并自我纠错的软件；买方是运营或工程团队，不是聊天榜单",
        "• 论点 3 — 限定空闲期智能体：只在书面权限范围内、于两次用户指令之间行动的企业运维智能体（AAS 空闲带高分仍少见）",
        "• 陷阱 — 为包装 MMLU 或智商分数的创业公司付钱，而买方已经在为工具、持续执行和纠错打分",
        "• 不宜投 — 自称智能体、但没有跨会话目标、没有工具调用合同、也不能完成数小时任务的聊天产品"
    ],
    "8": [
        "预测 3 — MAESTRO 安全基准 — 投资论点",
        "现有证据：MAESTRO 已进入操作手册和 CI；共享的公开排行榜仍在形成。",
        "• 论点 1 — CI 分层检查：把合并请求映射到 MAESTRO 各层并阻断高风险智能体合并的扫描器；买方是平台安全团队",
        "• 论点 2 — 智能体红队订阅：按层编写的周期性攻击包，附 MITRE ATLAS 对照，卖给银行、SaaS 和 AI 平台",
        "• 论点 3 — 鉴证报告：把 MAESTRO 分层证据打包给采购和监管机构的第三方报告（买方与 CSA STAR、AIUC-1 相同）",
        "• 陷阱 — 再为一份不能执行的静态 PDF 清单付钱；买方付钱买的是 CI 阻断和证据包",
        "• 不宜投 — 没有分层测试、没有 ATLAS 对照、没有扫描输出的「MAESTRO 合规」徽章"
    ],
    "9": [
        "预测 4 — 智能体风险管理 — 投资论点",
        "现有证据：AICM v1.1、NIST AI RMF、中国智能体监管（2026-07-15 起施行）、欧盟 AI 法案 — 风险与合规团队是买方。",
        "• 论点 1 — 智能体 GRC：一套控制目录和问卷，一次映射 NIST、AICM、欧盟 AI 法案和中国备案，并导出给合规团队的审计包",
        "• 论点 2 — 运行时风险引擎：对工具调用、自主等级和人工接管做允许或拒绝，按智能体动作收费",
        "• 论点 3 — 保险核保工作台：把 AIUC-1 控制结果和 AIVSS 分数转成保费与除外责任的承保工具",
        "• 陷阱 — 只能覆盖美国、导不出欧盟 AI 法案或中国备案证据的 GRC；跨国买方会流失",
        "• 不宜投 — 只会生成制度文档、不能在工具调用上做允许或拒绝的产品"
    ],
    "10": [
        "预测 5 — Vibe Coding 安全后遗症 — 投资论点",
        "现有证据：被审计的 vibe coding 应用约 91% 有漏洞（arXiv:2606.23130）；工具 CVE 和泄露的密钥在增加。",
        "• 论点 1 — 生成代码的应用安全：卖给应用安全团队的合并前 SAST/DAST，针对这些应用高频出现的缺陷（访问控制失效、IDOR、硬编码密钥）",
        "• 论点 2 — 安全的 vibe coding 平台：默认带认证、密钥库，以及部署前「修复或书面豁免」门禁的 IDE 和应用生成器",
        "• 论点 3 — 托管修复：修补上述 CWE 类别，并在合并前附上可利用性证明的服务",
        "• 陷阱 — 把通用 SAST 改名为「AI 安全」，却不检测访问控制失效、IDOR 或硬编码密钥",
        "• 不宜投 — 追求演示速度，并交付调试用 CORS、硬编码密钥和无认证 API 的 vibe coding 生成器"
    ],
    "11": [
        "预测 6 — 浏览器智能体仍难落地 — 投资论点",
        "现有证据：AG-UI 有状态漂移和性能问题；A2UI 处于 v0.9.1 / v1.0-rc；计算机操作仍易被提示注入。",
        "• 论点 1 — 协议可靠性：为 AG-UI / A2UI 生产系统提供消息序号、断线重同步、持久会话状态，并限制整页界面快照的大小和发送频率",
        "• 论点 2 — 已批准动作目录：只调用批准动作清单、不操作开放 DOM 的浏览器和桌面智能体，作为企业 RPA 替代品出售",
        "• 论点 3 — 计算机操作控制：注入检测、会话隔离，以及支付和发邮件点击前的人工审批",
        "• 陷阱 — 在重同步和注入检测尚未具备时，就把开放 DOM 的计算机操作当成可投产能力",
        "• 不宜投 — 可以支付或发邮件，但没有人工审批、也没有会话隔离的消费级浏览器智能体"
    ],
    "12": [
        "预测 7 — 企业内部优先 — 投资论点",
        "现有证据：Contentstack 2026 — 37% 以内部分为主、10% 以对外为主、53% 两者并行；已有生产项目的负责人中，78% 遇到内容或数据返工。",
        "• 论点 1 — 内部智能体平台：连接 ERP、ITSM 和财务系统的安全连接器，加上内容与数据管线；买方是中央 IT",
        "• 论点 2 — 后台流程智能体：面向已跟踪财务可审计 KPI 的运营负责人，做审批和路由（Contentstack：有 KPI 的内部项目中 94% 报告正收益）",
        "• 论点 3 — 受控的 B2B 发布：只有在 DPIA、人工审批和租户隔离齐备后，才把内部智能体开放给企业客户的软件",
        "• 陷阱 — 在内容和数据就绪之前部署智能体；同一调研里，生产项目会因此返工并推迟",
        "• 不宜投 — 内部流程还没有财务可审计的 KPI 之前就融资的公网消费级智能体"
    ],
    "13": [
        "预测 8 — 智能体生态 CVE — 投资论点",
        "现有证据：LangChain CVE-2026-55443、MCP CVE-2026-59950，以及编程智能体远程代码执行，已按普通软件 CVE 评级。",
        "• 论点 1 — 智能体 SBOM 与依赖防火墙：锁定并修补 LangChain、MCP SDK 和 IDE 插件版本，并把 CVE 推送给安全运营团队",
        "• 论点 2 — 安全 MCP 网关：Host 与 Origin 认证、最小权限的工具范围、沙箱逃逸防护，作为基础设施出售",
        "• 论点 3 — 能过采购的框架厂商：公开修补时长、CVSS 和签名发布包；买方是企业安全部门",
        "• 陷阱 — 以为模型厂商会承担框架和 MCP 的 CVE；有漏洞的代码在应用依赖库里",
        "• 不宜投 — 无认证的 MCP 服务器、用一把令牌调用全部工具的工具主机，以及没有 SBOM 或版本锁定的智能体栈"
    ],
    "14": [
        "预测 9 — MAESTRO v2 落地采用 — 投资论点",
        "现有证据：CSA MAESTRO v2 已于 2026-06-22 发布（10 层 + 信任控制平面）。",
        "• 论点 1 — 落地软件：分层模板、L1–L10 威胁编号，以及各层责任人矩阵，卖给安全工程团队",
        "• 论点 2 — 信任控制平面产品：对齐 v2 域的智能体身份、动作监控和中断路径；买方是智能体平台负责人",
        "• 论点 3 — 培训与认证：安全招聘负责人可以写进智能体安全岗位要求的付费课程",
        "• 陷阱 — 只办研讨班，从不把 L1–L10 检查放进客户能运行的工具",
        "• 不宜投 — 把身份与访问管理或可观测性改名为「信任平面」，却没有智能体身份和中断路径的产品"
    ],
    "15": [
        "预测 10 — OWASP AIVSS v1 — 投资论点",
        "现有证据：v0.8 已上线；v1.0 公开评审至 2026-10-01；目标在年底前冻结。",
        "• 论点 1 — 评分引擎：为智能体发布计算 AIVSS，并把分数送入工单和 SSVC 处置队列的产品",
        "• 论点 2 — 对照软件：为跨国安全买方提供 AIVSS、AIUC-1、MAESTRO 与 OWASP 智能体 Top 10 的同一套映射",
        "• 论点 3 — 发布门禁：v1 冻结后，AIVSS 分数超过设定阈值就阻断发布；买方是美、欧、中项目的发布负责人",
        "• 陷阱 — 在 v1 冻结前交付评分界面；方法一改就要返工，买方不会采信这个分数",
        "• 不宜投 — v1 成为公开标准后，仍拒绝对照 AIVSS、AIUC-1 和 MAESTRO 的专有「AI 风险分」"
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
