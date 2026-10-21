# How It Works: Spring Batch

Spring Batch uses a chunk-oriented processing model. Items are read one at a time by an ItemReader, buffered into a chunk (default size 1), then sent to an ItemProcessor for transformation. Once the chunk is full, the entire chunk is written by an ItemWriter. This allows efficient database batch operations while keeping memory usage predictable.
