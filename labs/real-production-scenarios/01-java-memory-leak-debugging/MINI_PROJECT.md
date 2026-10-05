# MINI_PROJECT — Reproduce, Detect, Fix a Memory Leak

## Objective
Inject an unbounded-cache leak in a Spring Boot demo, detect it from metrics, capture a dump, and fix with a bounded cache. ~90 minutes.

## 1. Setup (15 min)
```bash
java -version  # 17+
jcmd 1 GC.heap_info  # verify tool works
# starter: spring-boot demo with /orders endpoint (or plain java loop below)
```

## 2. Inject the Leak (15 min)
```java
// LeakEndpoint.java
@RestController class LeakEndpoint {
  static final Map<String, byte[]> CACHE = new HashMap<>();
  @GetMapping("/leak") String leak(@RequestParam(defaultValue="100") int n) {
    for (int i=0;i<n;i++) CACHE.put(UUID.randomUUID().toString(), new byte[10_000]);
    return "cached="+CACHE.size();
  }
}
```
Run with `-Xmx256m -XX:+HeapDumpOnOutOfMemoryError -Xlog:gc:file=gc.log:time`.

## 3. Detect (20 min)
- `curl` in a loop: `while true; do curl -s localhost:8080/leak?n=200; sleep 1; done`
- Watch: `jcmd <pid> GC.heap_info`, `jstat -gcutil <pid> 2s`, GC log pause growth.
- Record Old Gen after Full GC at 0/10/20 min → compute `r` and `T_oom`.

## 4. Capture Evidence (15 min)
```bash
jmap -histo:live <pid> | head -20
jmap -dump:live,format=b,file=/tmp/leak.hprof <pid>
jcmd <pid> JFR.start name=mini,settings=profile,filename=/tmp/mini.jfr duration=120s
```
Open dump in MAT or `jhsdb jmap --histo` — find dominator = `byte[]` via `HashMap`.

## 5. Fix (15 min)
Replace with Caffeine bounded cache (max 1000, 5-min TTL), redeploy, repeat load — prove Old Gen flatlines. Add Micrometer alert stub: heap >85% for 5m.

## Deliverables
1. Trend table (time → Old Gen) + computed T_oom. 2. Histo diff screenshot. 3. Before/after GC graph. 4. One-paragraph postmortem.

## Grading
Detect (40%): trend + T_oom correct. Evidence (30%): dump + dominator identified. Fix (30%): bounded cache + flat verification.
