# Apache Spark Interview Questions

## Beginner
**Q**: Explain the difference between transformations and actions in Spark.
**A**: Transformations (map, filter, groupBy) create new RDDs lazily. Actions (count, collect, save) trigger execution and return results to the driver.

## Intermediate
**Q**: How does Spark handle fault tolerance?
**A**: RDDs track lineage - the sequence of transformations used to build them. If a partition is lost, Spark recomputes it using the lineage, avoiding replication overhead.

## Advanced
**Q**: Explain adaptive query execution in Spark 3.x.
**A**: AQE dynamically optimizes query plans at runtime using statistics collected during execution. It can coalesce shuffle partitions, switch join strategies, and handle skew automatically.
