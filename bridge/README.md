# SRE Bridge — Teams Bot (P1 MVP)

在 Teams 群聊里 @ 机器人，用自然语言排查 Azure 虚拟机问题。复用现有的
metric / resource graph 查询能力，并通过 MAF + skills 扩展内部排障流程。

```
Teams 群聊  →  Azure Bot Service  →  app.py  →  bot.py  →  brain_maf.py
                                                         │ tools / skills
                                                         ▼
                                            tools/* + skills/*
```

- **channel 层**：`app.py` + `bot.py`（Bot Framework，支持 1:1 / 群聊 / 频道）
- **大脑层**：`brain_maf.py`（Microsoft Agent Framework + Foundry）
- **能力层**：`tools/*` + `skills/*`

### Query / Deep 双路由（保留 Kusto 核心实现）

- **查询类问题**（例如 VM 在哪个 node/container、resource id、subscription/RG 映射）只走主 agent。
- **其他问题**先由主 agent 做资源定位与基线查询，再进入 **nanite 深度模式**（独立专家智能体）。
- 深度模式会保留 nanite 的独立结构：
  - `naniteagent-playground/naniteagent/agents/nanite-agent.md`
  - `naniteagent-playground/naniteagent/.mcp.json`
  - `naniteagent-playground/naniteagent/hooks/hooks.json`
  - `naniteagent-playground/naniteagent/skills/*`

可通过环境变量控制深度模式是否启用：

- `NANITE_DEEP_MODE_ENABLED=true`（默认）
- `NANITE_DEEP_MODE_ENABLED=false`（仅主 agent）

---

## 1. 安装依赖

```pwsh
cd bridge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. 配置环境变量

```pwsh
Copy-Item .env.example .env
```

编辑 `.env`：

| 变量 | 说明 |
|---|---|
| `MicrosoftAppId` / `MicrosoftAppPassword` | 来自 Azure Bot（`az bot create` 输出的 App ID + secret）|
| `MicrosoftAppType` | `MultiTenant` 或 `SingleTenant`，与创建 Bot 时一致 |
| `MicrosoftAppTenantId` | SingleTenant 时必填；MultiTenant 可留空 |
| `FOUNDRY_PROJECT_ENDPOINT` | Foundry project endpoint，例如 `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| `FOUNDRY_TENANT_ID/FOUNDRY_CLIENT_ID/FOUNDRY_CLIENT_SECRET` | **Foundry 专用 SP，必填** |
| `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_MODEL` | 你的 Azure OpenAI 部署 |
| `AZURE_OPENAI_API_KEY` | 填了用 Key；留空则用 `az login` 的 AAD 身份 |
| `AZURE_TENANT_ID/CLIENT_ID/CLIENT_SECRET` | 查 Azure 数据用的 SP；留空则用 `az login` |

完整的部署人自定义配置清单见 `DEPLOYER_CONFIGURATION.md`。其中列出了每个可变配置所在文件和行号，以及如何在 Azure Portal、Azure CLI、Teams manifest 或本地模板中找到/生成对应值。

> 数据面查询需要凭据对目标订阅有 **Reader** 权限。
> Foundry 大脑(`brain_maf.py`)只使用 `FOUNDRY_*` 这组 SP，不再回退本机 Azure CLI 身份。

## Public 仓库安全规则

不要提交真实部署值。以下文件只应存在于部署人本机，已经在 `.gitignore` 中忽略：

- `bridge/.env`
- `bridge/customers.json`
- `bridge/session_environments.json`
- `bridge/runtime/`

提交到 public 仓库的只能是模板和说明，例如 `.env.example`、`customers.example.json`、`session_environments.example.json` 和 `DEPLOYER_CONFIGURATION.md`。如果真实 secret 曾经进入 Git 历史，仅删除当前文件不够；需要先旋转 secret，再用 `git-filter-repo` 或 BFG 清理历史，然后开启 GitHub secret scanning / push protection。

## 给同事最少步骤运行（推荐）

同事机器只做这 3 步：

1. 在仓库根目录管理员运行：

```pwsh
.\bootstrap.cmd
```

2. 同事只需登录 dev tunnel（不需要 az login）：

```pwsh
devtunnel user login
```

3. 拿到 `bridge` 目录并执行：

```pwsh
cd .\bridge
.\run.cmd
```

> 兼容命令：`.\start-colleague.cmd`（等价于 `run.cmd`）。

如果你在 `.env` 里配置了 `MGMT_SP_*`，脚本会自动更新 Azure Bot endpoint；同事不需要 Azure 订阅权限。

你需要提前准备（由你自己完成）：

1. `FOUNDRY_*`（给 bot 调 Foundry）
2. `BOT_RESOURCE_ID`（要更新的 bot）
3. `MGMT_SP_*`（有权限更新该 bot endpoint）

停止命令：

```pwsh
.\stop-bridge.cmd
```

### 持续在线与开机自启动（推荐）

1. 持续守护（自动拉起 bot + tunnel，掉线后重试）：

```pwsh
.\bridge-daemon.ps1
```

2. 安装开机自启动任务（管理员 PowerShell）：

```pwsh
.\install-autostart.ps1
```

3. 卸载开机自启动：

```pwsh
.\uninstall-autostart.ps1
```

4. tunnel 频繁重建会触发 rate limit，脚本已内置重试；建议保持单个长运行进程，不要频繁重启。

旧方式（同事自己 az login）仍可用，但不再是推荐路径。

---

旧说明（保留）：

1. 安装 Python 3.12、Azure CLI、Dev Tunnel CLI，并 `az login`。
2. 拿到 `bridge` 目录（git clone 或你打包给他）。
3. 在 `bridge` 下执行：

```pwsh
.\launch-bridge.ps1
```

脚本会自动完成：

- 创建 `.venv` 并安装依赖
- 清理占用 3978 的旧进程
- 启动 bot server
- 启动 dev tunnel
- 自动更新 Azure Bot Messaging endpoint（需 `.env` 有 `BOT_RESOURCE_ID`）

停止命令：

```pwsh
.\stop-bridge.ps1
```

## 3. 本地运行 + 暴露公网

### 启动前 ToDo（先做，再起 bot server 和 dev tunnel）

推荐直接运行独立预检脚本（服务器侧）：

```pwsh
.\preflight-check.ps1
```

可选：若存在 TODO 则返回非 0 退出码（CI/自动化可用）：

```pwsh
.\preflight-check.ps1 -FailOnTodo
```

1. Kusto token tenant 预登录（按你们内部要求）：

```pwsh
az login --tenant 72f988bf-86f1-41af-91ab-2d7cd011db47
```

2. 如需固定 tenant，可在 `.env` 配置：

```env
KUSTO_AZ_TENANT_ID=72f988bf-86f1-41af-91ab-2d7cd011db47
```

3. delegated 客户会话在 Teams 里先预认证：

```text
/env <delegated环境名>
/auth login
```

4. 浏览器打开 bot 返回的 `verification_uri`，输入 `user_code`，完成登录后：

```text
/auth status
```

5. delegated 认证默认不做本地超时失效（no timeout）；可在 `.env` 设置有限时长：

```env
DELEGATED_AUTH_TTL_MINUTES=0
```

> 例如设置 `DELEGATED_AUTH_TTL_MINUTES=480` 表示 8 小时后要求重新 `/auth login`。

> `app.py` 启动时会自动打印同样的 Preflight TODO 清单。

```pwsh
.\start-bot.ps1       # 启动 bot server，监听 http://localhost:3978
```

另开一个终端，用 dev tunnel 暴露：

```pwsh
.\start-tunnel.ps1
```

如果你要复用已有 tunnel，可以指定 ID：

```pwsh
.\start-tunnel.ps1 -TunnelId <existing-tunnel-id>
```

拿到形如 `https://xxxx-3978.asse.devtunnels.ms` 的地址，把 **Messaging endpoint** 更新到 Azure Bot：

```pwsh
az bot update --resource-group <rg> --name <bot-name> `
  --endpoint "https://xxxx-3978.asse.devtunnels.ms/api/messages"
```

也可以用脚本检查本机服务、公网 tunnel 和 Azure Bot endpoint：

```pwsh
.\check-bridge.ps1 -TunnelBaseUrl https://xxxx-3978.asse.devtunnels.ms
```

## 4. 打包并安装 Teams App

1. 编辑 `teams-app/manifest.json`，把两处 `00000000-0000-0000-0000-000000000000` 换成你的 `MicrosoftAppId`。
2. 按 `teams-app/ICONS_README.md` 放入 `color.png`(192x192) 和 `outline.png`(32x32)。
3. 打包：

   ```pwsh
   cd teams-app
   Compress-Archive -Path manifest.json,color.png,outline.png -DestinationPath ..\sre-bridge.zip -Force
   ```

4. Teams → **Apps → Manage your apps → Upload a custom app** → 选 `sre-bridge.zip`。
5. 把 App 加到某个**群聊**或**频道**。

> 别人也能装：把 `sre-bridge.zip` 发给同事（同租户 Single-Tenant 即可），
> 或让 Teams 管理员上架到组织应用目录。

## 5. 试用

在群里 @ 机器人：

```
@SRE Bridge 帮我看下 10.94.109.31 在 5/19 上午8点50 有没有问题
@SRE Bridge 再看下这台机器的网络流量
```

## 新机器快速开始（先做这个）

> 目标：避免先跑 `run.cmd` 才发现缺少 az/devtunnel/python。

1. 在仓库根目录先安装基础依赖（仅首次需要）：

```pwsh
cd ..
.\bootstrap.cmd
```

2. 重新打开一个新的 PowerShell 窗口（让 PATH 刷新生效）。

3. 回到 `bridge` 目录，准备配置：

```pwsh
cd .\bridge
Copy-Item .env.example .env
```

4. 按需登录：

```pwsh
devtunnel user login
az login
```

5. 可选先预检，再启动：

```pwsh
.\preflight-check.ps1
.\run.cmd
```

说明：
- `preflight-check.ps1` 负责检查，不负责安装。
- `bootstrap.cmd` 才负责安装 Python / Azure CLI / devtunnel。
- 若 delegated 环境未配置 tenant，预检会提示 TODO，但默认仍可继续启动。
机器人会：定位 VM → 查指标 → 给中文结论；同一会话保持多轮上下文。

---

## 先用 Emulator 本地调试（可选，不用 Teams）

装 [Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator/releases)，
连 `http://localhost:3978/api/messages`（本地调试 App ID/Password 可留空），
直接对话验证大脑 + 工具是否正常，再接 Teams。

## 目录

| 文件 | 作用 |
|---|---|
| `app.py` | aiohttp server，`/api/messages` 入口 |
| `bot.py` | 消息处理，群聊/多用户/多轮 |
| `brain_maf.py` | MAF 会话与工具调度 |
| `tools/azure_vm.py` | 客户订阅 Azure 查询工具 |
| `start-bot.ps1` | 启动本机 bot server |
| `start-tunnel.ps1` | 启动新的或已有的 dev tunnel |
| `check-bridge.ps1` | 检查本机服务、tunnel 和 Azure Bot endpoint |
| `config.py` | 环境变量 |
| `teams-app/` | Teams App manifest + 图标 |
