from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from store.models.db_model import Book, Order, OrderItem
from store.models.order_model import OrderCreate
from confluent_kafka import Producer
from store.kafka_config import PRODUCER_CONFIG
import json  

async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
    total = 0
    order_items = []

    for item in order_data.items:
        result = await db.execute(select(Book).where(Book.id == item.book_id))
        book = result.scalars().first()

        if not book:
            raise HTTPException(
                status_code=404, detail=f"Book ID {item.book_id} not found"
            )

        price = book.price
        subtotal = price * item.quantity
        total += subtotal

        order_item = OrderItem(
            book_id=book.id,
            quantity=item.quantity,
            price_per_item=price,
        )
        order_items.append(order_item)

    order = Order(total_amount=total, items=order_items)
    db.add(order)
    await db.commit()
    await db.refresh(order)

    try:
        order_payload = {
            "order_id": order.id,
            "total_amount": order.total_amount,
            "items": [
                {
                    "book_id": item.book_id,
                    "quantity": item.quantity,
                    "price_per_item": item.price_per_item,
                }
                for item in order.items
            ],
        }

        # Create Producer instance
        producer = Producer(PRODUCER_CONFIG)

        producer.produce(
            topic="order",
            key=str(order.id),
            value=json.dumps(order_payload),
            callback=delivery_callback,
        )
        
        producer.poll(0)
        producer.flush()  
    except Exception as e:
        print("Kafka Error:", str(e))

    return order


async def get_order(db: AsyncSession, order_id: int) -> Order:
    # Use selectinload to fetch related order_items eagerly
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


def delivery_callback(err, msg):
    if err:
        print("ERROR: Message failed delivery: {}".format(err))
    else:
        print(
            "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(),
                key=msg.key().decode("utf-8"),
                value=msg.value().decode("utf-8"),
            )
        )
