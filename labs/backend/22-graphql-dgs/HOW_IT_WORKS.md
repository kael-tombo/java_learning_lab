# How It Works: GraphQL DGS

When a GraphQL query arrives, DGS parses it, validates against the schema, and executes it by calling resolvers for each requested field. DataLoaders batch related database calls together. The result is JSON matching the query structure. Subscriptions use WebSocket connections to push real-time events.
