from telegram import AnnotatedGroup, OnCommand, OnCallbackQuery
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
    AnnotatedGroup(
        commands.warn_command,
        OnCommand("warn", public=True),
    ),
    AnnotatedGroup(
        commands.warns_command,
        OnCommand("warns", public=True),
    ),
    AnnotatedGroup(
        commands.decrease_warn_query,
        OnCallbackQuery("decrease-warn", ("/", 1)),
    ),
]
