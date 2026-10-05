# CODE_DEEP_DIVE — Deadlock Analysis

## 1. Capture Dumps (3× spaced)
```bash
PID=$(pgrep -f 'app.jar' | head -1)
for i in 1 2 3; do jstack -l $PID > /tmp/tdump-$i.txt; sleep 30; done
jcmd $PID Thread.print > /tmp/thread-print.txt
diff /tmp/tdump-1.txt /tmp/tdump-3.txt | head -40  # stuck = identical stacks
```

## 2. Spot the Cycle
```
Found one Java-level deadlock:
=============================
"order-12":
  waiting to lock monitor 0x00007f8a (object 0x..., lock OrderLock-B),
  which is held by "order-7"
"order-7":
  waiting to lock monitor 0x00007f89 (object 0x..., lock OrderLock-A),
  which is held by "order-12"
```
Map `waiting to lock X held by Y` chains until you return to start.

## 3. JFR Contention
```bash
jcmd $PID JFR.start name=locks,settings=profile,filename=/tmp/locks.jfr duration=180s
jfr print --events jdk.JavaMonitorEnter,jdk.ThreadPark /tmp/locks.jfr | head -80
```

## 4. async-profiler Wall Clock
```bash
./profiler.sh -e wall -d 60 -t -f /tmp/wall.html $PID  # -t = split threads
# look for wide BLOCKED / park plateaus on same frames
```

## 5. Buggy vs Fixed Ordering
```java
// BUGGY: opposite order deadlocks
void transfer(Account a, Account b, int n){
  synchronized(a){ synchronized(b){ a.debit(n); b.credit(n); } }
}
// FIXED: global order
void transfer(Account a, Account b, int n){
  Account first = System.identityHashCode(a)<System.identityHashCode(b)?a:b;
  Account second = first==a?b:a;
  synchronized(first){ synchronized(second){ a.debit(n); b.credit(n); } }
}
// DEFENSIVE: tryLock with timeout
if(!lockA.tryLock(2,TimeUnit.SECONDS)) throw new BusyException("lockA");
try{ if(!lockB.tryLock(2,TimeUnit.SECONDS)) throw new BusyException("lockB");
  try{ work(); } finally{ lockB.unlock(); } } finally{ lockA.unlock(); }
```

## 6. Pool + Health Signals
```bash
curl -s localhost:8080/actuator/metrics/tomcat.threads.busy | head -20
curl -s localhost:8080/actuator/metrics/hikaricp.connections.active | head -20
# busy≈max + queue rising + CPU flat = suspect deadlock, capture dumps now
```

## 7. Regression Test
```java
@Test(timeout=10000) void noDeadlockUnderInversion() throws Exception {
  // hammer transfer(a,b) and transfer(b,a) concurrently; fail on timeout
  ExecutorService p = Executors.newFixedThreadPool(16);
  for(int i=0;i<1000;i++){ Account x=i%2==0?a:b, y=x==a?b:a;
    p.submit(()->transfer(x,y,1)); }
  p.shutdown(); assertTrue(p.awaitTermination(8,SECONDS));
}
```

## 8. Checklist
Dumps×3, cycle diagram, ordering fix, tryLock timeouts, isolated health-check pool.
