# Mathematical Foundation: Spring Batch

## Chunk Size Optimization
Processing time for a batch of N items with chunk size C:
Total = ceil(N/C) * (C * R + C * P + W) where R=read time, P=process time, W=write time

## Memory Usage
Memory â‰ˆ C * (item_size + overhead) for buffered items

## Optimal Chunk Size
Optimal C minimizes: ceil(N/C) * W + N * (R + P) + C * overhead
Larger chunks reduce write overhead but increase memory.
