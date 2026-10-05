# Gossip Protocols - Mini Project

## Project: Push/Pull Gossip and SWIM Failure Detection

### Objective
Implement a gossip layer over a simulated network, measure convergence rounds, then add
SWIM's indirect probes and show the false-positive rate drop.

### Requirements
1. `GossipNode` — per-key version vectors, push and pull rounds on a timer
2. `GossipProtocol` — random neighbour selection from a membership set
3. `SwimProtocol` — direct + indirect probes, suspicion, and refutation
4. `NetworkSimulator` — configurable latency, drops, and partitions
5. `ConvergenceMetrics` — rounds to convergence, messages per node, detection accuracy

### Steps

**Step 1: Versioned state, not just values**
```java
final class GossipNode {
    private final Map<String, VersionedValue> state = new HashMap<>();

    /** push: share what I know that they probably do not */
    PushPayload pushFor(GossipNode peer) {
        return new PushPayload(state.entrySet().stream()
            .filter(e -> !peer.knowsAtLeast(e.getKey(), e.getValue().version()))
            .toList());
    }

    /** pull: take everything they have that is newer than mine */
    void merge(PushPayload from) {
        from.entries().forEach(e ->
            state.merge(e.key(), e.value(), (mine, theirs) ->
                theirs.version().compareTo(mine.version()) > 0 ? theirs : mine));
    }
}
```
Versioned merge is what makes gossip idempotent and commutative, so out-of-order and duplicate
delivery cannot corrupt state.

**Step 2: The round loop**
```java
void runRound() {
    var peer = membership.randomExcept(self());      // uniform, not round-robin
    peer.receive(self().pushFor(peer));              // push
    self().merge(peer.pullFor(self()));              // pull
}
```
Run one round every `T`. Expected convergence is roughly `O(log3 N)` rounds for the classic
push/pull pair. Measure it:
```java
long roundsToConverge(int nodeCount) {
    var network = new NetworkSimulator(nodeCount);
    network.spreadOneFactAt("node-42", "value-X");
    var start = network.roundCount();
    network.runUntilEveryNodeSees("value-X");
    return network.roundCount() - start;
}
```
Plot rounds against N for 8, 32, 128, 512, 2048. If the curve is linear, your neighbour
selection or RNG is wrong.

**Step 3: Measure the bandwidth**
```java
record BandwidthCost(int nodeCount, long messagesPerNodePerRound, int payloadBytes) {}
```
At 1000 nodes with 3 peers per round, the cluster produces roughly 3000 messages per round.
That is the real cost of gossip and the reason frequency is tuned, not fixed.

**Step 4: Plain gossip's failure problem**
Node A fails. Other nodes *suspect* A only when they have not heard from it directly *or
through the peer they gossiped with*. Because each node gossips with a few random peers,
suspicion spreads unevenly and some nodes take many rounds to conclude A is gone. Worse, a
single slow node can trigger suspicion across the cluster with no refutation path.

**Step 5: SWIM — indirect probes and suspicion**
```java
// step 1: direct probe
if (ping(target, shortTimeout)) return HEALTHY;

// step 2: indirect probe -- ask k peers to ping target for us
for (var helper : membership.kRandomExcept(self(), target, kHelpers)) {
    if (pingVia(helper, target, indirectTimeout)) return HEALTHY;
}

// step 3: suspect, not condemn -- give target a chance to refute
if (refuteMessages.consume(target)) return HEALTHY;
suspicion.target = target;
incarnation.set(target, incarnation.get(target) + 1);
broadcast(new Suspicion(self(), target, incarnation.get(target)));
```

The refutation step is the innovation. A node that is merely slow, not dead, receives the
suspicion about itself and broadcasts a refutation with a *higher* incarnation number, which
everyone accepts. Without it, network asymmetry produces cascading false positives.

```java
void onSuspicion(Suspicion s) {
    if (s.target().equals(id)) {                 // I was suspected -- refute
        gossip(new Refutation(id, incarnation.incrementAndGet()));
        return;
    }
    if (incarnation.get(s.target()) >= s.incarnation()) {
        suspect(s.target(), s.incarnation());    // already dead, or newer information
    }
}
```
Incarnation numbers are essential: a stale refutation or stale suspicion must never override
newer information.

**Step 6: Measure the difference**
Run the same fault (one node killed, plus one node merely slow for 2 seconds) against both
detectors. Record false positives for the slow node — SWIM should show far fewer.

### Deliverables
1. `GossipNode`, `GossipProtocol`, `NetworkSimulator`, `ConvergenceMetrics`
2. Rounds-to-converge table for 8 to 2048 nodes, plus messages-per-node cost
3. `SwimProtocol` with indirect probes, suspicion, refutation, and incarnation counters
4. A false-positive comparison: plain gossip vs SWIM against a slow (not dead) node

### Extension (CHALLENGE)
Implement SWIM's disseminator so suspicions propagate in O(1) hops instead of O(log N), then
measure the reduction in detection time at 1000 nodes.

### Estimated Time
4-5 hours