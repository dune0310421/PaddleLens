import time
import logging
from typing import *
from github import Github
from github import RateLimitExceededException, UnknownObjectException

T = TypeVar("T")
logger = logging.getLogger(__name__)

def request_github(
        gh: Github, gh_func: Callable[..., T], params: Tuple = (), default: Any = None
) -> Optional[T]:
    """
    This is a wrapper to ensure that any rate-consuming interactions with GitHub
      have proper exception handling.
    """
    for _ in range(0, 3):  # Max retry 3 times
        try:
            data = gh_func(*params)
            return data
        except RateLimitExceededException as ex:
            logger.info("{}: {}".format(type(ex), ex))
            sleep_time = gh.rate_limiting_resettime - time.time() + 10
            logger.info("Rate limit reached, wait for {} seconds...".format(sleep_time))
            time.sleep(max(1.0, sleep_time))
        except UnknownObjectException as ex:
            logger.error("{}: {}".format(type(ex), ex))
            break
        except Exception as ex:
            logger.error("{}: {}".format(type(ex), ex))
            time.sleep(5)
    return default