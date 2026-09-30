# RUNBOOK: Redis Incidents & Cache Triage
## Lab 12 | Production Engineering Academy

---

## RUNBOOK 01: Redis Memory Exhaustion (OOM & Eviction Spike)

**Severity**: P1  
**Symptom**: Application throwing `OOM command not allowed when used memory > 'maxmemory'`.

### Step 1: Inspect Redis Memory Breakdown
```bash
redis-cli -h redis-primary.internal INFO memory
```
Check:
- `used_memory_human` vs `maxmemory_human`
- `mem_fragmentation_ratio` (if $> 1.8$, fragmentation is severe).
- `evicted_keys`: High rate indicates keys are being dropped rapidly.

### Step 2: Identify Big Keys Consuming Space
Run non-blocking big keys scanner:
```bash
redis-cli -h redis-primary.internal --bigkeys
```
Or sample memory usage on candidate keys:
```bash
redis-cli MEMORY USAGE "user:session:super_tenant"
```

### Step 3: Emergency Actions
1. **Temporarily Bump Maxmemory**:
   ```bash
   redis-cli CONFIG SET maxmemory 28gb
   ```
2. **Enable Active Defragmentation**:
   ```bash
   redis-cli CONFIG SET activedefrag yes
   ```
3. **Delete Large Keys Safely** (NEVER use `DEL` on multi-gigabyte keys as it blocks Redis single thread for seconds! Use `UNLINK`):
   ```bash
   redis-cli UNLINK "runaway:massive:hash"
   ```

---

## RUNBOOK 02: Redis Slowlog & CPU 100% Triage
Check commands taking longer than 10ms:
```bash
redis-cli SLOWLOG GET 25
```
Common culprits: `KEYS *` (must be banned, use `SCAN`), `SMEMBERS` on large sets, or large `HGETALL`.
