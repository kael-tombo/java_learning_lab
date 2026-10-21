# Mock Interview: GraalVM Polyglot Function Execution Engine (Lab 09)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Problem Understanding (5 min)

**Interviewer:** Design a GraalVM polyglot function execution engine. What is GraalVM polyglot capability?

**Candidate:** GraalVM is a high-performance JDK that supports running code from multiple languages (JavaScript, Python, Ruby, R, Java, WASM) in the same runtime. Languages are executed in contexts that can be isolated. The Truffle framework allows languages to be JIT-compiled together enabling cross-language inlining and optimization. This means you can call JavaScript from Java and Java from JavaScript with minimal overhead.

**Interviewer:** What is the core abstraction for executing user-defined functions?

**Candidate:** The LanguageRuntime interface abstracts language-specific execution. Each runtime compiles source code into a CompiledFunction and executes it within an ExecutionContext. The context carries function arguments, a timeout, and a unique ID for tracing. The engine manages a function registry, compilation cache, and thread pool for isolated execution.

**Interviewer:** How does your engine handle cross-language function composition?

**Candidate:** Function composition is a pipeline: output of one function becomes input of the next. The compose method iterates through the pipeline executes each function with the current value and propagates the result. If any stage fails the pipeline stops and returns an error with the stage name. This allows users to chain JavaScript array transforms with Python statistical functions.

---

## Round 2: Medium Isolation and Sandboxing (10 min)

**Interviewer:** How do you sandbox a polyglot function execution?

**Candidate:** Three layers: (1) Each execution runs in a separate Future on a fixed thread pool preventing CPU starvation. (2) Timeouts are enforced by Future.get(timeout, unit) if execution exceeds timeout we cancel the future. (3) Memory limits via wrapping ByteArrayOutputStream for output and monitoring heap via MemoryMXBean.

**Interviewer:** How does GraalVM handle sandboxing natively?

**Candidate:** GraalVM provides Engine, Context, and PolyglotException API. Context can be created with Context.newBuilder().allowIO(false).allowCreateThread(false).option("engine.WarnInterpreterOnly", "false"). This restricts file system access, threading, and class loading. Combined with my layer this provides defense in depth. However true sandboxing against all side-channel attacks is still an open challenge.

**Interviewer:** Could one function consume all CPU and starve others?

**Candidate:** Yes that is why I use a fixed thread pool and timeouts. Infinite loops are caught by the timeout. For CPU-intensive functions I would add execution queue priorities and per-user CPU quotas with thread monitoring. GraalVM Truffle runtime supports AST call count limits that can interrupt execution.

---

## Round 3: Medium-Hard Caching and Performance (10 min)

**Interviewer:** You cache compiled functions. How does this work across different arguments?

**Candidate:** The cache key is functionName + ":" + sourceCode.hashCode(). If the same function source is registered again the cache is invalidated. The compiled function is language-specific the runtime compile() method parses and potentially JIT-compiles the source. In GraalVM Context.eval() internally compiles Truffle ASTs so my cache avoids repeated parsing.

**Interviewer:** What metrics would you track for performance monitoring?

**Candidate:** Per-function: success count, error count, average duration, min/max duration, error rate, cache hit ratio, execution throughput. I expose these through a MetricsCollector using ConcurrentHashMaps of AtomicLong counters. These identify slow functions, functions that frequently time out, and overall engine health.

**Interviewer:** How does the engine handle concurrent compilation?

**Candidate:** cache.computeIfAbsent() ensures compilation for the same function happens only once. If two threads request the same uncached function one compiles and the other waits. This prevents redundant compilation. For languages with slow JIT warmup like JavaScript I would pre-compile commonly used functions on startup.

---

## Round 4: Hard Limitations and Extensions (15 min)

**Interviewer:** What are the limitations of your simulated runtimes vs real GraalVM?

**Candidate:** My runtimes are simulated they pattern-match on source code rather than interpreting it. They demonstrate the architecture but do not execute real JavaScript or Python. A real implementation uses GraalVM Context.eval(language, source). The key difference is my version has predictable behavior for testing but cannot run arbitrary user code. The architecture (runtime interfaces, caching, metrics, composition) is identical to a real GraalVM implementation.

**Interviewer:** How would you extend this to support WASM or LLVM?

**Candidate:** I would add a WasmRuntime implementing LanguageRuntime using GraalVM WASM support (org.graalvm.wasm). Similarly an LLVMRuntime using the Sulong LLVM bitcode interpreter. The LanguageRuntime interface is pluggable adding a new language is a single class implementing compile() and execute().

**Interviewer:** What is the biggest production risk with polyglot execution?

**Candidate:** Resource exhaustion a user function could allocate unlimited memory or spawn threads. Even with timeouts and thread pool isolation, memory allocation during an infinite loop can trigger OOM. Solutions include per-execution memory limits using GraalVM Context resource limits or process-level isolation (fork per execution). For CPU, GraalVM provides execution time limits via Truffle.

**Interviewer:** How would you add authentication and authorization for user functions?

**Candidate:** Each function is associated with a user or tenant. On execution I verify the caller has permission to invoke the function. For resource limits I allocate a budget per user (max CPU seconds per day, max memory per execution). The budget is checked before and during execution. I would use a rate limiter per user and charge their account for execution time. This is similar to AWS Lambda pricing.

**Interviewer:** How would you implement function versioning and rollback?

**Candidate:** The function registry stores all versions of a function. Each registration call creates a new version. The user specifies which version to call or uses "latest". If a new version fails (high error rate detected by metrics) the system automatically rolls back to the previous stable version. Versioning is critical for production because user code can have bugs that only manifest under load.

---

## Round 5: Summary (5 min)

**Interviewer:** Summarize the key design decisions.

**Candidate:** (1) Pluggable LanguageRuntime interface allows adding new languages without modifying the engine core. (2) Compilation cache reduces repeated parsing overhead at the cost of memory. (3) Fixed thread pool and timeouts provide baseline resource isolation. (4) Metrics-driven operations enable monitoring and auto-rollback. (5) Function composition enables powerful cross-language pipelines. The most important decision is using the Strategy pattern for runtimes making the system extensible by design.
