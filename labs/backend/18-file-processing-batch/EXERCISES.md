# Exercises: Spring Batch

## Exercise 1: CSV to Database
Create a job that reads a CSV file and writes to a database.

### Task
1. Define a FlatFileItemReader for CSV input
2. Create a domain object matching CSV columns
3. Configure JdbcBatchItemWriter for database output
4. Run the job and verify data in H2 console

## Exercise 2: Data Transformation
Add item processing to transform data during batch.

### Task
1. Create an ItemProcessor that converts names to uppercase
2. Add validation logic (reject invalid records)
3. Configure skip logic for validation errors
4. Monitor skipped items in logs

## Exercise 3: Scheduled Batch Job
Schedule a batch job to run daily.

### Task
1. Enable scheduling with @EnableScheduling
2. Create a scheduled method that launches the job
3. Configure cron expression for daily execution
4. Log job execution results

## Exercise 4: Job with Multiple Steps
Create a multi-step job for ETL processing.

### Task
1. Step 1: Extract - read from CSV
2. Step 2: Transform - process data
3. Step 3: Load - write to database + generate summary report
4. Configure conditional flow (if step 2 fails, skip step 3)

## Exercise 5: Restart and Recovery
Implement error recovery in batch jobs.

### Task
1. Simulate a job failure (file not found)
2. Fix the file and restart the job
3. Verify it resumes from where it left off
4. Configure job restart behavior
