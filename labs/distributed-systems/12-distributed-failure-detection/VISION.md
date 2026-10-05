# Distributed Failure Detection - Vision

## The Big Picture
In a distributed system, failure is a spectrum, not a boolean. A node can be slow, hung,
partitioned, or dead — and your detector must decide which, fast, without crying wolf. The
unavoidable trade is detection latency versus false-positive rate.

## Why This Matters
Every orchestrator, service mesh, and client library on the planet runs a failure detector.
Get the threshold wrong in one direction and you failover during a brief GC pause; get it
wrong in the other and you wait thirty seconds for a dead node to be noticed.

## The Vision for This Lab
This lab compares three detectors — fixed timeouts, EWMA, and phi-accrual — on the same
fault injection, and turns the "false positive vs detection latency" curve into a tool you
can reason about instead of guess.

## Learning Philosophy
1. Suspension and failure look identical from the outside — design for the ambiguity
2. Fixed thresholds are always wrong for variable-latency systems
3. Probabilistic detectors are tunable by *consequence*, not by feel
4. Detector and policy are separate concerns — detect, then decide

## Future Path
- 15-gossip-protocols — the substrate that carries heartbeats
- 03-distributed-consensus — timeouts drive leader election
- 20-distributed-monitoring — detection is an alerting concern

## Success Metrics
You have mastered failure detection when you can:
- [ ] Implement timeout, EWMA, and phi-accrual detectors
- [ ] Inject GC pauses, network latency, and hard kills and measure each detector's response
- [ ] Compute the ROC curve and choose a threshold from a cost model
- [ ] Explain why phi-accrual is used by Cassandra and HashiCorp

## The Distributed Mindset
> You can never distinguish "dead" from "very slow" without a timeout, and every timeout is
a bet. Make the bet explicit: state the consequence of a false positive and of a false
negative, then pick the threshold that minimises the larger one.