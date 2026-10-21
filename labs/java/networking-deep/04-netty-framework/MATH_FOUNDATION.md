# Netty Framework -- Mathematical Foundation

## 1. Event Loop Mathematics
N_event_loops = N_CPU_cores for compute-bound
N_event_loops = 2 * N_CPU_cores for I/O-bound
Optimal throughput when event loop utilization < 70%

### Task Queue Depth
queue_depth = arrival_rate * processing_time
Queue grows when processing rate < arrival rate

## 2. ByteBuf Mathematics

### Buffer Types
DirectBuffer allocation: expensive (system call)
HeapBuffer allocation: cheap (JVM heap)
Pooled buffers: amortize allocation cost

### Reference Counting
ref_count reaches 0 -> buffer released
release() decrements, retain() increments
Memory freed when all references are released

## 3. ChannelPipeline Performance
Total time = sum of all handler processing times
Each connection has its own pipeline

## 4. Memory Pooling

### Arena Allocation
Arena per CPU core (reduces contention)
Chunk size: 16MB, Page size: 8KB
Tiny cache: <512 bytes, Small: 512B-8KB, Normal: 8KB-16MB

### Cache Efficiency
Thread-local caches: no synchronization
Pooled allocator: 10-100x faster than unpooled
