
from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

app = FastAPI()
Base = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///./logs.db"
engine = create_async_engine(DATABASE_URL, echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class LogData(BaseModel):
    message: str


@app.post("/log")
async def create_log(log: LogData):
    async with Session() as session:
        new_log = Log(message=log.message)
        session.add(new_log)
        await session.commit()
        return {"status": "logged"}
