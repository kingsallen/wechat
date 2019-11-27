import time
import inspect
import traceback

from contextlib import contextmanager
from globals import logger


@contextmanager
def log_this(context_alias, threshold=0):
    """
    log记录上下文管理器
    :param context_alias: 代码片段的别名，请避免重复，建议使用{class_name}_{func_name}_{alias}
    :param threshold:
    :return:
    """
    timer = time.perf_counter
    _start = timer()
    try:
        yield
    finally:
        end = timer()
        elapsed = (end - _start) * 1000
        if threshold <= 0 or threshold < elapsed:
            try:
                c = {
                    "context_alias": context_alias,
                    "func_stack": str(inspect.stack()[2]),
                    "time": elapsed,
                    "timestamp": time.time()
                }
                logger.info(c)
            except Exception as e:
                logger.warning("log_this error: {}".format(traceback.format_exc()))
