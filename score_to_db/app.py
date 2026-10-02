import json
import logging
import os



import psycopg2
from confluent_kafka import Consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connection = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

consumer = Consumer({
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"],
    "group.id": "score-to-db",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})
consumer.subscribe(["scores"])

try:
    while True:
        message = consumer.poll(1.0)
        if message is None:
            continue
        if message.error():
            logger.error("Kafka: %s", message.error())
            continue


        result = json.loads(message.value().decode("utf-8"))
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scores (transaction_id, score, fraud_flag)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (transaction_id) DO NOTHING
                    """,
                    (result["transaction_id"], 
                     float(result["score"]), 
                     int(result["fraud_flag"])),
                )
        consumer.commit(message=message, asynchronous=False)
        logger.info("Processed transaction %s", result["transaction_id"])

finally:
    consumer.close()
    connection.close()
