# Reflection: Lock Framework

## Check your model

1. Without looking: what does `state` mean for a lock, a semaphore, and a
   latch? What single sentence covers all three?
2. Sketch the queue after: A holds, B and C queue, B is interrupted. Which
   node is head, which is `CANCELLED`, where does D enqueue?
3. A teammate says "fair mode is strictly FIFO." What is the precise
   correction, and where is the residual barging window?
4. Why does `signal()` followed by immediate `unlock()` still require the
   woken thread to race? Who can beat it to the lock?
5. Your `Semaphore(5)` reports 8 permits at quiescence. Write the two most
   likely code shapes that caused it.

## Connect to your code

1. Find one `synchronized` block in your codebase. Which AQS capability —
   timeout, interruption, fairness, conditions, shared mode — would justify
   converting it? If none, leave it.
2. Find one `notifyAll()`. Could two conditions split its waiters? Name them.
3. Where would a `tryLock(deadline)` turn a production hang into a logged,
   retryable branch?

## Predict, then verify

1. Predict the throughput ranking: uncontended lock, contended nonfair with
   200ns body, contended fair with 200ns body, same with 10µs body. Then run
   the JMH sketch in PERFORMANCE.md and compare.
2. Predict `state` for readers=3/writer=1 in hex, then assert it with a
   debugger or a packing snippet.
3. Predict whether `writeLock().tryLock(200ms)` succeeds while you hold read.
   Run the EXERCISES.md upgrade demo and confirm.

## One-paragraph write-up

Explain barging to a junior: what the CAS does, what throughput gains, what
starvation risks, and why `tryLock()` ignores fairness. If the paragraph leans
on vague filler adjectives instead of specifics, rewrite it with queue
positions and method names.
