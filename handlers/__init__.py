from telegram import AnnotatedGroup, OnCommand
from . import general


HANDLERS = [
    AnnotatedGroup(
        general.start_command,
        OnCommand("start"),
    )
]
