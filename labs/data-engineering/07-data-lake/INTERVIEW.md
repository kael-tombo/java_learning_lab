# Data Lake Interview Questions

## Beginner
**Q**: What is the difference between a data lake and a data warehouse?
**A**: Data lakes store all data types (structured, semi-structured, raw) with schema-on-read. Data warehouses store processed, structured data with schema-on-write. Lakes are cheaper but require more processing.

## Intermediate
**Q**: Explain the medallion architecture.
**A**: Bronze (raw ingest), Silver (cleaned/validated), Gold (aggregated/business-ready). Each layer adds value and structure.

## Advanced
**Q**: Compare Delta Lake, Iceberg, and Hudi.
**A**: Delta Lake (Databricks) - best Spark integration, simple transaction log. Iceberg (Netflix) - best for partition evolution, multi-engine support. Hudi (Uber) - best for incremental processing and upserts at record level.
