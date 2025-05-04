from telegram import OnNewMessage, errors
from telegram.utils import resolve_target_id
from core import env, templates
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

    target_id = await resolve_target_id(event.message)

    if not target_id:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="mute"),
            reply_to=event.message.id,
        )
        return

    try:
        await event._client.edit_permissions(
            event.message.chat_id,
            target_id,
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
            templates.texts("user_not_found", target=target_id),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_muted", id=target_id),
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

    target_id = await resolve_target_id(event.message)

    if not target_id:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("command_need_target_1", command="unmute"),
            reply_to=event.message.id,
        )
        return

    try:
        await event._client.edit_permissions(
            event.message.chat_id,
            target_id,
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
            templates.texts("user_not_found", target=target_id),
            reply_to=event.message.id,
        )
    else:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("user_unmuted", id=target_id),
            reply_to=event.message.id,
        )
