# Why Data Lakes Exist

## The Problem
Traditional data warehouses are expensive, rigid, and can't handle unstructured data. Organizations need a place to store all data types - structured, semi-structured, and unstructured - without upfront schema design.

## Root Cause
- Data volume growing faster than warehouse capacity
- Variety of data formats (JSON, Avro, Parquet, images, logs)
- Schema-on-write requires upfront design
- Need for raw data preservation for ML and data science

## Data Lake Solution
- Cheap object storage (S3, ADLS, GCS)
- Schema-on-read (flexibility)
- Store everything, transform later
- Supports ML, AI, analytics workloads
