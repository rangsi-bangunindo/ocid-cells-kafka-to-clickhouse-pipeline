# OCID Cells Kafka Stream Pipeline

A containerized data pipeline for ingesting, transforming, and streaming OpenCelliD cell tower data using **Kafka**, **Python**, and **Go**.

- **Producer (Python)**: Reads cell tower data from CSV, encodes into Avro, and streams into Kafka (`cell_tower_raw`).
- **Transformer (Go)**: Consumes Avro records, enriches with additional fields, and publishes JSON messages into Kafka (`cell_tower_transformed`).
- **Kafka UI**: Web interface to inspect brokers, topics, partitions, and consumers.

---

## Project Structure

```
ocid-cells-kafka-stream-pipeline/
│── README.md
│── .gitignore
│── .env.example                    # sample env file to copy from
│── .env                            # actual env values
│── Dockerfile.producer             # Python producer
│── docker-compose.yml              # stack definition
├── data/
│   └── cell_towers.csv.gz          # source OpenCelliD dataset
├── common/
│   ├── __init__.py
│   ├── config/                     # shared config
│   │   ├── __init__.py
│   │   └── config.py
│   └── schema/                     # Avro schemas
│       ├── cell_raw.avsc
│       └── cell_transformed.avsc
└── services/
    ├── __init__.py
    ├── producer/                   # Python producer
    │   ├── __init__.py
    │   ├── producer.py
    │   ├── kafka_client.py
    │   └── requirements.txt
    └── transformer/                # Go transformer
        ├── Dockerfile
        ├── go.mod
        ├── go.sum
        ├── cmd/
        │   └── transformer/
        │       └── main.go
        ├── internal/
        │   ├── transformer.go
        │   └── schema.go
        └── pkg/
            └── kafka/
                ├── admin.go
                ├── producer.go
                └── consumer.go

```

---

## Getting Started

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### 2. Clone the Repository

```bash
git clone https://github.com/<your-org>/ocid-cells-kafka-stream-pipeline.git
cd ocid-cells-kafka-stream-pipeline
```

### 3. Environment Variables

Copy the example env file and adjust if necessary:

```bash
cp .env.example .env
```

Key variables:

- `KAFKA_BROKER` → Kafka broker address inside Docker network (`kafka:9092`)
- `KAFKA_TOPIC_RAW` → Topic for raw Avro (`cell_tower_raw`)
- `KAFKA_TOPIC_TRANSFORMED` → Topic for transformed JSON (`cell_tower_transformed`)
- `DATA_FILE_PATH` → Input CSV file path for producer

### 4. Start the Stack

```bash
docker-compose up --build
```

This will launch:

- Zookeeper
- Kafka broker
- Kafka-UI (web interface)
- Producer (Python)
- Transformer (Go)

---

## Kafka UI (Browser Dashboard)

Access the dashboard at:
http://localhost:8080

### Brokers

Shows broker ID, partitions, leaders, and disk usage.

### Topics

Inspect messages in `cell_tower_raw` (Avro) and `cell_tower_transformed` (JSON).

- `cell_tower_raw`: 1 partition, producer writes here
- `cell_tower_transformed`: 3 partitions, transformer writes here

### Consumers

Track consumer groups and lag.

- `transformer-service` subscribes to `cell_tower_raw`
- Writes results into `cell_tower_transformed`

---

## Data Flow

### 1. Producer

Reads `data/cell_towers.csv.gz` → serializes each record to Avro using `cell_raw.avsc` → sends to topic `cell_tower_raw`.

### 2. Transformer

Consumes `cell_tower_raw` → decodes Avro → enriches with dummy fields (`country`, `region`, `city`, etc.) → publishes JSON to topic `cell_tower_transformed`.

### 3. Kafka UI

Verify broker, topics, and consumer groups are healthy. You can also browse messages.

---

## Common Commands

Rebuild and restart services:

```bash
docker-compose up --build
```

Check logs for a specific service:

```bash
docker logs -f producer
docker logs -f transformer
```

Stop everything:

```bash
docker-compose down
```

---

## Validation

- Raw Topic (`cell_tower_raw`) → Should show Avro-encoded binary data.
- Transformed Topic (`cell_tower_transformed`) → Should show enriched JSON like:

```json
{
  "mcc": 432,
  "net": 35,
  "area": 42785,
  "cell": 37046,
  "lat": 37.2608,
  "lon": 49.5842,
  "radio": "GSM",
  "samples": 1,
  "range": 1000,
  "created": 1708732846,
  "updated": 1708732846,
  "country": "DummyCountry",
  "region": "DummyRegion",
  "city": "DummyCity",
  "timezone": "UTC+0",
  "population_density": 135.05
}
```

## Notes

- All services are isolated inside `kafka-net` Docker network.
- `producer` batch size and speed can be tuned in `.env` (`PRODUCER_BATCH_SIZE`, `TIME_SPEEDUP`).
- Make sure your `.env` file matches `.env.example`.
- To add more consumers, extend `services/consumer/`.
