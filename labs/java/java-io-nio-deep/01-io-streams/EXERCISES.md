# EXERCISES — I/O Streams

## 1. Buffer-size benchmark (beginner)
Time `bufferedCopy` on a 20 MB file with `B ∈ {512, 4096, 8192, 65536}`.
Plot time vs `B`. At what size do returns diminish, and why?
*Hint: measure with `System.nanoTime`, 3 warmup runs, average of 5.*

## 2. Unbuffered vs buffered (beginner)
Write `unbufferedCopy` (single-byte `read()`/`write(int)`). Compare wall
time against `bufferedCopy` on 5 MB. Predict the ratio from the syscall
math in MATH_FOUNDATION before running.

## 3. Order-sensitivity proof (intermediate)
Swap two reads in `readPrimitives` (e.g. `readDouble` before `readInt`) and
run. Record the failure mode (garbage vs exception). Explain *why* that
specific failure occurs given the byte layout (`int`=4B, `double`=8B).

## 4. Overlapping patterns (intermediate)
`findPattern({1,2,2,3}, {2,2,3})` — trace by hand, then run. Does the
pushback logic find it? Construct a case where naive single-byte-advance
misses an overlapping match, and explain what KMP would do differently.

## 5. Streaming concatenation (advanced)
Reimplement `concatenate` to accept `List<File>` (not byte arrays) and
stream directly to an `OutputStream` without materializing any part in
memory. Constraints: O(1) memory in part sizes, all inputs closed even if
a middle file throws. Verify with three 10 MB files and check peak heap
with `-Xmx64m`.
