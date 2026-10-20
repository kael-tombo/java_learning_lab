# Architecture: CQRS Axon

`
Command Side (Write)           Query Side (Read)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ CommandBus       â”‚           â”‚ QueryBus         â”‚
â”‚ →“                â”‚           â”‚ →“                â”‚
â”‚ CommandHandler   â”‚           â”‚ QueryHandler     â”‚
â”‚ → Aggregate      â”‚           â”‚ → Repository     â”‚
â”‚   →“ apply()     â”‚           â”‚   →“              â”‚
â”‚ EventBus → ES   â”‚           â”‚ Read Database    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
         â”‚                            â–²
         â”‚ Events via EventBus        â”‚
         â–¼                            â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Projections (Event handlers update read DB)  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\23-cqrs-axon "SECURITY.md") @"
# Security: CQRS Axon

- Authorize command execution (who can issue commands)
- Authorize query execution (who can read data)
- Use Axon's security interceptors
- Encrypt sensitive event data in event store
- Audit event log access
- Validate command inputs
