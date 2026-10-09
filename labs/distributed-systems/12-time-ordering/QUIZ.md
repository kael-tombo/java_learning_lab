# Quiz — Time Ordering

## Section 1: Multiple Choice

**1. What does a Lamport clock guarantee?**
a) C(a) < C(b) iff a -> b
b) If a -> b, then C(a) < C(b)
c) Total order by physical time
d) None

**Answer: b**

**2. Vector clock storage per process?**
a) O(1)
b) O(log n)
c) O(n)
d) O(n²)

**Answer: c**

**3. What is NOT an HLC property?**
a) Monotonically increasing
b) Causality preserving
c) Exact physical time
d) Bounded error

**Answer: c**

**4. Causal broadcast ensures:**
a) Any delivery order
b) Causally related messages delivered in order
c) Only total order
d) FIFO order

**Answer: b**

**5. Happens-before is:**
a) Total order
b) Partial order
c) Equivalence relation
d) Weak ordering

**Answer: b**

## Section 2: True or False

**6.** C(a) < C(b) for Lamport clocks means a -> b. **False**

**7.** Vector clocks can detect concurrent events. **True**

**8.** HLC values can decrease with clock rollback. **False**

**9.** Causal broadcast needs vector clocks. **True**

**10.** Version vectors and vector clocks are identical. **False**

## Section 3: Short Answer

**11.** Why isn't physical clock sync sufficient?

**Answer:** Clock drift, NTP skew (1-50ms), network latency, and leap seconds make physical time unreliable for distributed ordering. Logical clocks solve this by capturing causality.

**12.** Scenario where Lamport clocks mislead?

**Answer:** Two independent processes A and B never communicate. A's events might have timestamps that appear ordered relative to B's events, even though they are concurrent. Lamport clocks can't distinguish this.

**13.** Vector clock size with dynamic membership?

**Answer:** Fixed arrays don't work. Use HashMap-based sparse vectors, dotted version vectors, or Interval Tree Clocks.

## Section 4: Code Analysis

**14.** Bug in this Lamport clock?
`java
public class LamportClock {
    private int counter;
    public synchronized int tick() { return counter; }
    public synchronized int send() { return counter; }
    public synchronized void receive(int ts) {
        counter = Math.max(counter, ts);
    }
}
`
**Answer:** tick() and send() don't increment. receive() needs +1 after max.

## Section 5: Design

**15.** Design clock sync for a global database (US, EU, Asia) with 100-300ms latency and 1ms granularity.

**Answer:** Use HLC with NTP. HLC provides causality at 1ms granularity. For cross-region transactions, use TrueTime-style uncertainty intervals. Use vector clocks for reconciliation after partitions.
