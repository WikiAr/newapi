"""

from .api_utils.user_agent import default_user_agent

"""
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def default_user_agent():
    tool = os.getenv("HOME")
    # "/data/project/mdwiki"
    tool = tool.split("/")[-1] if tool else "himo"
    # ---
    li = f"{tool} bot/1.0 (https://{tool}.toolforge.org/; tools.{tool}@toolforge.org)"
    # ---
    # printe.output(f"default_user_agent: {li}")
    # ---
    return li

