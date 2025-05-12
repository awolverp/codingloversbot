from telegram import TelegramClient, OnNewMessage, OnCallbackQuery, errors, types
from telegram.utils import parse_command_message
from core import env, templates, utils
import models


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

        # if not has_access:
        #     has_access = await session.scalar(
        #         models.sql.select(models.Participant.id).where(
        #             models.Participant.user_id == event.message.sender_id,
        #             models.Participant.group_id == event.message.chat_id,
        #             models.Participant.is_trusted == True,
        #         )
        #     )

    if not has_access:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("permission_denied_1"),
            reply_to=event.message.id,
        )
        return

    try:
        target_id = await parse_command_message(event.message, duration_allowed=True)
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
    except ValueError:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="warn"),
            reply_to=event.message.id,
        )
        return

    async with models.db.begin() as session:
        warns = await session.execute(
            models.sql.select(models.Participant.id, models.Participant.warns).where(
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
                    votekicks=0,
                    group_id=event.message.chat_id,
                )
            )
            warns = 0
            action = 0  # avoid UnboundLocalError

        else:
            row_id, warns = warns.t

            await session.execute(
                models.sql.update(models.Participant)
                .values(
                    warns=(
                        0
                        if warns >= 2  # because will be perform action soon
                        else (warns + 1)
                    )
                )
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
            await _WARN_ACTIONS[action](
                event._client, event.message.chat_id, event.message.sender_id
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
                templates.texts("user_not_found", target=event.message.sender_id),
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


async def decrease_warn_query(event: OnCallbackQuery.Event):
    if event.chat_id not in env.GROUPS:
        return

    async with models.db() as session:
        has_access = await session.scalar(
            models.sql.select(models.Admin.id).where(
                models.Admin.user_id == event.sender_id,
                models.Admin.group_id == event.chat_id,
            )
        )

    if not has_access:
        await event.answer(templates.texts("permission_denied_1"), alert=True, cache_time=10)
        return

    user_id = event.data.split(b"/")[1].decode()

    try:
        user_id = int(user_id)
    except ValueError:
        pass

    async with models.db.begin() as session:
        warns = await session.execute(
            models.sql.select(models.Participant.id, models.Participant.warns).where(
                models.Participant.user_id == user_id,
                models.Participant.group_id == event.chat_id,
            )
        )
        row_id, warns = warns.fetchone().t

        assert warns > 0, f"warns ({warns}) is not greater than zero"

        await session.execute(
            models.sql.update(models.Participant)
            .values({models.Participant.warns: models.Participant.warns - 1})
            .where(models.Participant.id == row_id)
        )

    buttons = None
    if warns > 1:
        buttons = [
            [
                types.KeyboardButtonCallback(
                    templates.buttons("warns", "decrease"), f"decrease-warn/{user_id}"
                )
            ]
        ]

    await event._client.edit_message(
        event.chat_id,
        event.message_id,
        templates.texts("warn_decreased", id=user_id, warns=warns - 1),
        buttons=buttons,
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
