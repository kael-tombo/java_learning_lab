# Interview: Spring Batch

Q: How does Spring Batch handle failures?
A: Transaction rollback at chunk level. Items can be skipped or retried. Job can restart from last failed chunk.

Q: What is the difference between tasklet and chunk-oriented step?
A: Tasklet does single task, chunk processes items in groups.
