# Debugging Concurrent Data Structures

## Common Symptoms

| Symptom | Cause |
|---------|-------|
| Non-deterministic failures | Race condition |
| Hangs | Deadlock or livelock |
| Incorrect counts | Race in non-atomic increments |
| Performance collapse | Contention or false sharing |

## Tools

1. Thread dumps (jstack, jcmd)
2. Java Flight Recorder (JFR)
3. ThreadSanitizer (JVM TI)
4. Stress testing with Thread::yield()
