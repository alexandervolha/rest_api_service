import logging
import asyncio
from contextlib import wraps


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
    )
    logging.getLogger('aiokafka').setLevel(logging.WARNING)


def async_retry(max_tries=-1, retry_cooldown=1):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, _max_tries=max_tries, _retry_cooldown=retry_cooldown, **kwargs):
            while True:
                try:
                    return await func(*args, **kwargs)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    _max_tries -= 1
                    if not _max_tries:
                        raise e
                    await asyncio.sleep(_retry_cooldown)
        return wrapped
    return wrapper
