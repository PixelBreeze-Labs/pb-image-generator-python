# utils/monitoring.py
import time
from functools import wraps
from utils import logger

def timer(name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            logger.info(f"{name} took {time.time() - start:.2f} seconds")
            return result
        return wrapper
    return decorator