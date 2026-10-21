# Step by Step: Spring Batch

## Step 1: Configure Batch Database
`yaml
spring:
  batch:
    jdbc:
      initialize-schema: always
  datasource:
    url: jdbc:h2:mem:batchdb
    driver-class-name: org.h2.Driver
`

## Step 2: Create Domain Object
`java
public class Product {
    private String id;
    private String name;
    private double price;
    private String category;
    // getters/setters
}
`

## Step 3: Create Reader
`java
@Bean
public FlatFileItemReader<Product> reader() {
    return new FlatFileItemReaderBuilder<Product>()
        .name("productReader")
        .resource(new ClassPathResource("input/products.csv"))
        .delimited()
        .names("id", "name", "price", "category")
        .targetType(Product.class)
        .build();
}
`

## Step 4: Create Processor
`java
@Bean
public ItemProcessor<Product, Product> processor() {
    return product -> {
        product.setName(product.getName().toUpperCase());
        return product;
    };
}
`

## Step 5: Create Writer
`java
@Bean
public JdbcBatchItemWriter<Product> writer(DataSource ds) {
    return new JdbcBatchItemWriterBuilder<Product>()
        .sql("INSERT INTO products VALUES (:id, :name, :price, :category)")
        .dataSource(ds)
        .beanMapped()
        .build();
}
`

## Step 6: Create Job
`java
@Bean
public Job importProductJob(JobRepository repo, Step step) {
    return new JobBuilder("importProductJob", repo)
        .start(step)
        .build();
}

@Bean
public Step step1(JobRepository repo, PlatformTransactionManager tm) {
    return new StepBuilder("step1", repo)
        .<Product, Product>chunk(10, tm)
        .reader(reader())
        .processor(processor())
        .writer(writer())
        .build();
}
`
"@

# Remaining doc files for lab 18
Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\18-file-processing-batch "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: Spring Batch

## ChunkProvider and ChunkProcessor

The chunk-oriented processing in Spring Batch is implemented by:
1. **ChunkProvider**: Reads items and buffers them into a Chunk
2. **ChunkProcessor**: Processes and writes the Chunk

### RepeatTemplate
Both use RepeatTemplate for loop control:
- ChunkProvider repeats read() until chunk size or exhausted
- ChunkProcessor repeats process() and write()

### FaultTolerance
When skip is configured:
- ChunkProvider catches exceptions during read
- Failed items are added to skip list
- Processing continues with next item
- ChunkProcessor skips process/write for failed items
