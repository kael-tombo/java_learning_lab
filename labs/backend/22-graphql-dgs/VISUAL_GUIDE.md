# Visual Guide: GraphQL DGS

`
REST: /api/shows → returns ALL fields (overfetch)
      /api/shows/1/reviews → separate call (underfetch)

GraphQL:
query {
  shows { title, reviews { rating } }
}
→ One request, exactly the data needed
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\22-graphql-dgs "DEBUGGING.md") @"
# Debugging: GraphQL DGS

1. Use GraphQL playground (DGS provides /graphiql)
2. Enable DGS query logging
3. Check resolver execution order
4. Verify DataLoader batch sizes
5. Monitor query complexity scores
6. Check federation entity resolution
