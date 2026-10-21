# ETL Interview Questions

## Beginner
**Q**: What is the purpose of the staging area in ETL?
**A**: The staging area serves as a buffer zone where raw data is landed before transformation. It allows for error recovery, data validation, and auditing without affecting source or target systems.

## Intermediate
**Q**: How would you handle a slowly changing dimension Type 2?
**A**: Create a new row for each change with effective dates. Old rows get an end_date, new rows have current effective date and an indicator flag.

## Advanced
**Q**: Design an ETL system for a global retail company with 50TB of daily data.
**A**: Use partitioned data ingestion, Spark for distributed transform, Delta Lake for ACID transactions on data lake, incremental CDC from sources, and multi-hop data architecture (bronze, silver, gold layers).
