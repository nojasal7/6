from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.editor import safe_edit
from database import requests as db
from keyboards import inline as kb
from states.user_states import UserMessageOperator
from handlers.group import MESSAGE_MAP

router = Router()

@router.message(Command("start"))
async def user_start(message: Message, config, state: FSMContext):
    if message.from_user.id != config.admin_id:
        await state.clear()
        await message.answer_photo(photo=config.ui_image_file_id, caption="Main Menu", reply_markup=kb.user_main_menu())

@router.callback_query(F.data == "user_menu")
async def user_menu(callback: CallbackQuery, config, state: FSMContext):
    await state.clear()
    await safe_edit(callback.message, "Main Menu", kb.user_main_menu())
    await callback.answer()

@router.callback_query(F.data == "user_profile")
async def user_profile(callback: CallbackQuery, session):
    u = await db.get_user(session, callback.from_user.id)
    active = len([p for p in await db.get_user_participations(session, u.id) if p.status == "confirmed"])
    await safe_edit(callback.message, f"ID: {u.id}\n@{u.username}\nLevel: {u.level}\nActive: {active}", kb.back_kb("user_menu"))
    await callback.answer()

@router.callback_query(F.data == "user_tickets")
async def user_tickets(callback: CallbackQuery, session):
    parts = await db.get_user_participations(session, callback.from_user.id)
    if not parts: await safe_edit(callback.message, "No tickets.", kb.back_kb("user_menu"))
    else:
        b = InlineKeyboardBuilder()
        for p in parts:
            t = await db.get_ticket(session, p.ticket_id)
            b.row(InlineKeyboardButton(text=f"{t.title} ({p.status})", callback_data=f"user_view_ticket_{p.id}"))
        b.row(InlineKeyboardButton(text="🔙 Back", callback_data="user_menu"))
        await safe_edit(callback.message, "Your Tickets:", b.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("user_view_ticket_"))
async def user_view_ticket(callback: CallbackQuery, session):
    p_id = int(callback.data.split("_")[-1])
    p = await db.get_participation(session, p_id)
    t = await db.get_ticket(session, p.ticket_id)
    await safe_edit(callback.message, f"Ticket: {t.title}\nStatus: {p.status}", kb.user_ticket_details_kb(p.id, p.status == "confirmed"))
    await callback.answer()

@router.callback_query(F.data.startswith("ticket_confirm_"))
async def ticket_confirm(callback: CallbackQuery, session):
    p_id = int(callback.data.split("_")[-1])
    p = await db.get_participation(session, p_id)
    t = await db.get_ticket(session, p.ticket_id)
    if t.is_closed: await callback.answer("This ticket is closed", show_alert=True); return
    await safe_edit(callback.message, "Are you sure?", kb.ticket_confirm_sure_kb(p.id))
    await callback.answer()

@router.callback_query(F.data.startswith("ticket_yes_"))
async def ticket_yes(callback: CallbackQuery, session, bot, config):
    p_id = int(callback.data.split("_")[-1])
    p = await db.get_participation(session, p_id)
    t = await db.get_ticket(session, p.ticket_id)
    if t.is_closed: await callback.answer("This ticket is closed", show_alert=True); return
    if len(await db.get_user_participations(session, callback.from_user.id)) > 1:
        await callback.answer("Only 1 active ticket allowed!", show_alert=True); return
        
    await db.update_participation(session, p.id, status="pending")
    await safe_edit(callback.message, "Waiting for admin.", kb.back_kb("user_menu"))
    
    u = await db.get_user(session, callback.from_user.id)
    msg = await bot.send_message(config.work_group_id, f"Confirmation!\nTicket #{t.id}\nUser @{u.username} ({u.id})", reply_markup=kb.admin_ticket_action_kb(p.id))
    await db.update_participation(session, p.id, group_msg_id=msg.message_id)
    MESSAGE_MAP[msg.message_id] = p.user_id
    await callback.answer()

@router.callback_query(F.data.startswith("ticket_no_"))
async def ticket_no(callback: CallbackQuery, session):
    p_id = int(callback.data.split("_")[-1])
    await db.delete_participation(session, p_id)
    await safe_edit(callback.message, "Rejected.", kb.back_kb("user_menu"))
    await callback.answer()

@router.callback_query(F.data.startswith("user_msg_op_"))
async def start_msg_op(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserMessageOperator.waiting_message)
    await state.update_data(part_id=int(callback.data.split("_")[-1]))
    await safe_edit(callback.message, "Send message:", kb.back_kb("user_menu"))
    await callback.answer()

@router.message(UserMessageOperator.waiting_message)
async def send_to_op(message: Message, state: FSMContext, session, bot, config):
    d = await state.get_data()
    p = await db.get_participation(session, d["part_id"])
    u = await db.get_user(session, message.from_user.id)
    msg = await bot.send_message(config.work_group_id, f"[Ticket #{p.ticket_id}] User @{u.username} ({u.id}): {message.text}")
    MESSAGE_MAP[msg.message_id] = message.from_user.id
    await message.answer("Sent.")
    await state.clear()
