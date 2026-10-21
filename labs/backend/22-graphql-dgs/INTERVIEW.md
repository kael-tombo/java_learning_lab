# Interview: GraphQL DGS

Q: What is the N+1 problem in GraphQL? A: When querying a list and each item triggers a separate query for related data.

Q: How does DGS solve N+1? A: DataLoaders batch and deduplicate related queries.

Q: DGS vs REST? A: GraphQL gives clients control over response shape. REST is simpler for simple CRUD. GraphQL better for complex data requirements.
