from telegram import TelegramClient, OnNewMessage, errors, types
from telegram.utils import parse_command_message
from telethon.tl import functions
from core import env, templates, utils
import models
import time


async def ping_command(event: OnNewMessage.Event):
    if not event.message.is_private and event.message.chat_id not in env.GROUPS:
        return

    if not event.message.is_private:
        async with models.db() as session:
            has_access = await session.scalar(
                models.sql.select(models.Admin.id).where(
                    models.Admin.user_id == event.message.sender_id,
                    models.Admin.group_id == event.message.chat_id,
                )
            )

        if not has_access:
            return

    ping = time.time()
    await event._client(functions.PingRequest(0))
    ping = int((time.time() - ping) * 1000)

    await event._client.send_message(
        event.message.chat_id,
        templates.texts("pong", ping=ping),
        reply_to=event.message.id,
    )


async def mute_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target_id = await parse_command_message(event.message, duration_allowed=True)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="mute"),
            reply_to=event.message.id,
        )
        return

    try:
        await event._client.edit_permissions(
            event.message.chat_id,
            target_id.user_id,
            until_date=target_id.until_date,
            send_messages=False,
        )
    except errors.ChatAdminRequiredError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_me"),
            reply_to=event.message.id,
        )
    except (
        ValueError,
        errors.UserIdInvalidError,
        errors.PeerIdInvalidError,
        errors.ParticipantIdInvalidError,
    ):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.UserAdminInvalidError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_error"),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts(
                "user_muted",
                id=target_id.user_id,
                until=utils.format_datetime(target_id.until_date) if target_id.duration else "-",
            ),
            reply_to=event.message.id,
        )


async def unmute_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target_id = await parse_command_message(event.message, True, False)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="unmute"),
            reply_to=event.message.id,
        )
        return

    try:
        await event._client.edit_permissions(
            event.message.chat_id,
            target_id.user_id,
            send_messages=True,
        )
    except errors.ChatAdminRequiredError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_me"),
            reply_to=event.message.id,
        )
    except (
        ValueError,
        errors.UserIdInvalidError,
        errors.PeerIdInvalidError,
        errors.ParticipantIdInvalidError,
    ):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.UserAdminInvalidError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_error"),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_unmuted", id=target_id.user_id),
            reply_to=event.message.id,
        )


async def ban_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target_id = await parse_command_message(event.message, duration_allowed=True)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="ban"),
            reply_to=event.message.id,
        )
        return

    try:
        await event._client.edit_permissions(
            event.message.chat_id,
            target_id.user_id,
            until_date=target_id.until_date,
            view_messages=False,
        )
    except errors.ChatAdminRequiredError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_me"),
            reply_to=event.message.id,
        )
    except (
        ValueError,
        errors.UserIdInvalidError,
        errors.PeerIdInvalidError,
        errors.ParticipantIdInvalidError,
    ):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.UserAdminInvalidError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_error"),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts(
                "user_banned",
                id=target_id.user_id,
                until=utils.format_datetime(target_id.until_date) if target_id.duration else "-",
            ),
            reply_to=event.message.id,
        )


async def unban_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target_id = await parse_command_message(event.message, True, False)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="unban"),
            reply_to=event.message.id,
        )
        return

    try:
        await event._client.edit_permissions(event.message.chat_id, target_id.user_id)
    except errors.ChatAdminRequiredError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_me"),
            reply_to=event.message.id,
        )
    except (
        ValueError,
        errors.UserIdInvalidError,
        errors.PeerIdInvalidError,
        errors.ParticipantIdInvalidError,
    ):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.UserAdminInvalidError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("promote_error"),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_unbanned", id=target_id.user_id),
            reply_to=event.message.id,
        )


async def _mute_user_for_24(client: TelegramClient, chat_id: int, user_id: int):
    from datetime import timedelta

    await client.edit_permissions(
        chat_id,
        user_id,
        until_date=timedelta(hours=24),
        send_messages=False,
    )


async def _mute_user(client: TelegramClient, chat_id: int, user_id: int):
    await client.edit_permissions(
        chat_id,
        user_id,
        send_messages=False,
    )


async def _kick_user(client: TelegramClient, chat_id: int, user_id: int):
    await client.kick_participant(
        chat_id,
        user_id,
    )


async def _ban_user(client: TelegramClient, chat_id: int, user_id: int):
    await client.edit_permissions(
        chat_id,
        user_id,
        view_messages=False,
    )


_WARN_ACTIONS = {
    models.GroupWarnAction.MUTE_24H: _mute_user_for_24,
    models.GroupWarnAction.MUTE: _mute_user,
    models.GroupWarnAction.KICK: _kick_user,
    models.GroupWarnAction.BAN: _ban_user,
}


async def warn_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target = await parse_command_message(event.message)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="warn"),
            reply_to=event.message.id,
        )
        return

    async with models.db.begin() as session:
        is_admin = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == target.user_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

        if is_admin:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("warn_to_admin"),
                reply_to=event.message.id,
            )
            return

        warns = await session.execute(
            models.sql.select(
                models.Participant.id, models.Participant.warns, models.Participant.is_trusted
            ).where(
                models.Participant.user_id == target.user_id,
                models.Participant.group_id == event.message.chat_id,
            )
        )
        warns = warns.fetchone()

        if warns is None:
            await session.execute(
                models.sql.insert(models.Participant).values(
                    user_id=target.user_id,
                    is_trusted=False,
                    warns=1,
                    group_id=event.message.chat_id,
                )
            )
            warns = 0
            action = 0  # avoid UnboundLocalError

        else:
            row_id, warns, is_trusted = warns.t

            if is_trusted:
                await event._client.send_message(
                    event.message.chat_id,
                    templates.texts("warn_to_trusted"),
                    reply_to=event.message.id,
                )
                return

            await session.execute(
                models.sql.update(models.Participant)
                .values(warns=(warns + 1) % 3)
                .where(models.Participant.id == row_id)
            )

            action = await session.scalar(
                models.sql.select(models.Group.warn_action).where(
                    models.Group.id == event.message.chat_id
                )
            )

    if warns >= 2:
        # perform action
        try:
            await _WARN_ACTIONS[action](event._client, event.message.chat_id, target.user_id)
        except errors.ChatAdminRequiredError:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("promote_me"),
                reply_to=event.message.id,
            )
        except (
            ValueError,
            errors.UserIdInvalidError,
            errors.PeerIdInvalidError,
            errors.ParticipantIdInvalidError,
        ):
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("user_not_found", target=target.user_id),
                reply_to=event.message.id,
            )
        except errors.UserAdminInvalidError:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("promote_error"),
                reply_to=event.message.id,
            )
        else:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts(
                    "perform_warn_action", action=templates.texts("warn_action_" + str(action))
                ),
                reply_to=event.message.id,
            )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("warn_increased", id=target.user_id, warns=warns + 1),
            reply_to=event.message.id,
            buttons=[
                [
                    types.KeyboardButtonCallback(
                        templates.buttons("warns", "decrease"), f"decrease-warn/{target.user_id}"
                    )
                ]
            ],
        )


async def warns_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target = await parse_command_message(event.message)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="warns"),
            reply_to=event.message.id,
        )
        return

    async with models.db() as session:
        warns = await session.scalar(
            models.sql.select(models.Participant.warns).where(
                models.Participant.user_id == target.user_id,
                models.Participant.group_id == event.message.chat_id,
            )
        )
        warns = warns or 0

    buttons = None
    if warns > 1:
        buttons = [
            [
                types.KeyboardButtonCallback(
                    templates.buttons("warns", "decrease"), f"decrease-warn/{target.user_id}"
                )
            ]
        ]

    await event._client.send_message(
        event.message.chat_id,
        templates.texts("warns_info", id=target.user_id, warns=warns),
        reply_to=event.message.id,
        buttons=buttons,
    )


async def info_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

        if not has_access:
            has_access = await session.scalar(
                models.sql.select(models.Participant.id).where(
                    models.Participant.user_id == event.message.sender_id,
                    models.Participant.group_id == event.message.chat_id,
                    models.Participant.is_trusted == True,
                )
            )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_2"),
            reply_to=event.message.id,
        )
        return

    try:
        target = await parse_command_message(event.message)
        target = target.user_id
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="info"),
            reply_to=event.message.id,
        )
        return

    try:
        status: types.channels.ChannelParticipant = await event._client(
            functions.channels.GetParticipantRequest(
                channel=event.message.input_chat,
                participant=await event._client.get_input_entity(target),
            )
        )
    except errors.UserNotParticipantError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_participant"),
            reply_to=event.message.id,
        )
        return

    if isinstance(status.participant, types.ChannelParticipantLeft):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_has_left"),
            reply_to=event.message.id,
        )
        return

    if isinstance(status.participant, types.ChannelParticipantBanned):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts(
                "user_has_banned", kicked_by=status.participant.kicked_by or "<unknown>"
            ),
            reply_to=event.message.id,
        )
        return

    if isinstance(status.participant, types.ChannelParticipantSelf):
        # ignore request, admin is kidding me :/
        return

    target = status.participant.user_id

    async with models.db() as session:
        participant = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == target,
                models.Admin.group_id == event.message.chat_id,
            )
        )

        # means target is admin
        if participant:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("admin_user_info"),
                reply_to=event.message.id,
            )
            return

        participant = await session.scalar(
            models.sql.select(models.Participant).where(
                models.Participant.user_id == target,
                models.Participant.group_id == event.message.chat_id,
            )
        )

    if participant is None or not participant.is_trusted:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts(
                "normal_user_info",
                id=target,
                warns=participant.warns if participant else 0,
                votekicks=len(models.VOTEKICKS.get((event.message.chat_id, target), [])),
            ),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts(
                "trusted_user_info",
                id=target,
                warns=participant.warns,
            ),
            reply_to=event.message.id,
        )


async def trust_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target = await parse_command_message(event.message)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="trust"),
            reply_to=event.message.id,
        )
        return

    async with models.db.begin() as session:
        is_admin = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == target.user_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

        if is_admin:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("cannot_trust_1", id=target.user_id),
                reply_to=event.message.id,
            )
            return

        participant = await session.scalar(
            models.sql.select(models.Participant).where(
                models.Participant.user_id == target.user_id,
                models.Participant.group_id == event.message.chat_id,
            )
        )

        if participant and participant.is_trusted:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("cannot_trust_2", id=target.user_id),
                reply_to=event.message.id,
            )
            return

        if participant is None:
            await session.execute(
                models.sql.insert(models.Participant).values(
                    user_id=target.user_id,
                    is_trusted=True,
                    warns=0,
                    group_id=event.message.chat_id,
                )
            )
        else:
            await session.execute(
                models.sql.update(models.Participant)
                .values(warns=0, is_trusted=True)
                .where(models.Participant.id == participant.id)
            )

    await event._client.send_message(
        event.message.chat_id,
        templates.texts("user_trusted", id=target.user_id),
        reply_to=event.message.id,
    )


async def untrust_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target = await parse_command_message(event.message)
    except KeyError as e:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=str(e)),
            reply_to=event.message.id,
        )
        return
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="untrust"),
            reply_to=event.message.id,
        )
        return

    async with models.db.begin() as session:
        participant = await session.scalar(
            models.sql.select(models.Participant).where(
                models.Participant.user_id == target.user_id,
                models.Participant.group_id == event.message.chat_id,
            )
        )

        if participant is None or not participant.is_trusted:
            await event._client.send_message(
                event.message.chat_id,
                templates.texts("cannot_untrust", id=target.user_id),
                reply_to=event.message.id,
            )
            return
        else:
            await session.execute(
                models.sql.update(models.Participant)
                .values(warns=0, is_trusted=False)
                .where(models.Participant.id == participant.id)
            )

    await event._client.send_message(
        event.message.chat_id,
        templates.texts("user_untrusted", id=target.user_id),
        reply_to=event.message.id,
    )


async def settings_command(event: OnNewMessage.Event):
    if event.message.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.message.sender_id,
                models.Admin.group_id == event.message.chat_id,
            )
        )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    # chat_info: types.Channel = await event._client.get_entity(event.message.chat_id)

    async with models.db() as session:
        admins = await session.scalar(
            models.sql.select(models.sql.func.count(models.Admin.id)).where(
                models.Admin.group_id == event.message.chat_id
            )
        )
        trusted = await session.scalar(
            models.sql.select(models.sql.func.count(models.Participant.id)).where(
                models.Participant.group_id == event.message.chat_id,
                models.Participant.is_trusted == True,
            )
        )
        warned = await session.scalar(
            models.sql.select(models.sql.func.count(models.Participant.id)).where(
                models.Participant.group_id == event.message.chat_id,
                models.Participant.warns > 0,
            )
        )
        warn_action = await session.scalar(
            models.sql.select(models.Group.warn_action).where(
                models.Group.id == event.message.chat_id
            )
        )

    await event._client.send_message(
        event.message.chat_id,
        templates.texts(
            "settings",
            id=event.message.chat_id,
            admins=admins,
            trusted=trusted,
            warned=warned,
            warn_action=templates.texts("settings_warn_action_" + str(warn_action)),
        ),
        reply_to=event.message.id,
        buttons=[
            [
                types.KeyboardButtonCallback(
                    templates.buttons("settings", "change_warn_action"), "change-warn-action"
                )
            ]
        ],
    )
