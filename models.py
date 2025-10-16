from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3", echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(32), unique=True)
    username: Mapped[str | None] = mapped_column(String(32), unique=True)
    full_name: Mapped[str | None] = mapped_column(String(64))
    phone: Mapped[str | None] = mapped_column(String(16))
    role: Mapped[str] = mapped_column(String(16))  # admin, trainer, client
    created_at: Mapped[str | None] = mapped_column(String(32))
    updated_at: Mapped[str | None] = mapped_column(String(32))

class Trainer(Base):
    __tablename__ = "trainers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    bio: Mapped[str | None] = mapped_column(String(256))
    specialization: Mapped[str | None] = mapped_column(String(64))
    invite_code: Mapped[str | None] = mapped_column(String(16), unique=True)

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    goal: Mapped[str | None] = mapped_column(String(128))
    height: Mapped[int | None] = mapped_column(BigInteger)
    dob: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[str | None] = mapped_column(String(32))

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    type: Mapped[str] = mapped_column(String(32))
    start_date: Mapped[str] = mapped_column(String(16))
    end_date: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16))
    payment_id: Mapped[str | None] = mapped_column(String(64))

class Visit(Base):
    __tablename__ = "visits"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    date: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16))  # present/absent
    note: Mapped[str | None] = mapped_column(String(256))

class FoodLog(Base):
    __tablename__ = "food_logs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    date: Mapped[str] = mapped_column(String(16))
    calories: Mapped[int | None] = mapped_column(BigInteger)
    protein: Mapped[int | None] = mapped_column(BigInteger)
    fat: Mapped[int | None] = mapped_column(BigInteger)
    carbs: Mapped[int | None] = mapped_column(BigInteger)
    raw_input: Mapped[str | None] = mapped_column(String(512))

class Workout(Base):
    __tablename__ = "workouts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    name: Mapped[str] = mapped_column(String(128))
    exercises: Mapped[str] = mapped_column(String(1024))  # JSON string
    date: Mapped[str] = mapped_column(String(16))

class Schedule(Base):
    __tablename__ = "schedule"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    date_time: Mapped[str] = mapped_column(String(32))
    capacity: Mapped[int | None] = mapped_column(BigInteger)
    place: Mapped[str | None] = mapped_column(String(64))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_from: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_to: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String(1024))
    automated: Mapped[bool] = mapped_column()
    created_at: Mapped[str] = mapped_column(String(32))

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    question: Mapped[str] = mapped_column(String(256))
    answer: Mapped[str] = mapped_column(String(1024))
    embeddings: Mapped[str | None] = mapped_column(String(2048))  # vector as string

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[str | None] = mapped_column(String(2048))  # JSON string
    created_at: Mapped[str] = mapped_column(String(32))