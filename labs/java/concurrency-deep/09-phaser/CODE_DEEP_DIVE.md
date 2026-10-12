# Phaser — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Phases Advance 0 → 1 → 2, Arrival Values Are Exact

```java
import java.util.concurrent.Phaser;

public class PhaseCount {
    public static void main(String[] args) throws Exception {
        Phaser phaser = new Phaser(1);   // main registered
        phaser.bulkRegister(2);          // +2 workers = 3 parties
        System.out.println("registered = " + phaser.getRegisteredParties());
        System.out.println("phase 0 open: " + (phaser.getPhase() == 0));

        int phases = 3;
        int[] arrivals = new int[phases];
        Thread[] workers = new Thread[2];
        for (int w = 0; w < workers.length; w++) {
            workers[w] = new Thread(() -> {
                for (int i = 0; i < phases; i++) phaser.arriveAndAwaitAdvance();
            });
            workers[w].start();
        }
        for (int i = 0; i < phases; i++) arrivals[i] = phaser.arriveAndAwaitAdvance();
        for (Thread t : workers) t.join(10_000);

        System.out.println("returned phases = " + arrivals[0] + "," + arrivals[1] + "," + arrivals[2]);
        System.out.println("arriveAndAwaitAdvance returns POST-advance phase: "
                + (arrivals[0] == 1 && arrivals[1] == 2 && arrivals[2] == 3));
        System.out.println("final phase = " + phaser.getPhase());
        System.out.println("unarrived now = " + phaser.getUnarrivedParties());
        phaser.arriveAndDeregister();   // main leaves; cleanup, no hang on exit
    }
}
```

Expected output:
```
registered = 3
phase 0 open: true
returned phases = 1,2,3
arriveAndAwaitAdvance returns POST-advance phase: true
final phase = 3
unarrived now = 3
```

`arriveAndAwaitAdvance()` returns the phase *after* each advance (1, 2, 3)
— arriving during phase k yields k+1, as the source's `return nextPhase` /
woken-phase paths dictate. Contrast `arrive()` (snippet 5), which returns
the arrival phase itself. The last line (`unarrived now = 3`) shows the next
phase fully open: all three parties registered, none arrived yet. (Main
deregisters at the end so no stray registration outlives the demo.)

## 2. arrive() Signals Without Waiting

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Phaser;
import java.util.concurrent.atomic.AtomicBoolean;

public class ArriveNoWait {
    public static void main(String[] args) throws Exception {
        Phaser phaser = new Phaser(1);   // main
        phaser.register();               // +1 worker = 2 parties
        AtomicBoolean producerMovedOn = new AtomicBoolean();
        CountDownLatch workerArrived = new CountDownLatch(1);

        Thread worker = new Thread(() -> {
            int arrivalPhase = phaser.arrive();   // signal, DO NOT wait
            producerMovedOn.set(true);            // proceed immediately
            workerArrived.countDown();
            phaser.awaitAdvance(arrivalPhase);    // ...rendezvous later, elsewhere
        });
        worker.start();
        workerArrived.await();                    // worker has arrived + moved on
        System.out.println("producer moved on without waiting: " + producerMovedOn.get());
        System.out.println("phase still 0 (main hasn't arrived): " + (phaser.getPhase() == 0));
        System.out.println("unarrived = 1 (main outstanding): "
                + (phaser.getUnarrivedParties() == 1));
        phaser.arriveAndAwaitAdvance();           // main arrives: phase flips to 1
        worker.join(5000);
        System.out.println("phase advanced after main arrived: " + (phaser.getPhase() == 1));
        phaser.arriveAndDeregister();
    }
}
```

Expected output:
```
producer moved on without waiting: true
phase still 0 (main hasn't arrived): true
unarrived = 1 (main outstanding): true
phase advanced after main arrived: true
```

No barrier or latch allows this split: the worker's *signal* (`arrive`) and
its *synchronization* (`awaitAdvance`) are separate calls, possibly in
different methods or far apart in code. The phase waits for main regardless.

## 3. Deregistration Shrinks the Barrier Mid-Run

```java
import java.util.concurrent.Phaser;

public class ShrinkBarrier {
    public static void main(String[] args) throws Exception {
        Phaser phaser = new Phaser(1);   // main
        phaser.bulkRegister(2);          // 2 workers; 3 total
        java.util.concurrent.CountDownLatch retired =
                new java.util.concurrent.CountDownLatch(1);
        Thread[] workers = new Thread[2];
        for (int w = 0; w < workers.length; w++) {
            final int id = w;
            workers[w] = new Thread(() -> {
                phaser.arriveAndAwaitAdvance();       // phase 0 with everyone
                if (id == 0) {
                    phaser.arriveAndDeregister();     // worker 0 retires
                    retired.countDown();
                } else phaser.arriveAndAwaitAdvance();  // worker 1 continues
            });
            workers[w].start();
        }
        phaser.arriveAndAwaitAdvance();               // phase 0
        retired.await();                              // deregistration visible before reading
        System.out.println("registered after phase 0 = " + phaser.getRegisteredParties());
        phaser.arriveAndAwaitAdvance();               // phase 1 with 2 parties
        for (Thread t : workers) t.join(10_000);
        System.out.println("shrank 3 -> 2: " + (phaser.getRegisteredParties() == 2));
        System.out.println("phase advanced with survivors: " + (phaser.getPhase() == 2));
        phaser.arriveAndDeregister();
    }
}
```

Expected output:
```
registered after phase 0 = 2
shrank 3 -> 2: true
phase advanced with survivors: true
```

Worker 0's `arriveAndDeregister()` counts as its phase-0 arrival *and*
removes it — phase 1 needs only the two survivors. Iterative solvers use
exactly this to retire converged partitions without rebuilding the barrier.

## 4. onAdvance Terminates on Your Predicate

```java
import java.util.concurrent.Phaser;

public class TerminateWhen {
    static class TwoPhasePhaser extends Phaser {
        TwoPhasePhaser(int parties) { super(parties); }
        @Override protected boolean onAdvance(int phase, int registeredParties) {
            return phase >= 1 || registeredParties == 0;   // stop after phase 1
        }
    }

    public static void main(String[] args) throws Exception {
        TwoPhasePhaser phaser = new TwoPhasePhaser(1);
        System.out.println("not terminated initially: " + !phaser.isTerminated());
        phaser.arriveAndAwaitAdvance();   // phase 0 -> 1 (onAdvance(0,...) false)
        System.out.println("phase = " + phaser.getPhase()
                + ", alive: " + !phaser.isTerminated());
        phaser.arriveAndAwaitAdvance();   // phase 1 -> terminate (onAdvance(1,...) true)
        System.out.println("terminated: " + phaser.isTerminated());
        System.out.println("phase negative after termination: " + (phaser.getPhase() < 0));
        // post-termination: everything passes through (open gate, not broken barrier)
        System.out.println("arrive post-termination returns negative: "
                + (phaser.arrive() < 0));
        System.out.println("awaitAdvance post-termination returns at once: "
                + (phaser.awaitAdvance(5) == phaser.getPhase()));
    }
}
```

Expected output:
```
not terminated initially: true
phase = 1, alive: true
terminated: true
phase negative after termination: true
arrive post-termination returns negative: true
awaitAdvance post-termination returns at once: true
```

`onAdvance` runs at each advance point — keep it a pure predicate (it stalls
all parties while it runs). Termination is a state, not an error: unlike a
broken `CyclicBarrier`, no exceptions propagate; the gate simply opens.

## 5. Await Your Own Arrival Phase (Never a Stale getPhase())

```java
import java.util.concurrent.Phaser;

public class AwaitYours {
    public static void main(String[] args) {
        Phaser solo = new Phaser(1);   // single party: arrivals advance immediately
        int arrivalPhase = solo.arrive();          // 0; phase flips to 1 at once
        System.out.println("arrival phase = " + arrivalPhase);
        int waited = solo.awaitAdvance(arrivalPhase);  // current(1) != 0: instant
        System.out.println("awaitAdvance(arrival) returned: " + waited);
        System.out.println("no waiting happened (returned current phase): " + (waited == 1));

        // the stale-read trap: getPhase() observed early, awaited late
        Phaser two = new Phaser(2);    // main + one implied party that never arrives
        int stale = two.getPhase();    // 0
        // ...meanwhile nothing advances (second party outstanding)...
        long t0 = System.nanoTime();
        // do NOT actually block the harness: use arriveAndAwaitAdvance's return instead
        int mine = two.arriveAndDeregister();  // arrive + leave; other party still out
        long dtMs = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("deregistering arrival returned phase: " + mine);
        System.out.println("stale getPhase() was " + stale + " (awaiting it now would block"
                + " until the stranger arrives — always await YOUR arrival value)");
        System.out.println("returned without blocking: " + (dtMs < 5000));
    }
}
```

Expected output:
```
arrival phase = 0
awaitAdvance(arrival) returned: 1
no waiting happened (returned current phase): true
deregistering arrival returned phase: 0
stale getPhase() was 0 (awaiting it now would block until the stranger arrives — always await YOUR arrival value)
returned without blocking: true
```

`awaitAdvance(p)` waits while current == p. A phase number sampled from
`getPhase()` may already be stale (advanced since) — awaiting it returns
instantly and *looks* like synchronization that never happened. The arrival
return value is the only phase number with a defined meaning to its caller.

## Common Pitfalls Encountered Here

- **Awaiting `getPhase()` instead of your arrival value** — stale phases
  return instantly, skipping the rendezvous silently (snippet 5).
- **Forgetting deregistration on failure paths** — a dead thread between
  register and arrive holds its phase forever; `try/finally` with
  `arriveAndDeregister`, or a supervising `forceTermination()`.
- **Treating termination like breakage** — post-termination calls pass
  through with negative returns; no exceptions (snippet 4). Code that treats
  negative phases as errors invents failures.
- **Blocking work inside `onAdvance`** — it runs at the advance point with
  all parties waiting; keep it a predicate (snippet 4).
- **Registering and never arriving** — each `register()` adds an *unarrived*
  party the current phase must wait for; spawn-then-crash without arrival
  wedges the phase.
- **Phase-overflow blindness** — `int` phases wrap after 2³¹ advances to
  negative (spurious termination); realistic only for hot loops running
  months, but the guard (`phase < 0` checks) must not confuse it with real
  termination.
