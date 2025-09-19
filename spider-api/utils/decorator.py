# 文件路径: utils/decorators.py

from functools import wraps
from loguru import logger


def handle_spider_exceptions(func):
    """
    一个专门为 Data_Spider 方法设计的装饰器，用于：
    1. 统一处理预料之外的异常。
    2. 记录详细的错误日志。
    3. 返回一个统一的失败结果元组，格式为 ([], False, "错误信息")。
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # self 是 Data_Spider 的实例, args 和 kwargs 是传递给原始方法的其他参数
        func_name = func.__name__
        try:
            # 直接执行原始方法 (例如 spider_user_all_note)
            return func(self, *args, **kwargs)
        except KeyError as e:
            # 专门处理解析JSON时找不到Key的错误
            error_message = f"解析数据失败，可能是API结构已更改，缺少键: {e}"
            logger.error(f"Function '{func_name}' failed due to missing key: {e}")
            return [], False, error_message
        except Exception as e:
            # 处理所有其他未知异常
            error_message = f"未知错误: {e}"
            logger.error(f"An unexpected error occurred in '{func_name}': {e}")
            return [], False, error_message

    return wrapper