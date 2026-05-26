from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.editor import safe_edit
from database import requests as db
from keyboards import inline as kb
from states.admin_states import AdminCreateTicket, AdminBroadcast
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def admin_start(message: Message, config, session, state: FSMContext):
    # ✅ CRITICAL FIX: Explicitly skip non-admins so user.router catches /start
    if message.from_user.id != config.admin_id:
        return

    await state.clear()
    await message.answer("Admin Menu", reply_markup=kb.admin_main_menu())

@router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback.message, "Admin Menu", kb.admin_main_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_tickets")
async def admin_tickets(callback: CallbackQuery, session):
    tickets = await db.get_active_tickets(session)
    if not tickets: await safe_edit(callback.message, "No active tickets.", kb.back_kb("admin_menu"))
    else:
        b = InlineKeyboardBuilder()
        for t in tickets: b.row(InlineKeyboardButton(text=f"{t.id}: {t.title}", callback_data=f"admin_view_ticket_{t.id}"))
        b.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu"))
        await safe_edit(callback.message, "Active Tickets:", b.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_view_ticket_"))
async def admin_view_ticket(callback: CallbackQuery, session):
    t_id = int(callback.data.split("_")[-1])
    t = await db.get_ticket(session, t_id)
    text = f"Ticket #{t.id}\nOperator: {t.operator_name}\nTitle: {t.title}\nDesc: {t.description}\nTarget: {t.target}"
    await safe_edit(callback.message, text, kb.close_ticket_kb(t.id))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_close_ticket_"))
async def admin_close_ticket(callback: CallbackQuery, session, bot):
    t_id = int(callback.data.split("_")[-1])
    await db.close_ticket(session, t_id)
    
    # Fetch all users participating in this specific ticket
    participations = await db.get_ticket_participations(session, t_id)
    for p in participations:
        try: 
            await bot.send_message(p.user_id, f"Ticket #{t_id} has been closed by the admin.")
        except Exception as e: 
            print(f"Failed to notify user {p.user_id}: {e}")
            
    await safe_edit(callback.message, f"Ticket #{t_id} closed.", kb.back_kb("admin_menu"))
    await callback.answer("Closed")

# FSM Create Ticket
@router.callback_query(F.data == "admin_create_ticket")
async def start_create_ticket(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCreateTicket.operator_name)
    await safe_edit(callback.message, "Enter operator name:", kb.back_kb("admin_menu"))
    await callback.answer()

@router.message(AdminCreateTicket.operator_name)
async def get_op(message: Message, state: FSMContext):
    await state.update_data(operator_name=message.text)
    await state.set_state(AdminCreateTicket.title)
    await message.answer("Enter ticket title:")

@router.message(AdminCreateTicket.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AdminCreateTicket.description)
    await message.answer("Enter ticket description:")

@router.message(AdminCreateTicket.description)
async def get_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminCreateTicket.target)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="All approved", callback_data="target_all"))
    b.row(InlineKeyboardButton(text="Single user", callback_data="target_single"))
    await message.answer("Select target:", reply_markup=b.as_markup())

@router.callback_query(AdminCreateTicket.target, F.data == "target_all")
async def target_all(callback: CallbackQuery, state: FSMContext, session, bot):
    d = await state.get_data()
    t = await db.create_ticket(session, d["operator_name"], d["title"], d["description"], "all")
    for u in await db.get_approved_users(session):
        try:
            p = await db.add_participation(session, t.id, u.id)
            msg = await bot.send_message(u.id, f"New Ticket!\nTitle: {t.title}\nDesc: {t.description}", reply_markup=kb.ticket_confirm_kb(p.id))
            await db.update_participation(session, p.id, user_chat_msg_id=msg.message_id)
        except: pass
    await safe_edit(callback.message, f"Ticket #{t.id} sent.", kb.back_kb("admin_menu"))
    await state.clear(); await callback.answer()

@router.callback_query(AdminCreateTicket.target, F.data == "target_single")
async def target_single(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Enter user_id:")
    await callback.answer()

@router.message(AdminCreateTicket.target, F.text.isdigit())
async def target_single_id(message: Message, state: FSMContext, session, bot):
    d = await state.get_data()
    uid = int(message.text)
    t = await db.create_ticket(session, d["operator_name"], d["title"], d["description"], "single", uid)
    try:
        p = await db.add_participation(session, t.id, uid)
        msg = await bot.send_message(uid, f"New Ticket!\nTitle: {t.title}\nDesc: {t.description}", reply_markup=kb.ticket_confirm_kb(p.id))
        await db.update_participation(session, p.id, user_chat_msg_id=msg.message_id)
        await message.answer(f"Sent to {uid}.", reply_markup=kb.back_kb("admin_menu"))
    except Exception as e: await message.answer(f"Failed: {e}")
    await state.clear()

# Users Menu
@router.callback_query(F.data.startswith("admin_users:"))
async def admin_users(callback: CallbackQuery, session):
    page = int(callback.data.split(":")[1])
    count = await db.count_users(session)
    users = await db.get_all_users(session, page * 10, 10)
    await safe_edit(callback.message, f"Users (Page {page+1})", kb.user_list_kb(page, count, users))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_card(callback: CallbackQuery, session):
    uid = int(callback.data.split("_")[-1])
    u = await db.get_user(session, uid)
    text = f"ID: {u.id}\n@{u.username}\nApproved: {u.is_approved}\nBanned: {u.is_banned}\nLevel: {u.level}"
    await safe_edit(callback.message, text, kb.user_card_kb(u.id, u.is_banned, u.is_approved, u.level))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_toggle_ban_"))
async def toggle_ban(callback: CallbackQuery, session):
    uid = int(callback.data.split("_")[-1])
    u = await db.get_user(session, uid)
    await db.update_user_status(session, uid, is_banned=not u.is_banned)
    await admin_user_card(callback, session)

@router.callback_query(F.data.startswith("admin_toggle_approve_"))
async def toggle_approve(callback: CallbackQuery, session):
    uid = int(callback.data.split("_")[-1])
    u = await db.get_user(session, uid)
    await db.update_user_status(session, uid, is_approved=not u.is_approved)
    await admin_user_card(callback, session)

@router.callback_query(F.data.startswith("admin_set_level_"))
async def set_level(callback: CallbackQuery, session):
    _, _, _, uid, lvl = callback.data.split("_")
    await db.update_user_status(session, int(uid), level=int(lvl))
    await admin_user_card(callback, session)

@router.callback_query(F.data == "admin_approve_all")
async def approve_all(callback: CallbackQuery, session):
    await db.approve_all_users(session)
    await callback.answer("Approved!", show_alert=True)
    await admin_users(callback, session)

@router.callback_query(F.data == "admin_clear_db_confirm")
async def clear_db_confirm(callback: CallbackQuery):
    await safe_edit(callback.message, "Are you sure?", kb.clear_db_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_clear_db_yes")
async def clear_db_yes(callback: CallbackQuery, session):
    await db.clear_db(session)
    await safe_edit(callback.message, "DB cleared.", kb.back_kb("admin_menu"))
    await callback.answer()

# Broadcast
@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminBroadcast.text)
    await safe_edit(callback.message, "Enter text:", kb.back_kb("admin_menu"))
    await callback.answer()

@router.message(AdminBroadcast.text)
async def get_b_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="All", callback_data="b_target_all"))
    b.row(InlineKeyboardButton(text="Single", callback_data="b_target_single"))
    await message.answer("Target:", reply_markup=b.as_markup())
    await state.set_state(AdminBroadcast.target)

@router.callback_query(AdminBroadcast.target, F.data == "b_target_all")
async def b_target_all(callback: CallbackQuery, state: FSMContext, session, bot):
    d = await state.get_data()
    sent = 0
    for u in await db.get_approved_users(session):
        try: await bot.send_message(u.id, d["text"]); sent += 1
        except: pass
    await safe_edit(callback.message, f"Sent to {sent}.", kb.back_kb("admin_menu"))
    await state.clear(); await callback.answer()

@router.callback_query(AdminBroadcast.target, F.data == "b_target_single")
async def b_target_single(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("User ID:")
    await callback.answer()

@router.message(AdminBroadcast.target, F.text.isdigit())
async def b_target_single_id(message: Message, state: FSMContext, bot):
    d = await state.get_data()
    try: await bot.send_message(int(message.text), d["text"]); await message.answer("Sent.")
    except Exception as e: await message.answer(f"Fail: {e}")
    await state.clear()
