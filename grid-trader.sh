#!/bin/bash
# 网格交易系统管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/grid-trader.pid"
LOG_FILE="$SCRIPT_DIR/trading_system.log"

# Python虚拟环境配置
VENV_DIR="$SCRIPT_DIR/bot"  # 虚拟环境目录
VENV_ACTIVATE="$VENV_DIR/bin/activate"  # 激活脚本

# 检查虚拟环境是否存在
if [ -f "$VENV_ACTIVATE" ]; then
    # 激活虚拟环境
    source "$VENV_ACTIVATE"
    PYTHON_CMD="python"  # 虚拟环境中使用python
else
    # 如果虚拟环境不存在，使用系统Python
    PYTHON_CMD="python3"
    print_warning "未找到虚拟环境: $VENV_DIR"
    print_info "使用系统Python: $PYTHON_CMD"
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查进程是否运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 启动服务
start() {
    print_info "正在启动网格交易系统..."
    
    if is_running; then
        print_warning "服务已经在运行中 (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # 显示使用的Python环境
    if [ -f "$VENV_ACTIVATE" ]; then
        print_info "使用虚拟环境: $VENV_DIR"
    fi
    print_info "Python命令: $PYTHON_CMD"
    print_info "Python版本: $($PYTHON_CMD --version 2>&1)"
    
    cd "$SCRIPT_DIR"
    
    # 如果使用虚拟环境，需要在子shell中激活并启动
    if [ -f "$VENV_ACTIVATE" ]; then
        # 使用bash -c确保虚拟环境在守护进程中也生效
        bash -c "source '$VENV_ACTIVATE' && $PYTHON_CMD main.py --daemon --pid-file '$PID_FILE'"
    else
        $PYTHON_CMD main.py --daemon --pid-file "$PID_FILE"
    fi
    
    sleep 2
    
    if is_running; then
        print_success "服务启动成功 (PID: $(cat $PID_FILE))"
        print_info "日志文件: $LOG_FILE"
        print_info "PID文件: $PID_FILE"
    else
        print_error "服务启动失败，请查看日志: $LOG_FILE"
        return 1
    fi
}

# 停止服务
stop() {
    print_info "正在停止网格交易系统..."
    
    if ! is_running; then
        print_warning "服务未运行"
        # 清理残留的PID文件
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    print_info "发送TERM信号到进程 $PID"
    kill -TERM "$PID"
    
    # 等待进程结束
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            print_success "服务已停止"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done
    
    # 如果进程还在运行，强制杀死
    print_warning "进程未响应，强制终止..."
    kill -KILL "$PID" 2>/dev/null
    sleep 1
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        print_success "服务已强制停止"
        rm -f "$PID_FILE"
    else
        print_error "无法停止服务"
        return 1
    fi
}

# 重启服务
restart() {
    print_info "正在重启网格交易系统..."
    stop
    sleep 2
    start
}

# 查看状态
status() {
    echo "================================"
    echo "  网格交易系统状态"
    echo "================================"
    
    if is_running; then
        PID=$(cat "$PID_FILE")
        print_success "服务正在运行"
        echo "  PID: $PID"
        echo "  PID文件: $PID_FILE"
        echo "  日志文件: $LOG_FILE"
        echo ""
        echo "进程信息:"
        ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,etime
    else
        print_warning "服务未运行"
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
    fi
    
    echo ""
    echo "最近的日志 (最后20行):"
    echo "--------------------------------"
    if [ -f "$LOG_FILE" ]; then
        tail -n 20 "$LOG_FILE"
    else
        print_warning "日志文件不存在"
    fi
}

# 查看日志
logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_error "日志文件不存在: $LOG_FILE"
        return 1
    fi
    
    if [ "$1" == "-f" ] || [ "$1" == "--follow" ]; then
        print_info "实时查看日志 (Ctrl+C 退出)"
        tail -f "$LOG_FILE"
    else
        LINES=${1:-50}
        print_info "显示最后 $LINES 行日志"
        tail -n "$LINES" "$LOG_FILE"
    fi
}

# 显示帮助
help() {
    cat << EOF
网格交易系统管理脚本

用法: $0 {start|stop|restart|status|logs} [选项]

命令:
  start       启动服务（后台运行）
  stop        停止服务
  restart     重启服务
  status      查看服务状态
  logs        查看日志
              -f, --follow    实时查看日志
              [数字]          显示最后N行日志 (默认50)

示例:
  $0 start                    # 启动服务
  $0 stop                     # 停止服务
  $0 restart                  # 重启服务
  $0 status                   # 查看状态
  $0 logs                     # 查看最后50行日志
  $0 logs 100                 # 查看最后100行日志
  $0 logs -f                  # 实时查看日志

文件位置:
  PID文件: $PID_FILE
  日志文件: $LOG_FILE
  工作目录: $SCRIPT_DIR

EOF
}

# 主函数
main() {
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            logs "$2"
            ;;
        help|--help|-h)
            help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
