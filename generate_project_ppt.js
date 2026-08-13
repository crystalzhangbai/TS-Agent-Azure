const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'SRE Bridge Team';
pptx.company = 'Microsoft';
pptx.subject = 'SRE Bridge architecture and implementation';
pptx.title = 'SRE Bridge 项目架构与实现';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Segoe UI Semibold',
  bodyFontFace: 'Segoe UI',
  lang: 'zh-CN'
};

const colors = {
  bgDark: '0E1C36',
  bgLight: 'F4F7FB',
  primary: '1F6FEB',
  accent: '12B886',
  textDark: '102A43',
  textLight: 'E6EDF3',
  muted: '6C7A89',
  card: 'FFFFFF'
};

function addHeader(slide, title, subtitle = '') {
  slide.background = { color: colors.bgLight };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.75, fill: { color: colors.bgDark }, line: { color: colors.bgDark } });
  slide.addText(title, { x: 0.5, y: 0.15, w: 9.8, h: 0.35, color: colors.textLight, fontSize: 20, bold: true, margin: 0 });
  if (subtitle) {
    slide.addText(subtitle, { x: 0.5, y: 0.95, w: 12.2, h: 0.35, color: colors.muted, fontSize: 12, margin: 0 });
  }
}

function addCodeBlock(slide, code, x, y, w, h) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.04,
    fill: { color: '0B1220' },
    line: { color: '1F2937', pt: 1 }
  });
  slide.addText(code, {
    x: x + 0.18,
    y: y + 0.12,
    w: w - 0.36,
    h: h - 0.2,
    fontFace: 'Consolas',
    fontSize: 9,
    color: 'D1E7FF',
    breakLine: true,
    margin: 0,
    valign: 'top'
  });
}

// 1. Title
{
  const s = pptx.addSlide();
  s.background = { color: colors.bgDark };
  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.7, y: 0.9, w: 12.0, h: 5.7,
    rectRadius: 0.08,
    fill: { color: '12284C', transparency: 10 },
    line: { color: '274C77', pt: 1 }
  });
  s.addText('SRE Bridge 项目架构与实现', {
    x: 1.1, y: 1.45, w: 11.2, h: 0.8,
    fontSize: 42, bold: true, color: colors.textLight, margin: 0
  });
  s.addText('Teams + Bot Framework + MAF + Foundry + Skills', {
    x: 1.1, y: 2.35, w: 10.8, h: 0.5,
    fontSize: 18, color: 'BFD7FF', margin: 0
  });
  s.addText('覆盖内容：架构设计、代码结构、主要功能点、实现细节、后续 Action Plan', {
    x: 1.1, y: 3.0, w: 10.8, h: 0.45,
    fontSize: 14, color: 'C9D6E6', margin: 0
  });
  s.addText('Repository root: C:/ZhangBai/SRE/pythonsample-main/pythonsample-main', {
    x: 1.1, y: 5.9, w: 11, h: 0.3, fontSize: 10, color: '9FB3C8', margin: 0
  });
}

// 2. Architecture
{
  const s = pptx.addSlide();
  addHeader(s, '1) 架构设计概览', '数据流 + 控制流 + 运行形态');

  const y = 1.5;
  const h = 1.05;
  const nodes = [
    ['Teams User', 'Teams 群聊/@bot'],
    ['Azure Bot Service', '消息路由与鉴权'],
    ['bridge/app.py + bot.py', 'HTTP入口 + 会话消息处理'],
    ['bridge/brain_maf.py', 'MAF Agent + FoundryChatClient'],
    ['Tools + Skills', 'Azure VM/Kusto/Skill Loader']
  ];

  let x = 0.5;
  nodes.forEach((n, i) => {
    const w = i === 2 ? 2.5 : (i === 3 ? 2.5 : 2.2);
    s.addShape(pptx.ShapeType.roundRect, {
      x, y, w, h,
      rectRadius: 0.05,
      fill: { color: i % 2 === 0 ? 'E8F1FF' : 'EAFBF5' },
      line: { color: i % 2 === 0 ? '7AA2F7' : '63D2B0', pt: 1 }
    });
    s.addText(n[0], { x: x + 0.12, y: y + 0.15, w: w - 0.2, h: 0.28, fontSize: 13, bold: true, color: colors.textDark, margin: 0 });
    s.addText(n[1], { x: x + 0.12, y: y + 0.48, w: w - 0.2, h: 0.4, fontSize: 10, color: colors.muted, margin: 0 });
    if (i < nodes.length - 1) {
      s.addShape(pptx.ShapeType.chevron, {
        x: x + w + 0.08, y: y + 0.38, w: 0.24, h: 0.28,
        fill: { color: colors.primary }, line: { color: colors.primary }
      });
    }
    x += w + 0.45;
  });

  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.7, y: 3.1, w: 12.0, h: 2.9,
    rectRadius: 0.05,
    fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 }
  });
  s.addText('运行模式（当前）', { x: 1.0, y: 3.35, w: 2.2, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText([
    { text: '• 本地 PC 运行 bridge/app.py，监听 localhost:3978\n', options: { breakLine: true } },
    { text: '• devtunnel 暴露公网 URL，Azure Bot endpoint 指向 /api/messages\n', options: { breakLine: true } },
    { text: '• Foundry 调用通过专用 SP（FOUNDRY_*），与客户订阅 SP 分离\n', options: { breakLine: true } },
    { text: '• launch-bridge.ps1 可自动起服务、起 tunnel、自动更新 endpoint' }
  ], { x: 1.0, y: 3.75, w: 11.3, h: 1.9, fontSize: 12, color: colors.textDark, margin: 0 });
}

// 3. Code structure
{
  const s = pptx.addSlide();
  addHeader(s, '2) 代码结构与职责分层', '核心目录 + 关键文件职责');

  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 1.25, w: 6.25, h: 4.95, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });
  s.addShape(pptx.ShapeType.roundRect, { x: 6.95, y: 1.25, w: 5.85, h: 4.95, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });

  s.addText('项目结构（简化）', { x: 0.85, y: 1.5, w: 3, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  const tree = [
    'pythonsample-main/',
    '  bootstrap.ps1',
    '  bridge/',
    '    app.py',
    '    bot.py',
    '    brain_maf.py',
    '    config.py',
    '    skill_loader.py',
    '    agent_trace.py',
    '    tools/',
    '      azure_vm.py',
    '      kusto.py',
    '    skills/',
    '    launch-bridge.ps1',
    '    stop-bridge.ps1'
  ].join('\n');
  addCodeBlock(s, tree, 0.85, 1.9, 5.75, 4.05);

  s.addText('关键职责映射', { x: 7.25, y: 1.5, w: 2.8, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText([
    { text: '• bridge/app.py: aiohttp server, /api/messages, health\n', options: { breakLine: true } },
    { text: '• bridge/bot.py: Teams message handler + conversation id\n', options: { breakLine: true } },
    { text: '• bridge/brain_maf.py: Agent runtime, tool registry, Foundry credential\n', options: { breakLine: true } },
    { text: '• bridge/skill_loader.py: SKILL.md frontmatter 解析，索引+按需加载\n', options: { breakLine: true } },
    { text: '• bridge/tools/azure_vm.py: IP->VM + Monitor metrics\n', options: { breakLine: true } },
    { text: '• bridge/tools/kusto.py: internal Kusto query（公司 AAD）\n', options: { breakLine: true } },
    { text: '• bridge/launch-bridge.ps1: 一键启动与 endpoint 更新' }
  ], { x: 7.25, y: 1.95, w: 5.2, h: 3.9, fontSize: 11, color: colors.textDark, margin: 0 });
}

// 4. Core feature 1
{
  const s = pptx.addSlide();
  addHeader(s, '3) 功能点A：Teams 多轮会话到 MAF 调度', '入口、会话ID、工具执行、异常回传');

  s.addText('实现路径（绝对路径）', { x: 0.7, y: 1.08, w: 4.0, h: 0.25, fontSize: 11, bold: true, color: colors.muted });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/bot.py', { x: 0.7, y: 1.3, w: 6.1, h: 0.25, fontSize: 10, color: colors.primary });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/brain_maf.py', { x: 0.7, y: 1.55, w: 6.1, h: 0.25, fontSize: 10, color: colors.primary });

  const code = [
    'text = TurnContext.remove_recipient_mention(turn_context.activity)',
    'conv_id = turn_context.activity.conversation.id',
    'reply = await run_brain(text, conv_id)',
    '',
    'session = _sessions.get(conversation_id) or AgentSession()',
    'response = await agent.run(user_text, session=session)',
    'return text + format_trace()'
  ].join('\n');
  addCodeBlock(s, code, 0.7, 1.95, 6.0, 2.95);

  s.addShape(pptx.ShapeType.roundRect, { x: 7.0, y: 1.95, w: 5.6, h: 2.95, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });
  s.addText('设计意图', { x: 7.25, y: 2.2, w: 2.2, h: 0.3, fontSize: 13, bold: true, color: colors.textDark });
  s.addText([
    { text: '• Teams 消息先标准化，再进入 run_brain\n', options: { breakLine: true } },
    { text: '• 以 conversation.id 绑定 AgentSession，支持多轮记忆\n', options: { breakLine: true } },
    { text: '• 通过 on_message_activity 的 try/except 防止服务崩溃\n', options: { breakLine: true } },
    { text: '• format_trace() 将工具调用链反馈给工程师，增强可观测性' }
  ], { x: 7.25, y: 2.55, w: 5.1, h: 2.2, fontSize: 11, color: colors.textDark, margin: 0 });
}

// 5. Core feature 2
{
  const s = pptx.addSlide();
  addHeader(s, '4) 功能点B：Foundry 专用 SP + 职责隔离', '避免凭据混用，降低“看起来能跑，实际上越权”风险');

  s.addText('实现路径（绝对路径）', { x: 0.7, y: 1.08, w: 4.0, h: 0.25, fontSize: 11, bold: true, color: colors.muted });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/brain_maf.py', { x: 0.7, y: 1.3, w: 8, h: 0.25, fontSize: 10, color: colors.primary });

  const code = [
    'tenant_id = (CONFIG.FOUNDRY_TENANT_ID or "").strip()',
    'client_id = (CONFIG.FOUNDRY_CLIENT_ID or "").strip()',
    'client_secret = (CONFIG.FOUNDRY_CLIENT_SECRET or "").strip()',
    'if any(configured) and not all(configured): raise ValueError(...)',
    'if not all(configured): raise ValueError(...)',
    'return ClientSecretCredential(...)',
    '',
    'client = FoundryChatClient(project_endpoint=PROJECT_ENDPOINT,',
    '                          model=CONFIG.AOAI_MODEL,',
    '                          credential=_build_foundry_credential())'
  ].join('\n');
  addCodeBlock(s, code, 0.7, 1.95, 6.2, 3.4);

  s.addShape(pptx.ShapeType.roundRect, { x: 7.1, y: 1.95, w: 5.4, h: 3.4, rectRadius: 0.05, fill: { color: 'FFFDF5' }, line: { color: 'F2D9A6', pt: 1 } });
  s.addText('设计要点', { x: 7.35, y: 2.2, w: 2, h: 0.3, fontSize: 13, bold: true, color: '7A4A00' });
  s.addText([
    { text: '• 强制 Foundry 使用专用 SP（FOUNDRY_*）\n', options: { breakLine: true } },
    { text: '• 禁止静默回退到本机 Azure CLI 身份\n', options: { breakLine: true } },
    { text: '• 变量缺失时抛出清晰错误，减少排障成本\n', options: { breakLine: true } },
    { text: '• 客户订阅 SP 与内部 Foundry/Kusto 凭据隔离' }
  ], { x: 7.35, y: 2.55, w: 4.95, h: 2.6, fontSize: 11, color: '6B4F1D', margin: 0 });
}

// 6. Core feature 3
{
  const s = pptx.addSlide();
  addHeader(s, '5) 功能点C：Skill 可插拔 + Progressive Disclosure', '把静态 prompt 升级为可维护的技能知识层');

  s.addText('实现路径（绝对路径）', { x: 0.7, y: 1.08, w: 4.0, h: 0.25, fontSize: 11, bold: true, color: colors.muted });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/skill_loader.py', { x: 0.7, y: 1.3, w: 7.5, h: 0.25, fontSize: 10, color: colors.primary });

  const code = [
    'def list_skills():',
    '  # 扫描 skills/*/SKILL.md',
    'def build_skill_index():',
    '  # name + description 注入 system prompt',
    'def load_skill(skill_name):',
    '  # 按需加载 skill 正文',
    'def read_skill_file(skill_name, relative_path):',
    '  # 读取 references/* 并做路径越界防护'
  ].join('\n');
  addCodeBlock(s, code, 0.7, 1.95, 5.8, 2.9);

  s.addShape(pptx.ShapeType.roundRect, { x: 6.75, y: 1.95, w: 5.75, h: 2.9, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });
  s.addText('为什么不是“全量塞提示词”？', { x: 7.0, y: 2.2, w: 4.8, h: 0.3, fontSize: 13, bold: true, color: colors.textDark });
  s.addText([
    { text: '• 全量拼接 token 成本高，且上下文噪声大\n', options: { breakLine: true } },
    { text: '• 通过 skill index 先路由，再按需 load，效率更高\n', options: { breakLine: true } },
    { text: '• 便于团队独立维护 references/playbook，无需改核心代码\n', options: { breakLine: true } },
    { text: '• 可平滑演进到 workflow/state machine（下一步计划）' }
  ], { x: 7.0, y: 2.55, w: 5.25, h: 2.1, fontSize: 11, color: colors.textDark, margin: 0 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 5.05, w: 11.8, h: 1.0, rectRadius: 0.05, fill: { color: 'EAFBF5' }, line: { color: '8EE0C2', pt: 1 } });
  s.addText('当前关键 skill 目录：C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/skills/', { x: 0.95, y: 5.35, w: 11.3, h: 0.3, fontSize: 10, color: '116149', bold: true });
}

// 7. Feature 4
{
  const s = pptx.addSlide();
  addHeader(s, '6) 功能点D：工具层设计（VM/Kusto/Trace）', '从 IP 定位到指标、内部遥测、可观测调用链');

  s.addShape(pptx.ShapeType.roundRect, { x: 0.6, y: 1.2, w: 4.15, h: 4.9, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });
  s.addShape(pptx.ShapeType.roundRect, { x: 4.95, y: 1.2, w: 4.15, h: 4.9, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });
  s.addShape(pptx.ShapeType.roundRect, { x: 9.3, y: 1.2, w: 3.45, h: 4.9, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });

  s.addText('Azure VM Tool', { x: 0.85, y: 1.45, w: 3.6, h: 0.25, fontSize: 13, bold: true, color: colors.textDark });
  s.addText('path: .../bridge/tools/azure_vm.py', { x: 0.85, y: 1.72, w: 3.8, h: 0.22, fontSize: 9, color: colors.primary });
  s.addText('• find_vm_by_private_ip\n• get_vm_metrics\n• customers.json 多环境映射\n• credential_for_subscription 路由', { x: 0.85, y: 2.0, w: 3.7, h: 1.8, fontSize: 10.5, color: colors.textDark, margin: 0 });

  s.addText('Kusto Tool', { x: 5.2, y: 1.45, w: 2.5, h: 0.25, fontSize: 13, bold: true, color: colors.textDark });
  s.addText('path: .../bridge/tools/kusto.py', { x: 5.2, y: 1.72, w: 3.7, h: 0.22, fontSize: 9, color: colors.primary });
  s.addText('• run_kusto_query\n• DefaultAzureCredential（公司AAD）\n• 与客户SP隔离\n• 错误统一 JSON 回传', { x: 5.2, y: 2.0, w: 3.7, h: 1.8, fontSize: 10.5, color: colors.textDark, margin: 0 });

  s.addText('Trace', { x: 9.55, y: 1.45, w: 2.0, h: 0.25, fontSize: 13, bold: true, color: colors.textDark });
  s.addText('path: .../bridge/agent_trace.py', { x: 9.55, y: 1.72, w: 2.9, h: 0.22, fontSize: 9, color: colors.primary });
  s.addText('• start_trace\n• traced(fn)\n• format_trace\n• Teams 回复附带调用链', { x: 9.55, y: 2.0, w: 2.95, h: 1.7, fontSize: 10.5, color: colors.textDark, margin: 0 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.85, y: 4.15, w: 11.8, h: 1.65, rectRadius: 0.05, fill: { color: 'EEF4FF' }, line: { color: '9FBCEB', pt: 1 } });
  s.addText('工具编排入口（brain_maf.py）', { x: 1.1, y: 4.35, w: 4.0, h: 0.3, fontSize: 12, bold: true, color: colors.textDark });
  addCodeBlock(s,
    'tools=[\n  traced(find_vm_by_private_ip),\n  traced(get_vm_metrics),\n  traced(run_kusto_query),\n  traced(build_adx_deeplink),\n  traced(load_skill), traced(read_skill_file)\n]',
    1.0, 4.7, 10.8, 0.95
  );
}

// 8. Deployment & Ops
{
  const s = pptx.addSlide();
  addHeader(s, '7) 同事侧一键运行设计', 'bootstrap + launch + stop，尽量降低迁移门槛');

  s.addText('关键脚本（绝对路径）', { x: 0.7, y: 1.1, w: 3.5, h: 0.3, fontSize: 11, bold: true, color: colors.muted });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bootstrap.ps1', { x: 0.7, y: 1.35, w: 7.0, h: 0.22, fontSize: 10, color: colors.primary });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/launch-bridge.ps1', { x: 0.7, y: 1.58, w: 7.6, h: 0.22, fontSize: 10, color: colors.primary });
  s.addText('C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/stop-bridge.ps1', { x: 0.7, y: 1.81, w: 7.3, h: 0.22, fontSize: 10, color: colors.primary });

  const flowCode = [
    '1) bootstrap.ps1',
    '   - install Python/AzureCLI/devtunnel',
    '2) devtunnel user login',
    '3) bridge/launch-bridge.ps1',
    '   - create .venv + pip install',
    '   - kill old 3978 listener',
    '   - start app.py + start devtunnel',
    '   - update Azure Bot endpoint via MGMT_SP_* (or az)',
    '4) bridge/stop-bridge.ps1'
  ].join('\n');
  addCodeBlock(s, flowCode, 0.7, 2.2, 6.4, 3.6);

  s.addShape(pptx.ShapeType.roundRect, { x: 7.35, y: 2.2, w: 5.3, h: 3.6, rectRadius: 0.05, fill: { color: 'FFFDF5' }, line: { color: 'F2D9A6', pt: 1 } });
  s.addText('当前限制与注意', { x: 7.6, y: 2.45, w: 2.4, h: 0.3, fontSize: 13, bold: true, color: '7A4A00' });
  s.addText([
    { text: '• 本地 + tunnel 形态非长期生产（稳定性受PC与网络影响）\n', options: { breakLine: true } },
    { text: '• endpoint 只有一个生效，同一时刻只能指向一个运行节点\n', options: { breakLine: true } },
    { text: '• 建议后续迁移到 Azure VM/Container Apps 固定公网入口\n', options: { breakLine: true } },
    { text: '• secrets 管理建议逐步切到 Key Vault + Managed Identity' }
  ], { x: 7.6, y: 2.85, w: 4.85, h: 2.6, fontSize: 11, color: '6B4F1D', margin: 0 });
}

// 9. Action plan
{
  const s = pptx.addSlide();
  addHeader(s, '8) Action Plan（改进方向）', '从 Prompt+Tools 升级到 Workflow 驱动执行');

  s.addShape(pptx.ShapeType.roundRect, { x: 0.6, y: 1.2, w: 12.1, h: 4.95, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });

  s.addText('A. Skill 从“提示词注入”演进到 Workflow 状态机', { x: 0.95, y: 1.5, w: 11.4, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText('将 triage / evidence / hypothesis / verification 建模为有向图，节点绑定 tool + guardrail，输出结构化RCA对象。', { x: 1.0, y: 1.85, w: 11.2, h: 0.35, fontSize: 11, color: colors.muted });

  s.addText('B. 会话持久化与审计', { x: 0.95, y: 2.35, w: 4.0, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText('将 _sessions 从内存迁移到 Redis/Cosmos DB，支持重启续聊、审计、回放。', { x: 1.0, y: 2.68, w: 11.0, h: 0.35, fontSize: 11, color: colors.muted });

  s.addText('C. 身份模型升级（OBO）', { x: 0.95, y: 3.18, w: 4.0, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText('对内部 Kusto/ICM 使用发问人 OBO token，减少“共享工程师账号代理”风险。', { x: 1.0, y: 3.52, w: 11.0, h: 0.35, fontSize: 11, color: colors.muted });

  s.addText('D. 部署形态升级', { x: 0.95, y: 4.02, w: 3.8, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText('从本地+tunnel 迁移到 Azure VM/App Service/Container Apps，固定 443 endpoint + 自动扩缩容。', { x: 1.0, y: 4.35, w: 11.0, h: 0.35, fontSize: 11, color: colors.muted });

  s.addText('E. Skill 工程化', { x: 0.95, y: 4.85, w: 3.8, h: 0.3, fontSize: 14, bold: true, color: colors.textDark });
  s.addText('引入 skill lint/test：frontmatter schema 校验、引用完整性检查、样例回归。', { x: 1.0, y: 5.18, w: 11.0, h: 0.35, fontSize: 11, color: colors.muted });
}

// 10. Appendix with code references
{
  const s = pptx.addSlide();
  addHeader(s, '附录：关键源码引用（绝对路径）', '可直接用于 code walkthrough');

  const refs = [
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/app.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/bot.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/brain_maf.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/skill_loader.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/tools/azure_vm.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/tools/kusto.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/agent_trace.py',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bridge/launch-bridge.ps1',
    'C:/ZhangBai/SRE/pythonsample-main/pythonsample-main/bootstrap.ps1'
  ];

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.25, w: 12.0, h: 4.9, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'D4E0F0', pt: 1 } });
  s.addText(refs.map(r => `• ${r}`).join('\n'), {
    x: 1.0, y: 1.55, w: 11.4, h: 4.2, fontSize: 11, color: colors.textDark, margin: 0
  });
}

pptx.writeFile({ fileName: 'SRE-Bridge-Architecture-Design.pptx' });
