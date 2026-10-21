# Quiz: Concurrent Data Structures

1. What does CAS stand for? Compare-And-Swap
2. What is the ABA problem? Pointer returning to previous value
3. How does Treiber stack work? CAS on top pointer
4. What is lock striping? Multiple locks for different data partitions
5. Who designed java.util.concurrent? Doug Lea
6. What is false sharing? Threads on same cache line causing contention
7. What progress condition is strongest? Wait-Free
8. How does ConcurrentHashMap handle concurrency? CAS + lock striping
