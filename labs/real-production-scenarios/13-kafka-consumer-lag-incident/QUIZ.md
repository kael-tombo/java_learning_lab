# Lab 13 — Quiz: Kafka Consumer Lag (15 Questions)

1. Lag definition?
- [ ] A) log-end-offset minus committed offset
- [ ] B) Broker disk usage
- [ ] C) Request latency
- [ ] D) Partition count
> Answer: A

2. First triage command?
- [ ] A) kafka-consumer-groups.sh --describe
- [ ] B) rm -rf /tmp/kafka-logs
- [ ] C) Restart ZooKeeper
- [ ] D) Delete the topic
> Answer: A

3. One hot partition lagging suggests?
- [ ] A) Hot key / poison pill on that partition
- [ ] B) All consumers too slow
- [ ] C) Broker disk full
- [ ] D) DNS failure
> Answer: A

4. All partitions lagging suggests?
- [ ] A) Slow consumer code or broker issue
- [ ] B) Single bad message
- [ ] C) Wrong group id typo only
- [ ] D) Too many partitions
> Answer: A

5. Adding consumers beyond partition count?
- [ ] A) No gain — idle consumers (max = partitions)
- [ ] B) Linear speedup forever
- [ ] C) Fixes broker disk
- [ ] D) Resets offsets
> Answer: A

6. `max.poll.interval.ms` guards?
- [ ] A) Max time between polls before group kicks member (rebalance)
- [ ] B) Fetch size
- [ ] C) Retention period
- [ ] D) Replication factor
> Answer: A

7. Rebalance storm commonly from?
- [ ] A) Long GC / blocking poll exceeding timeouts
- [ ] B) Too much disk
- [ ] C) Too many topics
- [ ] D) Fast consumers
> Answer: A

8. Poison-pill fix?
- [ ] A) Bounded retries + DLQ + alert
- [ ] B) Infinite retry same message
- [ ] C) Delete group
- [ ] D) Increase retention only
> Answer: A

9. Best scale signal?
- [ ] A) Consumer lag, not CPU
- [ ] B) Node CPU only
- [ ] C) Random cron
- [ ] D) Manual guess
> Answer: A

10. Safe replay needs?
- [ ] A) Idempotent consumer
- [ ] B) No commits
- [ ] C) Sync producer only
- [ ] D) Single partition
> Answer: A

11. End-to-end latency measures?
- [ ] A) Produce timestamp → consume time
- [ ] B) Broker uptime
- [ ] C) ZooKeeper latency
- [ ] D) DNS lookup
> Answer: A

12. Under-replicated partitions indicate?
- [ ] A) Broker/ISR problem slowing fetch
- [ ] B) Healthy cluster
- [ ] C) Consumer bug
- [ ] D) Normal rebalance only
> Answer: A

13. `session.timeout.ms` vs heartbeat?
- [ ] A) Heartbeat (3s) must be << session timeout (10s) to avoid false failure
- [ ] B) Unrelated
- [ ] C) Heartbeat larger is better
- [ ] D) Disable both
> Answer: A

14. DLQ growth alerting matters because?
- [ ] A) Signals data loss risk + poison rate
- [ ] B) Wastes disk only
- [ ] C) Slows producers
- [ ] D) Irrelevant
> Answer: A

15. Long-term fix for hot key?
- [ ] A) Repartition / better key design + more partitions
- [ ] B) Bigger consumer heap only
- [ ] C) Delete topic daily
- [ ] D) Single consumer
> Answer: A

Scoring: 13–15 excellent, 10–12 good, <10 review THEORY + CODE_DEEP_DIVE.
