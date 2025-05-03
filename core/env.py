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

DATABASE: dict = _variables["database"]
assert "type" in DATABASE, "'type' field is required in database settings"
assert "name" in DATABASE, "'name' field is required in database settings"

assert DATABASE["type"] in ("mysql", "sqlite3"), (
    "acceptable values for 'type' field in database is 'mysql' and 'sqlite3'"
)

if DATABASE["type"] == "mysql":
    assert "host" in DATABASE, "'host' field is required in database settings"
    assert "port" in DATABASE, "'port' field is required in database settings"
    assert "user" in DATABASE, "'user' field is required in database settings"
    assert "password" in DATABASE, "'password' field is required in database settings"

GROUPS: list = _variables["groups"]
