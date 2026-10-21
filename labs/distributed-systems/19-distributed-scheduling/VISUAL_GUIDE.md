# Visual Guide — Distributed Scheduling

## Leader Election Flow
`
Node A, B, C all attempt to create /scheduler/leader (ephemeral)
  Node A succeeds: Leader
  Node B, C fail: Followers (watch /scheduler/leader)
  Node A crashes: /scheduler/leader disappears
    Node B watcher fires -> tries to create -> becomes Leader
`

## Cron Execution Timeline
`
12:00:00 - Job scheduled (@hourly)
12:00:01 - Leader evaluates cron expression
12:00:02 - Leader fires job execution
12:00:03 - Job completes, status updated in DB
`
"@ -Encoding UTF8

Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\19-distributed-scheduling\SECURITY.md" -Value @"
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
