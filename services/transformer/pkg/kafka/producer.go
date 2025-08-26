package kafka

import (
	"context"

	"github.com/segmentio/kafka-go"
)

// Producer wraps kafka.Writer
type Producer struct {
	writer *kafka.Writer
}

// NewProducer creates a new Producer instance
func NewProducer(broker string) *Producer {
	return &Producer{
		writer: kafka.NewWriter(kafka.WriterConfig{
			Brokers: []string{broker},
			Async:   true,
		}),
	}
}

// Close shuts down the writer
func (p *Producer) Close() error {
	return p.writer.Close()
}

// Write writes messages to Kafka
func (p *Producer) Write(ctx context.Context, msgs ...kafka.Message) error {
	return p.writer.WriteMessages(ctx, msgs...)
}

// Message helper for producing
func Message(topic string, value []byte) kafka.Message {
	return kafka.Message{
		Topic: topic,
		Value: value,
	}
}
