# transaction_service/main.py
import asyncio
import json
from confluent_kafka import Consumer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from store.models.db_model import Base, OrderTransaction  
from kafka_config import COMMON_CONFIG
import os

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

consumer_config = {**COMMON_CONFIG}

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
