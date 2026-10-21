# Math Foundations — Distributed Queues

## 1. Throughput vs Partitions

Throughput T = P * R where:
- P = number of partitions
- R = throughput per partition

## 2. Message Latency

End-to-end latency = queue_time + processing_time + ack_time

Under load, queue_time follows: W = L / (1 - rho)
Where rho = arrival_rate / service_rate

## 3. Deduplication Window

Memory for deduplication: M = R * W * ID_size
Where R = message rate, W = dedup window

## 4. Retry Backoff

Exponential backoff: delay = base * 2^attempt
With jitter: delay = random(base * 2^attempt, base * 2^(attempt+1))

## 5. DLQ Probability

P(DLQ) = P(failure)^max_retries
With P(failure)=10% and max_retries=3: P(DLQ)=0.1%
