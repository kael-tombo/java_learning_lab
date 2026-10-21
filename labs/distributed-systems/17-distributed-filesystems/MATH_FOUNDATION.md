# Math Foundations — Distributed Filesystems

## 1. Replication Durability

For 3x replication with node failure probability p:
P(data loss) = (1 - (1-p)^3)^N where N is number of blocks

## 2. Erasure Coding (Reed-Solomon)

For k data + m parity fragments:
- Storage: (k+m)/k = 1 + m/k
- Fault tolerance: m failures
- Reconstruction: need any k of (k+m) fragments

## 3. Availability Calculation

System availability = 1 - P(all replicas/fragments lost)
With replication factor r: P(loss) = p^r per block

## 4. CRUSH Algorithm

Pseudorandom placement using cluster map:
PG = hash(object_name) mod N
OSDs = CRUSH(PG, cluster_map, replication_factor)

## 5. HDFS Block Size

Block size trade-off:
- Large blocks: fewer blocks, less metadata, easier sequential access
- Small blocks: better parallelism, more metadata overhead
- HDFS default: 128MB (balance of the above)
