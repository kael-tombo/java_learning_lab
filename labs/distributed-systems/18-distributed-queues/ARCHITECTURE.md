# Architecture — Distributed Queues

## Queue System Architecture
`
Producer -> Queue Broker (partitioned)
              |
              +-> Partition 0 (ordered)
              +-> Partition 1 (ordered)
              +-> Partition 2 (ordered)
              |
Consumer Group -> subscribes to partitions
`

## Pulsar Architecture
`
Producer -> Pulsar Broker
              |
              +-> BookKeeper (persistent storage)
              +-> ZooKeeper (metadata)
              |
Consumer -> subscribes to topic
`

## Retry and DLQ Flow
`
send -> retry(3) -> DLQ
         |          |
         v          v
    process      manual inspect
      ack        or replay
`
"@

W "SECURITY.md" @"
# Security — Distributed Queues

## Threats
- Unauthorized message publishing/consumption
- Message tampering in transit
- Queue flooding (DoS)
- Sensitive data in messages

## Mitigations
- Authentication (OAuth2, TLS client certs)
- Authorization (topic-level ACLs)
- Encryption at rest and in transit
- Message payload encryption (application-level)
- Rate limiting per producer
- Audit logging of queue operations
