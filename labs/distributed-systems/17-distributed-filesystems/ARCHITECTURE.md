# Architecture — Distributed Filesystems

## HDFS Architecture
`
Client -> NameNode (metadata)
         +-> DataNode 1 (block A, B)
         +-> DataNode 2 (block B, C)
         +-> DataNode 3 (block A, C)
`

## Ceph Architecture
`
Client -> MON (cluster map) -> CRUSH algorithm
         +-> OSD 1-10 (data storage)
         +-> MDS (POSIX metadata, optional)
`

## MinIO Architecture
`
Client -> S3 API (HTTP/S)
         +-> MinIO Node 1 -> Local disk
         +-> MinIO Node 2 -> Local disk
         +-> MinIO Node 3 -> Local disk
         (Erasure coding across nodes)
`
"@

W "SECURITY.md" @"
# Security — Distributed Filesystems

## Threats
- Unauthorized data access
- Data tampering
- Metadata corruption
- Ransomware attacks

## Mitigations
- Kerberos authentication (HDFS)
- S3 IAM policies and bucket policies
- Server-side encryption (SSE-S3, SSE-KMS)
- Access logs and audit trails
- Immutable object versions (S3 Object Lock)
- Network isolation and firewalls
