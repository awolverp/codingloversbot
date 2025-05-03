from pathlib import Path
import msgspec
import typing

from .env import BASEDIR


class YamlParser:
    __slots__ = ("texts", "buttons", "filename")

    def __init__(self, filename: Path) -> None:
        self.filename = filename

        self.texts: typing.Dict[str, str] = {}
        self.buttons: typing.Dict[str, typing.Dict[str, str]] = {}

        self._load()

    def _load(self) -> None:
        data = msgspec.yaml.decode(self.filename.read_bytes(), type=dict)
        self.texts = dict(data["texts"] or {})
        self.buttons = dict(data["buttons"] or {})


template = YamlParser(BASEDIR / "data" / "data.yml")


def texts(key: str, /, **kwargs) -> str:
    if not kwargs:
        return template.texts[key]

    return template.texts[key].format_map(kwargs)


def buttons(key1: str, key2: str, /, **kwargs) -> str:
    if not kwargs:
        return template.buttons[key1][key2]

    return template.buttons[key1][key2].format_map(kwargs)
