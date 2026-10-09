# 14 - Distributed Locks

## Overview
Distributed locks coordinate access to shared resources across multiple nodes. This lab covers Redis Redlock, ZooKeeper locks, lease-based locking, and fencing tokens for safe distributed mutual exclusion.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems
- Familiarity with concurrency concepts

## Topics Covered
- Redis Redlock algorithm
- ZooKeeper ephemeral sequential znodes
- Lease-based locking with TTL
- Fencing tokens for resource protection
- Lock reentrancy in distributed systems
- Deadlock detection and recovery
- Split-brain scenarios and mitigation
- Comparison of lock providers

## Package Structure
- com.distributed.distributedlocks — Core implementations
  - DistributedLock.java — Lock interface
  - RedisLock.java — Redis-based distributed lock
  - ZooKeeperLock.java — ZooKeeper-based lock
  - FencingToken.java — Fencing token management
  - LeaseManager.java — Lease-based lock management
