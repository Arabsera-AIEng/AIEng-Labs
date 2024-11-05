import os
import json
import time
import logging
import random
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_data():
    # Simulate data retrieval
    data = {
        'timestamp': int(time.time()),
        'value': random.randint(0, 100)
    }
    return data


def produce_data():
    kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    topic = os.getenv('KAFKA_TOPIC', 'test_topic')

    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    logger.info(f"Connected to Kafka at {kafka_bootstrap_servers}, producing to topic '{topic}'")

    try:
        while True:
            data = get_data()
            producer.send(topic, data)
            logger.info(f"Sent data: {data}")
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error producing data: {e}")
    finally:
        producer.close()


if __name__ == "__main__":
    produce_data()
