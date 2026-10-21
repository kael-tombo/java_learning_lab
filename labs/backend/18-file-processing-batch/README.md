# Lab 18: File Processing with Spring Batch

## Overview
Spring Batch provides a lightweight, comprehensive framework for batch processing. Learn chunk-oriented processing, readers/writers, scheduling, and fault tolerance.

## Topics Covered
- Spring Batch architecture (Job, Step, Chunk)
- ItemReader, ItemProcessor, ItemWriter
- Flat file processing (CSV, fixed-width)
- Database readers/writers (JdbcCursorItemReader)
- Job scheduling with @Scheduled
- Job monitoring and restart
- Multi-threaded steps
- Skip and retry logic

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- Basic SQL knowledge

## Getting Started
`ash
mvn spring-boot:run
# Access H2 Console: http://localhost:8080/h2-console
`

## Key Dependencies
`xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-batch</artifactId>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\18-file-processing-batch "THEORY.md") @"
# Theory: Spring Batch

## 1. Chunk-Oriented Processing

Spring Batch processes data in chunks rather than one record at a time. Each chunk goes through:
1. **Read**: ItemReader reads one item from input
2. **Process**: ItemProcessor transforms the item
3. **Buffer**: Items are buffered until chunk size reached
4. **Write**: ItemWriter writes the entire chunk

## 2. Job and Step Architecture

- **Job**: Complete batch process, contains one or more Steps
- **Step**: Sequential phase of a job
- **JobInstance**: Logical run of a job with parameters
- **JobExecution**: Single attempt to run a JobInstance
- **StepExecution**: Single attempt to run a Step
- **JobRepository**: Persists execution metadata

## 3. Readers and Writers

### ItemReader Implementations
- FlatFileItemReader: CSV/fixed-width files
- JdbcCursorItemReader: Database cursor
- JdbcPagingItemReader: Database with pagination
- StaxEventItemReader: XML files
- JsonItemReader: JSON files
- MultiResourceItemReader: Multiple files

### ItemWriter Implementations
- FlatFileItemWriter: CSV output
- JdbcBatchItemWriter: JDBC batch inserts
- JpaItemWriter: JPA entity persistence
- CompositeItemWriter: Multiple writers
- StaxEventItemWriter: XML output

## 4. Skip and Retry Logic

Spring Batch handles failures at the chunk level:
- skippable-exception-classes: Exceptions that skip the item
- retryable-exception-classes: Exceptions that trigger retry
- skip-limit: Max skips before job fails
- retry-limit: Max retries per item

## 5. Job Scheduling

Use @EnableScheduling and @Scheduled to trigger jobs:
- Fixed rate
- Cron expressions
- Trigger customizer

## 6. Multi-threaded Processing

- Multi-threaded step: Single process, multiple threads
- Parallel steps: Multiple steps run concurrently
- Partitioning: Master/slave step distribution
- Remote chunking: Distributed processing
