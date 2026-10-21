# 17 - Distributed Filesystems

## Overview
Distributed filesystems provide scalable, fault-tolerant storage across multiple nodes. This lab covers HDFS, Ceph, MinIO, erasure coding, replication strategies, and POSIX vs object storage semantics.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems
- Storage and filesystem basics

## Topics Covered
- HDFS architecture (NameNode, DataNode)
- Ceph architecture (MON, OSD, MDS)
- MinIO object storage
- Erasure coding vs replication
- POSIX vs object storage semantics
- Data locality and rack awareness
- Metadata management strategies
- Storage tiering and lifecycle

## Package Structure
- com.distributed.filesystems — Core implementations
  - DistributedFileSystem.java — DFS interface
  - HdfsClient.java — HDFS client wrapper
  - MinioClient.java — MinIO/S3 client
  - ErasureCodec.java — Erasure coding implementation
  - FileReplicator.java — Replication manager
  - MetadataStore.java — Metadata management
