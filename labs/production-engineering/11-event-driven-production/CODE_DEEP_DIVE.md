# CODE DEEP DIVE: Event-Driven & Kafka Production Engineering
## Lab 11 | Production Engineering Academy

---

## Pattern 1: Production Kafka Consumer with Non-Blocking Dead Letter Queue (DLQ)

```java
package com.learning.production.lab11;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.ContainerProperties;
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer;
import org.springframework.kafka.listener.DefaultErrorHandler;
import org.springframework.kafka.support.serializer.ErrorHandlingDeserializer;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.util.backoff.ExponentialBackOff;

import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableKafka
public class ProductionKafkaConsumerConfig {

    @Bean
    public ConsumerFactory<String, Object> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-broker-1:9092,kafka-broker-2:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processing-v2");

        // 1. Cooperative Sticky Assignor (Eliminates Stop-the-world rebalance storms)
        props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
                "org.apache.kafka.clients.consumer.CooperativeStickyAssignor");

        // 2. Poll pacing to prevent false eviction
        props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600_000); // 10 minutes
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 50);          // Max 50 items per poll

        // 3. Offset management: Manual immediate ack
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        // 4. Resilient Deserialization Wrappers (Catches poison pills before listener)
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
        props.put(ErrorHandlingDeserializer.KEY_DESERIALIZER_CLASS, StringDeserializer.class);
        props.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS, JsonDeserializer.class);
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.learning.domain.*");

        return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory(
            ConsumerFactory<String, Object> consumerFactory,
            KafkaTemplate<String, Object> kafkaTemplate) {

        ConcurrentKafkaListenerContainerFactory<String, Object> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.setConcurrency(4); // 4 consumer worker threads per container pod
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);

        // 5. Non-Blocking Retry with Exponential Backoff + DLQ Recovery
        ExponentialBackOff backOff = new ExponentialBackOff(500L, 2.0); // 500ms, 1s, 2s
        backOff.setMaxAttempts(3);

        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(kafkaTemplate);
        DefaultErrorHandler errorHandler = new DefaultErrorHandler(recoverer, backOff);

        // Do NOT retry poison pill serialization errors; send directly to DLQ
        errorHandler.addNotRetryableExceptions(
                org.apache.kafka.common.errors.SerializationException.class,
                com.fasterxml.jackson.core.JsonParseException.class
        );

        factory.setCommonErrorHandler(errorHandler);
        return factory;
    }
}
```

---

## Pattern 2: The Transactional Outbox Entity & Repository

```java
package com.learning.production.lab11;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    private UUID id;

    @Column(nullable = false)
    private String aggregateType;

    @Column(nullable = false)
    private String aggregateId;

    @Column(nullable = false)
    private String eventType;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String payload; // JSON representation of the domain event

    @Column(nullable = false)
    private Instant createdAt;

    public OutboxEvent() {}

    public OutboxEvent(String aggregateType, String aggregateId, String eventType, String payload) {
        this.id = UUID.randomUUID();
        this.aggregateType = aggregateType;
        this.aggregateId = aggregateId;
        this.eventType = eventType;
        this.payload = payload;
        this.createdAt = Instant.now();
    }
    // Getters and Setters
}
```
