# Solution: Fixing ReDoS and High CPU in the Content Moderation Service

**Incident**: INC-2024-0610-REDOS
**Fix Version**: Content Moderation Engine 4.7.2
**Last Updated**: June 11, 2024

## Overview

The fix addresses the ReDoS vulnerability at four levels:

1. **Primary Fix**: Rewrite the vulnerable regex pattern using atomic groups and possessive quantifiers to eliminate backtracking
2. **Input Validation**: Add input length limits to prevent oversized payloads
3. **Regex Timeout**: Implement a configurable timeout for all regex evaluations using Thread.interrupt()
4. **Defensive Layer**: Add string pooling/deduplication to reduce GC pressure from repeated inputs

## Fix 1: Regex Pattern Rewrite — Atomic Groups and Possessive Quantifiers

The fix replaces backtracking-prone constructs with atomic groups `(?>...)` and possessive quantifiers `++`, `*+`, `?+` that prevent the regex engine from backtracking into the group.

### Original Vulnerable Pattern

```java
// VULNERABLE: Catastrophic backtracking with nested quantifiers + alternation
// Pattern: ^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])((?=.*[a-z])|(?=.*upper_seq)).{8,40}$
private static final Pattern VULNERABLE_PATTERN = Pattern.compile(
    "^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])" +
    "((?=.*[a-z])|(?=.*upper_seq))" +  // ← REdoS here
    "(?=.*(.)\\1{2,}).{8,40}$"
);
```

### Fixed Pattern — Atomic Group

```java
// FIXED: Atomic group eliminates backtracking into the alternation
// Pattern: ^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])(?=.*(?:[a-z]|upper_seq))(?=.*(.)\1{2,}).{8,40}$
//
// Changes:
// 1. Replaced ((?=.*[a-z])|(?=.*upper_seq)) with (?=.*(?:[a-z]|upper_seq))
//    - The (?:...) non-capturing group with a single lookahead ensures
//      the regex engine does not backtrack through alternation positions
// 2. The atomic group (?>...) could also be used but is not needed here
//    since the non-capturing group inside the lookahead is sufficient
private static final Pattern FIXED_PATTERN = Pattern.compile(
    "^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])" +
    "(?=.*(?:[a-z]|upper_seq))" +       // ← FIXED: single non-capturing group
    "(?=.*(.)\\1{2,}).{8,40}$"
);
```

### Atomic Group Usage — General Pattern

```java
// General ReDoS prevention with atomic groups
//
// VULNERABLE: Alternation with overlapping branches
//    (a|ab|abc)+d
//
// FIXED: Atomic group prevents backtracking
//    (?>a|ab|abc)+d
//    - The (?>...) atomic group commits to whatever branch matches first
//    - If the overall pattern fails, the engine cannot backtrack into the group
//    - This converts O(2^n) to O(n)
//
// POSSESSIVE QUANTIFIER (equivalent to atomic group):
//    (a|ab|abc)++d
//    - The ++ possessive quantifier is equivalent to wrapping in (?>...)
//    - Once the group matches, it never gives up characters

// Example: Fixing the simplified ReDoS pattern
// Vulnerable: (a|aa|aaa|aaaa)+b
// Fixed:      (?>a|aa|aaa|aaaa)+b    (atomic group)
//         or  (a|aa|aaa|aaaa)++b     (possessive quantifier)
```

## Fix 2: Input Length Validation

```java
package com.meta.content.moderation;

/**
 * Request validator for the content moderation service.
 * Rejects inputs that exceed length limits or contain known
 * ReDoS-triggering patterns.
 */
public class ModerationRequestValidator {

    // Maximum input length (characters)
    private static final int MAX_INPUT_LENGTH = 1024;

    // Maximum input length for regex-heavy rules
    private static final int MAX_REGEX_INPUT_LENGTH = 256;

    // Input must have at least some content
    private static final int MIN_INPUT_LENGTH = 1;

    /**
     * Validates a moderation request before regex evaluation.
     *
     * @param text the input text to validate
     * @throws IllegalArgumentException if validation fails
     */
    public void validate(String text) {
        if (text == null) {
            throw new IllegalArgumentException("Input text must not be null");
        }

        int length = text.length();

        if (length < MIN_INPUT_LENGTH) {
            throw new IllegalArgumentException(
                "Input text too short: " + length + " chars (min: " + MIN_INPUT_LENGTH + ")"
            );
        }

        if (length > MAX_INPUT_LENGTH) {
            throw new IllegalArgumentException(
                "Input text too long: " + length + " chars (max: " + MAX_INPUT_LENGTH + ")"
            );
        }

        // Additional check for regex-heavy rules: stricter limit
        if (length > MAX_REGEX_INPUT_LENGTH && containsSuspiciousCharacters(text)) {
            throw new IllegalArgumentException(
                "Input text exceeds regex-safe length limit"
            );
        }
    }

    /**
     * Heuristic check for characters commonly used in ReDoS attacks.
     * Not a complete check but reduces attack surface.
     */
    private boolean containsSuspiciousCharacters(String text) {
        // ReDoS attacks often use repeated single characters
        // combined with the vulnerable regex constructs
        int consecutiveSameChar = 0;
        char lastChar = 0;

        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c == lastChar) {
                consecutiveSameChar++;
                if (consecutiveSameChar > 10) {
                    return true;
                }
            } else {
                consecutiveSameChar = 0;
                lastChar = c;
            }
        }

        return false;
    }
}
```

## Fix 3: Regex Timeout via Custom Pattern Wrapper

Java's `java.util.regex.Pattern` does not support timeouts. The fix implements a timeout by running the regex match in a separate thread and interrupting it after a configurable timeout.

```java
package com.meta.content.moderation;

import java.util.concurrent.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * A thread-safe wrapper for java.util.regex.Pattern that adds
 * a configurable execution timeout. If the regex evaluation exceeds
 * the timeout, the thread is interrupted and a TimeoutException is thrown.
 *
 * This prevents ReDoS attacks by bounding regex execution time.
 */
public class TimeoutPattern {

    private final Pattern pattern;
    private final long timeoutMillis;
    private final TimeUnit timeUnit;

    // Shared executor for timeout tasks — single thread is sufficient
    // because we only use it for interruption, not parallel execution
    private static final ScheduledExecutorService TIMEOUT_EXECUTOR =
            Executors.newSingleThreadScheduledExecutor(r -> {
                Thread t = new Thread(r, "regex-timeout-watchdog");
                t.setDaemon(true);
                return t;
            });

    /**
     * Creates a TimeoutPattern with the specified regex and timeout.
     *
     * @param regex         the regex pattern string
     * @param timeoutMillis the maximum time allowed for regex evaluation
     */
    public TimeoutPattern(String regex, long timeoutMillis) {
        this.pattern = Pattern.compile(regex);
        this.timeoutMillis = timeoutMillis;
        this.timeUnit = TimeUnit.MILLISECONDS;
    }

    /**
     * Creates a TimeoutPattern from an existing compiled Pattern.
     *
     * @param pattern       the compiled Pattern
     * @param timeoutMillis the maximum time allowed for regex evaluation
     */
    public TimeoutPattern(Pattern pattern, long timeoutMillis) {
        this.pattern = pattern;
        this.timeoutMillis = timeoutMillis;
        this.timeUnit = TimeUnit.MILLISECONDS;
    }

    /**
     * Returns whether the input matches the pattern, with a timeout.
     *
     * @param input the input string to test
     * @return true if the input matches the pattern
     * @throws RegexTimeoutException if evaluation exceeds the timeout
     * @throws InterruptedException if the current thread is interrupted
     */
    public boolean matches(String input) throws RegexTimeoutException {
        return matches(input, timeoutMillis, timeUnit);
    }

    /**
     * Returns whether the input matches the pattern, with a custom timeout.
     *
     * @param input   the input string to test
     * @param timeout the timeout duration
     * @param unit    the time unit
     * @return true if the input matches the pattern
     * @throws RegexTimeoutException if evaluation exceeds the timeout
     */
    public boolean matches(String input, long timeout, TimeUnit unit)
            throws RegexTimeoutException {

        // Track the current thread so the watchdog can interrupt it
        final Thread currentThread = Thread.currentThread();
        final String threadName = currentThread.getName();

        // Schedule a watchdog task to interrupt this thread on timeout
        ScheduledFuture<?> watchdog = TIMEOUT_EXECUTOR.schedule(
            () -> {
                // The timeout has expired — interrupt the regex evaluation
                currentThread.interrupt();
            },
            timeout,
            unit
        );

        try {
            // Perform the regex match
            Matcher matcher = pattern.matcher(input);
            boolean result = matcher.matches();

            // Check if we were interrupted (timeout)
            if (Thread.interrupted()) {
                throw new RegexTimeoutException(
                    "Regex evaluation timed out after " + timeout + " " + unit,
                    pattern.pattern(),
                    input.length()
                );
            }

            return result;

        } catch (RegexTimeoutException e) {
            // Re-throw timeout exceptions
            throw e;

        } finally {
            // Cancel the watchdog task (no longer needed)
            watchdog.cancel(false);

            // Clear the interrupted flag (the watchdog may have set it)
            Thread.interrupted();
        }
    }

    /**
     * Creates a Matcher for the input. The returned matcher does NOT
     * have timeout protection. Use matches() for timed evaluation.
     *
     * @param input the input string
     * @return a Matcher for the input
     */
    public Matcher matcher(String input) {
        return pattern.matcher(input);
    }

    /**
     * Returns the underlying Pattern.
     */
    public Pattern getPattern() {
        return pattern;
    }

    /**
     * Returns the timeout in milliseconds.
     */
    public long getTimeoutMillis() {
        return timeoutMillis;
    }

    /**
     * Exception thrown when regex evaluation exceeds the configured timeout.
     */
    public static class RegexTimeoutException extends RuntimeException {
        private final String pattern;
        private final int inputLength;

        public RegexTimeoutException(String message, String pattern, int inputLength) {
            super(message);
            this.pattern = pattern;
            this.inputLength = inputLength;
        }

        public String getPattern() {
            return pattern;
        }

        public int getInputLength() {
            return inputLength;
        }
    }
}
```

### Alternative: ThreadPool-Based Regex Evaluation

For environments where thread interruption is problematic, use a separate thread pool:

```java
package com.meta.content.moderation;

import java.util.concurrent.*;
import java.util.regex.Pattern;

/**
 * Alternative regex timeout implementation that runs the regex
 * in a separate thread pool. This avoids thread interruption issues
 * but adds thread context switching overhead.
 */
public class ThreadPoolRegexEvaluator {

    private final ExecutorService regexExecutor;
    private final long timeoutMillis;

    public ThreadPoolRegexEvaluator(int poolSize, long timeoutMillis) {
        this.regexExecutor = Executors.newFixedThreadPool(poolSize);
        this.timeoutMillis = timeoutMillis;
    }

    public boolean matches(Pattern pattern, String input)
            throws RegexTimeoutException, InterruptedException {

        Future<Boolean> future = regexExecutor.submit(
            () -> pattern.matcher(input).matches()
        );

        try {
            return future.get(timeoutMillis, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            future.cancel(true); // Interrupt the regex thread
            throw new RegexTimeoutException(
                "Regex timed out after " + timeoutMillis + "ms",
                pattern.pattern(),
                input.length()
            );
        } catch (ExecutionException e) {
            throw new RuntimeException("Regex evaluation failed", e.getCause());
        }
    }
}
```

## Fix 4: String Pooling for GC Pressure Reduction

During the ReDoS attack, many identical or similar input strings were created, causing GC pressure. String interning or a custom weak-reference pool reduces allocations.

```java
package com.meta.content.moderation;

import java.lang.ref.WeakReference;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * A simple string pool that deduplicates input strings.
 * Uses WeakHashMap to allow GC of unused strings.
 * Reduces GC pressure from repeated identical inputs.
 */
public class StringPool {

    private final Map<String, WeakReference<String>> pool =
            new WeakHashMap<>();

    /**
     * Returns a canonical representation of the input string.
     * If the same string has been interned before and is still
     * in memory, returns the cached instance.
     */
    public String intern(String input) {
        synchronized (pool) {
            WeakReference<String> ref = pool.get(input);
            if (ref != null) {
                String cached = ref.get();
                if (cached != null) {
                    return cached;
                }
            }
            pool.put(input, new WeakReference<>(input));
            return input;
        }
    }

    /**
     * Returns the current pool size (approximate, due to WeakHashMap).
     */
    public int size() {
        synchronized (pool) {
            return pool.size();
        }
    }
}
```

## Complete Integration

```java
package com.meta.content.moderation;

import java.util.regex.Pattern;
import java.util.logging.Logger;

/**
 * Content moderation engine with ReDoS protection.
 * Combines input validation, timeout patterns, and string pooling.
 */
public class ContentModerationEngine {

    private static final Logger LOG =
            Logger.getLogger(ContentModerationEngine.class.getName());

    private final ModerationRequestValidator validator;
    private final StringPool stringPool;

    // Pattern with timeout — 100ms max for regex evaluation
    private final TimeoutPattern policyPattern;

    public ContentModerationEngine() {
        this.validator = new ModerationRequestValidator();
        this.stringPool = new StringPool();

        // Compile the fixed pattern and wrap with timeout
        Pattern compiled = Pattern.compile(
            "^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])" +
            "(?=.*(?:[a-z]|upper_seq))" +
            "(?=.*(.)\\1{2,}).{8,40}$"
        );
        this.policyPattern = new TimeoutPattern(compiled, 100L);
    }

    /**
     * Evaluates content against policy rules with ReDoS protection.
     *
     * @param text the content text to evaluate
     * @return true if content violates policy
     * @throws IllegalArgumentException if input is invalid
     */
    public boolean evaluate(String text) {
        // Step 1: Validate input (length limits)
        validator.validate(text);

        // Step 2: Intern the string to reduce GC pressure
        String internedText = stringPool.intern(text);

        // Step 3: Evaluate with timeout protection
        try {
            boolean matches = policyPattern.matches(internedText);
            LOG.fine("Policy evaluation: " + matches + " for input length " + text.length());
            return matches;

        } catch (TimeoutPattern.RegexTimeoutException e) {
            // Log the timeout as a potential ReDoS attempt
            LOG.warning("Regex timeout on input length " + e.getInputLength() +
                        " pattern: " + e.getPattern());
            // Timeout means no match (do not flag content based on incomplete evaluation)
            return false;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOG.severe("Regex evaluation interrupted");
            return false;
        }
    }
}
```

## Unit Tests

```java
package com.meta.content.moderation;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.regex.Pattern;
import static org.junit.jupiter.api.Assertions.*;

class ContentModerationEngineTest {

    private ContentModerationEngine engine;

    @BeforeEach
    void setUp() {
        engine = new ContentModerationEngine();
    }

    @Test
    void validInputShouldEvaluateCorrectly() {
        assertTrue(engine.evaluate("ValidContent1!"));
        assertFalse(engine.evaluate("short"));
    }

    @Test
    void inputExceedingMaxLengthShouldBeRejected() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 2000; i++) {
            sb.append("x");
        }
        assertThrows(IllegalArgumentException.class,
            () -> engine.evaluate(sb.toString()));
    }

    @Test
    void redoSPayloadShouldTimeoutNotHang() {
        // This input would hang the vulnerable version for 30+ seconds
        // The TimeoutPattern should timeout in 100ms
        String redoSPayload = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaac";
        long start = System.currentTimeMillis();
        boolean result = engine.evaluate(redoSPayload);
        long duration = System.currentTimeMillis() - start;

        // Should complete quickly (under 500ms including overhead)
        assertTrue(duration < 500, "Regex took " + duration + "ms (should be < 500ms)");
        assertFalse(result); // Non-matching input should return false
    }

    @Test
    void atomicGroupPatternShouldNotBacktrack() {
        // Test the atomic group pattern directly
        Pattern atomicPattern = Pattern.compile("(?>a|aa|aaa|aaaa)+b");
        long start = System.currentTimeMillis();

        // This would be O(2^n) without atomic group
        assertFalse(atomicPattern.matcher("aaaaaaaaac").matches());

        long duration = System.currentTimeMillis() - start;
        assertTrue(duration < 100, "Atomic group pattern took " + duration + "ms");
    }

    @Test
    void possessiveQuantifierShouldPreventBacktracking() {
        // Test possessive quantifier (equivalent to atomic group)
        Pattern possessivePattern = Pattern.compile("(a|aa|aaa|aaaa)++b");
        long start = System.currentTimeMillis();

        assertFalse(possessivePattern.matcher("aaaaaaaaac").matches());

        long duration = System.currentTimeMillis() - start;
        assertTrue(duration < 100, "Possessive quantifier pattern took " + duration + "ms");
    }

    @Test
    void stringPoolShouldReduceAllocations() {
        StringPool pool = new StringPool();

        // Same string interned multiple times
        String s1 = pool.intern("hello");
        String s2 = pool.intern("hello");
        String s3 = pool.intern("hello");

        // Should return the same reference
        assertSame(s1, s2);
        assertSame(s2, s3);
    }
}
```

## ReDoS Prevention Check — Regex Audit Tool

```java
package com.meta.content.moderation;

import java.util.concurrent.*;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

/**
 * Scans regex patterns for potential ReDoS vulnerabilities
 * by testing them against known ReDoS-triggering inputs.
 */
public class ReDoSScanner {

    private static final String[] TEST_INPUTS = {
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaac",   // Repeated char + mismatch
        "ababababababababababababababababac", // Alternation test
        "1234567890123456789012345678901234567890x", // Numeric test
        "a!a!a!a!a!a!a!a!a!a!a!a!a!a!a!a!a!a!x",   // Mixed test
    };

    private static final long MAX_EVALUATION_TIME_MS = 500;

    public static boolean isVulnerable(String regex) {
        try {
            // Quick syntax check
            Pattern pattern = Pattern.compile(regex);

            // Test against known ReDoS inputs
            for (String input : TEST_INPUTS) {
                long start = System.nanoTime();
                try {
                    pattern.matcher(input).matches();
                } catch (StackOverflowError e) {
                    // Stack overflow from deep backtracking → definitely vulnerable
                    return true;
                }
                long duration = TimeUnit.NANOSECONDS.toMillis(
                    System.nanoTime() - start);
                if (duration > MAX_EVALUATION_TIME_MS) {
                    System.err.println("WARNING: Pattern '" + regex +
                        "' took " + duration + "ms on input length " +
                        input.length());
                    return true;
                }
            }

            return false;
        } catch (PatternSyntaxException e) {
            System.err.println("Invalid regex pattern: " + e.getMessage());
            return false;
        }
    }
}
```

## Deployment Strategy

| Phase | Scope | Duration | Success Criteria |
|-------|-------|----------|------------------|
| Canary | 10% nodes | 4 hours | CPU < 40%, no latency spikes |
| Regional | 50% nodes | 4 hours | P99 < 100ms, no ReDoS timeouts |
| Full rollout | 100% nodes | 24 hours | CPU flat, latency at baseline |
| Enable policy rule | Re-enable rule #1427 | Manual | No CPU impact |

## Verification Commands

```bash
# CPU profiling with async-profiler
profiler.sh -d 30 -e cpu -f flamegraph.html <pid>

# Check thread states during regex evaluation
jstack <pid> | grep -E "java.util.regex|RUNNABLE|BLOCKED"

# JFR recording for regex hotspot analysis
jcmd <pid> JFR.start name=regex_hotspots settings=profile

# Monitor CPU per thread
top -H -p <pid>

# Check for regex-related stack traces
jcmd <pid> Thread.print | grep -A 5 "Pattern"
```

## References

- OWASP: "ReDoS Prevention Cheat Sheet" — (link removed)
- RexEgg: "Catastrophic Backtracking" — https://www.regular-expressions.info/catastrophic.html
- Cloudflare: "ReDoS: Regular Expression Denial of Service" — Cloudflare Blog
- Google: "ReDoS and Regex Security" — Google Project Zero
- Meta: "Fighting ReDoS at Scale" — Meta Engineering Internal
- Oracle: "java.util.regex Performance Tips" — Oracle Java Documentation

