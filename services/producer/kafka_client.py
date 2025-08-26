import json
import time
import socket
from kafka import KafkaProducer, errors
from common.config.config import config

def get_kafka_producer(max_retries=5, retry_interval=5):
    """
    Returns a Kafka producer instance configured for JSON messages
    with retries until Kafka broker is available.
    """

    # Check if broker hostname resolves
    try:
        broker_host = config["KAFKA_BROKER"].split("://")[-1].split(":")[0]  # Extract hostname
        ip = socket.gethostbyname(broker_host)
        print(f"Broker '{broker_host}' resolves to IP: {ip}")
    except Exception as e:
        print(f"Failed to resolve broker hostname '{broker_host}': {e}")
        raise

    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[config["KAFKA_BROKER"]],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=str.encode,
                linger_ms=10,
                acks='all',
            )
            return producer
        except errors.NoBrokersAvailable:
            print(f"Kafka broker not ready, retrying in {retry_interval}s... ({attempt+1}/{max_retries})")
            time.sleep(retry_interval)

    raise RuntimeError("Kafka broker not available after retries")
