from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from store.database import init_db
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

app = FastAPI()
Base = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///./logs.db"
engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


class LogData(BaseModel):
    message: str


@app.post("/log")
async def create_log(log: LogData):
    async with Session() as session:
        new_log = Log(message=log.message)
        session.add(new_log)
        await session.commit()
        return {"status": "logged"}


if __name__ == "__main__":
    uvicorn.run("store.log:app", host="127.0.0.1", port=9000, reload=True)
