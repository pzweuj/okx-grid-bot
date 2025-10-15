import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from config import WECHAT_WEBHOOK_KEY
import time
import psutil
import os
from logging.handlers import TimedRotatingFileHandler
import sys
from datetime import datetime

def format_trade_message(side, symbol, price, amount, total, grid_size, retry_count=None):
    """格式化交易消息为美观的文本格式
    
    Args:
        side (str): 交易方向 ('buy' 或 'sell')
        symbol (str): 交易对
        price (float): 交易价格
        amount (float): 交易数量
        total (float): 交易总额
        grid_size (float): 网格大小
        retry_count (tuple, optional): 重试次数，格式为 (当前次数, 最大次数)
    
    Returns:
        str: 格式化后的消息文本
    """
    # 使用emoji增加可读性
    direction_emoji = "🟢" if side == 'buy' else "🔴"
    direction_text = "买入" if side == 'buy' else "卖出"
    
    # 构建消息主体
    message = f"""
{direction_emoji} {direction_text} {symbol}
━━━━━━━━━━━━━━━━━━━━
💰 价格：{price:.2f} USDT
📊 数量：{amount:.4f} OKB
💵 金额：{total:.2f} USDT
📈 网格：{grid_size}%
"""
    
    # 如果有重试信息，添加重试次数
    if retry_count:
        current, max_retries = retry_count
        message += f"🔄 尝试：{current}/{max_retries}次\n"
    
    # 添加时间戳
    message += f"⏰ 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    return message

def send_wechat_message(content, title="交易信号通知"):
    """发送企业微信机器人消息
    
    Args:
        content (str): 消息内容
        title (str): 消息标题
    """
    if not WECHAT_WEBHOOK_KEY or WECHAT_WEBHOOK_KEY == "your_webhook_key_here":
        logging.debug("未配置有效的WECHAT_WEBHOOK_KEY，跳过推送通知")
        return
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECHAT_WEBHOOK_KEY}"
    
    # 构建markdown格式的消息
    markdown_content = f"### {title}\n{content}"
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content
        }
    }
    
    try:
        logging.debug(f"发送推送通知: {title}")
        response = requests.post(url, json=data)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('errcode') == 0:
            logging.debug(f"推送成功: {title}")
        else:
            logging.error(f"推送失败: 状态码={response.status_code}, 响应={response_json}, 标题={title}")
    except Exception as e:
        logging.error(f"推送异常: {str(e)}, 标题={title}", exc_info=True)

# 保持向后兼容的别名
send_pushplus_message = send_wechat_message

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def safe_fetch(method, *args, **kwargs):
    try:
        return await method(*args, **kwargs)
    except Exception as e:
        logging.error(f"请求失败: {str(e)}")
        raise 

def debug_watcher():
    """资源监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            mem_before = psutil.virtual_memory().used
            logging.debug(f"[DEBUG] 开始执行 {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                cost = time.time() - start
                mem_used = psutil.virtual_memory().used - mem_before
                logging.debug(f"[DEBUG] {func.__name__} 执行完成 | 耗时: {cost:.3f}s | 内存变化: {mem_used/1024/1024:.2f}MB")
        return wrapper
    return decorator 

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # 为不同级别添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname:8s}{self.RESET}"
        
        # 为模块名添加颜色
        record.name = f"\033[34m{record.name:20s}{self.RESET}"
        
        return super().format(record)


class LogConfig:
    SINGLE_LOG = True  # 强制单文件模式
    BACKUP_DAYS = 7    # 保留7天日志
    LOG_DIR = os.path.dirname(__file__)  # 与main.py相同目录
    LOG_LEVEL = logging.INFO

    @staticmethod
    def setup_logger():
        logger = logging.getLogger()
        logger.setLevel(LogConfig.LOG_LEVEL)
        
        # 清理所有现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 文件处理器 - 详细格式
        file_handler = TimedRotatingFileHandler(
            os.path.join(LogConfig.LOG_DIR, 'trading_system.log'),
            when='midnight',
            interval=1,
            backupCount=LogConfig.BACKUP_DAYS,
            encoding='utf-8',
            delay=True
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器 - 彩色简洁格式
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    @staticmethod
    def clean_old_logs():
        if not os.path.exists(LogConfig.LOG_DIR):
            return
        now = time.time()
        for fname in os.listdir(LogConfig.LOG_DIR):
            if LogConfig.SINGLE_LOG and fname != 'trading_system.log':
                continue
            path = os.path.join(LogConfig.LOG_DIR, fname)
            if os.stat(path).st_mtime < now - LogConfig.BACKUP_DAYS * 86400:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"删除旧日志失败 {fname}: {str(e)}")


class LogHelper:
    """日志辅助工具类 - 提供统一的日志格式"""
    
    @staticmethod
    def log_section(logger, title, level=logging.INFO):
        """打印分节标题"""
        separator = "=" * 60
        logger.log(level, separator)
        logger.log(level, f"  {title}")
        logger.log(level, separator)
    
    @staticmethod
    def log_trade_signal(logger, signal_type, price, trigger_price, threshold_pct):
        """记录交易信号"""
        emoji = "📈" if signal_type == "买入" else "📉"
        logger.info(
            f"{emoji} 触发{signal_type}信号 | "
            f"当前价: {price:.4f} | "
            f"触发价: {trigger_price:.4f} | "
            f"阈值: {threshold_pct:.2f}%"
        )
    
    @staticmethod
    def log_balance_check(logger, check_type, required, available, sufficient):
        """记录余额检查"""
        status = "✅ 充足" if sufficient else "❌ 不足"
        logger.info(
            f"💰 {check_type}余额检查 | "
            f"所需: {required:.4f} | "
            f"可用: {available:.4f} | "
            f"状态: {status}"
        )
    
    @staticmethod
    def log_position_check(logger, current_ratio, after_ratio, limit_ratio, action, allowed):
        """记录仓位检查"""
        status = "✅ 允许" if allowed else "⛔ 拒绝"
        logger.info(
            f"📊 仓位检查 | "
            f"操作: {action} | "
            f"当前: {current_ratio:.2%} | "
            f"预计: {after_ratio:.2%} | "
            f"限制: {limit_ratio:.2%} | "
            f"结果: {status}"
        )
    
    @staticmethod
    def log_order_execution(logger, side, retry, max_retry, price, amount, amount_usdt):
        """记录订单执行"""
        emoji = "🟢" if side == "buy" else "🔴"
        action = "买入" if side == "buy" else "卖出"
        logger.info(
            f"{emoji} 执行{action}订单 [{retry}/{max_retry}] | "
            f"价格: {price:.4f} | "
            f"数量: {amount:.6f} | "
            f"金额: {amount_usdt:.2f} USDT"
        )
    
    @staticmethod
    def log_order_result(logger, side, order_id, status, price=None, filled=None):
        """记录订单结果"""
        action = "买入" if side == "buy" else "卖出"
        if status == "closed":
            logger.info(
                f"✅ {action}订单成交 | "
                f"ID: {order_id} | "
                f"价格: {price:.4f} | "
                f"成交量: {filled:.6f}"
            )
        elif status == "cancelled":
            logger.warning(f"⚠️ {action}订单已取消 | ID: {order_id}")
        else:
            logger.info(f"⏳ {action}订单状态: {status} | ID: {order_id}")
    
    @staticmethod
    def log_grid_adjustment(logger, old_grid, new_grid, volatility, reason=""):
        """记录网格调整"""
        change = ((new_grid - old_grid) / old_grid * 100) if old_grid > 0 else 0
        direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        logger.info(
            f"{direction} 网格调整 | "
            f"{old_grid:.2f}% → {new_grid:.2f}% ({change:+.1f}%) | "
            f"波动率: {volatility:.2%}" +
            (f" | {reason}" if reason else "")
        )
    
    @staticmethod
    def log_transfer(logger, transfer_type, currency, amount, from_account, to_account, success):
        """记录资金划转"""
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(
            f"💸 {transfer_type} | "
            f"{currency} {amount:.4f} | "
            f"{from_account} → {to_account} | "
            f"{status}"
        )
    
    @staticmethod
    def log_error(logger, operation, error_msg, retry_info=None):
        """记录错误信息"""
        msg = f"❌ {operation}失败 | 错误: {error_msg}"
        if retry_info:
            current, max_retry = retry_info
            msg += f" | 重试: {current}/{max_retry}"
        logger.error(msg)
    
    @staticmethod
    def log_performance(logger, operation, duration, success=True):
        """记录性能指标"""
        status = "✅" if success else "❌"
        logger.debug(f"{status} {operation} | 耗时: {duration:.3f}s") 