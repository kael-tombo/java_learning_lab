# Mathematical Foundation: GraphQL DGS

## N+1 Problem
Without DataLoader: N+1 queries = 1 (list) + N (item details)
With DataLoader: 1 (list) + 1 (batched details) = 2 queries
Saving: N-1 queries

## Query Complexity
complexity = sum(data_fetching_cost * number_of_items) for each field
Depth-based limits prevent exponential queries.
