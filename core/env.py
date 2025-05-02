"""
Here we read .env file variables
"""

from pathlib import Path as _Path
import msgspec


with open("settings.yml", "rb") as fd:
    _variables = msgspec.yaml.decode(fd.read(), type=dict)


BASEDIR = _Path(__file__).parent.parent

TOKEN: str = _variables["token"]

API_ID: int = int(_variables["api_id"])
API_HASH: str = _variables["api_hash"]

ADMINS: list = _variables["admins"]

MYSQL_HOST: str = _variables["database"]["host"]
MYSQL_PORT: int = int(_variables["database"]["port"])
MYSQL_USER: str = _variables["database"]["user"]
MYSQL_PASSWORD: str = _variables["database"]["password"]
MYSQL_DATABASE: str = _variables["database"]["name"]

SUPPORT: str = _variables["support"]
