from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import requests as db

router = Router()
MESSAGE_MAP = {}

@router.message(F.chat.type.in_(["group", "supergroup"]))
async def group_handler(message: Message, config, bot):
    if message.chat.id == config.work_group_id:
        if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
            uid = MESSAGE_MAP.get(message.reply_to_message.message_id)
            if uid:
                try: await bot.send_message(uid, f"Operator reply:\n{message.text}")
                except Exception as e: print(f"Reply err: {e}")

@router.callback_query(F.data.startswith("admin_part_confirm_"))
async def admin_part_confirm(callback: CallbackQuery, session, bot, config):
    if callback.from_user.id != config.admin_id: return await callback.answer("No", show_alert=True)
    p = await db.get_participation(session, int(callback.data.split("_")[-1]))
    await db.update_participation(session, p.id, status="confirmed")
    await bot.send_message(p.user_id, "Dialog opened.")
    await callback.message.edit_text(f"Confirmed.")
    await callback.answer()

@router.callback_query(F.data.startswith("admin_part_reject_"))
async def admin_part_reject(callback: CallbackQuery, session, bot, config):
    if callback.from_user.id != config.admin_id: return await callback.answer("No", show_alert=True)
    p = await db.get_participation(session, int(callback.data.split("_")[-1]))
    await db.delete_participation(session, p.id)
    try: await bot.send_message(p.user_id, "Rejected.")
    except: pass
    await callback.message.edit_text(f"Rejected.")
    await callback.answer()
