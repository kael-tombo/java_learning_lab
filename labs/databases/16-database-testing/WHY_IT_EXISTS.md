# Why It Exists: Database Testing

## The Fundamental Problem
Databases have physical limits. No matter how powerful a single machine is, there are hard boundaries.

**Storage Limits:**
- Largest enterprise SSDs: 30TB
- Maximum practical single-node database: ~10-50TB

**Compute Limits:**
- Maximum vCPUs per machine: ~128-256
- Practical throughput: ~10,000-100,000 ops/sec

**Network Limits:**
- Single NIC bandwidth: 25-100 Gbps
- TCP connection limit per process: ~65,535

**Geographic Limits:**
- Speed of light: ~200ms around the world
- Data cannot be in two places at once

## Why These Limits Exist

### Physics
- Data must be stored on physical media
- Data must travel through physical cables
- Processing requires physical CPU cycles

### Economics
- Super-servers cost exponentially more than commodity hardware
- Maintenance costs increase with system complexity

### Engineering
- Single-machine reliability has upper bounds
- MTBF decreases with system complexity

## What Distributed Databases Do About It

| Limit | Solution |
|-------|----------|
| Storage | Each node has own storage, total = sum of all nodes |
| Compute | Queries distributed across nodes, parallel execution |
| Network | Each node has its own network interface |
| Geography | Nodes can be placed in different regions |

## Why Not Just Use a Bigger Database?
Larger databases exist (AWS Aurora supports 128TB), but:
1. They're expensive: ~/TB/year
2. They have limits too: Even the largest instance has maximums
3. Write bottlenecks: Single-node write path remains
4. Geographic limits: Can't distribute a single instance

## The Real Reason
Distributed databases exist because data growth is exponential and hardware capacity grows linearly. The gap between data velocity and hardware capability is widening, not narrowing.

In 2000, a 1TB database was large. In 2026, many applications generate 1TB daily. Without distributed architectures, every growing application eventually hits a wall.

This is not an optimization—it's a fundamental requirement for building systems that can grow without bound. It represents the practical application of the divide-and-conquer principle to data management.

## Why It's Not Going Away
- **Data continues to grow**: IoT, AI, video, real-time analytics
- **Hardware improvements are slowing**: Moore's Law is ending
- **Global distribution is increasingly important**: Users expect low latency everywhere
- **Regulatory requirements**: Data sovereignty requires geographic placement

Distributed database skills will remain critical for the foreseeable future.
