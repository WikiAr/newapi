#
import os
from configparser import ConfigParser

if os.getenv("HOME"):
    project = "/data/project/himo"
else:
    project = 'I:/core/bots/core1'

db_connect_file = f"{project}/confs/db.ini"

print(f"{db_connect_file=}")

main_dir = os.path.dirname(__file__)
print(f"{main_dir=}")
print(f"{__file__=}")

config2 = ConfigParser()
config2.read(db_connect_file)

try:
    user = config2["client"]["user"]
    print(f"{user=}")
except KeyError as e:
    print(f"error: {e}")
