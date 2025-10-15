# OKX自动化网格交易机器人

这是一个基于 Python 的自动化交易程序，专为OKX交易所的 OKB-USDT 交易对设计。该程序采用网格交易策略，旨在通过动态调整网格和仓位来捕捉市场波动，并内置风险管理机制。

## 核心功能

*   **自动化网格交易**: 针对 OKB-USDT 交易对执行网格买卖策略。
*   **动态网格调整**: 根据市场波动率自动调整网格大小 (`config.py` 中的 `GRID_PARAMS`)。
*   **风险管理**:
    *   最大回撤限制 (`MAX_DRAWDOWN`)
    *   每日亏损限制 (`DAILY_LOSS_LIMIT`)
    *   最大仓位比例限制 (`MAX_POSITION_RATIO`)
*   **Web 用户界面**: 提供一个简单的 Web 界面 (通过 `web_server.py`)，用于实时监控交易状态、账户信息、订单和调整配置。
*   **状态持久化**: 将交易状态保存到 `data/` 目录下的 JSON 文件中，以便重启后恢复。
*   **通知推送**: 可通过企业微信机器人发送重要事件和错误通知 (`WECHAT_WEBHOOK_KEY`)。
*   **日志记录**: 详细的运行日志记录在 `trading_system.log` 文件中。

## 环境要求

*   Python 3.8+
*   依赖库见 `requirements.txt` 文件。
*   **最低服务器配置建议**：
    *   CPU：1核及以上（推荐2核）
    *   内存：512MB 及以上（推荐1GB或2GB）
    *   硬盘：500MB 可用空间
    *   操作系统：Windows、Linux 或 macOS
    *   网络：需能访问OKX API和企业微信（如启用通知）
    *   网络建议：建议选择延迟低的网络，如日本等地区。

## 安装步骤

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/tingxifa/okx-grid-bot
    cd okx-grid-bot
    ```

2.  **创建并激活虚拟环境** (推荐):
    *   **Windows**:
        ```bash
        python -m venv bot
        .\bot\Scripts\activate
        ```
    *   **Linux / macOS**:
        ```bash
        python3 -m venv bot
        source bot/bin/activate
        ```
    
    > 💡 **提示**: 使用 `bot` 作为虚拟环境名称，管理脚本会自动识别并激活。

3.  **安装依赖**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## 配置

1.  **创建 `.env` 文件**:
    在项目根目录下创建一个名为 `.env` 的文件。

2.  **配置环境变量**:
    在 `.env` 文件中添加以下必要的环境变量，并填入你的信息：
    ```dotenv
    # OKX API (必须)
    OKX_API_KEY=YOUR_OKX_API_KEY
    OKX_SECRET_KEY=YOUR_OKX_SECRET_KEY
    OKX_PASSPHRASE=YOUR_OKX_PASSPHRASE

    # 企业微信机器人 Webhook Key (可选, 用于消息推送)
    WECHAT_WEBHOOK_KEY=YOUR_WECHAT_WEBHOOK_KEY

    # 初始设置 (可选, 影响首次运行和统计)
    # 如不设置，INITIAL_PRINCIPAL 和 INITIAL_BASE_PRICE 默认为 0
    INITIAL_PRINCIPAL=1000.0  # 你的初始总资产 (USDT)
    INITIAL_BASE_PRICE=600.0   # 你认为合适的初始基准价格 (用于首次启动确定方向)
    ```
    *   **重要**: 确保你的OKX API Key 具有现货交易权限，但**不要**开启提现权限。

3.  **调整交易参数 (可选)**:
    你可以根据自己的策略需求修改 `config.py` 文件中的参数，例如：
    *   `BASE_SYMBOL` : 'OKB'  # 基础币种
    *   `QUOTE_SYMBOL` : 'USDT'  # 计价币种
    *   `INITIAL_GRID`: 初始网格大小 (%)
    *   `MIN_TRADE_AMOUNT`: 最小交易金额 (USDT)
    *   `MAX_POSITION_RATIO`, `MIN_POSITION_RATIO`: 最大/最小仓位比例
    *   风险参数 (`MAX_DRAWDOWN`, `DAILY_LOSS_LIMIT`)
    *   波动率与网格对应关系 (`GRID_PARAMS['volatility_threshold']`)

## 运行方式

### 方式1：前台运行（开发/调试）

在激活虚拟环境的项目根目录下运行主程序：

```bash
# 激活虚拟环境
source bot/bin/activate  # Linux/Mac
# 或 .\bot\Scripts\activate  # Windows

# 运行程序
python main.py
```

### 方式2：后台运行（生产环境，仅Linux/Unix）

#### 使用管理脚本（推荐）

```bash
# 1. 添加执行权限
chmod +x grid-trader.sh

# 2. 启动服务（自动激活虚拟环境）
./grid-trader.sh start

# 3. 查看状态
./grid-trader.sh status

# 4. 查看日志
./grid-trader.sh logs

# 5. 实时查看日志
./grid-trader.sh logs -f

# 6. 停止服务
./grid-trader.sh stop

# 7. 重启服务
./grid-trader.sh restart
```

#### 直接使用Python命令

```bash
# 后台运行（守护进程）
python main.py --daemon

# 指定PID文件和日志级别
python main.py --daemon --pid-file /var/run/grid-trader.pid --log-level INFO

# 查看帮助
python main.py --help
```

#### 命令行参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-d, --daemon` | 后台运行（守护进程模式） | 关闭 |
| `-p, --pid-file` | PID文件路径 | `grid-trader.pid` |
| `-l, --log-level` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `-h, --help` | 显示帮助信息 | - |

### 方式3：使用systemd开机自启（Linux）

1. 创建服务文件：
```bash
sudo nano /etc/systemd/system/grid-trader.service
```

2. 添加以下内容：
```ini
[Unit]
Description=Grid Trading Bot
After=network.target

[Service]
Type=forking
User=your_username
WorkingDirectory=/path/to/okx-grid-bot
ExecStart=/usr/bin/python3 /path/to/okx-grid-bot/main.py --daemon
PIDFile=/path/to/okx-grid-bot/grid-trader.pid
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启用并启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable grid-trader
sudo systemctl start grid-trader
sudo systemctl status grid-trader
```


## docker部署

部署前请先根据上文说明配置好 .env 文件的环境变量。

```bash
# 拉取代码
#（如已在上方步骤完成可跳过）
git clone https://github.com/tingxifa/okx-grid-bot
cd okx-grid-bot
# 部署镜像
docker-compose up -d
```

*如需自定义端口，请修改 docker-compose.yml 中的端口映射。*

## Web 界面

程序启动后，会自动运行一个 Web 服务器。你可以通过浏览器访问以下地址来监控和管理交易机器人：

`http://127.0.0.1:58080`

*注意: 端口号 (58080) 在 `web_server.py` 中定义，如果无法访问请检查该文件。*

Web 界面可以让你查看当前状态、账户余额、持仓、挂单、历史记录，并可能提供一些手动操作或配置调整的功能。

## 日志管理

### 日志文件

- **位置**: `trading_system.log`
- **轮转**: 每天午夜自动轮转
- **保留**: 最近7天的日志
- **格式**: `YYYY-MM-DD HH:MM:SS | LEVEL | MODULE | MESSAGE`

### 查看日志

```bash
# 使用管理脚本查看
./grid-trader.sh logs          # 查看最后50行
./grid-trader.sh logs 100      # 查看最后100行
./grid-trader.sh logs -f       # 实时查看

# 直接使用命令
tail -f trading_system.log     # 实时查看
grep "ERROR" trading_system.log  # 过滤错误
grep "买入" trading_system.log   # 查看买入记录
```

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息（默认）
- **WARNING**: 警告信息
- **ERROR**: 错误信息

前台运行时，日志同时输出到控制台和文件；后台运行时，只输出到文件。

## Python虚拟环境

### 为什么使用虚拟环境？

- ✅ 隔离项目依赖，避免版本冲突
- ✅ 便于管理和部署
- ✅ 不污染系统Python环境

### 自动激活

管理脚本 `grid-trader.sh` 会自动检测并激活虚拟环境：
- **默认路径**: `bot/bin/activate`
- **自动激活**: 启动时自动执行 `source bot/bin/activate`
- **回退机制**: 如果虚拟环境不存在，使用系统Python

### 自定义虚拟环境路径

如果您的虚拟环境在其他位置，编辑 `grid-trader.sh` 第9行：

```bash
# 默认配置
VENV_DIR="$SCRIPT_DIR/bot"

# 修改为您的路径
VENV_DIR="$SCRIPT_DIR/venv"        # 使用 venv
VENV_DIR="$SCRIPT_DIR/.venv"       # 使用 .venv
VENV_DIR="/opt/envs/trading-bot"   # 绝对路径
```

或创建符号链接：
```bash
ln -s venv bot
```

## 进程管理

### 查看进程状态

```bash
# 使用管理脚本
./grid-trader.sh status

# 手动查看
cat grid-trader.pid
ps aux | grep "python main.py"
```

### 停止进程

```bash
# 使用管理脚本（推荐）
./grid-trader.sh stop

# 手动停止
kill -TERM $(cat grid-trader.pid)  # 优雅停止
kill -KILL $(cat grid-trader.pid)  # 强制停止
```

## 故障排查

### 问题1：启动失败

```bash
# 检查日志
tail -n 50 trading_system.log

# 检查Python环境
python --version
pip list | grep okx

# 检查配置
cat .env
```

### 问题2：找不到虚拟环境

```bash
# 检查虚拟环境是否存在
ls -la bot/bin/activate

# 如果不存在，创建虚拟环境
python3 -m venv bot
source bot/bin/activate
pip install -r requirements.txt
```

### 问题3：进程意外退出

```bash
# 查看系统日志
dmesg | tail
journalctl -xe

# 检查是否被OOM杀死
grep -i "killed process" /var/log/syslog
```

### 问题4：无法连接Web界面

- 检查端口是否被占用：`netstat -tulpn | grep 58080`
- 检查防火墙设置
- 确认程序正常运行：`./grid-trader.sh status`

## 注意事项

### ⚠️ 交易风险

*   所有交易决策均由程序自动执行，但市场存在固有风险
*   请务必了解策略原理和潜在风险，并自行承担交易结果
*   不建议在未充分理解和测试的情况下投入大量资金
*   建议先在模拟环境或小资金测试

### 🔐 安全建议

*   **API Key 安全**: 妥善保管你的 API Key 和 Secret，不要泄露给他人
*   **权限设置**: API Key 只开启现货交易权限，**不要**开启提现权限
*   **文件权限**: 确保 `.env` 文件权限设置为 `600`（仅所有者可读写）
*   **定期更新**: 定期更新依赖包，修复安全漏洞

### ⚙️ 配置建议

*   确保 `config.py` 和 `.env` 中的配置符合你的预期和风险承受能力
*   定期检查日志，及时发现异常
*   建议配置企业微信通知，及时接收重要事件
*   定期备份交易历史数据（`data/` 目录）

### 🖥️ 系统要求

*   **守护进程**: 仅支持 Linux/Unix 系统
*   **Windows用户**: 请使用前台运行或 `pythonw` 命令
*   **网络**: 建议使用低延迟网络（如日本等地区）
*   **监控**: 建议配合监控工具（如 supervisor、monit）或 systemd 自动重启

## 贡献

欢迎提交 Pull Requests 或 Issues 来改进项目。

## 快速参考

### 常用命令

```bash
# 启动服务
./grid-trader.sh start

# 查看状态
./grid-trader.sh status

# 查看日志
./grid-trader.sh logs -f

# 停止服务
./grid-trader.sh stop

# 重启服务
./grid-trader.sh restart
```

### 文件说明

| 文件/目录 | 说明 |
|-----------|------|
| `main.py` | 主程序入口 |
| `trader.py` | 交易逻辑核心 |
| `config.py` | 配置参数 |
| `.env` | 环境变量（API密钥等） |
| `grid-trader.sh` | 管理脚本 |
| `trading_system.log` | 运行日志 |
| `grid-trader.pid` | 进程ID文件 |
| `data/` | 交易历史数据 |
| `bot/` | Python虚拟环境 |

### 目录结构

```
okx-grid-bot/
├── bot/                    # 虚拟环境
│   ├── bin/
│   │   ├── activate       # 激活脚本
│   │   └── python
│   └── lib/
├── data/                   # 数据目录
│   ├── trade_history.json
│   └── archives/
├── main.py                 # 主程序
├── trader.py               # 交易逻辑
├── config.py               # 配置文件
├── exchange_client.py      # 交易所客户端
├── risk_manager.py         # 风险管理
├── order_tracker.py        # 订单跟踪
├── web_server.py           # Web服务器
├── helpers.py              # 辅助工具
├── grid-trader.sh          # 管理脚本
├── requirements.txt        # 依赖列表
├── .env                    # 环境变量
├── trading_system.log      # 运行日志
└── grid-trader.pid         # 进程ID
```

## 更新日志

### 最新优化

- ✅ 添加后台运行支持（守护进程）
- ✅ 添加管理脚本 `grid-trader.sh`
- ✅ 自动激活Python虚拟环境
- ✅ 优化日志系统（减少冗余输出）
- ✅ 添加命令行参数支持
- ✅ 修复risk_manager简单赚币余额计算
- ✅ 清理未使用代码（约300行）
- ✅ 增加订单历史保留数量（100→500条）
- ✅ 优化缓存系统（TTL: 0.2s→5s）

## 致谢

本项目基于 [GridBNB-USDT](https://github.com/EBOLABOY/GridBNB-USDT) 项目改编而来，特此感谢 [@EBOLABOY](https://github.com/EBOLABOY) 提供的优秀开源项目。

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

**祝您交易顺利！** 🚀

如有问题或建议，欢迎提交 Issue 或 Pull Request。
