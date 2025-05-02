from .events import (
    TelegramClient as TelegramClient,
    OnNewMessage as OnNewMessage,
    OnCommand as OnCommand,
    OnCallbackQuery as OnCallbackQuery,
)
from telethon.events import StopPropagation as StopPropagation
from telethon import types as types, errors as errors


class AnnotatedGroup:
    def __init__(self, origin, *args) -> None:
        self.__origin__ = origin
        self.__metadata__ = args
