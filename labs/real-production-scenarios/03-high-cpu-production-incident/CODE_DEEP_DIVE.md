# CODE_DEEP_DIVE — High CPU Production Incident

## 1. Confirm It Is CPU (not lock/IO)
```bash
top -H -p <pid>          # per-thread CPU; note hot TID (decimal)
ps -Lo pid,tid,pcpu,stat,wchan:20 -p <pid> | sort -k3 -nr | head -20
vmstat 1 5; mpstat -P ALL 1 3
# TID decimal→hex for jstack: printf '%x\n' <tid>
```

## 2. Thread Dump + Hot-Thread Map
```bash
jstack -l <pid> > /tmp/cpu-tdump.txt
printf '%x\n' 12345   # → 3039, then grep nid=0x3039 in dump
grep -A20 "nid=0x3039" /tmp/cpu-tdump.txt | head -30
jcmd <pid> Thread.print > /tmp/cpu-print.txt
```

## 3. async-profiler CPU Flame (king tool)
```bash
./profiler.sh -e cpu -d 60 -f /tmp/cpu.html <pid>
./profiler.sh -e cpu -d 30 -t -f /tmp/cpu-threads.html <pid>  # per-thread
./profiler.sh -e wall -d 60 -f /tmp/wall.html <pid>  # compare: cpu-narrow vs wall-wide
./profiler.sh -e lock -d 60 -f /tmp/lock.html <pid>  # rule out contention
```

## 4. JFR Method Profiling
```bash
jcmd <pid> JFR.start name=cpu,settings=profile,filename=/tmp/cpu.jfr duration=180s
jfr print --events jdk.ExecutionSample /tmp/cpu.jfr | head -40
# open in JDK Mission Control: hottest stack = culprit frame
```

## 5. GC vs App CPU
```bash
jstat -gcutil <pid> 2s 10
# YGCT+FGCT climbing fast + high CPU = GC thrash, not app loop — check heap path instead
tail -50 /logs/gc.log
```

## 6. Log Snippets
```
# hot regex backtracking (one thread 99%, rest idle)
"http-nio-7" nid=0x3039 runnable [0x...]
  java.lang.Thread.State: RUNNABLE
  at java.util.regex.Pattern$Curly.match(Pattern.java:...)
  at com.shop.SearchFilter.matches(SearchFilter.java:88)
# infinite retry loop
  at com.shop.PriceClient.poll(PriceClient.java:41)  # line 41 = while(true) without backoff
```

## 7. Guilty Patterns + Fixes
```java
// catastrophic backtracking
Pattern.compile("(a+)+b");  // FIX: possessive/atomic: "(a++)b" or limit input length + timeout
// busy spin
while(!ready){}             // FIX: LockSupport.parkNanos / Condition.await / backoff
// retry storm
while(true){ call(); }      // FIX: exponential backoff + jitter + circuit breaker
// runaway stream
list.parallelStream().map(x->heavy(x))  // FIX: bound pool, cache, paginate
```

## 8. K8s Throttle Check
```bash
kubectl top pod <pod>; cat /sys/fs/cgroup/cpu/cpu.stat  # nr_throttled rising = limit too low
# distinguish: throttle = flat at limit across threads; hot-thread = 1 thread pegged
```

## 9. Checklist
Hot TID→stack, CPU flame, wall/flame compare, fix loop/regex, throttle check, p99 verify.
