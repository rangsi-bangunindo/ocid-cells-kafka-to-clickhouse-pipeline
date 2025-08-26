# Builder
FROM golang:1.24.4-alpine AS builder

WORKDIR /app

# Copy Go module files from services/transformer
COPY services/transformer/go.mod services/transformer/go.sum ./
RUN go mod download

# Copy the rest of the source
COPY services/transformer/ ./

RUN CGO_ENABLED=0 GOOS=linux go build -o transformer ./cmd/transformer

# Runtime
FROM alpine:latest

WORKDIR /app

# Copy binary
COPY --from=builder /app/transformer .

# Copy schema directory (from repo root)
COPY common/schema ./common/schema

ENTRYPOINT ["./transformer"]
