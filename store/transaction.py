import asyncio
import json
import os
from datetime import datetime, timezone

from confluent_kafka import Consumer
from dotenv import load_dotenv
from kafka_config import CONSUMER_CONFIG
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

load_dotenv()
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/book_store"
)


class OrderTransaction(Base):
    __tablename__ = "order_transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True)
    total_amount = Column(Integer)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

consumer_config = {**CONSUMER_CONFIG, "group.id": "transaction-service"}

consumer = Consumer(consumer_config)
consumer.subscribe(["order"])


async def save_transaction(order_data):
    async with async_session() as session:
        transaction = OrderTransaction(
            order_id=order_data["order_id"], total_amount=order_data["total_amount"]
        )
        session.add(transaction)
        await session.commit()
        print(f"[TRANSACTION] Stored order {order_data['order_id']}")


async def consume():
    print("Transaction Service started.")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg and not msg.error():
                order_data = json.loads(msg.value().decode("utf-8"))
                await save_transaction(order_data)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


asyncio.run(consume())
