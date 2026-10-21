# Architecture — Distributed Scheduling

## Scheduler Architecture
`
Scheduler Cluster
  +-- Leader (executes jobs)
  |     +-- Cron Evaluator
  |     +-- Job Executor
  |     +-- Misfire Handler
  +-- Followers (standby)
        +-- Health Monitor
        +-- Election Watcher

Job Store (database)
  +-- Job definitions
  +-- Trigger definitions
  +-- Execution history
`

## Flow
`
1. All nodes check cron expressions
2. Leader executes when trigger fires
3. Leader updates job status
4. Followers detect leader through heartbeats
5. On leader failure, new leader elected
6. New leader checks for missed jobs
`
"@

W "SECURITY.md" @"
# Security — Distributed Scheduling

## Threats
- Unauthorized job registration/modification
- Malicious job code execution
- Sensitive data in job parameters
- Denial of service (excessive job scheduling)

## Mitigations
- Authentication for job management API
- Job code sandboxing (classloader isolation)
- Encrypted job parameters
- Rate limiting per user/application
- Audit trail for all scheduling operations
- Job execution timeout enforcement
