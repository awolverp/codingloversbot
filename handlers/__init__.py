from telegram import AnnotatedGroup, OnCommand
from . import general


HANDLERS = [
    AnnotatedGroup(
        general.start_private_command,
        OnCommand("start", private=True),
    )
]
