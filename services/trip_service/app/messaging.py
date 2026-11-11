import json
import os

import pika


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


if __name__ == "__main__":
    consume_messages("trip_events")
