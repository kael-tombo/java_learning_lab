# Common Mistakes: Spring Batch

1. **Too small chunk size**: Default 1 is too small for large datasets
2. **Not configuring skip logic**: One bad record fails entire job
3. **Forgetting JobRepository**: Must configure database for metadata
4. **Incorrect field mapping**: CSV columns must match domain properties
5. **No restart configuration**: Jobs should be restartable
