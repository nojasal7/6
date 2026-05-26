from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    banned_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operator_name: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    target: Mapped[str] = mapped_column(String) 
    target_user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Participation(Base):
    __tablename__ = "participations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="pending") 
    user_chat_msg_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    group_msg_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

class Log(Base):
    __tablename__ = "logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
