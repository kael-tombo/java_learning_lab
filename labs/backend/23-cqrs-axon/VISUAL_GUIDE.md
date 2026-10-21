# Visual Guide: CQRS Axon

`
Time â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶
Event Store: [OrdCre][OrdPaid][OrdShip][OrdDel]
                 â”‚        â”‚        â”‚        â”‚
Aggregate: Reading event stream to rebuild state
                 â”‚        â”‚
                 â–¼        â–¼
Projections: Listening to events, updating read DB
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\23-cqrs-axon "DEBUGGING.md") @"
# Debugging: CQRS Axon

1. Check event store table for persisted events
2. Verify command handler registration
3. Monitor event bus publication
4. Check aggregate replay from event store
5. Enable Axon DEBUG logging
6. Verify saga association values
7. Test event versioning
