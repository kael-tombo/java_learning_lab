# Common Mistakes: GraphQL DGS

1. Not using DataLoader for related entities (N+1 problem)
2. Exposing schema introspection in production
3. No query depth limiting (DoS risk)
4. Circular dependencies in type definitions
5. Missing error handling in resolvers
6. Not batching database calls in DataLoaders
7. Large responses without pagination
