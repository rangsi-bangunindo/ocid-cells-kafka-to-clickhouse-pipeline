import gzip
import csv
import time
from datetime import datetime
from services.producer.kafka_client import get_kafka_producer
from common.config.config import config

DATA_FILE_PATH = config["DATA_FILE_PATH"]
TOPIC_RAW = config["KAFKA_TOPIC_RAW"]
BATCH_SIZE = config["PRODUCER_BATCH_SIZE"]
TIME_SPEEDUP = config["TIME_SPEEDUP"]

def load_and_sort_csv(file_path):
    """Load CSV from .gz and sort by 'updated' ascending"""
    rows = []
    with gzip.open(file_path, mode='rt', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['updated'] = int(row['updated'])
            rows.append(row)
    rows.sort(key=lambda r: r['updated'])
    return rows

def calculate_sleep(prev_ts, current_ts):
    """Calculate sleep duration based on timestamps and TIME_SPEEDUP"""
    delta_sec = current_ts - prev_ts
    sleep_time = delta_sec / TIME_SPEEDUP
    return sleep_time

def run_producer():
    producer = get_kafka_producer()
    rows = load_and_sort_csv(DATA_FILE_PATH)
    
    prev_updated = None
    batch = []
    
    for row in rows:
        key_str = f"{row['mcc']}-{row['net']}-{row['area']}-{row['cell']}"
        
        # Calculate sleep to preserve relative event time
        if prev_updated is not None:
            sleep_sec = calculate_sleep(prev_updated, row['updated'])
            if sleep_sec > 0:
                time.sleep(sleep_sec)
        
        batch.append((key_str, row))
        prev_updated = row['updated']
        
        # Send batch
        if len(batch) >= BATCH_SIZE:
            for key, msg in batch:
                producer.send(TOPIC_RAW, key=key, value=msg)
            producer.flush()
            batch.clear()
    
    # Send remaining
    for key, msg in batch:
        producer.send(TOPIC_RAW, key=key, value=msg)
    producer.flush()
    print("All records produced successfully.")

if __name__ == "__main__":
    run_producer()