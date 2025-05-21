from telegram import OnNewMessage
from telegram.utils import parse_command_message
from core import env, templates
import datetime
import cachebox
import models
import typing


async def votekick_command(event: OnNewMessage.Event):
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
            templates.texts("command_need_target_1", command="votekick"),
            reply_to=event.message.id,
        )
        return

    async with models.db() as session:
        is_trusted = await session.scalar(
            models.sql.select(models.Participant.id).where(
                models.Participant.user_id == target.user_id,
                models.Participant.group_id == event.message.chat_id,
                models.Participant.is_trusted == True,
            )
        )

    if is_trusted:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("votekick_to_trusted"),
            reply_to=event.message.id,
        )
        return

    key = (event.message.chat_id, target.user_id)

    if key not in models.VOTEKICKS:
        models.VOTEKICKS[key] = [event.message.sender_id]
    else:
        if event.message.sender_id in models.VOTEKICKS[key]:
            return
        
        models.VOTEKICKS[key].append(event.message.sender_id)

    votekick_participants, remaining = models.VOTEKICKS.get_with_expire(key)

    if len(votekick_participants) >= 3:
        models.VOTEKICKS.pop(key)

        await event._client.edit_permissions(
            event.message.chat_id,
            target.user_id,
            view_messages=False,
            until_date=datetime.timedelta(hours=24),
        )

        await event._client.send_message(
            event.message.chat_id,
            templates.texts("votekick_agree", id=target.user_id),
            reply_to=event.message.id,
        )

    else:
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        remaining_seconds = remaining % 60

        await event._client.send_message(
            event.message.chat_id,
            templates.texts(
                "votekick_pending",
                id=target.user_id,
                votekicks=", ".join(str(i) for i in votekick_participants),
                duration="{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(remaining_seconds)),
            ),
            reply_to=event.message.id,
        )
