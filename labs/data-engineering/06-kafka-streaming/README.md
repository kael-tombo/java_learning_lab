# Kafka Streaming

## Overview
Kafka Streams is a client library for building stream processing applications that run on top of Apache Kafka, providing exactly-once semantics, stateful processing, and real-time data pipelines.

## Key Concepts
- **KStream**: Record stream, each record is independent
- **KTable**: Changelog stream, each record is an update
- **GlobalKTable**: Fully replicated table for joins
- **State Store**: Local state for stateful operations
- **Exactly-Once**: Guaranteed processing semantics

## Java Example
`java
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.KTable;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;

public class WordCountApp {
    public static void main(String[] args) {
        StreamsBuilder builder = new StreamsBuilder();

        KStream<String, String> textLines = builder.stream("input-topic");

        KTable<String, Long> wordCounts = textLines
            .flatMapValues(line -> Arrays.asList(line.toLowerCase().split("\\W+")))
            .groupBy((key, word) -> word)
            .count(Materialized.as("counts-store"));

        wordCounts.toStream().to("output-topic", Produced.with(Serdes.String(), Serdes.Long()));

        KafkaStreams streams = new KafkaStreams(builder.build(), getStreamsConfig());
        streams.start();
    }

    private static Properties getStreamsConfig() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "wordcount-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
        return props;
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Kafka Streaming Theory

## Streams Architecture
Kafka Streams is a lightweight library (not a cluster) that embeds directly into Java applications.

## Stream-Table Duality
- **KStream**: Append-only log of facts
- **KTable**: Update log (changelog) representing current state
- Either can be derived from the other

## Processing Guarantees
- **At-most-once**: No retries, may lose data
- **At-least-once**: Retry on failure, may duplicate
- **Exactly-once**: Transactional producers + idempotent writes

## State Stores
- **RocksDB**: Embedded key-value store (default)
- **InMemory**: Pure in-memory store
- **Timestamped**: Stores with timestamp per record

## Windowing
- **Tumbling**: Fixed non-overlapping windows
- **Hopping**: Fixed overlapping windows
- **Session**: Activity-based windows
- **Sliding**: Time-based join windows
