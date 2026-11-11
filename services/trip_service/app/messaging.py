import json
import os
import time
import pika
from datetime import datetime, timezone

from database import SessionLocal
from models import OutboxEvent


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        username=os.getenv("RABBITMQ_USER", "guest"),
        password=os.getenv("RABBITMQ_PASSWORD", "guest")
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            credentials=credentials
        )
    )

    return connection


def publish_message(queue_name: str, message: dict):
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message, ensure_ascii=False),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()


def consume_messages(queue_name: str):
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body.decode("utf-8"))
        print("Получено сообщение:", message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback
    )

    print(f"Ожидание сообщений из очереди {queue_name}...")
    channel.start_consuming()


def publish_outbox_events():
    db = SessionLocal()

    try:
        events = (
            db.query(OutboxEvent)
            .filter(OutboxEvent.processed_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .all()
        )

        for event in events:
            publish_message(
                queue_name="trip_events",
                message=event.payload
            )

            event.processed_at = datetime.now(timezone.utc)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def run_outbox_worker():
    while True:
        try:
            publish_outbox_events()
        except Exception as error:
            print("Ошибка обработки Outbox:", error)

        time.sleep(5)


if __name__ == "__main__":
    consume_messages("trip_events")
