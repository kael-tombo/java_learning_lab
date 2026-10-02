# Distributed Consensus

## Overview
This lab covers consensus algorithms (Raft, Paxos, Zab), leader election, log replication, cluster membership changes, and production considerations for building fault-tolerant distributed systems.

## Learning Objectives
- Implement Raft consensus from scratch
- Understand Paxos variants (Basic, Multi-Paxos, Fast Paxos)
- Design leader election with lease mechanisms
- Handle cluster membership changes safely
- Debug consensus-related production issues

## Prerequisites
- Distributed systems fundamentals
- Network programming (RPC, timeouts)
- FLP impossibility understanding

## Topics Covered
1. Consensus problem definition and FLP
2. Raft: leader election, log replication, safety
3. Paxos: basic, multi-paxos, optimizations
4. Zab (ZooKeeper Atomic Broadcast)
5. Cluster membership changes (joint consensus)
6. Lease mechanisms and read optimization
7. Production: snapshotting, performance, debugging