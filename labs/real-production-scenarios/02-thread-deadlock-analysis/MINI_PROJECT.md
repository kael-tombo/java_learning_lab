# MINI_PROJECT — Reproduce, Detect, Fix a Deadlock

## Objective
Create a classic lock-order deadlock, prove the cycle from dumps, and fix via ordering + tryLock. ~75 min.

## 1. Setup (10 min)
Plain JDK 17, no framework. Terminal + `jstack` ready.

## 2. Inject (15 min)
```java
// Deadlock.java
record Acct(int id){} static final Object L1=new Object(), L2=new Object();
static void a2b(){ synchronized(L1){ sleep(100); synchronized(L2){ System.out.print("."); } } }
static void b2a(){ synchronized(L2){ sleep(100); synchronized(L1){ System.out.print("*"); } } }
public static void main(String[] a){ Thread t1=new Thread(()->{while(true)a2b();}); t1.setName("a2b");
 Thread t2=new Thread(()->{while(true)b2a();}); t2.setName("b2a"); t1.start(); t2.start(); }
```
`javac Deadlock.java && java Deadlock` — output stalls within seconds.

## 3. Detect (20 min)
```bash
jps -l  # find pid
for i in 1 2 3; do jstack -l <pid> > dump-$i.txt; sleep 15; done
grep -A6 "Found one Java-level deadlock" dump-1.txt
grep "waiting to lock" dump-*.txt | sort | uniq -c
```
Deliverable: draw cycle L1→L2→L1 with thread names; show identical stacks across 3 dumps.

## 4. Fix (20 min)
- Fix A: global order (always L1→L2). Rerun 2 min — no stall.
- Fix B: `ReentrantLock.tryLock(1, SECONDS)` with retry+jitter. Compare clarity.
- Add JUnit inversion test (1000 mixed transfers, 8s timeout assertion).

## 5. Harden (10 min)
Add `jvm_threads_deadlocked`-style check: script that greps `jstack` for deadlock banner and exits nonzero. Wire as health-check sketch.

## Deliverables
Cycle diagram, 3-dump excerpts, before/after run logs, ordering fix diff, regression test.

## Grading
Reproduce (25%), detect/cycle (35%), fix+verify (25%), regression test (15%).
