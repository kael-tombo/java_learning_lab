# Math Foundations — Distributed Scheduling

## 1. Cron Expression Grammar

`
* * * * * command
| | | | |
| | | | +-- Day of week (0-7, 0/7=Sun)
| | | +---- Month (1-12)
| | +------ Day of month (1-31)
| +-------- Hour (0-23)
+---------- Minute (0-59)
`

## 2. Next Fire Time Calculation

Algorithm: increment through each field from left to right
- Find next matching value for each field
- If overflow, carry to next higher field
- O(1) for pre-computed schedules, O(N) for complex expressions

## 3. Leader Election (Raft/ZK)

Election time = 2 * round_trip + heartbeat_timeout

With RTT=1ms, timeout=150ms: election ≈ 152ms

## 4. Partition Distribution

For N nodes and J jobs (with consistent hash):
Jobs per node = ceil(J / N) on average
Rebalancing on node change: J * (1 - (N-1)/N) jobs move

## 5. Duplicate Prevention

Probability of duplicate execution:
P(dup) = P(leader crash) * P(new leader runs same job)

Mitigation: fencing tokens, job status persistence
