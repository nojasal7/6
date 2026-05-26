from sqlalchemy import select, update, delete, func
from .models import User, Ticket, Participation, Log
from datetime import datetime

async def get_user(session, user_id):
    return (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()

async def add_user(session, user_id, username):
    user = User(id=user_id, username=username)
    session.add(user)
    await session.commit()
    return user

async def update_user_status(session, user_id, **kwargs):
    stmt = update(User).where(User.id == user_id).values(**kwargs)
    await session.execute(stmt)
    await session.commit()

async def get_all_users(session, offset, limit):
    return (await session.execute(select(User).offset(offset).limit(limit))).scalars().all()

async def count_users(session):
    return (await session.execute(select(func.count()).select_from(User))).scalar_one()

async def approve_all_users(session):
    await session.execute(update(User).where(User.is_banned == False).values(is_approved=True))
    await session.commit()

async def clear_db(session):
    for table in [Participation, Ticket, User, Log]:
        await session.execute(delete(table))
    await session.commit()

async def create_ticket(session, operator_name, title, description, target, target_user_id=None):
    ticket = Ticket(operator_name=operator_name, title=title, description=description, target=target, target_user_id=target_user_id)
    session.add(ticket)
    await session.commit()
    return ticket

async def get_ticket(session, ticket_id):
    return (await session.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one_or_none()

async def get_active_tickets(session):
    return (await session.execute(select(Ticket).where(Ticket.is_closed == False))).scalars().all()

async def close_ticket(session, ticket_id):
    await session.execute(update(Ticket).where(Ticket.id == ticket_id).values(is_closed=True))
    await session.execute(update(Participation).where(Participation.ticket_id == ticket_id).values(status="closed"))
    await session.commit()

async def add_participation(session, ticket_id, user_id, user_chat_msg_id=None):
    part = Participation(ticket_id=ticket_id, user_id=user_id, user_chat_msg_id=user_chat_msg_id)
    session.add(part)
    await session.commit()
    return part
async def get_ticket_participations(session, ticket_id):
    return (await session.execute(select(Participation).where(Participation.ticket_id == ticket_id))).scalars().all()
    
async def get_user_participations(session, user_id):
    return (await session.execute(select(Participation).where(Participation.user_id == user_id, Participation.status.in_(["pending", "confirmed"])))).scalars().all()

async def get_participation(session, part_id):
    return (await session.execute(select(Participation).where(Participation.id == part_id))).scalar_one_or_none()

async def update_participation(session, part_id, **kwargs):
    await session.execute(update(Participation).where(Participation.id == part_id).values(**kwargs))
    await session.commit()

async def delete_participation(session, part_id):
    await session.execute(delete(Participation).where(Participation.id == part_id))
    await session.commit()

async def log_message(session, user_id, text):
    session.add(Log(user_id=user_id, text=text))
    await session.commit()

async def get_approved_users(session):
    return (await session.execute(select(User).where(User.is_approved == True, User.is_banned == False))).scalars().all()
