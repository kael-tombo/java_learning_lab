# Architecture — Gossip Protocols

## Node Architecture
`
GossipNode
  +-- MemberList (known peers, heartbeats)
  +-- MessageStore (recent messages)
  +-- PeerSelector (random, round-robin)
  +-- Scheduler (periodic gossip rounds)
  +-- FailureDetector (phi-accrual)
  +-- NetworkLayer (UDP/TCP)
`

## Deployment
- All nodes equal (no hierarchy)
- Typically uses UDP for efficiency
- Periodic rounds: 100ms-1s depending on scale
- Fan-out: 3-5 typically
