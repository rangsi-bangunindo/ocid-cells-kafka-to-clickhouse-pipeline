package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/hamba/avro/v2"

	"ocid-cells-kafka-to-clickhouse-pipeline/services/transformer/internal"
	"ocid-cells-kafka-to-clickhouse-pipeline/services/transformer/pkg/kafka"
)

func main() {
	// Load Avro schema
	if err := internal.LoadSchema(); err != nil {
		log.Fatalf("failed to load schema: %v", err)
	}

	broker := os.Getenv("KAFKA_BROKER")
	topicIn := os.Getenv("KAFKA_TOPIC_RAW")
	topicOut := os.Getenv("KAFKA_TOPIC_TRANSFORMED")
	groupID := os.Getenv("TRANSFORMER_GROUP_ID")

	// Ensure the output topic exists
	if err := kafka.EnsureTopic(broker, topicOut, 3, 1); err != nil {
		log.Fatalf("failed to ensure topic %s: %v", topicOut, err)
	}

	if broker == "" || topicIn == "" || topicOut == "" || groupID == "" {
		log.Fatal("missing required env vars (KAFKA_BROKER, KAFKA_TOPIC_RAW, KAFKA_TOPIC_TRANSFORMED, TRANSFORMER_GROUP_ID)")
	}

	// Create consumer & producer (no error return)
	consumer := kafka.NewConsumer(broker, topicIn, groupID)
	defer consumer.Close()

	producer := kafka.NewProducer(broker)
	defer producer.Close()

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Handle shutdown signals
	go func() {
		sigchan := make(chan os.Signal, 1)
		signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)
		<-sigchan
		cancel()
	}()

	fmt.Println("Transformer service started")

	// Consume loop
	for {
		select {
		case <-ctx.Done():
			fmt.Println("shutting down transformer...")
			return
		default:
			msg, err := consumer.ReadMessage(ctx)
			if err != nil {
				log.Printf("failed to read message: %v", err)
				continue
			}

			// Decode incoming Avro into map
			var raw map[string]interface{}
			if err := avro.Unmarshal(internal.CellRawSchema, msg.Value, &raw); err != nil {
				log.Printf("failed to decode Avro: %v", err)
				continue
			}

			// Transform message
			transformed := internal.Transform(raw)

			// Encode back to JSON
			outBytes, err := json.Marshal(transformed)
			if err != nil {
				log.Printf("failed to marshal transformed message: %v", err)
				continue
			}

			// Produce enriched record
			if err := producer.Write(ctx, kafka.Message(topicOut, outBytes)); err != nil {
				log.Printf("failed to produce message: %v", err)
			}
		}
	}
}
