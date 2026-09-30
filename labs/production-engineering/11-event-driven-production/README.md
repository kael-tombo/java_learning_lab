# Lab 11: Event-Driven Architecture & Kafka in Production
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Messaging / Event-Driven

---

## 🎯 Objectives

- Design event-driven systems with proper event schemas
- Configure Kafka producers and consumers for production
- Handle exactly-once semantics (or at-least-once correctly)
- Monitor Kafka consumer lag and implement alerting
- Design dead letter queues and error handling strategies
- Implement event sourcing and outbox pattern
- Handle schema evolution with Avro and Schema Registry

---

## 📖 Real-World Context

**"The Consumer Lag Catastrophe"**: An order processing consumer fell behind by 2 million messages during a traffic spike. The team tried to speed it up by increasing `max.poll.records`. Instead, processing took longer per poll, triggering session timeouts. Kafka kicked the consumer out of the group, causing rebalances, causing more lag. A rebalance storm that took 6 hours to recover. The right fix was to add more consumer instances and tune `max.poll.interval.ms`.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Kafka internals, event-driven patterns, exactly-once |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Consumer lag, rebalance storms, poison pill messages |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Spring Kafka, Avro, Schema Registry, outbox pattern |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Event sourcing, CQRS, saga decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Consumer lag incident runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Kafka and event-driven design questions |
| [EXERCISES.md](./EXERCISES.md) | Build an event-sourced order system |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Kafka anti-patterns (wrong offsets, no DLQ, etc.) |
| [CHECKLIST.md](./CHECKLIST.md) | Kafka production readiness checklist |

---

## ⚙️ Production Kafka Consumer Config

```java
@Bean
KafkaListenerContainerFactory<ConcurrentMessageListenerContainer<String, OrderEvent>> kafkaListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConcurrency(3);  // 3 consumer threads per instance
    factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
    factory.getContainerProperties().setPollTimeout(3000);
    
    Map<String, Object> configs = new HashMap<>();
    configs.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 100);       // Process 100 per poll
    configs.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000); // 5min processing budget
    configs.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 45000);
    configs.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 3000);
    // ... schema registry, deserializer config
    return factory;
}
```

---

## 🔗 Related Labs
- Lab 04: [Distributed Resilience](../04-distributed-resilience/)
- Lab 06: [Microservices at Scale](../06-microservices-scale/)
- Lab 17: [Data Architecture](../17-data-architecture/)
