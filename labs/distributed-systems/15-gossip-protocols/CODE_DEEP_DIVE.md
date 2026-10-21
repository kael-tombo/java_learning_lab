# Code Deep Dive — Gossip Protocols

## 1. GossipProtocol Interface

`java
public interface GossipProtocol {
    void start();
    void stop();
    void broadcast(byte[] data);
    void onMessage(NodeId from, byte[] data);
}
`

## 2. GossipNode Implementation

Each node maintains:
- Member list (known peers with heartbeats)
- Message store (recent messages)
- Random peer selection
- Periodic gossip rounds (scheduled executor)

## 3. SWIM Protocol

### Suspicion Mechanism
- When a node doesn't respond to ping, mark as suspect
- Propagate suspicion via gossip
- After suspicion timeout, mark as dead
- If suspected node responds, mark as alive

### Indirect Probing
- Ask k random nodes to probe the suspect
- If any get a response, mark alive
- Reduces false positives from network issues

## 4. Failure Detector

- Based on phi-accrual failure detection
- Compute suspicion level (phi) from historical heartbeat data
- Adaptive thresholds based on network conditions
- Lower false positives in variable networks
