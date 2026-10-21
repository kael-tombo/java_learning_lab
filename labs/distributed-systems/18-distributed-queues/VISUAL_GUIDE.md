# Visual Guide — Distributed Queues

## Queue Partition Layout
`
Topic "orders"
  Partition 0: [order1, order4, order7] (FIFO within partition)
  Partition 1: [order2, order5, order8]
  Partition 2: [order3, order6, order9]
Consumer A -> Partition 0, 1
Consumer B -> Partition 2
`

## Retry and DLQ Flow
`
send -> process() -> success: ack
send -> process() -> fail: retry(3x waiting)
send -> process() -> fail after retries: DLQ
DLQ -> manual inspect -> replay or discard
`
"@ -Encoding UTF8

Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\18-distributed-queues\SECURITY.md" -Value @"
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
