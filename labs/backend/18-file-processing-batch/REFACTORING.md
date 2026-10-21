# Refactoring: Spring Batch

Before: Manual file processing with BufferedReader
After: FlatFileItemReader with field mapping

Before: Manual database inserts in loop
After: JdbcBatchItemWriter with batch SQL
