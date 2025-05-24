from telegram import OnCallbackQuery, types
from core import env, templates
import models


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


async def change_warn_action_query(event: OnCallbackQuery.Event):
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

    async with models.db.begin() as session:
        admins = await session.scalar(
            models.sql.select(models.sql.func.count(models.Admin.id)).where(
                models.Admin.group_id == event.chat_id
            )
        )
        trusted = await session.scalar(
            models.sql.select(models.sql.func.count(models.Participant.id)).where(
                models.Participant.group_id == event.chat_id,
                models.Participant.is_trusted == True,
            )
        )
        warned = await session.scalar(
            models.sql.select(models.sql.func.count(models.Participant.id)).where(
                models.Participant.group_id == event.chat_id,
                models.Participant.warns > 0,
            )
        )
        warn_action = await session.scalar(
            models.sql.select(models.Group.warn_action).where(models.Group.id == event.chat_id)
        )
        warn_action = (warn_action + 1) % 4

        await session.execute(
            models.sql.update(models.Group)
            .values(warn_action=warn_action)
            .where(models.Group.id == event.chat_id)
        )

    await event._client.edit_message(
        event.chat_id,
        event.message_id,
        templates.texts(
            "settings",
            id=event.chat_id,
            admins=admins,
            trusted=trusted,
            warned=warned,
            warn_action=templates.texts("settings_warn_action_" + str(warn_action)),
        ),
        buttons=[
            [
                types.KeyboardButtonCallback(
                    templates.buttons("settings", "change_warn_action"), "change-warn-action"
                )
            ]
        ],
    )
