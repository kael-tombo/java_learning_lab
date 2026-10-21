# Distributed Filesystems - Interview Preparation

> Key interview questions about distributed file systems.

---

## Core Interview Questions

### Q1: Explain GFS architecture
**Answer**: Single master (metadata), chunk servers (data), clients. 64MB chunks replicated 3x. Master stores namespace, chunk locations, access control. Lease-based mutation order (primary replica). Data pipelined along chunk servers. Shadow masters for read scalability. Append-heavy workload optimization.

### Q2: How does HDFS differ from GFS?
**Answer**: HDFS: open-source GFS implementation. Single NameNode (master), DataNodes (chunk servers). 128MB default block size. Replication factor 3 (default). Rack-aware placement. Secondary NameNode for checkpointing. No append optimization. Mostly Java-based.

### Q3: What is Colossus (GFS v2)?
**Answer**: GFS successor. Removed single master bottleneck (distributed metadata). Chunk storage on commodity hardware. Better performance for small files. Supports multi-tenant workloads. Lower latency. Uses Reed-Solomon erasure coding instead of 3x replication.

### Q4: How does consistent hashing work in distributed filesystems?
**Answer**: File path hash determines placement across storage nodes. CRUSH (Ceph): pseudo-random, deterministic placement based on cluster map. No central metadata needed. Supports weighted distribution. Adapts to cluster changes with minimal data movement.

### Q5: What is the difference between POSIX and non-POSIX filesystems?
**Answer**: POSIX: full filesystem semantics (metadata operations, locks, permissions). Hard to scale globally (Lustre, Ceph FS). Non-POSIX: simpler semantics, better scale (GFS, S3). Tradeoff: application compatibility vs scalability.

## Company-Specific Focus

| Company | Filesystem Focus |
|---------|-----------------|
| Google | "GFS -> Colossus evolution" |
| Amazon | "S3 object storage architecture" |
| Apache | "HDFS: NameNode HA, federation" |
| Ceph | "CRUSH algorithm for distributed placement" |

## LeetCode Connections

| Problem | # | Filesystem Concept |
|---------|---|-------------------|
| Design In-Memory File System | 588 | Hierarchical filesystem |
| Serialize and Deserialize N-ary Tree | 428 | Metadata serialization |
| Find Duplicate File in System | 609 | Content addressing |
| Encode and Decode TinyURL | 535 | Path mapping |

## System Design Connections

- **Design a Distributed File System**: Use GFS-like architecture
- **Design a Cloud Storage Service**: S3-like with bucket/object model
- **Design a Data Lake**: Object storage with catalog layer
- **Design a Backup System**: Chunk-based storage with replication

> **Key Insight**: Most interviewers ask about GFS. Focus on: 64MB chunks, master-slave architecture, append-heavy optimization, and single master as bottleneck.