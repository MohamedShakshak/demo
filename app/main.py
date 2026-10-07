from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import llm
from .config import settings
from .db import Base, engine, get_db
from .models import User
from .schemas import ChatRequest, ChatResponse, UserOut

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Stage 1 only: auto-create tables. We'll replace this with Alembic later.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/users", response_model=list[UserOut])
async def list_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(min(limit, 100)))
    return result.scalars().all()

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = await llm.chat(req.messages)
    return ChatResponse(reply=reply, model=settings.cohere_model)