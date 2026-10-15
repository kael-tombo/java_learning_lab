# Math Foundation - Java Fundamentals (fundamentals)

Quantitative rules behind types, overflow, cost analysis, and memory sizing. All outputs observed.
## Integer arithmetic and overflow
- `7 / 2` is 3: int division truncates toward zero. `7 / 2.0` is 3.5: one double widens all.
- `Integer.MAX_VALUE + 1` is -2147483648: int arithmetic wraps modulo 2^32, never throws.
- Observed: div=3, divD=3.5, wrap=-2147483648, big=2147483648 (widen to long BEFORE adding).
- Rule: cast one operand to long before the operation, not after: `(long) a + b`.
- `Math.addExact` throws ArithmeticException on overflow; use it for money and sizes.
- `%` keeps the dividend sign: `-7 % 3` is -1. `/` by zero throws for ints, gives Infinity for doubles.
## Big-O basics (track level)
- O(1): ArrayList.get(i); HashMap get/put average with a good hashCode.
- O(log n): TreeMap get/put; Collections.binarySearch on a sorted list.
- O(n): one linear scan; a stream pipeline with filter/map over n elements.
- O(n log n): library sort of n elements.
- O(n^2): nested loop over all pairs; 10k elements means ~10^8 inner steps.
- Amortized O(1): ArrayList.add; most adds are cheap, rare resizes copy O(n).
- Worst cases are real: HashMap degrades toward O(n) under hash collision; measure, do not assume.
## Memory-size arithmetic
- Primitive sizes are fixed: byte 1, short 2, char 2, int 4, float 4, long 8, double 8.
- int[n] payload is exactly 4n bytes: n=1000000 gives len=1000000, bytes=4000000 (observed).
- long[n] / double[n] payload is 8n bytes: 1M elements cost 8MB payload.
- Reference arrays cost 4 bytes per slot under default compressed oops on 64-bit JVMs, 8 without.
- Total footprint is payload plus a fixed per-object header; header size is VM-dependent.
- Rule: size the payload with n*elementSize first, then confirm totals with a heap dump.
- boolean[] stores one byte per element; BitSet packs 8 flags per byte for large flag sets.
- Boxing cost: Integer objects carry header plus 4 payload bytes; prefer int[] over List<Integer> for bulk numerics.
## Worked checks (run these)
- Overflow drill: print 7/2, 7/2.0, MAX_VALUE+1; confirm div=3, divD=3.5, wrap=-2147483648.
- Payload drill: allocate new int[1000000]; confirm len=1000000 and 4M payload bytes.
- Cost drill: time ArrayList.get in a loop vs indexOf scan; confirm flat vs linear scaling.
- Sort drill: double n, confirm sort time grows ~n log n, not ~n^2.
- Rules of thumb: measure before tuning; one variable at a time; p99 beats mean for SLAs.
