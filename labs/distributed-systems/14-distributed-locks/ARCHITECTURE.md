# Architecture — Distributed Locks

## Lock Service Architecture
Client -> Lock Service (Redis/ZK/Etcd)
    +-- Lock Manager
    |     - Grant locks, maintain leases, generate fencing tokens
    +-- Health Check
    |     - Heartbeat monitoring, lease expiry detection
    +-- Resource Gateway
          - Token validation, access control

## Deployment
- Redis: 3-5 nodes, asynchronous replication
- ZooKeeper: 3-5 nodes, majority writes
- Etcd: 3-5 nodes, Raft consensus
