# Data Warehousing Interview Questions

## Beginner
**Q**: Explain the difference between OLTP and OLAP.
**A**: OLTP is for transactional processing (row-oriented, many small writes); OLAP is for analytical processing (column-oriented, complex queries on large datasets).

## Intermediate
**Q**: When would you use a snowflake schema over a star schema?
**A**: When storage is a concern and dimension tables are very large with deep hierarchies. Star is preferred for query performance.

## Advanced
**Q**: How would you design a warehouse for 100TB of data with sub-second query SLAs?
**A**: Use partitioning by date, bucketing by high-cardinality keys, materialized views for common aggregations, columnar storage, and MPP compute. Implement data skipping with statistics and bloom filters.
