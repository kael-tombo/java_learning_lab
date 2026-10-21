# Apache Flink

## Overview
Apache Flink is a distributed stream processing framework for real-time data processing with exactly-once semantics, event-time processing, and state management.

## Key Concepts
- **DataStream**: Continuous stream of events
- **Event Time**: Time when events actually occurred
- **Watermarks**: Signals tracking progress in event time
- **State**: Managed, fault-tolerant state for operators
- **Checkpointing**: Distributed snapshots for fault recovery

## Java Example
`java
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;

public class FlinkJob {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(5000);

        DataStream<Event> stream = env
            .addSource(new FlinkKafkaConsumer<>("events", new EventDeserializer(), props))
            .assignTimestampsAndWatermarks(
                WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
                    .withTimestampAssigner((event, timestamp) -> event.getTimestamp()));

        stream.keyBy(Event::getCategory)
            .window(TumblingEventTimeWindows.of(Time.minutes(5)))
            .aggregate(new AverageAggregate())
            .print();

        env.execute("Flink Streaming Job");
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Apache Flink Theory

## Stream Processing Models
- **Batch**: Bounded data processed as a stream
- **Streaming**: Unbounded data processed continuously
- **Event-driven**: Applications react to incoming events

## Time Semantics
- **Event Time**: When the event occurred (source timestamp)
- **Processing Time**: When the event is processed
- **Ingestion Time**: When event enters Flink

## State Management
- **Keyed State**: Scoped to key in keyed streams
- **Operator State**: Scoped to operator parallelism
- **Managed State**: Automatically managed by Flink
- **Raw State**: Custom state implementation

## Exactly-Once Semantics
- **Idempotent Sinks**: Duplicate writes are safe
- **Transactional Sinks**: Two-phase commit protocol
- **Flink exactly-once**: Checkpoint + transactional sink

## Windows
- **Tumbling**: Fixed-size, non-overlapping
- **Sliding**: Fixed-size, overlapping
- **Session**: Gaps between events define windows
- **Global**: Single window for all records
- **Count-based**: Window by record count
