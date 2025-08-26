import gzip
import csv
import time
import fastavro
from io import BytesIO
from services.producer.kafka_client import get_kafka_producer
from common.config.config import config
from pathlib import Path
import json

DATA_FILE_PATH = config["DATA_FILE_PATH"]
TOPIC_RAW = config["KAFKA_TOPIC_RAW"]
BATCH_SIZE = config["PRODUCER_BATCH_SIZE"]
TIME_SPEEDUP = config["TIME_SPEEDUP"]

# Load schema once (source of truth)
schema_path = Path(__file__).parents[2] / "common" / "schema" / "cell_raw.avsc"
with open(schema_path) as f:
    schema = json.load(f)

def normalize_row(row):
    """Cast CSV strings into types matching cell_raw.avsc"""
    return {
        "radio": row["radio"],
        "mcc": int(row["mcc"]),
        "net": int(row["net"]),
        "area": int(row["area"]),
        "cell": int(row["cell"]),
        "unit": int(row["unit"]),
        "lon": float(row["lon"]),
        "lat": float(row["lat"]),
        "range": int(row["range"]),
        "samples": int(row["samples"]),
        "changeable": int(row["changeable"]),
        "created": int(row["created"]),
        "updated": int(row["updated"]),
        "averageSignal": int(row["averageSignal"]),
    }

def avro_serialize(record):
    """Serialize dict into Avro binary using schemaless_writer"""
    buf = BytesIO()
    fastavro.schemaless_writer(buf, schema, record)
    return buf.getvalue()

def load_and_sort_csv(file_path):
    """Load CSV from .gz and sort by 'updated' ascending"""
    rows = []
    with gzip.open(file_path, mode="rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["updated"] = int(row["updated"])
            rows.append(row)
    rows.sort(key=lambda r: r["updated"])
    return rows

def calculate_sleep(prev_ts, current_ts):
    """Calculate sleep duration based on timestamps and TIME_SPEEDUP"""
    delta_sec = current_ts - prev_ts
    return delta_sec / TIME_SPEEDUP

def run_producer():
    producer = get_kafka_producer()
    rows = load_and_sort_csv(DATA_FILE_PATH)

    prev_updated = None
    batch = []

    for row in rows:
        record = normalize_row(row)
        key_str = f"{record['mcc']}-{record['net']}-{record['area']}-{record['cell']}"

        # Throttle according to event-time compression
        if prev_updated is not None:
            sleep_sec = calculate_sleep(prev_updated, record["updated"])
            if sleep_sec > 0:
                time.sleep(sleep_sec)

        batch.append((key_str, record))
        prev_updated = record["updated"]

        # Flush batch
        if len(batch) >= BATCH_SIZE:
            for key, rec in batch:
                # Key is str, KafkaProducer already encodes it
                producer.send(TOPIC_RAW, key=key, value=avro_serialize(rec))
            producer.flush()
            batch.clear()

    # Flush remaining
    for key, rec in batch:
        producer.send(TOPIC_RAW, key=key, value=avro_serialize(rec))
    producer.flush()

    print("All records produced successfully (Avro, schema-driven)")

if __name__ == "__main__":
    run_producer()
