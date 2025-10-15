import asyncio
import logging
import traceback
import platform
import sys
import argparse
import os
from trader import GridTrader
from helpers import LogConfig, send_pushplus_message
from web_server import start_web_server
from exchange_client import ExchangeClient
from config import TradingConfig

# 在Windows平台上设置SelectorEventLoop
if platform.system() == 'Windows':
    import asyncio
    # 在Windows平台上强制使用SelectorEventLoop
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logging.info("已设置Windows SelectorEventLoop策略")

async def main(args):
    try:
        # 初始化统一日志配置
        if args.daemon:
            # 守护进程模式：只输出到文件，不输出到控制台
            LogConfig.setup_logger(console_output=False)
        else:
            LogConfig.setup_logger()
        logging.info("="*50)
        logging.info("网格交易系统启动")
        logging.info("="*50)
        
        # 创建交易所客户端和配置实例
        exchange = ExchangeClient()
        config = TradingConfig()
        
        # 使用正确的参数初始化交易器
        trader = GridTrader(exchange, config)
        
        # 初始化交易器
        await trader.initialize()
        
        # 启动Web服务器
        web_server_task = asyncio.create_task(start_web_server(trader))
        
        # 启动交易循环
        trading_task = asyncio.create_task(trader.main_loop())
        
        # 等待所有任务完成
        await asyncio.gather(web_server_task, trading_task)
        
    except Exception as e:
        error_msg = f"启动失败: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        send_pushplus_message(error_msg, "致命错误")
        
    finally:
        if 'trader' in locals():
            try:
                await trader.exchange.close()
                logging.info("交易所连接已关闭")
            except Exception as e:
                logging.error(f"关闭连接时发生错误: {str(e)}")

def daemonize():
    """将进程转为守护进程（仅Linux/Unix）"""
    try:
        # 第一次fork
        pid = os.fork()
        if pid > 0:
            # 父进程退出
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"fork #1 failed: {e}\n")
        sys.exit(1)
    
    # 脱离父环境
    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    # 第二次fork
    try:
        pid = os.fork()
        if pid > 0:
            # 第一个子进程退出
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"fork #2 failed: {e}\n")
        sys.exit(1)
    
    # 重定向标准文件描述符
    sys.stdout.flush()
    sys.stderr.flush()
    
    # 关闭标准输入输出
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

def write_pid_file(pid_file):
    """写入PID文件"""
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='网格交易系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 前台运行（默认）
  python main.py
  
  # 后台运行（守护进程）
  python main.py --daemon
  
  # 后台运行并指定PID文件
  python main.py --daemon --pid-file /var/run/grid-trader.pid
  
  # 设置日志级别
  python main.py --log-level DEBUG
  
  # 查看运行状态
  cat /var/run/grid-trader.pid
  ps aux | grep python
        '''
    )
    
    parser.add_argument(
        '-d', '--daemon',
        action='store_true',
        help='守护进程模式运行（后台运行，仅Linux/Unix）'
    )
    
    parser.add_argument(
        '-p', '--pid-file',
        type=str,
        default='grid-trader.pid',
        help='PID文件路径 (默认: grid-trader.pid)'
    )
    
    parser.add_argument(
        '-l', '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    LogConfig.LOG_LEVEL = getattr(logging, args.log_level)
    
    # 如果是守护进程模式
    if args.daemon:
        if platform.system() == 'Windows':
            print("错误: Windows系统不支持守护进程模式")
            print("请使用 pythonw 或 Windows服务来后台运行")
            sys.exit(1)
        
        print(f"启动守护进程...")
        print(f"PID文件: {args.pid_file}")
        print(f"日志文件: trading_system.log")
        print(f"日志级别: {args.log_level}")
        
        # 转为守护进程
        daemonize()
        
        # 写入PID文件
        write_pid_file(args.pid_file)
    
    # 运行主程序
    asyncio.run(main(args))