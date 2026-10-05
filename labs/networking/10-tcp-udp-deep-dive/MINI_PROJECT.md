# TCP/UDP Deep Dive - MINI PROJECT

## Project: CongestLab — a TCP congestion-control simulator plus a reliable UDP transfer

Build a discrete-event simulator implementing Reno, CUBIC, and BBR congestion control
over a lossy link, then implement a reliable UDP file transfer with your own congestion
control and compare it against TCP on the same simulated network.

### Architecture

```
  SIMULATOR (discrete event, virtual clock)
  ─────────────────────────────────────────
  Sender                          Network (bottleneck)
  ┌──────────────────────┐        ┌────────────────────────────┐
  │ cwnd, ssthresh, rtt  │───────▶│ link: bandwidth + delay     │
  │ rtt estimator (SRTT) │        │ queue: buffer_btl_drop     │
  │ loss detection (dup  │        │ random loss %              │
  │ ACK or timeout)      │◀───────│ delay: propagation + queue  │
  └──────────────────────┘  ACK   └────────────────────────────┘
        │  metrics: throughput, RTT, cwnd, retransmits, fairness
        ▼
  ALGORITHMS: Reno | CUBIC | BBR | ReliableUdp (yours)

  Reliable UDP transfer (real sockets)
  ────────────────────────────────────
  chunked file ──▶ window-limited sender ──▶ UDP socket ──▶ receiver
                  ▲ cwnd from loss/RTT feedback, exponential backoff
                  └── ACK bitmap, selective retransmit
```

### Implementation

The congestion window, implemented once and shared by all algorithms:

```java
class TcpSender {
    private double cwnd;            // congestion window, in bytes (or segments)
    private double ssthresh;
    private double rttEstimator;   // smoothed RTT
    private double rttDeviation;
    private int ssthreshPackets = 1 << 14;   // hmm, per-RTT pacing below ssthresh
    private int dupAcks = 0;

    /** RTT estimation per RFC 6298: SRTT = 7/8*SRTT + 1/8*R, RTTVAR = 3/4*RTTVAR + 1/4*|SRTT-R|. */
    void updateRtt(double measuredRtt) {
        if (Double.isNaN(rttEstimator)) { rttEstimator = measuredRtt; rttDeviation = measuredRtt / 2; }
        else {
            rttDeviation = 0.75 * rttDeviation + 0.25 * Math.abs(rttEstimator - measuredRtt);
            rttEstimator = 0.875 * rttEstimator + 0.125 * measuredRtt;
        }
    }

    /** Duplicate ACK -> fast retransmit: 3 dup ACKs is the standard signal. */
    boolean onDuplicateAck() {
        return ++dupAcks == 3;
    }

    /** Timeout is a much stronger signal than a dup ACK: it means RTO fired. */
    void onTimeout(Algorithm algorithm) {
        ssthresh = Math.max(cwnd / 2, 2);
        cwnd = 1;                     // slow start from 1 MSS
        dupAcks = 0;
        algorithm.onTimeout(ssthresh);
    }
}
```

Reno: slow start then congestion avoidance, with fast recovery:

```java
class Reno extends Algorithm {
    /**
     * Congestion window growth is linear in bytes-per-RTT, not per ACK. The distinction
     * matters: a common bug is growing cwnd per ACK, which makes slow start roughly
     * 2x too aggressive and fast recovery behave incorrectly.
     */
    void onAck(int ackedBytes, int mss) {
        if (cwnd < ssthresh) {
            cwnd += Math.min(ackedBytes, mss);          // slow start: +1 MSS per ACK
        } else {
            // Congestion avoidance: +1 MSS per RTT = cwnd += mss*mms/cwnd per ACK
            cwnd += (mss * (double) mss) / cwnd;
        }
    }

    void onFastRecovery(int mss) {
        cwnd = ssthresh + 3 * mss;   // inflate for the 3 dup ACKs already received
    }

    void exitFastRecovery(int mss) {
        cwnd = ssthresh;             // deflate: the network is congested, be conservative
    }
}
```

CUBIC, which is what modern Linux actually uses — and why the curve looks the way it does:

```java
class Cubic extends Algorithm {
    private static final double C = 0.4, BETA = 0.7, K = 0.7;
    private double lastMaxCwnd;

    /**
     * CUBIC grows as a cubic function of time since the last loss, not linearly in RTT.
     * Motivation: on high-BDP links, a loss-based linear ramp needs one RTT per increment,
     * which takes minutes. CUBIC's whole point is to probe aggressively far from the
     * last loss and gently close in as you approach it, so BDP estimation converges fast.
     */
    void onAck(int ackedBytes, int mss) {
        double t = timeSinceLastLoss();
        double target = C * Math.pow(t - K, 3) * mss + lastMaxCwnd;   // the cubic curve
        double cwndCubic = target;

        // TCP-friendly region: when cwnd < lastMaxCwnd, Reno-style growth is faster than
        // the cubic curve, so we take the max. This is why CUBIC is not purely cubic.
        double cwndReno = cwnd + (mss * (double) mss) / cwnd;
        cwnd = Math.max(cwndCubic, cwndReno);
    }

    /** Beta multiplies, not halves: CUBIC is deliberately gentler than Reno after loss. */
    void onLoss() {
        lastMaxCwnd = cwnd;
        ssthresh = (double) (cwnd * BETA);
        cwnd = ssthresh;
    }
}
```

BBR, which optimises for delivery rate rather than for avoiding loss:

```java
class Bbr extends Algorithm {
    /**
     * The conceptual break: BBR does not treat loss as congestion. It measures bottleneck
     * bandwidth and round-trip propagation time, and paces at bandwidth * RTT. Loss is
     * handled as a separate signal for the recovery phase, not as the congestion signal.
     * This is why BBR can keep full rate on links with random loss that would collapse
     * a loss-based algorithm.
     */
    enum State { STARTUP, DRAIN, PROBE_BW, PROBE_RTT }

    double bottleneckBandwidthBps;   // max delivery rate sampled over a window
    double propagationRttUs;         // minimum RTT observed
    State state = State.STARTUP;

    void onDeliverySample(double deliveredBytes, double intervalSeconds, double rttUs) {
        bottleneckBandwidthBps = maxFilter(bottleneckBandwidthBps, deliveredBytes / intervalSeconds);
        propagationRttUs = Math.min(propagationRttUs, rttUs);
    }

    /** The pacing rate that everything else derives from. */
    double pacingRate() {
        return state == State.PROBE_RTT ? pacingForRtt() : 1.25 * bottleneckBandwidthBps;
    }

    /** 8-phase probe: gain cycles between 0.9x and 1.25x to find the edge without a
     *  loss-based cliff, and utilisation is maintained rather than cwnd-driven. */
    double probeBwGain(int cycle) {
        double[] gains = { 1.25, 0.75, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00 };
        return gains[cycle % gains.length];
    }

    /** PROBE_RTT drains the queue every 10s: if the min RTT has not improved, reduce
     *  inflight to flush standing queues, then return to PROBE_BW. */
    boolean shouldEnterProbeRtt() {
        return rttUs > 1.25 * propagationRttUs && timeInState() > 10_000_000;  // microseconds
    }
}
```

The network model, where the interesting behaviour emerges:

```java
class BottleneckLink {
    private final double capacityBps;
    private final double propagationDelaySeconds;
    private final double bufferBytes;       // bufferbloat lives here
    private double queuedBytes;
    private final double lossProbability;

    void transmit(double bytes, double now) {
        double serviceTime = (bytes * 8) / capacityBps;
        queuedBytes += bytes;
        if (queuedBytes > bufferBytes) {
            // TAIL DROP. This single line is the whole of classic bufferbloat: a large
            // buffer converts loss-based congestion control into a latency-based queue,
            // because the sender keeps sending until the buffer is full, and by then
            // RTT has multiplied.
            queuedBytes = bufferBytes;      // drop
            sender.onPacketLost();
            stats.tailDrops++;
            return;
        }
        stats.queuedBytes.observe(queuedBytes);
        stats.queueingDelay.observe(queuedBytes * 8 / capacityBps);
        deliveryAt = now + propagationDelaySeconds * 2 + (queuedBytes * 8 / capacityBps);
        queuedBytes -= bytes;
        sender.scheduleAck(deliveryAt, serviceTime);
    }

    /** Buffer size that yields a BDP: bandwidth * RTT. Under-provisioning causes loss;
     *  massively over-provisioning causes bufferbloat. This ratio is the tunable. */
    static double recommendedBufferBytes(double capacityBps, double rttSeconds) {
        return capacityBps / 8 * rttSeconds;
    }
}
```

Reliable UDP with your own congestion control, so the simulator has something to compare:

```java
class ReliableUdpSender {
    // cwnd in bytes; ssthresh; RTT estimate; unacked window
    void onAck(AckPacket ack) {
        updateRtt(ack.rttSampleMs());
        if (ack.missing().isEmpty()) {
            if (cwnd < ssthresh) cwnd += ackedBytes();             // slow start
            else cwnd += Math.max(1, (long)(mss * mss / cwnd));    // congestion avoidance
        } else {
            onLoss(ack.missing().size());   // multiplicative decrease
        }
    }

    void onLoss(int lost) {
        ssthresh = Math.max(cwnd / 2, 2 * mss);
        cwnd = mss;                    // back to slow start
        // Selective retransmit: only the missing chunks, not the whole window. TCP-style
        // go-back-to-retransmit wastes a whole RTT per loss, which dominates on lossy paths.
        retransmitQueue.addAll(lost);
    }

    void pump() {
        while (inFlight() + mss <= cwnd && retransmitQueue.isEmpty() && hasMoreData())
            transmit(nextChunk());
    }
}
```

### Test It

```java
@Test void slowStartDoublesCwndPerRtt() {
    var link = newLink(capacity: 10, bufferBdp: 100, loss: 0.0);
    var reno = new Reno(send(link, mss: 1000, rtt: 0.1));
    // After RTT 1: cwnd ~2 MSS. After RTT n: cwnd ~2^n, until ssthresh.
    assertThat(reno.cwndAfterRtts(5)).isBetween(20_000.0, 40_000.0);
}

@Test void cubicConvergesFasterThanRenoOnHighBdp() {
    var link = newLink(capacity: 100, bufferBdp: 100, loss: 0.001);   // 100ms * 100Mbps = high BDP
    var reno = new Reno(send(link, mss: 1460, rtt: 0.1));
    var cubic = new Cubic(send(link, mss: 1460, rtt: 0.1));
    // CUBIC should reach a given throughput fraction notably faster.
    assertThat(cubic.timeToReach(0.9 * bdp(link))).isLessThan(reno.timeToReach(0.9 * bdp(link)) * 0.6);
}

@Test void bbrToleratesRandomLossThatCollapsesReno() {
    var link = newLink(capacity: 100, bufferBdp: 2, loss: 0.02);     // 2% random loss, small buffer
    var reno = new Reno(send(link, mss: 1460, rtt: 0.05));
    var bbr  = new Bbr(send(link, mss: 1460, rtt: 0.05));
    // Reno collapses toward low throughput; BBR keeps most of the link.
    assertThat(bbr.throughput()).isGreaterThan(reno.throughput() * 3);
}

@Test void largeBufferCausesBufferbloat() {
    var small = newLink(capacity: 100, bufferBdp: 4,  loss: 0.0);
    var large = newLink(capacity: 100, bufferBdp: 400, loss: 0.0);
    run(small); run(large);
    // Same throughput, wildly different latency. This is the whole point.
    assertThat(small.p99Rtt()).isLessThan(0.1);
    assertThat(large.p99Rtt()).isGreaterThan(1.0);   // 1+ second of standing queue
    assertThat(small.throughput()).isCloseTo(large.throughput(), within(5.0));
}

@Test void reliableUdpFasterThanTcpOnLossyLink() {
    var link = newLink(capacity: 10, bufferBdp: 10, loss: 0.05);   // 5% loss
    var tcpFile = tcpTransfer(link, mtu: 1460);
    var udpFile = reliableUdpTransfer(link, mtu: 1200);
    // Selective retransmit wins when loss is frequent, because TCP retransmits a whole
    // window's worth of already-received data.
    assertThat(udpFile.elapsed()).isLessThan(tcpFile.elapsed() * 0.7);
    assertThat(udpFile.integrityVerified()).isTrue();
}
```

## Deliverables

- [ ] Discrete-event simulator with a bottleneck link, queue, loss, and propagation delay
- [ ] RFC 6298-compliant RTT estimator (SRTT/RTTVAR) shared by all algorithms
- [ ] Reno with slow start, congestion avoidance, fast retransmit, and fast recovery
- [ ] CUBIC with the cubic window function, the TCP-friendly region, and beta decrease
- [ ] BBR with bandwidth/RTT estimation, the 8-phase probe, and PROBE_RTT
- [ ] Bufferbloat demonstration: equal throughput, orders of magnitude apart in p99 RTT
- [ ] Reliable UDP sender with selective retransmit and its own congestion control
- [ ] Comparison charts of throughput, RTT, and cwnd over time for each algorithm
- [ ] A writeup attributing each performance plateau to a specific mechanism
