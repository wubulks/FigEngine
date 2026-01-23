# figengine/utils/logger.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: logger.py
Author: Mute
Date: 2026/01/18
License: MIT License
Description: Centralized logging utility. Provides a hierarchical logger factory 
             that automatically names loggers based on the calling module.
"""

import logging
import sys
import inspect
from typing import Optional

# 定义全局主 logger 名称
# 所有子模块的日志都将是它的子节点 (e.g. "FigEngine.core.image")
LOGGER_NAME = "FigEngine"

def _get_console_handler(formatter: logging.Formatter) -> logging.StreamHandler:
    """
    [Internal] 创建控制台处理器 (Stdout)。
    
    :param formatter: 日志格式化器。
    :return: 配置好的 StreamHandler。
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    return handler

def _get_file_handler(formatter: logging.Formatter, log_path: str) -> logging.FileHandler:
    """
    [Internal] 创建文件处理器。
    
    :param formatter: 日志格式化器。
    :param log_path: 日志文件路径。
    :return: 配置好的 FileHandler (UTF-8编码)。
    """
    handler = logging.FileHandler(log_path, encoding='utf-8')
    handler.setFormatter(formatter)
    return handler

def setup_logger(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    全局初始化或重新配置 FigEngine 的根 Logger。
    
    只需要在程序入口调用一次，所有子模块通过 get_logger() 获取的实例都会继承此配置。
    
    :param level: 日志级别 (type: str, default: "INFO")。
                  options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"。
    :param log_file: (可选) 日志文件路径 (type: str)。
                     如果提供，日志将同时输出到控制台和该文件。
    :return: 配置完成的 Root Logger 实例。
    """
    # 1. 获取核心 Logger (父节点)
    logger = logging.getLogger(LOGGER_NAME)
    
    # 2. 转换日志级别字符串
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # 3. 清理旧的 Handler (防止重复打印，比如在 Jupyter 中多次运行)
    if logger.hasHandlers():
        logger.handlers.clear()

    # 4. 定义格式
    # 关键修改：%(name)s 会显示具体的子模块名称 (e.g., FigEngine.core.image)
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%H:%M:%S" # 简化时间显示，只看时分秒
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # 5. 添加控制台输出
    logger.addHandler(_get_console_handler(formatter))

    # 6. (可选) 添加文件输出
    if log_file:
        logger.addHandler(_get_file_handler(formatter, log_file))

    # 7. 禁止向上传播 (防止被 Python Root Logger 再次捕获导致双重打印)
    logger.propagate = False
    
    # 打印一条调试信息确认初始化完成
    # logger.debug(f"FigEngine Logger initialized at level {level}")
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取 Logger 实例。
    
    [Magic Feature]: 
    如果未指定 name，该函数会自动通过 inspect 堆栈分析调用者所在的模块，
    并自动生成层级化的 Logger 名称 (e.g. "FigEngine.core.image")。
    
    这确保了：
    1. 日志来源清晰可查。
    2. 所有自动生成的 Logger 都是 LOGGER_NAME ("FigEngine") 的子节点，
       从而自动继承 setup_logger 设置的 Handler 和 Level。
    
    :param name: (可选) 手动指定 Logger 名称。通常不需要。
    :return: logging.Logger 实例。
    """
    if name is None:
        try:
            # 1. 获取调用栈的上一帧 (即调用 get_logger 的地方)
            stack = inspect.stack()
            caller_frame = stack[1]
            # 2. 获取该帧所在的模块
            module = inspect.getmodule(caller_frame[0])
            
            if module:
                # e.g., module_name = "figengine.core.image"
                module_name = module.__name__
                
                # 3. 优化命名显示
                # 将 "figengine" 替换为 "FigEngine" (保持大小写一致性)
                # 或者直接作为子节点挂载
                if module_name.startswith("figengine"):
                    # 替换前缀，变为 "FigEngine.core.image"
                    # 这样它就是 LOGGER_NAME ("FigEngine") 的子 Logger
                    # 会自动继承父节点的 Handler 和 Level
                    name = module_name.replace("figengine", LOGGER_NAME, 1)
                else:
                    # 如果是在外部脚本 (e.g. __main__) 中调用
                    name = f"{LOGGER_NAME}.{module_name}"
            else:
                name = LOGGER_NAME
        except Exception:
            # 兜底：如果 inspect 失败，返回主 logger
            name = LOGGER_NAME

    return logging.getLogger(name)

# --- 默认初始化 ---
# 默认开启 INFO，防止 import 时什么都不显示
# 用户可以在 main 函数中再次调用 setup_logger(level="DEBUG") 来覆盖此设置
setup_logger(level="INFO")