"""

python3 bots/new/newapi/except_err.py

from .except_err import exception_err
from .except_err import exception_err, warn_err

"""

import inspect
import logging
import traceback
from warnings import warn

logger = logging.getLogger(__name__)


def warn_err(err):
    """
    Return formatted warning message with error details.
    """
    err = str(err)
    nn = inspect.stack()[2][3]
    return f"\ndef {nn}(): {err}"


common_errors = [
    "the JSON object must be str, bytes or bytearray, not NoneType",
]


def exception_err(e, text=""):
    # ---
    if not isinstance(text, str):
        text = str(text)
    # ---
    logger.info("<<yellow>> start exception_err:")
    # ---
    logger.error("Traceback (most recent call last):")
    warn(warn_err(f"Exception:{str(e)}"), UserWarning, stacklevel=3)
    logger.warning(text)
    # ---
    if str(e) not in common_errors:
        # ---
        err = traceback.format_exc(limit=4)
        err = str(err).replace("Traceback (most recent call last):", "").strip()
        logger.warning(err)
    # ---
    logger.critical("CRITICAL:")
