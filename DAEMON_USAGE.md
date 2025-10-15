# 网格交易系统 - 后台运行指南

## 🚀 快速开始

### 前置要求

如果您使用Python虚拟环境（推荐），请确保：
- 虚拟环境位于 `bot/` 目录下
- 激活脚本位于 `bot/bin/activate`

脚本会自动检测并激活虚拟环境！

### 方法1：使用管理脚本（推荐）

```bash
# 1. 给脚本添加执行权限
chmod +x grid-trader.sh

# 2. 启动服务（自动激活虚拟环境）
./grid-trader.sh start

# 3. 查看状态
./grid-trader.sh status

# 4. 查看日志
./grid-trader.sh logs

# 5. 停止服务
./grid-trader.sh stop
```

### 方法2：直接使用Python命令

```bash
# 后台运行
python main.py --daemon

# 后台运行并指定PID文件
python main.py --daemon --pid-file /var/run/grid-trader.pid

# 设置日志级别为DEBUG
python main.py --daemon --log-level DEBUG

# 前台运行（调试用）
python main.py

# 查看帮助
python main.py --help
```

---

## 📋 管理脚本命令

### 启动服务
```bash
./grid-trader.sh start
```
输出示例：
```
[INFO] 正在启动网格交易系统...
启动守护进程...
PID文件: /path/to/grid-trader.pid
日志文件: trading_system.log
日志级别: INFO
[SUCCESS] 服务启动成功 (PID: 12345)
[INFO] 日志文件: /path/to/trading_system.log
[INFO] PID文件: /path/to/grid-trader.pid
```

### 停止服务
```bash
./grid-trader.sh stop
```

### 重启服务
```bash
./grid-trader.sh restart
```

### 查看状态
```bash
./grid-trader.sh status
```
输出示例：
```
================================
  网格交易系统状态
================================
[SUCCESS] 服务正在运行
  PID: 12345
  PID文件: /path/to/grid-trader.pid
  日志文件: /path/to/trading_system.log

进程信息:
  PID  PPID CMD                         %CPU %MEM     ELAPSED
12345     1 python main.py --daemon      2.5  1.2    01:23:45

最近的日志 (最后20行):
--------------------------------
2025-10-15 10:50:00 | INFO     | GridTrader           | 网格交易系统启动
...
```

### 查看日志
```bash
# 查看最后50行日志（默认）
./grid-trader.sh logs

# 查看最后100行日志
./grid-trader.sh logs 100

# 实时查看日志（类似tail -f）
./grid-trader.sh logs -f
```

---

## 🔧 命令行参数说明

### Python main.py 参数

| 参数 | 短选项 | 说明 | 默认值 |
|------|--------|------|--------|
| `--daemon` | `-d` | 守护进程模式运行（后台） | 关闭 |
| `--pid-file` | `-p` | PID文件路径 | `grid-trader.pid` |
| `--log-level` | `-l` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `--help` | `-h` | 显示帮助信息 | - |

### 示例

```bash
# 完整参数示例
python main.py \
    --daemon \
    --pid-file /var/run/grid-trader.pid \
    --log-level INFO

# 简写形式
python main.py -d -p /var/run/grid-trader.pid -l INFO
```

---

## 🐍 Python虚拟环境配置

### 自动检测

脚本会自动检测并激活虚拟环境：
- **默认路径**: `bot/bin/activate`
- **自动激活**: 启动时自动执行 `source bot/bin/activate`
- **回退机制**: 如果虚拟环境不存在，使用系统Python

### 修改虚拟环境路径

如果您的虚拟环境在其他位置，编辑 `grid-trader.sh`：

```bash
# 修改第9行
VENV_DIR="$SCRIPT_DIR/bot"  # 改为您的虚拟环境路径

# 例如：
VENV_DIR="$SCRIPT_DIR/venv"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_DIR="/opt/python-envs/trading-bot"
```

### 创建虚拟环境

如果还没有虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv bot

# 激活虚拟环境
source bot/bin/activate

# 安装依赖
pip install -r requirements.txt

# 测试运行
python main.py
```

### 验证虚拟环境

启动服务时会显示Python环境信息：

```bash
$ ./grid-trader.sh start
[INFO] 正在启动网格交易系统...
[INFO] 使用虚拟环境: /path/to/okx-grid-bot/bot
[INFO] Python命令: python
[INFO] Python版本: Python 3.9.7
[SUCCESS] 服务启动成功 (PID: 12345)
```

---

## 📁 文件说明

### PID文件
- **默认位置**: `grid-trader.pid`
- **作用**: 记录守护进程的进程ID
- **内容**: 单行数字，例如 `12345`

### 日志文件
- **位置**: `trading_system.log`
- **格式**: 按天轮转，保留7天
- **命名**: 
  - 当前: `trading_system.log`
  - 历史: `trading_system.log.2025-10-14`

---

## 🔍 进程管理

### 查看进程
```bash
# 通过PID文件查看
cat grid-trader.pid

# 查看进程详情
ps aux | grep "python main.py"

# 查看进程树
pstree -p $(cat grid-trader.pid)
```

### 手动停止进程
```bash
# 优雅停止（推荐）
kill -TERM $(cat grid-trader.pid)

# 强制停止（不推荐）
kill -KILL $(cat grid-trader.pid)
```

### 检查进程是否运行
```bash
if ps -p $(cat grid-trader.pid) > /dev/null 2>&1; then
    echo "进程正在运行"
else
    echo "进程未运行"
fi
```

---

## 📊 日志查看技巧

### 实时查看日志
```bash
tail -f trading_system.log
```

### 过滤特定内容
```bash
# 只看ERROR级别
grep "ERROR" trading_system.log

# 只看交易相关
grep "订单" trading_system.log

# 查看最近的买入信号
grep "买入信号" trading_system.log | tail -n 10
```

### 日志分析
```bash
# 统计ERROR数量
grep -c "ERROR" trading_system.log

# 查看今天的日志
grep "$(date +%Y-%m-%d)" trading_system.log

# 查看最近1小时的日志
grep "$(date +%Y-%m-%d\ %H)" trading_system.log
```

---

## 🔄 开机自启动

### 使用systemd（推荐）

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
ExecStart=/usr/bin/python3 /path/to/okx-grid-bot/main.py --daemon --pid-file /var/run/grid-trader.pid
PIDFile=/var/run/grid-trader.pid
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
```

4. 管理服务：
```bash
# 查看状态
sudo systemctl status grid-trader

# 停止服务
sudo systemctl stop grid-trader

# 重启服务
sudo systemctl restart grid-trader

# 查看日志
sudo journalctl -u grid-trader -f
```

### 使用crontab

```bash
# 编辑crontab
crontab -e

# 添加开机启动
@reboot cd /path/to/okx-grid-bot && python main.py --daemon
```

---

## ⚠️ 注意事项

### 1. 权限问题
- 确保有权限写入PID文件和日志文件
- 如果使用 `/var/run/`，可能需要root权限

### 2. 环境变量
- 守护进程模式下，确保 `.env` 文件在正确位置
- 或者在启动前 `export` 必要的环境变量

### 3. 工作目录
- 守护进程会切换到 `/` 目录
- 所有路径最好使用绝对路径

### 4. 日志轮转
- 日志文件每天午夜自动轮转
- 保留最近7天的日志
- 旧日志自动删除

### 5. 进程监控
- 建议配合监控工具（如 supervisor、monit）
- 或使用 systemd 的自动重启功能

---

## 🐛 故障排查

### 问题1：启动失败
```bash
# 检查日志
tail -n 50 trading_system.log

# 检查Python环境
python --version
pip list | grep okx

# 检查配置文件
cat .env
```

### 问题2：进程意外退出
```bash
# 查看系统日志
dmesg | tail
journalctl -xe

# 检查是否被OOM杀死
grep -i "killed process" /var/log/syslog
```

### 问题3：无法停止进程
```bash
# 查看进程状态
ps aux | grep python

# 强制杀死
kill -9 $(cat grid-trader.pid)

# 清理PID文件
rm -f grid-trader.pid
```

---

## 📞 获取帮助

```bash
# Python命令帮助
python main.py --help

# 管理脚本帮助
./grid-trader.sh help
```

---

## ✅ 最佳实践

1. **使用管理脚本** - 简化操作，避免手动管理
2. **配置systemd** - 实现开机自启和自动重启
3. **定期查看日志** - 及时发现问题
4. **监控进程状态** - 确保服务正常运行
5. **备份配置文件** - 防止配置丢失

---

## 🎯 完整工作流示例

```bash
# 1. 首次部署
cd /opt/okx-grid-bot
chmod +x grid-trader.sh
cp env.example .env
vim .env  # 配置API密钥

# 2. 启动服务
./grid-trader.sh start

# 3. 验证运行
./grid-trader.sh status
./grid-trader.sh logs -f  # 观察几分钟

# 4. 配置开机自启（可选）
sudo cp grid-trader.service /etc/systemd/system/
sudo systemctl enable grid-trader

# 5. 日常维护
./grid-trader.sh logs 100  # 每天查看日志
./grid-trader.sh restart   # 需要时重启
```

---

祝您交易顺利！🚀
