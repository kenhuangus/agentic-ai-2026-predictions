#!/usr/bin/env python3
"""Apply grok-reviewed investor thesis / anti-thesis fixes (EN+ZH)."""
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
    "PYTHONIOENCODING": "utf-8",
    "GIT_AUTHOR_NAME": "DistributedApps.AI",
    "GIT_AUTHOR_EMAIL": "kenhuangus@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "DistributedApps.AI",
    "GIT_COMMITTER_EMAIL": "kenhuangus@users.noreply.github.com",
}

REVISED_EN = {
    1: [
        "P1 — Self-Improving / RSI Agents — Investor theses",
        "Evidence so far: AIDE² is Level-1 RSI (net-positive R&D under a fixed budget); production still needs hidden evals and governance.",
        "• Thesis 1 — Evaluation infrastructure: hidden-eval harnesses, reward-hacking detectors, and RSI regression suites sold to frontier labs and AI R&D teams",
        "• Thesis 2 — Governed self-modification: agents may rewrite tools or prompts only after policy approval, audit logs, and a human stop (US labs; China filing plus human override)",
        "• Thesis 3 — Vertical RSI for ML ops: auto-research agents that improve a training or inference pipeline under a fixed dollar budget; buyer is the AI infrastructure team",
        "• Pitfall — Treating Level-1 (faster than a human baseline on a fixed budget) as Level-2 (the improver gets better at improving); Level-2 is not shown, and reward hacking is common",
        "• Do not invest — Public-web apps marketed as self-improving AGI that rewrite their own code with no hidden eval and no dollar cap",
    ],
    2: [
        "P2 — Agency > Intelligence — Investor theses",
        "Evidence so far: AgencyBench (multi-hour tool tasks, ACL 2026) and AAS (Active vs Ambient bands).",
        "• Thesis 1 — Agency scores for procurement: plan, tool-use, and persistence scores sold into model selection and vendor RFPs",
        "• Thesis 2 — Long-horizon task agents: software that finishes multi-hour tool workflows and self-corrects; buyer is ops or engineering, not a chat leaderboard",
        "• Thesis 3 — Scoped idle-period agents: enterprise ops agents that act between user prompts only inside a written permission boundary (high AAS Ambient scores remain uncommon)",
        "• Pitfall — Paying for MMLU or IQ-score wrappers while buyers already score tools, persistence, and correction",
        "• Do not invest — Chat products labeled as agents with no cross-session goal, no tool contract, and no multi-hour task completion",
    ],
    3: [
        "P3 — MAESTRO Security Benchmarks — Investor theses",
        "Evidence so far: MAESTRO is in playbooks and CI; shared public leaderboards are still maturing.",
        "• Thesis 1 — CI layer checks: scanners that map a pull request to MAESTRO layers and block high-risk agent merges; buyer is the platform security team",
        "• Thesis 2 — Agent red-team subscription: recurring attack packs mapped to layers, plus a MITRE ATLAS crosswalk, sold to banks, SaaS, and AI platforms",
        "• Thesis 3 — Assurance reports: third-party reports that package MAESTRO layer evidence for procurement and regulators (same buyers as CSA STAR and AIUC-1)",
        "• Pitfall — Paying for another static PDF checklist; buyers pay for a CI block and an evidence pack",
        "• Do not invest — \"MAESTRO-compliant\" badges with no layer tests, no ATLAS mapping, and no scanner output",
    ],
    4: [
        "P4 — Agentic Risk Management — Investor theses",
        "Evidence so far: AICM v1.1, NIST AI RMF, China agent regulation (enforceable 2026-07-15), EU AI Act — risk and compliance teams are the buyer.",
        "• Thesis 1 — Agent GRC: one control catalog and questionnaire mapped to NIST, AICM, the EU AI Act, and China filing, exported as an auditor pack for the compliance team",
        "• Thesis 2 — Runtime risk engines: allow or deny on tool calls, autonomy tier, and human override, priced per agent action",
        "• Thesis 3 — Insurance underwriting workbenches: carrier tools that turn an AIUC-1 control result and an AIVSS score into a premium and an exclusion",
        "• Pitfall — US-only GRC that cannot export EU AI Act or China filing evidence; multinational buyers will leave",
        "• Do not invest — Policy-document generators with no runtime allow or deny on tool calls",
    ],
    5: [
        "P5 — Vibe Coding Security Hangover — Investor theses",
        "Evidence so far: about 91% of audited vibe-coded apps had vulnerabilities (arXiv:2606.23130); tool CVEs and exposed secrets continue to increase.",
        "• Thesis 1 — AppSec for generated code: pre-merge SAST/DAST sold to AppSec teams, tuned for flaws these apps ship (broken access control, IDOR, hardcoded secrets)",
        "• Thesis 2 — Secure vibe platforms: IDEs and app builders with default authentication, a secrets store, and a fix-or-waive gate before deploy",
        "• Thesis 3 — Managed remediation: a service that patches those CWE classes and attaches a proof of exploitability before merge",
        "• Pitfall — Generic SAST renamed \"AI security\" that does not test broken access control, IDOR, or hardcoded secrets",
        "• Do not invest — Vibe builders that optimize demo speed and ship debug CORS, hardcoded keys, and APIs with no authentication",
    ],
    6: [
        "P6 — Browser Agents Struggle — Investor theses",
        "Evidence so far: AG-UI drift and performance issues; A2UI at v0.9.1 / v1.0-rc; computer-use is still exposed to prompt injection.",
        "• Thesis 1 — Protocol reliability: sequence numbers, resync, persistent session state, and limits on full-UI snapshot size and frequency for AG-UI / A2UI production stacks",
        "• Thesis 2 — Approved action catalogs: browser and desktop agents that call only an approved action list, not an open DOM, sold as an enterprise RPA replacement",
        "• Thesis 3 — Computer-use controls: injection detection, session isolation, and human approval for payment and email-send clicks",
        "• Pitfall — Funding open-DOM computer-use as production-ready before resync and injection checks exist",
        "• Do not invest — Consumer browser agents that can pay or send email with no human approval and no session isolation",
    ],
    7: [
        "P7 — Enterprise Internal-First — Investor theses",
        "Evidence so far: Contentstack 2026 — 37% internal-primary, 10% external-primary, 53% both; 78% of leaders with a production program hit content or data rework.",
        "• Thesis 1 — Internal agent platforms: secure ERP, ITSM, and finance connectors plus content and data pipelines; buyer is central IT",
        "• Thesis 2 — Back-office workflow agents: approvals and routing for ops leaders who track a finance-audited KPI (Contentstack: 94% of KPI-measured internal programs reported a positive return)",
        "• Thesis 3 — Controlled B2B release: software that publishes an internal agent to a business customer only with a DPIA, human approval, and tenant isolation",
        "• Pitfall — Deploying agents before content and data are ready; that rework is what delayed production programs in the same survey",
        "• Do not invest — Public-web consumer agents funded before an internal workflow has a KPI finance can audit",
    ],
    8: [
        "P8 — Agentic Ecosystem CVEs — Investor theses",
        "Evidence so far: LangChain CVE-2026-55443, MCP CVE-2026-59950, and coding-agent RCEs are scored like other software CVEs.",
        "• Thesis 1 — Agent SBOM and dependency firewall: version-pin and patch LangChain, MCP SDKs, and IDE plugins, and stream CVEs to the security operations team",
        "• Thesis 2 — Secure MCP gateways: Host and Origin authentication, least-privilege tool scopes, and sandbox-escape controls, sold as infrastructure",
        "• Thesis 3 — Framework vendors that pass procurement: publish time-to-patch, CVSS, and signed releases; buyer is enterprise security",
        "• Pitfall — Assuming the model vendor covers framework and MCP CVEs; the vulnerable code is in the application dependency tree",
        "• Do not invest — MCP servers with no authentication, tool hosts that use one token for every tool, and agent stacks with no SBOM or version pin",
    ],
    9: [
        "P9 — MAESTRO v2 Practical Adoption — Investor theses",
        "Evidence so far: MAESTRO v2 is not published yet. The CSA-adopted model in use is still seven layers (L1–L7); a 10-layer v2 release has not shipped.",
        "• Thesis 1 — Seven-layer implementation software: L1–L7 templates, threat IDs, and a layer-owner matrix sold to the security engineering team",
        "• Thesis 2 — Adoption into CI and playbooks: scanners and questionnaires that encode today’s seven-layer MAESTRO while v2 is still in draft",
        "• Thesis 3 — Training on the published model: paid courses that hiring managers can list for agent-security roles against L1–L7",
        "• Pitfall — Selling “MAESTRO v2” or “10-layer Trust Control Plane” before CSA publishes v2; buyers will treat that as vapor",
        "• Do not invest — Pre-release “v2-compliant” badges, or products that rename IAM “trust plane” with no agent identity and no interrupt path",
    ],
    10: [
        "P10 — OWASP AIVSS v1 — Investor theses",
        "Evidence so far: v0.8 live; v1.0 public review through 2026-10-01; freeze targeted before year-end.",
        "• Thesis 1 — Scoring engines: products that compute AIVSS for an agent release and send the score to ticketing and SSVC priority queues",
        "• Thesis 2 — Crosswalk software: one mapping across AIVSS, AIUC-1, MAESTRO, and OWASP Agentic Top 10 for multinational security buyers",
        "• Thesis 3 — Release gates: after the v1 freeze, block a release when the AIVSS score crosses a set threshold; buyer is the release owner in US, EU, and China programs",
        "• Pitfall — Shipping a scoring interface before the v1 freeze; method changes force rework, and buyers will not trust the number",
        "• Do not invest — Proprietary \"AI risk scores\" that, after v1 is the published standard, still refuse a mapping to AIVSS, AIUC-1, and MAESTRO",
    ],
}

REVISED_ZH = {
    1: [
        "预测 1 — 自我改进 / RSI 智能体 — 投资论点",
        "现有证据：AIDE² 属于一级 RSI（固定预算下研发效率高于人工基线）；生产仍需要隐藏评测与治理。",
        "• 论点 1 — 评测基础设施：向前沿实验室和 AI 研发团队销售隐藏评测框架、奖励作弊检测和 RSI 回归测试套件",
        "• 论点 2 — 受控自我修改：智能体只有在策略审批、审计日志和人工急停之后才能改写工具或提示词（美国实验室；中国备案加人工接管）",
        "• 论点 3 — ML 运维的垂直 RSI：在固定美元预算内改进训练或推理管线的自动研究智能体；买方是 AI 基础设施团队",
        "• 陷阱 — 把一级（固定预算下高于人工基线）当成二级（改进者自己变得更会改进）；二级尚未被实验证实，奖励作弊常见",
        "• 不宜投 — 面向公网、宣传「自我改进 AGI」、且在无隐藏评测、无美元上限下自行改代码的应用",
    ],
    2: [
        "预测 2 — 自主性 > 智力 — 投资论点",
        "现有证据：AgencyBench（数小时工具任务，ACL 2026）与 AAS（任务执行带 vs 空闲带）。",
        "• 论点 1 — 用于采购的自主性分数：把规划、工具使用和持续执行分数卖进模型选型和供应商招标",
        "• 论点 2 — 长时程任务智能体：能完成数小时工具流程并自我纠错的软件；买方是运营或工程团队，不是聊天榜单",
        "• 论点 3 — 限定空闲期智能体：只在书面权限范围内、于两次用户指令之间行动的企业运维智能体（AAS 空闲带高分仍少见）",
        "• 陷阱 — 为包装 MMLU 或智商分数的创业公司付钱，而买方已经在为工具、持续执行和纠错打分",
        "• 不宜投 — 自称智能体、但没有跨会话目标、没有工具调用合同、也不能完成数小时任务的聊天产品",
    ],
    3: [
        "预测 3 — MAESTRO 安全基准 — 投资论点",
        "现有证据：MAESTRO 已进入操作手册和 CI；共享的公开排行榜仍在形成。",
        "• 论点 1 — CI 分层检查：把合并请求映射到 MAESTRO 各层并阻断高风险智能体合并的扫描器；买方是平台安全团队",
        "• 论点 2 — 智能体红队订阅：按层编写的周期性攻击包，附 MITRE ATLAS 对照，卖给银行、SaaS 和 AI 平台",
        "• 论点 3 — 鉴证报告：把 MAESTRO 分层证据打包给采购和监管机构的第三方报告（买方与 CSA STAR、AIUC-1 相同）",
        "• 陷阱 — 再为一份不能执行的静态 PDF 清单付钱；买方付钱买的是 CI 阻断和证据包",
        "• 不宜投 — 没有分层测试、没有 ATLAS 对照、没有扫描输出的「MAESTRO 合规」徽章",
    ],
    4: [
        "预测 4 — 智能体风险管理 — 投资论点",
        "现有证据：AICM v1.1、NIST AI RMF、中国智能体监管（2026-07-15 起施行）、欧盟 AI 法案 — 风险与合规团队是买方。",
        "• 论点 1 — 智能体 GRC：一套控制目录和问卷，一次映射 NIST、AICM、欧盟 AI 法案和中国备案，并导出给合规团队的审计包",
        "• 论点 2 — 运行时风险引擎：对工具调用、自主等级和人工接管做允许或拒绝，按智能体动作收费",
        "• 论点 3 — 保险核保工作台：把 AIUC-1 控制结果和 AIVSS 分数转成保费与除外责任的承保工具",
        "• 陷阱 — 只能覆盖美国、导不出欧盟 AI 法案或中国备案证据的 GRC；跨国买方会流失",
        "• 不宜投 — 只会生成制度文档、不能在工具调用上做允许或拒绝的产品",
    ],
    5: [
        "预测 5 — Vibe Coding 安全后遗症 — 投资论点",
        "现有证据：被审计的 vibe coding 应用约 91% 有漏洞（arXiv:2606.23130）；工具 CVE 和泄露的密钥在增加。",
        "• 论点 1 — 生成代码的应用安全：卖给应用安全团队的合并前 SAST/DAST，针对这些应用高频出现的缺陷（访问控制失效、IDOR、硬编码密钥）",
        "• 论点 2 — 安全的 vibe coding 平台：默认带认证、密钥库，以及部署前「修复或书面豁免」门禁的 IDE 和应用生成器",
        "• 论点 3 — 托管修复：修补上述 CWE 类别，并在合并前附上可利用性证明的服务",
        "• 陷阱 — 把通用 SAST 改名为「AI 安全」，却不检测访问控制失效、IDOR 或硬编码密钥",
        "• 不宜投 — 追求演示速度，并交付调试用 CORS、硬编码密钥和无认证 API 的 vibe coding 生成器",
    ],
    6: [
        "预测 6 — 浏览器智能体仍难落地 — 投资论点",
        "现有证据：AG-UI 有状态漂移和性能问题；A2UI 处于 v0.9.1 / v1.0-rc；计算机操作仍易被提示注入。",
        "• 论点 1 — 协议可靠性：为 AG-UI / A2UI 生产系统提供消息序号、断线重同步、持久会话状态，并限制整页界面快照的大小和发送频率",
        "• 论点 2 — 已批准动作目录：只调用批准动作清单、不操作开放 DOM 的浏览器和桌面智能体，作为企业 RPA 替代品出售",
        "• 论点 3 — 计算机操作控制：注入检测、会话隔离，以及支付和发邮件点击前的人工审批",
        "• 陷阱 — 在重同步和注入检测尚未具备时，就把开放 DOM 的计算机操作当成可投产能力",
        "• 不宜投 — 可以支付或发邮件，但没有人工审批、也没有会话隔离的消费级浏览器智能体",
    ],
    7: [
        "预测 7 — 企业内部优先 — 投资论点",
        "现有证据：Contentstack 2026 — 37% 以内部分为主、10% 以对外为主、53% 两者并行；已有生产项目的负责人中，78% 遇到内容或数据返工。",
        "• 论点 1 — 内部智能体平台：连接 ERP、ITSM 和财务系统的安全连接器，加上内容与数据管线；买方是中央 IT",
        "• 论点 2 — 后台流程智能体：面向已跟踪财务可审计 KPI 的运营负责人，做审批和路由（Contentstack：有 KPI 的内部项目中 94% 报告正收益）",
        "• 论点 3 — 受控的 B2B 发布：只有在 DPIA、人工审批和租户隔离齐备后，才把内部智能体开放给企业客户的软件",
        "• 陷阱 — 在内容和数据就绪之前部署智能体；同一调研里，生产项目会因此返工并推迟",
        "• 不宜投 — 内部流程还没有财务可审计的 KPI 之前就融资的公网消费级智能体",
    ],
    8: [
        "预测 8 — 智能体生态 CVE — 投资论点",
        "现有证据：LangChain CVE-2026-55443、MCP CVE-2026-59950，以及编程智能体远程代码执行，已按普通软件 CVE 评级。",
        "• 论点 1 — 智能体 SBOM 与依赖防火墙：锁定并修补 LangChain、MCP SDK 和 IDE 插件版本，并把 CVE 推送给安全运营团队",
        "• 论点 2 — 安全 MCP 网关：Host 与 Origin 认证、最小权限的工具范围、沙箱逃逸防护，作为基础设施出售",
        "• 论点 3 — 能过采购的框架厂商：公开修补时长、CVSS 和签名发布包；买方是企业安全部门",
        "• 陷阱 — 以为模型厂商会承担框架和 MCP 的 CVE；有漏洞的代码在应用依赖库里",
        "• 不宜投 — 无认证的 MCP 服务器、用一把令牌调用全部工具的工具主机，以及没有 SBOM 或版本锁定的智能体栈",
    ],
    9: [
        "预测 9 — MAESTRO v2 落地采用 — 投资论点",
        "现有证据：MAESTRO v2 尚未发布。CSA 已采用、实际在用的仍是七层模型（L1–L7）；所谓十层 v2 并未上市。",
        "• 论点 1 — 七层落地软件：L1–L7 模板、威胁编号和各层责任人矩阵，卖给安全工程团队",
        "• 论点 2 — 写入 CI 与操作手册：在 v2 仍为草稿时，把现行七层 MAESTRO 编进扫描器和问卷",
        "• 论点 3 — 基于已发布模型的培训：招聘负责人可按 L1–L7 写进智能体安全岗位要求的付费课程",
        "• 陷阱 — 在 CSA 发布 v2 之前销售「MAESTRO v2」或「十层信任控制平面」；买方会视为空谈",
        "• 不宜投 — 未发布前的「v2 合规」徽章，或把身份与访问管理改名为「信任平面」、却没有智能体身份和中断路径的产品",
    ],
    10: [
        "预测 10 — OWASP AIVSS v1 — 投资论点",
        "现有证据：v0.8 已上线；v1.0 公开评审至 2026-10-01；目标在年底前冻结。",
        "• 论点 1 — 评分引擎：为智能体发布计算 AIVSS，并把分数送入工单和 SSVC 处置队列的产品",
        "• 论点 2 — 对照软件：为跨国安全买方提供 AIVSS、AIUC-1、MAESTRO 与 OWASP 智能体 Top 10 的同一套映射",
        "• 论点 3 — 发布门禁：v1 冻结后，AIVSS 分数超过设定阈值就阻断发布；买方是美、欧、中项目的发布负责人",
        "• 陷阱 — 在 v1 冻结前交付评分界面；方法一改就要返工，买方不会采信这个分数",
        "• 不宜投 — v1 成为公开标准后，仍拒绝对照 AIVSS、AIUC-1 和 MAESTRO 的专有「AI 风险分」",
    ],
}


def run(args, input_text=None, check=True):
    r = subprocess.run(
        args,
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        env=ENV,
        encoding="utf-8",
    )
    if check and r.returncode:
        sys.stderr.write(r.stderr or "")
        sys.stderr.write(r.stdout or "")
        raise SystemExit(r.returncode)
    return r


def main() -> None:
    for p in range(1, 11):
        assert len(REVISED_EN[p]) == len(REVISED_ZH[p]) == 7, p

    text = BUILD.read_text(encoding="utf-8")
    m_en = re.search(r"SLIDES_EN = (\[.*?\])\n\nSLIDES_ZH = ", text, re.S)
    m_zh = re.search(r"SLIDES_ZH = (\{.*?\})\n\nPHRASES = ", text, re.S)
    en = ast.literal_eval(m_en.group(1))
    zh = ast.literal_eval(m_zh.group(1))

    for s in en:
        m = re.match(r"P(\d+)\s*—", s["raw_lines"][0])
        if not m:
            continue
        pnum = int(m.group(1))
        s["raw_lines"] = REVISED_EN[pnum]
        zh[str(s["number"])] = REVISED_ZH[pnum]

    # Update thesis map table to match revised surfaces
    for s in en:
        if s["raw_lines"][0].startswith("Thesis Map at a Glance"):
            s["raw_lines"] = [
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
                "| 9 | MAESTRO v2 | 7-layer tooling + adoption + training / avoid pre-release v2 or 10-layer badges |",
                "| 10 | AIVSS v1 | Scoring + crosswalk + release gates / avoid proprietary unmapped scores |",
            ]
            zh[str(s["number"])] = [
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
                "| 9 | MAESTRO v2 | 七层落地工具 + 采用 + 培训 / 不宜投未发布的 v2 或十层徽章 |",
                "| 10 | AIVSS v1 | 评分 + 对照 + 发布门禁 / 不宜投拒绝对照的专有分 |",
            ]

    def to_py(obj):
        s = json.dumps(obj, ensure_ascii=False, indent=4)
        return s.replace(": true", ": True").replace(": false", ": False").replace(": null", ": None")

    text2 = text[: m_en.start(1)] + to_py(en) + text[m_en.end(1) : m_zh.start(1)] + to_py(zh) + text[m_zh.end(1) :]
    BUILD.write_text(text2, encoding="utf-8")

    r = subprocess.run([sys.executable, str(ROOT / "build_slides.py")], cwd=ROOT, env=ENV)
    if r.returncode:
        raise SystemExit(r.returncode)
    r = subprocess.run([sys.executable, str(ROOT / "cleanup_slides.py")], cwd=ROOT, env=ENV)
    if r.returncode:
        raise SystemExit(r.returncode)

    shutil.copy2(ROOT / "slides.html", ROOT / "docs" / "slides.html")
    shutil.copy2(ROOT / "slides-zh.js", ROOT / "docs" / "slides-zh.js")

    html = (ROOT / "slides.html").read_text(encoding="utf-8")
    data = json.loads(re.search(r"const slidesData = (\[.*?\]);", html, re.S).group(1))
    zhjs = json.loads((ROOT / "slides-zh.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    for s in data:
        n = str(s["number"])
        assert len(zhjs["lines"][n]) == len(s["raw_lines"]), (n, s["raw_lines"][0])
        m = re.match(r"P(\d+)", s["raw_lines"][0])
        if m:
            p = int(m.group(1))
            assert s["raw_lines"] == REVISED_EN[p], (p, "EN mismatch")
            assert zhjs["lines"][n] == REVISED_ZH[p], (p, "ZH mismatch")
            print("OK", p)

    run(["git", "add", "-A"])
    if run(["git", "status", "--porcelain"]).stdout.strip():
        tree = run(["git", "write-tree"]).stdout.strip()
        head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
        msg = (
            "Review and tighten investor theses, pitfalls, and Chinese wording.\n"
            "\n"
            "Fixes overclaims, cross-slide duplicates, vague payers, and investor-facing ZH.\n"
        )
        new = run(["git", "commit-tree", tree, "-p", head], input_text=msg).stdout.strip()
        run(["git", "reset", "--soft", new])
        assert "Co-authored-by" not in run(["git", "log", "-1", "--format=%B"]).stdout
        run(["git", "push", "origin", "HEAD:main"])
        print("COMMIT", new)
    print("DONE")


if __name__ == "__main__":
    main()
