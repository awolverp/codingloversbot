from telegram import AnnotatedGroup, OnCommand
from . import general, commands


HANDLERS = [
    AnnotatedGroup(
        general.start_command,
        OnCommand("start"),
    ),
    AnnotatedGroup(
        commands.ban_command,
        OnCommand("mute", public=True),
    ),
    AnnotatedGroup(
        commands.unmute_command,
        OnCommand("unmute", public=True),
    ),
    AnnotatedGroup(
        commands.ban_command,
        OnCommand("ban", public=True),
    ),
    AnnotatedGroup(
        commands.unban_command,
        OnCommand("unban", public=True),
    ),
]
