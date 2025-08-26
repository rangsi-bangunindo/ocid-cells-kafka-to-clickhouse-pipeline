import os

config = {
    "KAFKA_BROKER": os.getenv("KAFKA_BROKER", "kafka:9092"),
    "KAFKA_TOPIC_RAW": os.getenv("KAFKA_TOPIC_RAW"),
    "DATA_FILE_PATH": os.getenv("DATA_FILE_PATH"),
    "PRODUCER_BATCH_SIZE": int(os.getenv("PRODUCER_BATCH_SIZE", "1000")),
    "TIME_SPEEDUP": float(os.getenv("TIME_SPEEDUP", "8640")),
}
