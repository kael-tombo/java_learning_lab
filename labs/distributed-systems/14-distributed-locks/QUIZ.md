# Quiz — Distributed Locks

1. Redlock requires majority of how many nodes? Answer: 5
2. ZK locks use which znode type? Answer: Ephemeral sequential
3. Fencing tokens prevent what? Answer: Stale lock holder access
4. Split-brain means? Answer: Two processes think they hold lock
5. Lease solves what problem? Answer: Crash recovery (auto-release)
6. Redlock is safe under async networks? False
7. ZK locks are fair? True (FIFO)
8. Leases require clock sync? True
9. Fencing tokens must be monotonic? True
10. GC pauses affect distributed locks? True
