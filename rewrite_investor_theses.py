#!/usr/bin/env python3
"""Tag current scorecard version, then rewrite P1–P10 as investor theses (≤3 each)."""
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
TAG = "v1-midyear-scorecard"
BRANCH = "archive/v1-midyear-scorecard"

ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "DistributedApps.AI",
    "GIT_AUTHOR_EMAIL": "kenhuangus@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "DistributedApps.AI",
    "GIT_COMMITTER_EMAIL": "kenhuangus@users.noreply.github.com",
}

# Investor-lens content for each prediction slide (EN). Line counts must match ZH.
P_SLIDES_EN = {
    1: {  # will map by title prefix after load
        "title": "P1 — The Self-Improving Agentic AI System",
        "lines": [
            "P1 — Self-Improving / RSI Agents — Investor theses",
            "Evidence so far: Level-1 RSI demos (e.g. AIDE²); production still gated by eval + governance.",
            "• Thesis 1 — Evaluation infrastructure: bet on hidden-eval harnesses, reward-hacking detectors, and RSI regression suites sold to frontier labs and AI R&D teams",
            "• Thesis 2 — Governed self-modification: platforms that allow agents to rewrite tools/prompts only behind policy gates, audit logs, and human kill-switches (US labs + CN filing regimes)",
            "• Thesis 3 — Vertical RSI for code/ML ops: auto-research agents that improve training/inference pipelines under a fixed $ budget — not open-web general RSI",
        ],
    },
    2: {
        "title": "P2 — Agency > Intelligence",
        "lines": [
            "P2 — Agency > Intelligence — Investor theses",
            "Evidence so far: AgencyBench, AAS, enterprise buyers scoring tool-use and persistence over raw IQ.",
            "• Thesis 1 — Agency measurement layer: startups that productize agency scores (plan/tool/persist) for model selection, vendor RFP, and insurance underwriting",
            "• Thesis 2 — Long-horizon task agents: invest in products that win on multi-hour tool workflows and self-correction, not chatbot leaderboard deltas",
            "• Thesis 3 — Ambient / always-on agents: scarce Ambient agency (Idle-Gap) is the next premium — companions and ops agents that act between user prompts under hard scopes",
        ],
    },
    3: {
        "title": "P3 — New Security Benchmarks via MAESTRO",
        "lines": [
            "P3 — MAESTRO Security Benchmarks — Investor theses",
            "Evidence so far: MAESTRO operationalized in playbooks/CI; shared public leaderboards still maturing.",
            "• Thesis 1 — Continuous threat modeling in CI: TITO-class scanners that map PRs to MAESTRO layers and block risky agent merges",
            "• Thesis 2 — Agent red-team as a service: recurring layer-mapped attack packs + ATLAS crosswalks sold to banks, SaaS, and AI platforms",
            "• Thesis 3 — Assurance products: STAR / AIUC-1 style attestations that package MAESTRO evidence for buyers, insurers, and regulators",
        ],
    },
    4: {
        "title": "P4 — Agentic AI Risk Management Takes Center Stage",
        "lines": [
            "P4 — Agentic Risk Management — Investor theses",
            "Evidence so far: AICM v1.1, NIST AI RMF, China agent law, EU AI Act — risk is the buying center.",
            "• Thesis 1 — GRC for agents: control catalogs + questionnaires that map once to NIST / AICM / EU AI Act / CN filing and export auditor packs",
            "• Thesis 2 — Runtime risk engines: policy decision points on tool calls, autonomy tier, and human override — priced per agent-action",
            "• Thesis 3 — AI insurance & underwriting tech: AIUC-1 / AIVSS scoring feeds that let carriers price agent deployments",
        ],
    },
    5: {
        "title": "P5 — The \"Vibe Coding\" Security Hangover",
        "lines": [
            "P5 — Vibe Coding Security Hangover — Investor theses",
            "Evidence so far: ~91% of audited vibe-coded apps vulnerable; tool CVEs and secrets sprawl rising.",
            "• Thesis 1 — AI-native AppSec for generated code: shift-left SAST/DAST tuned to AI failure modes (BAC, IDOR, hardcoded secrets)",
            "• Thesis 2 — Secure vibe platforms: IDEs/builders that ship with auth defaults, secret vaults, and fix-or-waive gates before deploy",
            "• Thesis 3 — Managed remediation: services/products that auto-patch AI-introduced CWE classes and prove exploitability pre-merge",
        ],
    },
    6: {
        "title": "P6 — The Struggle of Browser Agents",
        "lines": [
            "P6 — Browser Agents Struggle — Investor theses",
            "Evidence so far: AG-UI drift/perf issues; A2UI maturing; computer-use still injection-fragile.",
            "• Thesis 1 — Protocol reliability layer: sequence/resync, durable state, and snapshot-tax control for AG-UI / A2UI production stacks",
            "• Thesis 2 — Constrained action catalogs: browser/desktop agents that only call approved UI actions (safer than open DOM) for enterprise RPA replacement",
            "• Thesis 3 — Defense for computer-use: injection detection, session isolation, and human-in-the-loop for high-impact clicks (payments, email send)",
        ],
    },
    7: {
        "title": "P7 — Enterprise Deployment: Internal First",
        "lines": [
            "P7 — Enterprise Internal-First — Investor theses",
            "Evidence so far: internal ops preferred; dual programs growing; open-web B2C still cautious.",
            "• Thesis 1 — Internal agent platforms: secure connectors to ERP/ITSM/finance with data-ready pipelines (the 78% readiness gap)",
            "• Thesis 2 — Agentic back-office ROI: finance/ops automation with measurable P&L payback (fastest ROI categories in 2026 surveys)",
            "• Thesis 3 — Controlled externalization: products that graduate internal agents to B2B with DPIA, HITL, and tenant isolation — not consumer viral agents first",
        ],
    },
    8: {
        "title": "P8 — More CVEs for the Agentic Ecosystem",
        "lines": [
            "P8 — Agentic Ecosystem CVEs — Investor theses",
            "Evidence so far: LangChain/MCP/coding-agent CVEs treated like classic software severity.",
            "• Thesis 1 — Agent SBOM + dependency firewall: pin/patch LangChain, MCP SDKs, IDE plugins with CVE streaming to SecOps",
            "• Thesis 2 — Secure MCP gateways: Host/Origin auth, least-privilege tool scopes, and sandbox escape prevention as infrastructure",
            "• Thesis 3 — Vendor security brands: agent-framework vendors that win enterprise on response time, CVSS clarity, and signed releases",
        ],
    },
    9: {
        "title": "P9 — MAESTRO v2: Making It Practical",
        "lines": [
            "P9 — MAESTRO v2 Practical Adoption — Investor theses",
            "Evidence so far: CSA MAESTRO v2 shipped 2026-06-22 (10 layers + Trust Control Plane).",
            "• Thesis 1 — MAESTRO implementation suites: templates, L1–L10 threat IDs, and SSRM ownership matrices sold as consulting + software",
            "• Thesis 2 — Trust Control Plane startups: identity, monitoring, and safety as horizontal control planes aligned to v2 domains",
            "• Thesis 3 — Training & certification: courses/cert paths that make MAESTRO the default hiring skill for agent security engineers",
        ],
    },
    10: {
        "title": "P10 — Official Release of OWASP AIVSS v1",
        "lines": [
            "P10 — OWASP AIVSS v1 — Investor theses",
            "Evidence so far: v0.8 live; v1.0 public review through 2026-10-01; freeze targeted before year-end.",
            "• Thesis 1 — Scoring engines: products that compute AIVSS for agent releases and feed ticketing / SSVC prioritization",
            "• Thesis 2 — Crosswalk platforms: one risk graph across AIVSS ↔ AIUC-1 ↔ MAESTRO ↔ OWASP Agentic Top 10 for multinational buyers",
            "• Thesis 3 — Compliance acceleration: EU/US/CN programs that treat AIVSS scores as release gates and insurer inputs once v1 freezes",
        ],
    },
}

P_SLIDES_ZH = {
    1: [
        "预测 1 — 自我改进 / RSI 智能体 — 投资论点",
        "现有证据：一级 RSI 演示（如 AIDE²）；生产仍受评估与治理约束。",
        "• 论点 1 — 评估基础设施：押注隐藏评估 harness、奖励作弊检测与 RSI 回归套件，卖给前沿实验室与 AI 研发团队",
        "• 论点 2 — 受治理的自我修改：仅在策略门禁、审计日志与人类急停之后允许智能体改写工具/提示（适配美国实验室与中国备案制度）",
        "• 论点 3 — 面向代码/ML Ops 的垂直 RSI：在固定美元预算下改进训练/推理管线的自动研究智能体 — 而非开放网络通用 RSI",
    ],
    2: [
        "预测 2 — 自主性 > 智力 — 投资论点",
        "现有证据：AgencyBench、AAS；企业买方更看重工具使用与持续执行，而非原始智商。",
        "• 论点 1 — 自主性度量层：将规划/工具/持续目标分数产品化，用于模型选型、供应商 RFP 与保险核保",
        "• 论点 2 — 长时程任务智能体：投资能赢多数小时工具工作流与自我纠错的产品，而非聊天机器人榜单分差",
        "• 论点 3 — Ambient / 常驻智能体：稀缺的 Ambient 自主性（Idle-Gap）将成为溢价 — 在硬范围下于用户提示之间行动的伙伴与运维智能体",
    ],
    3: [
        "预测 3 — MAESTRO 安全基准 — 投资论点",
        "现有证据：MAESTRO 已进入手册/CI；共享公共排行榜仍在成熟。",
        "• 论点 1 — CI 中的持续威胁建模：将 PR 映射到 MAESTRO 层并阻断高风险智能体合并的 TITO 类扫描器",
        "• 论点 2 — 智能体红队即服务：面向银行、SaaS 与 AI 平台的分层攻击包 + ATLAS 对照，按周期订阅",
        "• 论点 3 — 保障产品：将 MAESTRO 证据打包给买方、保险公司与监管的 STAR / AIUC-1 类证明",
    ],
    4: [
        "预测 4 — 智能体风险管理 — 投资论点",
        "现有证据：AICM v1.1、NIST AI RMF、中国智能体法规、欧盟 AI 法案 — 风险是采购中心。",
        "• 论点 1 — 面向智能体的 GRC：一次映射 NIST / AICM / 欧盟 AI 法案 / 中国备案并导出审计包的控制目录与问卷",
        "• 论点 2 — 运行时风险引擎：对工具调用、自主等级与人类否决的策略决策点 — 按智能体动作计费",
        "• 论点 3 — AI 保险与核保技术：让承保方为智能体部署定价的 AIUC-1 / AIVSS 评分供给",
    ],
    5: [
        "预测 5 — 氛围编程安全后遗症 — 投资论点",
        "现有证据：约 91% 被审计的氛围编程应用存在漏洞；工具 CVE 与密钥扩散上升。",
        "• 论点 1 — 面向生成代码的 AI 原生 AppSec：针对 AI 失败模式（访问控制、IDOR、硬编码密钥）调优的左移 SAST/DAST",
        "• 论点 2 — 安全的氛围编程平台：默认认证、密钥保险库与部署前「修复或豁免」门禁的 IDE/构建器",
        "• 论点 3 — 托管修复：自动修补 AI 引入的 CWE 类别并在合并前证明可利用性的服务/产品",
    ],
    6: [
        "预测 6 — 浏览器智能体艰难之路 — 投资论点",
        "现有证据：AG-UI 漂移/性能问题；A2UI 成熟中；计算机使用仍易受注入影响。",
        "• 论点 1 — 协议可靠性层：为 AG-UI / A2UI 生产栈提供序号/重同步、耐久状态与快照税控制",
        "• 论点 2 — 受约束动作目录：仅调用已批准 UI 动作的浏览器/桌面智能体（比开放 DOM 更安全），替代企业 RPA",
        "• 论点 3 — 计算机使用防御：注入检测、会话隔离，以及对高影响点击（支付、发信）的人类在环",
    ],
    7: [
        "预测 7 — 企业内部优先 — 投资论点",
        "现有证据：内部运营优先；双线项目增长；开放网络 B2C 仍谨慎。",
        "• 论点 1 — 内部智能体平台：通向 ERP/ITSM/财务的安全连接器与数据就绪管线（填补 78% 就绪缺口）",
        "• 论点 2 — 智能体后台 ROI：具有可度量损益回收的财务/运营自动化（2026 调研中最快回收类别）",
        "• 论点 3 — 受控外部化：以 DPIA、HITL 与租户隔离将内部智能体升级到 B2B 的产品 — 而非先做消费级病毒式智能体",
    ],
    8: [
        "预测 8 — 智能体生态 CVE — 投资论点",
        "现有证据：LangChain/MCP/编程智能体 CVE 已按传统软件严重度对待。",
        "• 论点 1 — 智能体 SBOM + 依赖防火墙：钉死/修补 LangChain、MCP SDK、IDE 插件，并向 SecOps 流式推送 CVE",
        "• 论点 2 — 安全 MCP 网关：Host/Origin 认证、最小权限工具范围与防沙箱逃逸，作为基础设施出售",
        "• 论点 3 — 厂商安全品牌：以响应速度、CVSS 清晰度与签名发布赢得企业的智能体框架厂商",
    ],
    9: [
        "预测 9 — MAESTRO v2 落地采用 — 投资论点",
        "现有证据：CSA MAESTRO v2 已于 2026-06-22 发布（10 层 + 信任控制平面）。",
        "• 论点 1 — MAESTRO 实施套件：以咨询 + 软件形式出售的模板、L1–L10 威胁 ID 与 SSRM 责任矩阵",
        "• 论点 2 — 信任控制平面创业公司：对齐 v2 域的身份、监控与安全横向控制平面",
        "• 论点 3 — 培训与认证：使 MAESTRO 成为智能体安全工程师默认招聘技能的课程/认证路径",
    ],
    10: [
        "预测 10 — OWASP AIVSS v1 — 投资论点",
        "现有证据：v0.8 已上线；v1.0 公开评审至 2026-10-01；计划年底前冻结。",
        "• 论点 1 — 评分引擎：为智能体发布计算 AIVSS 并馈入工单 / SSVC 优先级的产品",
        "• 论点 2 — 交叉映射平台：覆盖 AIVSS ↔ AIUC-1 ↔ MAESTRO ↔ OWASP 智能体 Top 10 的单一风险图，服务跨国买方",
        "• 论点 3 — 合规加速：一旦 v1 冻结，将 AIVSS 分数作为发布门禁与保险输入的美欧中项目",
    ],
}


def run(args, input_text=None, check=True):
    r = subprocess.run(args, cwd=ROOT, input=input_text, text=True, capture_output=True, env=ENV)
    if check and r.returncode:
        sys.stderr.write(r.stdout or "")
        sys.stderr.write(r.stderr or "")
        raise SystemExit(r.returncode)
    return r


def preserve_version() -> None:
    # Tag + archive branch at current HEAD (pre-investor rewrite)
    tags = run(["git", "tag", "-l", TAG]).stdout.strip()
    if TAG not in tags.splitlines():
        run(["git", "tag", "-a", TAG, "-m", "Mid-year scorecard snapshot before investor-thesis rewrite"])
        print("Tagged", TAG)
    else:
        print("Tag already exists", TAG)
    # Create/update archive branch pointing at tag
    run(["git", "branch", "-f", BRANCH, TAG])
    run(["git", "push", "origin", TAG], check=False)
    run(["git", "push", "origin", BRANCH, "--force"], check=False)
    print("Pushed tag/branch", TAG, BRANCH)


def load_build():
    text = BUILD.read_text(encoding="utf-8")
    m_en = re.search(r"SLIDES_EN = (\[.*?\])\n\nSLIDES_ZH = ", text, re.S)
    m_zh = re.search(r"SLIDES_ZH = (\{.*?\})\n\nPHRASES = ", text, re.S)
    if not m_en or not m_zh:
        raise SystemExit("parse failed")
    en = ast.literal_eval(m_en.group(1))
    zh = ast.literal_eval(m_zh.group(1))
    return text, m_en, m_zh, en, zh


def rewrite_slides(en, zh):
    # Map P1..P10 by raw title prefix
    pred_idx = []
    for i, s in enumerate(en):
        title = s["raw_lines"][0]
        m = re.match(r"P(\d+)\s*—", title)
        if m:
            pred_idx.append((i, int(m.group(1))))

    if len(pred_idx) != 10:
        raise SystemExit(f"expected 10 prediction slides, found {pred_idx}")

    for i, pnum in pred_idx:
        en_lines = P_SLIDES_EN[pnum]["lines"]
        zh_lines = P_SLIDES_ZH[pnum]
        assert len(en_lines) == len(zh_lines), (pnum, len(en_lines), len(zh_lines))
        # Preserve slide_type if any
        st = en[i].get("slide_type")
        en[i] = {"number": en[i]["number"], "raw_lines": en_lines}
        if st:
            en[i]["slide_type"] = st
        zh[str(en[i]["number"])] = zh_lines

    # Update title / about / scorecard / closing for investor framing
    for s in en:
        if s["number"] == 1:
            s["raw_lines"] = [
                "Top 10 Predictions for Agentic AI in 2026",
                "Investor thesis scorecard — as of September 27, 2026",
                "Original predictions: Cloud Security Alliance, January 16, 2026",
                "Author: Ken Huang, CEO & Chief AI Officer, DistributedApps.ai",
                "Adjunct Professor, University of San Francisco: https://www.usfca.edu/faculty/ken-huang",
                "Lens: up to 3 investment theses per trend · US · China · EU evidence",
                "CSA article: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
                "Archive snapshot on GitHub tag: v1-midyear-scorecard",
            ]
            zh["1"] = [
                "2026 智能体 AI 十大预测",
                "投资论点成绩单 — 截至 2026 年 9 月 27 日",
                "原始预测：云安全联盟（CSA），2026 年 1 月 16 日",
                "作者：Ken Huang，DistributedApps.ai 首席执行官兼首席 AI 官",
                "旧金山大学（USF）客座教授：https://www.usfca.edu/faculty/ken-huang",
                "视角：每个趋势最多 3 条投资论点 · 美 · 中 · 欧证据",
                "CSA 原文：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
                "GitHub 存档标签：v1-midyear-scorecard",
            ]
        elif s["raw_lines"][0].startswith("About This Scorecard"):
            s["raw_lines"] = [
                "About This Investor Scorecard",
                "• Origin: Ken Huang — My Top 10 Predictions for Agentic AI in 2026 (CSA, 2026-01-16)",
                "• CSA URL: https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
                "• Method: convert each prediction into ≤3 investable theses grounded in US/China/EU evidence through 2026-09-27",
                "• Prior mid-year audit (status only) preserved as GitHub tag v1-midyear-scorecard / branch archive/v1-midyear-scorecard",
                "• Thesis bar: who pays, what product category, why now — not generic “AI will grow” claims",
                "• Regions still matter: US lab/CVE markets, China agent regulation, EU AI Act / CRA gates shape where capital can deploy",
            ]
            zh[str(s["number"])] = [
                "关于本投资成绩单",
                "• 出处：Ken Huang —《My Top 10 Predictions for Agentic AI in 2026》（CSA，2026-01-16）",
                "• CSA 链接：https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026",
                "• 方法：将每条预测转化为 ≤3 条可投资论点，并锚定截至 2026-09-27 的美/中/欧证据",
                "• 先前年中审计（仅状态判定）保留为 GitHub 标签 v1-midyear-scorecard / 分支 archive/v1-midyear-scorecard",
                "• 论点标准：谁付费、什么产品类别、为何是现在 — 而非笼统的「AI 会增长」",
                "• 区域仍关键：美国实验室/CVE 市场、中国智能体监管、欧盟 AI 法案/CRA 门禁决定资本可部署之处",
            ]
        elif s["raw_lines"][0].startswith("Scorecard at a Glance"):
            s["raw_lines"] = [
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
                "| 10 | AIVSS v1 | Scoring engines · crosswalks · release gates |",
            ]
            zh[str(s["number"])] = [
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
                "| 10 | AIVSS v1 | 评分引擎 · 交叉映射 · 发布门禁 |",
            ]
        elif s["raw_lines"][0].startswith("Closing"):
            s["raw_lines"] = [
                "Closing — Where capital meets agentic security",
                "• Each of the 10 CSA trends maps to ≤3 theses with a payer and a product surface",
                "• Strongest near-term wallets: enterprise GRC/runtime controls, AI AppSec for vibe coding, MCP/gateway security",
                "• Structural openers into Q4: AIVSS v1 freeze, A2UI reliability, independent RSI replication",
                "• Status-only archive remains at tag v1-midyear-scorecard for comparison",
                "• Continue: kenhuangus.substack.com · aivss.owasp.org · CSA AI Safety working groups",
                "• Contact: DistributedApps.ai · LinkedIn linkedin.com/in/kenhuang8",
            ]
            zh[str(s["number"])] = [
                "结语 — 资本与智能体安全交汇之处",
                "• CSA 的 10 个趋势各自映射到 ≤3 条带付费方与产品表面的投资论点",
                "• 近期最强钱包：企业 GRC/运行时控制、氛围编程 AI AppSec、MCP/网关安全",
                "• 进入第四季度的结构性窗口：AIVSS v1 冻结、A2UI 可靠性、独立 RSI 复现",
                "• 仅状态判定的存档仍在标签 v1-midyear-scorecard，便于对照",
                "• 继续对话：kenhuangus.substack.com · aivss.owasp.org · CSA AI 安全工作组",
                "• 联系：DistributedApps.ai · LinkedIn linkedin.com/in/kenhuang8",
            ]
        elif s["raw_lines"][0].startswith("What Remains Open"):
            s["raw_lines"] = [
                "Open Questions for Capital — Q4 2026",
                "• Does AIVSS v1 freeze create a scoring-engine category winner, or stay a free checklist?",
                "• Will AG-UI/A2UI reliability layers become infrastructure picks or stay framework features?",
                "• Is RSI investable beyond eval vendors before Level-2 ignition evidence?",
                "• Do internal-first platforms capture budget before open-web B2C agents clear trust?",
                "• Can AI AppSec vendors cut the ~91% vibe-coded vuln baseline enough to become default CI?",
                "• Watch regulation: CN agent filing costs vs US CVE velocity vs EU CRA/AI Act gates",
            ]
            zh[str(s["number"])] = [
                "给资本的未决问题 — 2026 年第四季度",
                "• AIVSS v1 冻结会造就评分引擎类别赢家，还是停留在免费清单？",
                "• AG-UI/A2UI 可靠性层会成为基础设施标的，还是框架附带功能？",
                "• 在二级点火证据出现前，RSI 是否只在评估供应商层面可投资？",
                "• 内部优先平台能否在开放网络 B2C 智能体建立信任前拿下预算？",
                "• AI AppSec 厂商能否把约 91% 的氛围编程漏洞基线压到成为默认 CI？",
                "• 关注监管：中国智能体备案成本 vs 美国 CVE 速度 vs 欧盟 CRA/AI 法案门禁",
            ]
        elif s["raw_lines"][0].startswith("Regional Pattern"):
            s["raw_lines"] = [
                "Regional Capital Lens — United States · China · European Union",
                "| Theme | United States | China | European Union |",
                "|---|---|---|---|",
                "| Where $ pools | Labs, CVE tooling, enterprise surveys | Internal ops under localization + filing | Compliance software + human-oversight UX |",
                "| RSI / agency | Eval + vertical RSI startups | Regulated autonomy tiers | Research > open deploy; autonomy as risk object |",
                "| Security stack | MAESTRO/AIVSS productization, AppSec | Patch velocity + CNVD mirror | CRA/NIS2 build gates, AI Act mappings |",
                "| Browser agents | Protocol reliability + CUA defense | Constrained catalogs in productivity apps | A2UI std + oversight-friendly UX |",
                "| Enterprise | Internal platforms, dual programs | Data-local agent platforms | HITL-first externalization |",
            ]
            zh[str(s["number"])] = [
                "区域资本视角 — 美国 · 中国 · 欧盟",
                "| 主题 | 美国 | 中国 | 欧盟 |",
                "|---|---|---|---|",
                "| 资金池 | 实验室、CVE 工具、企业调研 | 本地化 + 备案下的内部运营 | 合规软件 + 人类监督体验 |",
                "| RSI / 自主性 | 评估 + 垂直 RSI 创业公司 | 受监管的自主等级 | 研究 > 开放部署；自主性即风险对象 |",
                "| 安全栈 | MAESTRO/AIVSS 产品化、AppSec | 补丁速度 + CNVD 镜像 | CRA/NIS2 构建门禁、AI 法案映射 |",
                "| 浏览器智能体 | 协议可靠性 + 计算机使用防御 | 生产力应用中的受约束目录 | A2UI 标准 + 便于监督的体验 |",
                "| 企业 | 内部平台、双线项目 | 数据本地智能体平台 | HITL 优先的外部化 |",
            ]

    # Hero text in slides.html for title slide
    return en, zh


def write_build(text, m_en, m_zh, en, zh):
    def to_py(obj):
        s = json.dumps(obj, ensure_ascii=False, indent=4)
        return s.replace(": true", ": True").replace(": false", ": False").replace(": null", ": None")

    text2 = text[: m_en.start(1)] + to_py(en) + text[m_en.end(1) : m_zh.start(1)] + to_py(zh) + text[m_zh.end(1) :]
    BUILD.write_text(text2, encoding="utf-8")


def patch_hero():
    path = ROOT / "slides.html"
    t = path.read_text(encoding="utf-8")
    old_en = "Original predictions published by the Cloud Security Alliance (2026-01-16): https://cloudsecurityalliance.org/blog/2026/01/16/my-top-10-predictions-for-agentic-ai-in-2026 — this scorecard audits US, China, and EU evidence through 2026-09-27."
    new_en = "Investor thesis scorecard from the CSA Top 10 (2026-01-16). Up to 3 investable theses per trend, grounded in US · China · EU evidence through 2026-09-27. Prior status audit: GitHub tag v1-midyear-scorecard."
    old_zh = "原始预测发表于云安全联盟（2026-01-16）。本成绩单审计截至 2026-09-27 在美国、中国与欧盟的公开证据兑现情况。"
    new_zh = "基于 CSA 十大预测（2026-01-16）的投资论点成绩单。每个趋势最多 3 条可投资论点，锚定美 · 中 · 欧至 2026-09-27 的证据。状态审计存档：GitHub 标签 v1-midyear-scorecard。"
    if old_en in t:
        t = t.replace(old_en, new_en)
    if old_zh in t:
        t = t.replace(old_zh, new_zh)
    # Also update build_slides hero strings if present
    bp = BUILD.read_text(encoding="utf-8")
    bp = bp.replace(old_en, new_en).replace(old_zh, new_zh)
    BUILD.write_text(bp, encoding="utf-8")
    path.write_text(t, encoding="utf-8")


def update_index():
    idx = ROOT / "index.html"
    t = idx.read_text(encoding="utf-8")
    t = t.replace(
        "Mid-year scorecard · cut-off 2026-09-27",
        "Investor thesis scorecard · cut-off 2026-09-27 · archive tag v1-midyear-scorecard",
    )
    t = t.replace(
        "How the Top 10 Agentic AI predictions are holding up in the United States, China, and the EU",
        "Up to 3 investment theses per Agentic AI trend — grounded in United States, China, and EU evidence",
    )
    # Soften scorecard table header note
    if "Archive snapshot" not in t:
        t = t.replace(
            '<span class="chip">8 / 10 confirmed, mostly confirmed, or on track</span>',
            '<span class="chip">≤3 theses per trend</span>\n'
            '        <span class="chip">Archive: v1-midyear-scorecard</span>',
        )
    idx.write_text(t, encoding="utf-8")
    shutil.copy2(idx, ROOT / "docs" / "index.html")


def commit_push():
    run(["git", "add", "-A"])
    st = run(["git", "status", "--porcelain"]).stdout.strip()
    if not st:
        print("nothing to commit")
        return
    tree = run(["git", "write-tree"]).stdout.strip()
    head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    msg = (
        "Rewrite prediction slides as investor theses (up to 3 per trend).\n"
        "\n"
        "Keeps prior mid-year status audit at tag v1-midyear-scorecard / "
        "branch archive/v1-midyear-scorecard.\n"
    )
    new = run(["git", "commit-tree", tree, "-p", head], input_text=msg).stdout.strip()
    run(["git", "reset", "--soft", new])
    body = run(["git", "log", "-1", "--format=%B"]).stdout
    if "Co-authored-by" in body:
        raise SystemExit("trailer present")
    run(["git", "push", "origin", "HEAD:main"])
    print("COMMIT", new)
    print("Pushed main")


def main():
    preserve_version()
    text, m_en, m_zh, en, zh = load_build()
    en, zh = rewrite_slides(en, zh)
    write_build(text, m_en, m_zh, en, zh)
    patch_hero()
    r = subprocess.run([sys.executable, str(ROOT / "build_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)
    r = subprocess.run([sys.executable, str(ROOT / "cleanup_slides.py")], cwd=ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)
    patch_hero()  # rebuild may not touch hero; ensure again
    update_index()
    # sync docs
    shutil.copy2(ROOT / "slides.html", ROOT / "docs" / "slides.html")
    shutil.copy2(ROOT / "slides-zh.js", ROOT / "docs" / "slides-zh.js")
    # verify line parity
    t = (ROOT / "slides.html").read_text(encoding="utf-8")
    data = json.loads(re.search(r"const slidesData = (\[.*?\]);", t, re.S).group(1))
    zhjs = json.loads((ROOT / "slides-zh.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    for s in data:
        n = str(s["number"])
        assert len(zhjs["lines"][n]) == len(s["raw_lines"]), (n, s["raw_lines"][0])
    print("slides", len(data))
    for s in data:
        if s["raw_lines"][0].startswith("P"):
            theses = sum(1 for l in s["raw_lines"] if "Thesis" in l or "论点" in l)
            print(s["number"], s["raw_lines"][0][:50], "theses_lines", theses)
    commit_push()
    print("Archive:", f"https://github.com/kenhuangus/agentic-ai-2026-predictions/tree/{TAG}")
    print("Public:", "https://kenhuangus.github.io/agentic-ai-2026-predictions/slides.html?lang=en")


if __name__ == "__main__":
    main()
