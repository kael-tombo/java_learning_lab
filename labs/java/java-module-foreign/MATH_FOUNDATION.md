# Math Foundation — Foreign Memory

## 1. Address Arithmetic
`addr(elem_i) = base + i × sizeof(T)`.
Point{x,y} ints: stride 8, elem_5 at base+40.

## 2. Struct Size + Padding
`size = ceil(sum+pads, maxAlign)`.
Example: byte+long → 1+7pad+8 = 16.

## 3. Alignment
`offset % align == 0`. Misaligned → fault/slow.
Layout: `b.byteAlignment()`.

## 4. Array Footprint
`bytes = n × sizeof(T)`. 1M ints = 4MB off-heap.

## 5. Copy Cost
`T_copy = bytes / memcpy_bw` (~20GB/s). 4MB ≈ 0.2ms.

## 6. Arena Lifetime
Live(t) = allocated − freed_at_close. Confined frees O(1) bulk.

## 7. Downcall Overhead
`T = stub + native + bounds_check`. FFM ~5–20ns vs JNI ~50ns+.

## 8. String Bytes
UTF-8 C str = `utf8_len + 1 (NUL)`. "héllo" = 6+1=7.

## 9. Page/Mmap Granularity
Map length rounds to 4KB pages. `pages = ceil(n/4096)`.

## 10. Bounds Check Cost
O(1) compare per access; vectorized loops amortize.

## Recap
```
addr = base + i·size
size = align(sum)
bytes = n·sizeof
T = bytes/bw
pages = ⌈n/4096⌉
```
Drill: layout {long,byte,int} → offsets/sizes; 10M longs footprint + copy time.
