# 15 - Gossip Protocols

## Overview
Gossip protocols enable information dissemination in large-scale distributed systems through epidemic-style communication. This lab covers gossip dissemination, SWIM protocol, infection-style algorithms, and convergence properties.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems
- Network programming basics

## Topics Covered
- Gossip dissemination algorithms
- SWIM (Scalable Weakly-consistent Infection-style) protocol
- Infection-style epidemic propagation
- Failure detection with gossip
- Convergence and fan-out analysis
- Membership protocols
- Gossip-based data aggregation

## Package Structure
- com.distributed.gossip — Core implementations
  - GossipNode.java — Base gossip node
  - GossipProtocol.java — Protocol interface
  - SwimProtocol.java — SWIM implementation
  - GossipDisseminator.java — Information spreading
  - FailureDetector.java — Gossip-based detection
