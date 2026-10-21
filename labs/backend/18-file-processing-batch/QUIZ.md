# Quiz: Spring Batch

## Question 1
What is a chunk in Spring Batch?
A) A single record
B) A group of records processed together
C) A job parameter
D) A step execution

**Answer: B** - A chunk is a group of records read, processed, and written as a unit.

## Question 2
Which interface transforms data between read and write?
A) ItemReader
B) ItemProcessor
C) ItemWriter
D) ItemStream

**Answer: B** - ItemProcessor transforms items between reading and writing.

## Question 3
What is the default commit interval in Spring Batch?
A) 1
B) 10
C) 100
D) 1000

**Answer: A** - Default commit interval is 1 (process one item at a time).

## Question 4
Which annotation starts a scheduled job?
A) @BatchJob
B) @Scheduled
C) @JobLaunch
D) @Cron

**Answer: B** - @Scheduled triggers job execution on a schedule.

## Question 5
What stores batch execution metadata?
A) JobRepository
B) JobMetadataStore
C) BatchMetaData
D) ExecutionContext

**Answer: A** - JobRepository persists job and step execution metadata.
