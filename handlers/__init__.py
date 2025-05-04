from telegram import AnnotatedGroup, OnCommand
from . import general, commands


HANDLERS = [
    AnnotatedGroup(
        general.start_command,
        OnCommand("start"),
    ),
    AnnotatedGroup(
        commands.mute_command,
        OnCommand("mute", public=True),
    ),
    AnnotatedGroup(
        commands.unmute_command,
        OnCommand("unmute", public=True),
    ),
]
