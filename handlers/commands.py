from telegram import OnNewMessage, errors
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
    except (ValueError, errors.UserIdInvalidError, errors.PeerIdInvalidError):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.ParticipantIdInvalidError:
        pass
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
    except (ValueError, errors.UserIdInvalidError, errors.PeerIdInvalidError):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.ParticipantIdInvalidError:
        pass
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
    except (ValueError, errors.UserIdInvalidError, errors.PeerIdInvalidError):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.ParticipantIdInvalidError:
        pass
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
    except (ValueError, errors.UserIdInvalidError, errors.PeerIdInvalidError):
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_not_found", target=target_id.user_id),
            reply_to=event.message.id,
        )
    except errors.ParticipantIdInvalidError:
        pass
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
