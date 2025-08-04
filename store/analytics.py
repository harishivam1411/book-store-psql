import json

import requests
from confluent_kafka import Consumer

from kafka_config import CONSUMER_CONFIG

LOG_SERVICE_URL = "http://localhost:9000/log"

consumer_config = {**CONSUMER_CONFIG, "group.id": "analytics-service"}

consumer = Consumer(consumer_config)
consumer.subscribe(["order"])


def send_log(message: str):
    try:
        response = requests.post(LOG_SERVICE_URL, json={"message": message})
        print(f"[ANALYTICS] Logged: {response.status_code}")
    except Exception as e:
        print("[ANALYTICS] Failed to send log:", str(e))


print("Analytics Consumer listening...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg and not msg.error():
            order_data = json.loads(msg.value().decode("utf-8"))
            log_message = f"Order ID {order_data['order_id']} with total ₹{order_data['total_amount']} received."
            send_log(log_message)
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
