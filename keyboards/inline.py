from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_main_menu():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📂 Tickets", callback_data="admin_tickets"),
          InlineKeyboardButton(text="➕ Create ticket", callback_data="admin_create_ticket"))
    b.row(InlineKeyboardButton(text="👥 Users", callback_data="admin_users:0"),
          InlineKeyboardButton(text="🧹 Clear DB", callback_data="admin_clear_db_confirm"))
    b.row(InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"))
    return b.as_markup()

def user_main_menu():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔵 Profile", callback_data="user_profile"),
          InlineKeyboardButton(text="🔵 Guides", callback_data="user_guides"))
    b.row(InlineKeyboardButton(text="🟢 Tickets", callback_data="user_tickets"))
    b.row(InlineKeyboardButton(text="🟢 Contacts", callback_data="user_contacts"),
          InlineKeyboardButton(text="🟢 Useful links", callback_data="user_links"))
    return b.as_markup()

def ticket_confirm_kb(part_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🟢 Confirm", callback_data=f"ticket_confirm_{part_id}")]])

def ticket_confirm_sure_kb(part_id):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Yes", callback_data=f"ticket_yes_{part_id}"),
          InlineKeyboardButton(text="❌ No", callback_data=f"ticket_no_{part_id}"))
    return b.as_markup()

def admin_ticket_action_kb(part_id):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Confirm", callback_data=f"admin_part_confirm_{part_id}"),
          InlineKeyboardButton(text="❌ Reject", callback_data=f"admin_part_reject_{part_id}"))
    return b.as_markup()

def user_list_kb(page, count, users):
    b = InlineKeyboardBuilder()
    for u in users:
        b.row(InlineKeyboardButton(text=f"{u.id} - {u.username}", callback_data=f"admin_user_{u.id}"))
    nav = []
    if page > 0: nav.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"admin_users:{page-1}"))
    if (page + 1) * 10 < count: nav.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"admin_users:{page+1}"))
    if nav: b.row(*nav)
    b.row(InlineKeyboardButton(text="✅ Approve All", callback_data="admin_approve_all"))
    b.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu"))
    return b.as_markup()

def user_card_kb(user_id, is_banned, is_approved, level):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="❌ Ban" if not is_banned else "✅ Unban", callback_data=f"admin_toggle_ban_{user_id}"),
          InlineKeyboardButton(text="✅ Approve" if not is_approved else "❌ Revoke", callback_data=f"admin_toggle_approve_{user_id}"))
    for lvl in [1, 2, 3]:
        text = f"🟢 Lvl {lvl}" if lvl == level else f"Lvl {lvl}"
        b.row(InlineKeyboardButton(text=text, callback_data=f"admin_set_level_{user_id}_{lvl}"))
    b.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_users:0"))
    return b.as_markup()

def clear_db_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⚠️ Yes, clear all", callback_data="admin_clear_db_yes"),
          InlineKeyboardButton(text="🔙 Cancel", callback_data="admin_menu"))
    return b.as_markup()

def close_ticket_kb(ticket_id):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="❌ Close Ticket", callback_data=f"admin_close_ticket_{ticket_id}"))
    b.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_tickets"))
    return b.as_markup()

def user_ticket_details_kb(part_id, is_confirmed):
    b = InlineKeyboardBuilder()
    if is_confirmed:
        b.row(InlineKeyboardButton(text="💬 Message Operator", callback_data=f"user_msg_op_{part_id}"))
    b.row(InlineKeyboardButton(text="🔙 Back", callback_data="user_tickets"))
    return b.as_markup()

def back_kb(target):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data=target)]])
