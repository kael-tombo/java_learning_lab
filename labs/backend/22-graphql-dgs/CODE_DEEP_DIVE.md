# Code Deep Dive: DGS GraphQL

## Schema-first contract

```graphql
type Book { id: ID!, title: String!, author: Author }
type Author { id: ID!, name: String!, books: [Book!]! }
type Query { book(id: ID!): Book, books(limit: Int = 10): [Book!]! }
```

`.graphqls` files under `src/main/resources/schema` are the source of truth;
`dgs-codegen` generates `com.example.codegen.types.*` records and resolver
interfaces at build time.

## Query + data resolvers

```java
@DgsComponent
public class BookDatafetcher {
    @DgsQuery
    public List<Book> books(@InputArgument int limit) {
        return bookRepo.findAll(PageRequest.of(0, limit));
    }

    @DgsData(parentType = "Book", field = "author")
    public CompletableFuture<Author> author(DgsDataFetchingEnvironment dfe) {
        Book b = dfe.getSource();
        return dfe.getDataLoader("authorLoader").load(b.getAuthorId());
    }
}
```

Pitfall: returning `authorRepo.findById(...)` directly inside `@DgsData`
reintroduces N+1. The loader call is the whole point.

## DataLoader registry — kills the N+1

```java
@Configuration
public class LoaderConfig {
    @Bean
    BatchLoaderRegistry batchLoaderRegistry(AuthorRepository repo) {
        BatchLoaderRegistry r = new BatchLoaderRegistry();
        r.registerBatchLoader("authorLoader",
            (List<Long> ids) -> repo.findAllById(ids).stream()
                .collect(java.util.function.Function.identity(),
                         Collectors.toMap(Author::getId, Function.identity()),
                         (a, b) -> a).values().stream()
                .collect(Collectors.toList()),
            AuthorRepository::class.java);
        return r;
    }
}
```

Cleaner with a dedicated constructor:

```java
r.registerBatchLoader("authorLoader", ids -> {
    Map<Long, Author> byId = repo.findAllById(ids).stream()
                                 .collect(toMap(Author::getId, a -> a));
    return ids.stream().map(byId::get).toList();   // ORDER MUST MATCH INPUT
}, Long.class);
```

Pitfall: DataLoader contract requires the result list aligned by index with
the ids. Returning `repo.findAllById(ids)` order directly is wrong when rows
come back unordered — map then align.

## Error union instead of HTTP codes

```java
@DgsData(parentType = "Query", field = "search")
@HystrixCommand(fallbackMethod = "searchDown")
public Object search(String term) {
    if (term.isBlank()) return new InvalidInput("term must not be blank");
    return searchIndex.query(term);   // SearchResult union
}
```

## Depth & cost limiting

```java
@Bean
public MaxQueryDepthInstrumentation depth() { return new MaxQueryDepthInstrumentation(10); }

@Bean
public MaxAliasesInstrumentation aliases() { return new MaxAliasesInstrumentation(5); }
```

Without these, `{a{b{c{d...` at depth 40 multiplies resolver invocations.

## Upload and streaming

```java
@DgsQuery
public String uploadCover(@InputArgument MultipartFile file) throws IOException {
    return storage.put(file.getInputStream(), file.getSize());
}
```

Pitfall: multipart uploads in GraphQL use the `graphql-multipart-request-spec`;
missing `gavax.servlet.multipart` config yields null streams.

## Federation note

```graphql
type Book @key(fields: "id") { id: ID! @external, title: String }
```

`@key` + `@external` let the gateway stitch types owned by other subgraphs;
forgetting `@external` makes the subgraph compose-invalid and the gateway
refuses to start until fixed.
