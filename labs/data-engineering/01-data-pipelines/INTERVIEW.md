# Interview Questions: Data Pipelines

## Beginner
**Q**: Explain what a data pipeline is in simple terms.
**A**: A data pipeline is like an automated assembly line for data - it moves information from where it's collected to where it's used, cleaning and transforming it along the way.

## Intermediate
**Q**: Compare ETL and ELT approaches.
**A**: ETL transforms data before loading to the target, good for complex transformations on smaller data. ELT loads raw data first and transforms in the warehouse, better for big data since the warehouse handles transformation at scale.

## Advanced
**Q**: How would you implement exactly-once processing in a streaming pipeline?
**A**: This requires: 1) Idempotent sinks 2) Transactional source offset management 3) Checkpointing for state recovery. In Spark + Kafka, this means using the Kafka transaction API for offset commits alongside sink idempotency.

## Senior
**Q**: Design a data pipeline for a real-time fraud detection system.
**A**: Key components: 1) Kafka for event ingestion 2) Flink/Spark for real-time feature computation 3) ML model serving layer 4) Rules engine for threshold alerts 5) Feedback loop for model retraining. Must handle 10K+ events/sec with sub-second latency.
