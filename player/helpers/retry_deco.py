import time
from functools import wraps


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """
    :what it does:
        Retry calling the decorated function using an exponential backoff.

        http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
        original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param 
        ExceptionToCheck: Exception or tuple 
            the exception to check. may be a tuple of exceptions to check
    :param 
        tries: int expected
            number of times to try (not retry) before giving up 
    :param 
        delay: int expected 
            initial delay between retries in seconds
    :param 
        backoff: int expected
            backoff multiplier e.g. value of 2 will double the delay 
            each retry
    :param 
        logger: logging.Logger instance
            logger to use. If None, print
    """
    def deco_retry(f):

        @wraps(f)
        async def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return await f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return await f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry