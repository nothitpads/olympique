from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from models import async_session, Base, engine, User, Trainer, Client, Subscription, Visit, FoodLog, Schedule, KnowledgeBase, Message, AnalyticsEvent
from pydantic import BaseModel
from sqlalchemy import select
import asyncio

app = FastAPI(title="Fitness Trainer Mini-App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")

class TelegramAuthRequest(BaseModel):
    telegram_id: str
    username: str | None = None
    full_name: str | None = None
    phone: str | None = None
    language_code: str | None = None

@app.post("/api/v1/auth/telegram")
async def auth_telegram(data: TelegramAuthRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = result.scalar_one_or_none()
    if user:
        return {"status": "ok", "user_id": user.id}
    new_user = User(
        telegram_id=data.telegram_id,
        username=data.username,
        full_name=data.full_name,
        phone=data.phone,
        role="client",
        created_at="",  # Fill with actual timestamp
        updated_at=""
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"status": "created", "user_id": new_user.id}

class LinkTrainerRequest(BaseModel):
    client_id: int
    invite_code: str

from sqlalchemy.exc import NoResultFound

@app.post("/api/v1/link_trainer")
async def link_trainer(data: LinkTrainerRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trainer).where(Trainer.invite_code == data.invite_code))
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    result = await db.execute(select(Client).where(Client.id == data.client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.trainer_id = trainer.id
    await db.commit()
    return {"status": "linked", "trainer_id": trainer.id}

class SubscriptionPurchaseRequest(BaseModel):
    client_id: int
    trainer_id: int
    type: str
    start_date: str
    end_date: str
    payment_id: str | None = None

@app.post("/api/v1/subscription/purchase")
async def purchase_subscription(data: SubscriptionPurchaseRequest, db: AsyncSession = Depends(get_db)):
    sub = Subscription(
        client_id=data.client_id,
        trainer_id=data.trainer_id,
        type=data.type,
        start_date=data.start_date,
        end_date=data.end_date,
        status="active",
        payment_id=data.payment_id
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return {"status": "created", "subscription_id": sub.id}

@app.get("/api/v1/subscription/status")
async def subscription_status(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription).where(Subscription.client_id == client_id, Subscription.status == "active"))
    sub = result.scalar_one_or_none()
    if not sub:
        return {"status": "none"}
    return {"status": "active", "subscription": {
        "id": sub.id,
        "trainer_id": sub.trainer_id,
        "type": sub.type,
        "start_date": sub.start_date,
        "end_date": sub.end_date,
        "payment_id": sub.payment_id
    }}

class AttendanceRequest(BaseModel):
    client_id: int
    trainer_id: int
    date: str
    status: str  # present/absent
    note: str | None = None

@app.post("/api/v1/clients/{client_id}/checkin")
async def checkin(client_id: int, data: AttendanceRequest, db: AsyncSession = Depends(get_db)):
    visit = Visit(
        client_id=client_id,
        trainer_id=data.trainer_id,
        date=data.date,
        status=data.status,
        note=data.note
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return {"status": "checked_in", "visit_id": visit.id}

@app.get("/api/v1/clients/{client_id}/attendance_history")
async def attendance_history(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visit).where(Visit.client_id == client_id))
    visits = result.scalars().all()
    return [{
        "id": v.id,
        "trainer_id": v.trainer_id,
        "date": v.date,
        "status": v.status,
        "note": v.note
    } for v in visits]

class FoodLogRequest(BaseModel):
    client_id: int
    date: str
    calories: int | None = None
    protein: int | None = None
    fat: int | None = None
    carbs: int | None = None
    raw_input: str | None = None

@app.post("/api/v1/foodlog")
async def log_food(data: FoodLogRequest, db: AsyncSession = Depends(get_db)):
    log = FoodLog(
        client_id=data.client_id,
        date=data.date,
        calories=data.calories,
        protein=data.protein,
        fat=data.fat,
        carbs=data.carbs,
        raw_input=data.raw_input
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return {"status": "logged", "food_log_id": log.id}

@app.get("/api/v1/clients/{client_id}/foodlogs")
async def get_foodlogs(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FoodLog).where(FoodLog.client_id == client_id))
    logs = result.scalars().all()
    return [{
        "id": l.id,
        "date": l.date,
        "calories": l.calories,
        "protein": l.protein,
        "fat": l.fat,
        "carbs": l.carbs,
        "raw_input": l.raw_input
    } for l in logs]

class ScheduleRequest(BaseModel):
    trainer_id: int
    date_time: str
    capacity: int | None = None
    place: str | None = None
    created_by: int

@app.post("/api/v1/schedule")
async def create_schedule(data: ScheduleRequest, db: AsyncSession = Depends(get_db)):
    sched = Schedule(
        trainer_id=data.trainer_id,
        date_time=data.date_time,
        capacity=data.capacity,
        place=data.place,
        created_by=data.created_by
    )
    db.add(sched)
    await db.commit()
    await db.refresh(sched)
    return {"status": "created", "schedule_id": sched.id}

@app.get("/api/v1/schedule")
async def get_schedule(client_id: int = None, trainer_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(Schedule)
    if trainer_id:
        query = query.where(Schedule.trainer_id == trainer_id)
    result = await db.execute(query)
    schedules = result.scalars().all()
    return [{
        "id": s.id,
        "trainer_id": s.trainer_id,
        "date_time": s.date_time,
        "capacity": s.capacity,
        "place": s.place,
        "created_by": s.created_by
    } for s in schedules]

class KnowledgeQueryRequest(BaseModel):
    trainer_id: int
    question: str

@app.post("/api/v1/knowledge/query")
async def knowledge_query(data: KnowledgeQueryRequest, db: AsyncSession = Depends(get_db)):
    # Primary: FAQ from knowledge_base
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.trainer_id == data.trainer_id, KnowledgeBase.question == data.question))
    kb = result.scalar_one_or_none()
    if kb:
        return {"answer": kb.answer, "source": "faq"}
    # Secondary: fallback to trainer notes or LLM (not implemented here)
    return {"answer": "No answer found. Please contact your trainer.", "source": "fallback"}

@app.get("/api/v1/clients")
async def get_clients(trainer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.trainer_id == trainer_id))
    clients = result.scalars().all()
    return [{
        "id": c.id,
        "goal": c.goal,
        "height": c.height,
        "dob": c.dob,
        "created_at": c.created_at
    } for c in clients]

@app.get("/api/v1/clients/{client_id}/progress")
async def get_progress(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FoodLog).where(FoodLog.client_id == client_id))
    logs = result.scalars().all()
    # Aggregate nutrition progress
    total_calories = sum(l.calories or 0 for l in logs)
    total_protein = sum(l.protein or 0 for l in logs)
    total_fat = sum(l.fat or 0 for l in logs)
    total_carbs = sum(l.carbs or 0 for l in logs)
    return {
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_fat": total_fat,
        "total_carbs": total_carbs,
        "days_logged": len(logs)
    }

@app.get("/api/v1/reports/summary")
async def get_summary(trainer_id: int, period: str = None, db: AsyncSession = Depends(get_db)):
    # Example: count clients, visits, food logs
    result = await db.execute(select(Client).where(Client.trainer_id == trainer_id))
    clients = result.scalars().all()
    client_ids = [c.id for c in clients]
    visit_count = 0
    foodlog_count = 0
    if client_ids:
        result = await db.execute(select(Visit).where(Visit.client_id.in_(client_ids)))
        visit_count = len(result.scalars().all())
        result = await db.execute(select(FoodLog).where(FoodLog.client_id.in_(client_ids)))
        foodlog_count = len(result.scalars().all())
    return {
        "client_count": len(clients),
        "visit_count": visit_count,
        "foodlog_count": foodlog_count
    }

class MessageRequest(BaseModel):
    user_from: int
    user_to: int
    text: str
    automated: bool = False
    created_at: str

@app.post("/api/v1/messages/send")
async def send_message(data: MessageRequest, db: AsyncSession = Depends(get_db)):
    msg = Message(
        user_from=data.user_from,
        user_to=data.user_to,
        text=data.text,
        automated=data.automated,
        created_at=data.created_at
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"status": "sent", "message_id": msg.id}

class AnalyticsEventRequest(BaseModel):
    user_id: int
    event_type: str
    payload: str | None = None
    created_at: str

@app.post("/api/v1/analytics/log")
async def log_analytics_event(data: AnalyticsEventRequest, db: AsyncSession = Depends(get_db)):
    event = AnalyticsEvent(
        user_id=data.user_id,
        event_type=data.event_type,
        payload=data.payload,
        created_at=data.created_at
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return {"status": "logged", "event_id": event.id}

@app.get("/api/v1/analytics")
async def get_analytics(user_id: int = None, event_type: str = None, db: AsyncSession = Depends(get_db)):
    query = select(AnalyticsEvent)
    if user_id:
        query = query.where(AnalyticsEvent.user_id == user_id)
    if event_type:
        query = query.where(AnalyticsEvent.event_type == event_type)
    result = await db.execute(query)
    events = result.scalars().all()
    return [{
        "id": e.id,
        "user_id": e.user_id,
        "event_type": e.event_type,
        "payload": e.payload,
        "created_at": e.created_at
    } for e in events]

def require_role(required_role: str):
    async def role_dependency(user_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or user.role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return Security(role_dependency)

# Example usage for a trainer-only endpoint:
# @app.get("/api/v1/trainer/clients")
# async def trainer_clients(user: User = Depends(require_role("trainer")), db: AsyncSession = Depends(get_db)):
#     ...
