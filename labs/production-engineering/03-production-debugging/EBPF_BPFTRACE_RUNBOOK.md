# ADVANCED RUNBOOK: Linux eBPF Tracing & Headless Core Dump Diagnostics (`jhsdb`)
## Lab 03 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Zero-Overhead Linux eBPF (`bpftrace`) Tracing for Java

Extended Berkeley Packet Filter (eBPF) allows running sandboxed byte code directly inside the Linux kernel without modifying the JVM or adding profiler overhead.

### Script 1: Measuring Disk Block I/O Latency (`biolatency.bt`)
When a Java service suffers random 200ms latency spikes without GC pauses, the cause is often Linux kernel filesystem flushes or slow block I/O.
```bash
# Traces all block I/O requests and prints power-of-2 histogram in microseconds
bpftrace -e '
kprobe:blk_account_io_start { @start[arg0] = nsecs; }
kprobe:blk_account_io_done /@start[arg0]/ {
    @usecs = hist((nsecs - @start[arg0]) / 1000);
    delete(@start[arg0]);
}'
```

### Script 2: Off-CPU Sleep Analysis (`offcputime.bt`)
Standard profilers only show what code does while running on CPU. When threads are stalled waiting on kernel locks, disk reads, or socket writes, off-CPU profiling is required:
```bash
# Capture why Java threads are sleeping (sampling kernel finish_task_switch)
bpftrace -e '
kprobe:finish_task_switch {
    $prev = (struct task_struct *)arg0;
    if ($prev->comm == "java") {
        @start[$prev->pid] = nsecs;
    }
    if (@start[curtask->pid]) {
        $duration_us = (nsecs - @start[curtask->pid]) / 1000;
        if ($duration_us > 10000) { // Slept for > 10ms
            @[kstack, ustack] = hist($duration_us);
        }
        delete(@start[curtask->pid]);
    }
}'
```

---

## 2. Post-Mortem Headless Core Dump Forensics with `jhsdb clhsdb`

When a JVM crashes abruptly with `SIGSEGV` or is hung so severely that `jcmd` fails with "Unable to attach", the only way to inspect state is a Linux core dump.

### Step 1: Force Linux Core Dump Generation
```bash
# Enable core dumps
ulimit -c unlimited
# If process is hung, force dump without killing:
gcore -o /dumps/jvm-core $(pgrep -f java)
```

### Step 2: Launch HotSpot Serviceability Agent (`jhsdb`)
```bash
jhsdb clhsdb --core /dumps/jvm-core --exe $JAVA_HOME/bin/java
```

### Step 3: Essential `clhsdb` Diagnostic Commands
```text
hsdb> jstack -v
# Prints Java stack traces with lock addresses for EVERY thread directly from memory

hsdb> universe
# Dumps exact Eden, Survivor, and Old Gen heap pointers and boundaries

hsdb> scanoops 0x00007f8b90000000 0x00007f8ba0000000 com.learning.Order
# Scans raw memory addresses for instances of a specific Java class

hsdb> class com.learning.Order
# Dumps JVM internal Klass layout and vtable offsets
```
- Operates entirely offline; does not require the JVM process to be alive.
- Works even if the JVM heap is severely corrupted.
