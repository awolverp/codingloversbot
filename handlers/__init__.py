from telegram import AnnotatedGroup, OnCommand, OnCallbackQuery
from . import general, commands, queries, votekick


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
        queries.decrease_warn_query,
        OnCallbackQuery("decrease-warn", ("/", 1)),
    ),
    AnnotatedGroup(
        commands.info_command,
        OnCommand("info", public=True),
    ),
    AnnotatedGroup(
        commands.trust_command,
        OnCommand("trust", public=True),
    ),
    AnnotatedGroup(
        commands.untrust_command,
        OnCommand("untrust", public=True),
    ),
    AnnotatedGroup(
        commands.ping_command,
        OnCommand("ping", public=True),
    ),
    AnnotatedGroup(
        votekick.votekick_command,
        OnCommand("votekick", public=True),
    ),
]
