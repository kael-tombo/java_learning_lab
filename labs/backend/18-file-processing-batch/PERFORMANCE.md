# Performance: Spring Batch

- Tune chunk size (50-1000 depending on data)
- Use multi-threaded steps for CPU-bound processing
- Use partitioning for I/O-bound processing
- Configure connection pool size for database writers
- Monitor job metrics (read/write counts, processing time)
