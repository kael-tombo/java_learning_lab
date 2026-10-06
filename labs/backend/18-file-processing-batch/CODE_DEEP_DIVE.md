# Code Deep Dive: Spring Batch

## FlatFileItemReader wiring

```java
@Bean
public FlatFileItemReader<OrderCsv> orderReader(Resource input) {
    FlatFileItemReader<OrderCsv> reader = new FlatFileItemReader<>();
    reader.setResource(input);
    reader.setLinesToSkip(1);                      // header row
    reader.setLineTokenizer(new DelimitedLineTokenizer() {{
        setNames("id", "amount", "currency");
    }});
    reader.setFieldSetMapper(new BeanWrapperFieldSetMapper<>() {{
        setTargetType(OrderCsv.class);
    }});
    return reader;
}
```

Pitfall: `BeanWrapperFieldSetMapper` binds by name and will fail on `int`
columns of empty strings. Parse with a custom `LineAggregator`/tokenizer if
columns can be blank, or map nulls explicitly.

## Chunk step with fault tolerance

```java
@Bean
public Step importStep(JobRepository jobs, PlatformTransactionManager tx,
                       ItemReader<OrderCsv> reader,
                       ItemProcessor<OrderCsv, Order> processor,
                       ItemWriter<Order> writer, SkipListener<OrderCsv, Order> listener) {
    return new StepBuilder("importStep", jobs)
        .<OrderCsv, Order>chunk(500, tx)           // 500 rows per TX
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .skip(FlatFileParseException.class)
        .skipLimit(100)                            // give up past 100 bad rows
        .retry(PessimisticLockingFailureException.class)
        .retryLimit(3)
        .listener(listener)
        .build();
}
```

Pitfall: `skipLimit` counts *per step run*. A job restarting after 99 skips
and skipping 2 more in the next run does not trip the limit semantics people
expect; pair with a skip listener that alerts, not just logs.

## Idempotent writer for safe restart

```java
@Bean
public JdbcBatchItemWriter<Order> orderWriter(DataSource ds) {
    JdbcBatchItemWriter<Order> writer = new JdbcBatchItemWriter<>();
    writer.setDataSource(ds);
    // INSERT ... ON CONFLICT (id) DO UPDATE — safe to re-run the chunk
    writer.setSql("""
        INSERT INTO orders (id, amount, currency)
        VALUES (:id, :amount, :currency)
        ON CONFLICT (id) DO UPDATE SET amount = EXCLUDED.amount""");
    writer.setItemSqlParameterSourceProvider(new BeanPropertyItemSqlParameterSourceProvider<>());
    return writer;
}
```

Pitfall: a plain `INSERT` makes every mid-chunk restart fail with
duplicate-key errors, turning a resumable job into a manual SQL cleanup.

## Partitioned parallel step

```java
@Bean
public Step partitionStep(Step importStep, JobRepository jobs) {
    SimpleAsyncTaskExecutor exec = new SimpleAsyncTaskExecutor("part-");
    return new StepBuilder("partitionStep", jobs)
        .partitioner("importStep", new MultiResourcePartitioner(new Resource[]{file1, file2}))
        .step(importStep)
        .gridSize(4)
        .taskExecutor(exec)
        .build();
}
```

Pitfall: each partition gets its own reader instance via `StepBuilder`
re-creation in a `@StepScope` bean; a singleton-scoped reader shared across
partitions corrupts cursors and silently drops rows. `@StepScope` beans are
proxied — inject `ItemReader` normally and Spring resolves it per partition.

## Skip listener that keeps evidence

```java
public class ErrorFileSkipListener implements SkipListener<OrderCsv, Order> {
    private final BufferedWriter err; // rows + cause + line number
    @Override public void onSkipInRead(Throwable t) throws Exception {
        err.write("READ-ERROR," + t.getMessage() + "\n");
    }
    @Override public void onSkipInProcess(OrderCsv item, Throwable t) throws Exception {
        err.write("PROCESS-ERROR," + item.id() + "," + t.getMessage() + "\n");
    }
    @Override public void onSkipInWrite(Order item, Throwable t) throws Exception {
        err.write("WRITE-ERROR," + item.id() + "," + t.getMessage() + "\n");
    }
}
```

Pitfall: with no skip listener, bad rows vanish; with one, the file handle
must be closed in a `JobExecutionListener.afterJob` or process shutdown loses
the buffer.
