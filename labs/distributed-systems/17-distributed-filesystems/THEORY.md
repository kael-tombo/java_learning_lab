# Theory of Distributed Filesystems

## 1. Why Distributed Filesystems?

Single-node filesystems have capacity, throughput, and availability limits. Distributed filesystems aggregate storage across nodes, providing:
- Capacity scaling (add nodes for more storage)
- Throughput scaling (parallel access)
- Fault tolerance (data survives node failures)
- Location transparency (access from any node)

## 2. HDFS Architecture

### NameNode
- Single master, manages metadata
- Stores file-to-block mapping
- Tracks block locations
- Single point of failure (mitigated by HA)

### DataNode
- Stores blocks (typically 128MB)
- Reports block locations to NameNode
- Handles reads and writes from clients
- Replicates blocks to other DataNodes

## 3. Ceph Architecture

### Monitors (MON)
- Maintain cluster state (quorum)
- Provide consensus via Paxos
- Typically 3-5 nodes

### OSDs (Object Storage Daemon)
- Store data on local filesystem
- Handle replication and recovery
- Self-manage with CRUSH algorithm

### MDS (Metadata Server)
- POSIX metadata management
- Dynamic subtree partitioning
- Multiple MDS for scalability

## 4. MinIO / S3 Object Storage

- Bucket + key addressing model
- No directory hierarchy (flat namespace)
- RESTful API via HTTP/S
- Eventually consistent (S3) or strongly consistent (MinIO)
- Erasure coding for durability

## 5. Erasure Coding vs Replication

### Replication (3x)
- Storage overhead: 300%
- Durability: high (3 copies)
- Read performance: high
- Simple implementation

### Erasure Coding (e.g., 10+4)
- Storage overhead: 140%
- Durability: very high (tolerates 4 failures)
- Read performance: moderate (rebuild from fragments)
- Compute overhead: encoding/decoding cost

## 6. Data Locality

HDFS and Ceph attempt to schedule computation near data:
- Reduces network bandwidth usage
- Improves processing throughput
- Crucial for large-scale data processing (MapReduce, Spark)
