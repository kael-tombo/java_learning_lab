# Internals: GraphQL DGS

## GraphQL-Java Execution
1. Parse query to Document
2. Validate against schema
3. Build ExecutionStrategy
4. Execute fields in parallel where possible
5. Handle DataLoaders via DataLoaderRegistry
6. Collect and return result

## DGS Auto-Configuration
DGS starter auto-configures:
- DgsWebMvcController (HTTP endpoint)
- GraphQL schema parser
- DataFetcher registration
- DataLoaderRegistryFactory
- Exception handling
- Metrics (Micrometer)
