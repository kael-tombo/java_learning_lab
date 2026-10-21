# Visual Guide — Distributed Locks

## Redis Lock Flow
`
Client -> Redis SET NX key value PX 30000
  Success: Lock acquired (with 30s TTL)
  Failure: Lock held by another client

Client -> Redis DEL key (release)
`

## ZooKeeper Lock Flow
`
1. Create /locks/mylock/seq-0000000042 (ephemeral sequential)
2. Get children: [seq-0000000040, seq-0000000041, seq-0000000042]
3. Ours is 0000000042, not the lowest (0000000040)
4. Watch preceding node (0000000041)
5. When 0000000041 disappears: lock acquired
`

## Fencing Token
`
Acquisition 1 -> Token 1 -> Resource (valid: token >= 1)
Acquisition 2 -> Token 2 -> Resource (valid: token >= 2)
Stale client with Token 1 -> Resource (rejected: 1 < 2)
`
"@ -Encoding UTF8

# Lab 15 missing VISUAL_GUIDE.md
Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\15-gossip-protocols\VISUAL_GUIDE.md" -Value @"
# Visual Guide — Gossip Protocols

## Push Gossip Flow
`
Round 1:   A -> B, C
Round 2:   A -> D, E   B -> F, G   C -> H, I
Round 3:   ... (all nodes eventually reached)
`

## SWIM Protocol Flow
`
Node A pings Node B
  If B responds: alive
  If B doesn't respond:
    A asks C and D to probe B (indirect)
    If any get response: B is alive (network issue)
    If all fail: B marked suspect
    After suspicion timeout: B marked dead (gossiped to all)
`

## Convergence Visualization
`
Time t0: [A] has info X
Time t1: [A,B,C] have X  (A gossips to B, C)
Time t2: [A,B,C,D,E,F,G] have X
Time t3: All nodes have X
`
"@ -Encoding UTF8

# Lab 16 missing VISUAL_GUIDE.md
Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\16-distributed-caching\VISUAL_GUIDE.md" -Value @"
# Visual Guide — Distributed Caching

## Cache-Aside Pattern
`
Client -> Cache: GET key
  Cache hit: return value
  Cache miss:
    Client -> DB: SELECT value
    Client -> Cache: SET key value
    Client: return value
`

## Write-Behind Pattern
`
Client -> Cache: SET key value (immediate)
Cache: acknowledge immediately
Cache -> DB: async write (batched, eventually)

Risk: if cache fails before DB write, data lost
`

## Multi-Tier Cache
`
Application -> L1 Cache (local, Caffeine)
                  |
          L1 miss -> L2 Cache (Redis Cluster)
                       |
               L2 miss -> Database
`
"@ -Encoding UTF8

# Lab 17 missing files
Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\17-distributed-filesystems\VISUAL_GUIDE.md" -Value @"
# Visual Guide — Distributed Filesystems

## HDFS Read Flow
`
Client -> NameNode: getBlockLocations(/file)
NameNode -> Client: [block1: NodeA, NodeB], [block2: NodeB, NodeC]
Client -> DataNode A: read block1
Client -> DataNode B: read block2
`

## Erasure Coding (4+2)
`
Data: D1 D2 D3 D4
Parity: P1 P2

Storage: 6 nodes, each stores 1 fragment
Fault tolerance: any 2 nodes can fail
Read: need any 4 of 6 fragments to reconstruct
`
"@ -Encoding UTF8

Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\17-distributed-filesystems\SECURITY.md" -Value @"
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
