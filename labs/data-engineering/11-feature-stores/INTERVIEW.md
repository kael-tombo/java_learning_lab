# Feature Store Interview Questions

## Beginner
**Q**: What problem does a feature store solve?
**A**: It solves the problem of feature duplication, training/serving skew, and lack of feature discovery by providing a centralized platform for feature engineering, storage, and serving.

## Intermediate
**Q**: Explain the difference between online and offline feature stores.
**A**: The online store (Redis, Cassandra) provides low-latency access to the latest feature values for real-time serving. The offline store (S3, Delta Lake) stores all historical feature values for training data generation.

## Advanced
**Q**: Design a feature store that handles both batch and streaming features.
**A**: Use Spark for batch feature computation (daily/hourly) and Flink for streaming features (real-time). Store in Delta Lake for offline, materialize latest to Redis for online. Use a feature registry with metadata, and implement point-in-time correct joins for training.
