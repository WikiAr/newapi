"""Timing decorator for profiling function execution."""

import functools
import logging
import time

logger = logging.getLogger(__name__)


def function_timer(func):
    """Log how long a function takes to run."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} finished in {time.perf_counter() - start:.4f}s")
        return result

    return wrapper
