# Messaging Patterns - THEORY

## Overview

Messaging enables asynchronous communication, loose coupling, and scalability in distributed systems.

## 1. Message Patterns

### Point-to-Point
```java
public class PointToPointMessaging {
    public void send(String queue, Message message) {
        producer.send(queue, message);
    }
    
    public Message receive(String queue) {
        return consumer.receive(queue);
    }
}
```

### Publish-Subscribe
```java
public class PubSubMessaging {
    public void publish(String topic, Event event) {
        producer.publish(topic, event);
    }
    
    public void subscribe(String topic, Consumer<Event> handler) {
        consumer.subscribe(topic, handler);
    }
}
```

## 2. Message Broker Comparison

| Broker | Type | Throughput | Use Case |
|--------|------|------------|----------|
| Kafka | Pub/Sub | Very High | Event streaming |
| RabbitMQ | Hybrid | High | Task queues |
| ActiveMQ | Hybrid | Medium | Legacy integration |

## 3. Spring Integration

```java
@Configuration
@EnableIntegration
public class MessagingConfig {
    @Bean
    public MessageChannel orderChannel() {
        return new DirectChannel();
    }
    
    @Bean
    public IntegrationFlow orderFlow() {
        return f -> f
            .channel("orderChannel")
            .transform(orderTransformer())
            .handle(orderHandler());
    }
}
```

## Summary

1. **Point-to-Point**: One consumer per message (queues)
2. **Pub/Sub**: Multiple consumers (topics)
3. **Chose broker**: Kafka for streaming, RabbitMQ for tasks
4. **Use Spring**: Integration framework simplifies messaging

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Enabling Seamless Kafka Async Queuing with Consumer Proxy — Uber Engineering (31 Aug 2021) — https://www.uber.com/us/en/blog/kafka-async-queuing-with-consumer-proxy/ — Kafka is stream-oriented (ordered, one consumer per partition) while queueing wants unordered any-consumer delivery — this is the production rationale behind the lab's point-to-point-vs-pub/sub split and broker comparison table.
- Enabling Seamless Kafka Async Queuing with Consumer Proxy — Uber Engineering (31 Aug 2021) — https://www.uber.com/us/en/blog/kafka-async-queuing-with-consumer-proxy/ — Partition-scalability trap: at 1s downstream RPC latency, 1000 events/s needs ~1000 partitions, capping a 200k-partition cluster at ~200 such topics while each partition idles at 1 msg/s vs 10 MB/s capacity — size partitions from consumer latency, not just broker throughput.
- Enabling Seamless Kafka Async Queuing with Consumer Proxy — Uber Engineering (31 Aug 2021) — https://www.uber.com/us/en/blog/kafka-async-queuing-with-consumer-proxy/ — Uber's push-based Consumer Proxy adds intra-partition parallelism, out-of-order single-message acks (at-least-once), and a dead-letter queue for poison pills to defeat head-of-line blocking — harden any lab Kafka queueing design with the same three mechanisms.