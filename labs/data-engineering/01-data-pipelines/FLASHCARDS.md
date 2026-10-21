# Flashcards: Data Pipelines

## Card 1
**Front**: What is a data pipeline?
**Back**: A series of data processing steps that move data from sources to destinations, transforming and enriching it along the way.

## Card 2
**Front**: What are the three main stages of an ETL pipeline?
**Back**: Extract (read from source), Transform (process/clean), Load (write to target)

## Card 3
**Front**: What is the difference between batch and stream processing?
**Back**: Batch processes finite data sets on a schedule; stream processes continuous data in real-time.

## Card 4
**Front**: What is a DAG in pipeline processing?
**Back**: Directed Acyclic Graph - a graph of processing steps where edges represent data dependencies and cycles are forbidden.

## Card 5
**Front**: What is backpressure?
**Back**: A flow control mechanism where downstream components signal upstream to slow down when they can't keep up.

## Card 6
**Front**: What is exactly-once semantics?
**Back**: A processing guarantee that each record is processed exactly one time, even in the event of failures.

## Card 7
**Front**: What is a dead letter queue?
**Back**: A storage location for messages that fail processing, allowing for later inspection and reprocessing.

## Card 8
**Front**: What is the role of Apache Kafka in data pipelines?
**Back**: Kafka serves as a distributed event streaming platform that acts as the central nervous system for data pipelines.

## Card 9
**Front**: What is a watermark in stream processing?
**Back**: A threshold that defines how late data can arrive and still be included in window computations.

## Card 10
**Front**: What is schema evolution in pipelines?
**Back**: The ability of a pipeline to handle changes in data schema over time without breaking.
