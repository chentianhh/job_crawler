# utils/logger.py
import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger


class LogSetup:
    """日志系统配置类"""

    def __init__(self):
        self.log_dir = Path("logs")
        self._init_log_dir()

        # 移除默认配置
        logger.remove()

        # 控制台输出配置
        self._add_console_handler()

        # 文件输出配置
        self._add_file_handler()

        # 异常捕获
        self._catch_exceptions()

    def _init_log_dir(self):
        """创建日志目录"""
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)

    def _add_console_handler(self):
        """控制台日志处理器"""
        logger.add(
            sink=sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )

    def _add_file_handler(self):
        """文件日志处理器"""
        logger.add(
            sink=self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="10 MB",  # 日志轮换：10MB 或每天
            retention="30 days",  # 保留策略
            compression="zip",  # 压缩格式
            enqueue=True,  # 线程安全
            encoding="utf-8"
        )

    def _catch_exceptions(self):
        """全局异常捕获"""

        @logger.catch
        def catch_exceptions(exception_type, exception_value, tb):
            logger.error(
                "Uncaught exception occurred:",
                exc_info=(exception_type, exception_value, tb)
            )
        sys.excepthook = catch_exceptions


def setup_logging():
    """初始化日志配置"""
    LogSetup()


# 初始化日志系统
setup_logging()

# 导出预配置的logger实例
__all__ = ['logger']
