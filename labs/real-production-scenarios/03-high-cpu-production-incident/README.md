# Lab 03: High CPU Production Incident — Meta Infrastructure ReDoS

## Situation Overview

Meta's (Facebook) content moderation infrastructure experienced a critical production incident where P99 latency spiked from 50ms to over 10 seconds during peak traffic hours. The affected service was responsible for scanning user-generated content against policy rules using a Java-based regex evaluation engine. Under normal conditions, the engine processed 50,000+ requests per minute across Meta's global deployment. During the incident, a single user post containing a carefully crafted text payload triggered catastrophic backtracking in the Java regex engine (java.util.regex.Pattern), causing an effective ReDoS (Regular Expression Denial of Service).

The regex pattern was a content policy rule designed to detect specific patterns of text. When evaluated against the malicious input, the regex engine's backtracking algorithm explored an exponential number of paths, consuming 100% CPU on the thread for over 30 seconds before the pattern was either matched or timed out. Because the service used a fixed-size thread pool (200 threads per node), 4-5 concurrent ReDoS attacks could saturate all available threads. New requests queued up, causing latency to spike to 10+ seconds for all users.

The incident involved Meta's Content AI team, SRE (Site Reliability Engineering), and Java Platform team over 8 hours. The root cause was a combination of an inefficient regex pattern with nested quantifiers and the absence of input length validation and regex execution timeouts.

## Severity Assessment

| Criteria | Rating | Details |
|----------|--------|---------|
| Impact Scope | P0 | All content uploads affected globally |
| User Facing | Yes | All uploads experienced 10s+ latency or timeout |
| Duration Per Event | ~8 hours until fix deployed |
| Frequency | Continuous during peak traffic |
| Detectability | Good | CPU alerts fired immediately |
| Root Cause Complexity | Medium | ReDoS from nested quantifiers in regex |
| Fix Complexity | Low | Add backtracking limit, input validation, regex timeout |
| Blast Radius | Global | All regions served by affected service |

## System Architecture

```
                         ┌──────────────────────┐
                         │   User Uploads        │
                         │   (Text, Image, Video) │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   CDN / Load Balancer  │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Content Moderation   │
                         │   API Gateway          │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Regex Evaluation     │ ◄── HIGH CPU / ReDoS
                         │   Engine (JVM)         │
                         │   - 200 threads/node   │
                         │   - 500 nodes global   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Policy Rules DB     │
                         │   (Regex patterns)    │
                         └──────────────────────┘
```

## Regex Pattern (The Vulnerability)

The vulnerable regex pattern was designed to detect a specific type of policy violation. It used nested quantifiers and alternation constructs that caused catastrophic backtracking on certain inputs:

```
Pattern: ^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])((?=.*[a-z])|(?=.*upper_seq))(?=.*(.)\\1{2,}).{8,40}$
```

The critical part causing the ReDoS was: `((?=.*[a-z])|(?=.*upper_seq))` combined with the backtracking within the overall pattern on longer inputs.

Simplified vulnerable pattern used in the lab:
```
(a|aa|aaa|aaaa)+b
```

When evaluated against input "aaaaaaaaac", the regex engine tries:
1. First a, second a, third a, ... → fails on 'c'
2. Backtracks: tries first a, then aa (as one group), then rest... → fails
3. Exponential permutations of the alternation groups

## Learning Objectives

1. Identify ReDoS vulnerabilities in regex patterns
2. Use async-profiler to find hot methods and CPU bottlenecks
3. Use JFR for identifying thread hotspots
4. Analyze CPU flame graphs to identify the offending code
5. Fix regex patterns to avoid catastrophic backtracking
6. Implement input validation length limits
7. Configure regex timeouts using ThreadLocal or custom Pattern classes
8. Set up string deduplication pooling to reduce GC pressure

## References

- Meta Engineering: "Fighting ReDoS in Production" — Meta Engineering Blog
- Google: "ReDoS: Regular Expression Denial of Service" — Google Project Zero
- OWASP: "Regular Expression Denial of Service (ReDoS)" — (link removed)
- Cloudflare: "How to Prevent ReDoS Attacks" — Cloudflare Blog
- Oracle: "java.util.regex Performance" — Oracle Documentation
- Baeldung: "Guide to java.util.regex Pattern" — https://www.baeldung.com/regular-expressions-java
- Netflix: "Applying Async-Profiler to Production" — Netflix Tech Blog
- Stack Overflow: "Catastrophic Backtracking in Regex" — RexEgg.com
- JDK 9+: "java.util.regex.Pattern improvements" — JDK Release Notes

## Prerequisites

- Java 11+ runtime
- async-profiler (https://github.com/async-profiler/async-profiler)
- JDK Mission Control for JFR analysis
- Basic understanding of regex engine internals (NFA, DFA, backtracking)
- Understanding of catastrophic backtracking concept

## Exercises

1. Identify the ReDoS-vulnerable regex pattern in the codebase
2. Generate inputs that trigger catastrophic backtracking
3. Use async-profiler to generate a CPU flame graph during the attack
4. Analyze the flame graph to identify the hot methods (Pattern$GroupHead, Pattern$Curly)
5. Fix the regex by reducing backtracking (atomic groups, possessive quantifiers)
6. Add input length validation to reject oversized inputs
7. Implement a regex timeout using a custom Pattern with interrupted thread
8. Test the fix by running the attack payload against the patched code

## Technical Deep Dive: Java Regex Engine Internals

### NFA vs. DFA: Why Java's Engine Can Be Exploited

Java's java.util.regex uses an NFA (Nondeterministic Finite Automaton) engine with backtracking. This design choice prioritizes:

1. **Feature support**: NFA engines support advanced features like backreferences, lookahead/lookbehind, and atomic groups
2. **Simplicity**: The implementation is straightforward and fits within the JDK's codebase
3. **Backward compatibility**: The NFA behavior has been consistent since Java 1.4

The trade-off is worst-case exponential time complexity. An NFA engine must try every possible path through the pattern. With nested quantifiers like `(a|aa|aaa|aaaa)+`, the number of paths grows exponentially with input length.

A DFA (Deterministic Finite Automaton) engine processes each input character exactly once, guaranteeing O(n) time. However, DFA engines do not support backreferences, lookahead/lookbehind, or capturing groups. Google's RE2 library is a DFA-based alternative.

### Catastrophic Backtracking Explained

For the pattern `(a|aa|aaa|aaaa)+b` and input "aaaaaaaaac" (10 'a' characters plus 'c'):

The engine tries to match the group `(a|aa|aaa|aaaa)` one or more times, followed by 'b'. Since the input is 'c', not 'b', the engine must backtrack:

- Path exploration tree (simplified):
  ```
  Level 1: a | aa | aaa | aaaa            (4 choices)
  Level 2: a | aa | aaa | aaaa            (4 choices)  
  Level 3: a | aa | aaa | aaaa            (4 choices)
  ...
  ```

For n characters, the number of paths is approximately O(4^(n/4)) — exponential growth.

### How Atomic Groups Prevent This

`(?>a|aa|aaa|aaaa)+b` — the atomic group `(?>...)` tells the engine: "once you match this group, never backtrack into it." If the group matches "a" at position 0, the engine commits to that match and never tries "aa" or "aaa" even if the overall pattern fails later. This reduces complexity from O(4^(n/4)) to O(n).

### Why CPU Spikes Look Like This

When a thread enters catastrophic backtracking:

1. CPU usage jumps to 100% for that thread (no I/O, no waiting, pure computation)
2. The thread stays in RUNNABLE state (not BLOCKED, not WAITING)
3. No GC activity (regex evaluation does not allocate much)
4. Other threads are unaffected until thread pool saturates
5. Once thread pool saturates, latency spikes for all requests

### Regex Patterns Known to Cause ReDoS

| Pattern | Risk | Input Trigger | Fix |
|---------|------|---------------|-----|
| `(a+)+b` | CRITICAL | 20+ 'a's + mismatch | `(?>a+)+b` or `a+b` |
| `(a\|aa)+b` | HIGH | 15+ 'a's | `(?>a\|aa)+b` |
| `(\d+\| \d+)+$` | HIGH | Repeated numbers | `(?>[\d ]+)+$` |
| `(.\|..\|...)+` | MEDIUM | Long repeated chars | `(?>...)+` |
| `(\w+\s*)+` | MEDIUM | Long text | `(?>[\\w ]+)+` |
| `x*(x+\|y)+` | HIGH | Many 'x's | Atomic group needed |
| `(a\|aa)+\*b` | HIGH | Many 'a's | Refactor pattern |

### Flame Graph Analysis

When profiling a ReDoS attack with async-profiler:

```
Pattern$GroupHead.match   35.2%
  └─ Pattern$Branch.match 28.1%
      └─ Pattern$GroupTail.match 12.4%
          └─ Pattern$Curly.match 10.3%
              └─ Pattern$BitClass.match 5.1%
                  └─ Pattern$Single.match 3.8%
```

The flame graph should show:
- 85%+ of samples in java.util.regex.* methods
- Deep call stacks (many levels of GroupHead/Branch recursion)
- No other significant CPU consumers (GC, I/O, application code)

This is the classic signature of a ReDoS attack.

## Real-World ReDoS Incidents

| Company | Year | Impact | Pattern |
|---------|------|--------|---------|
| Stack Overflow | 2016 | Site down for 30+ minutes | `(a+)+` variant |
| Cloudflare | 2019 | Global outage, CPU 100% | `(?:.*=.*)+` in WAF rules |
| GitHub | 2020 | Enterprise outage | Email validation regex |
| Meta | 2024 | Content moderation latency spike | Nested lookahead + alternation |

## Defense Strategy Summary

| Layer | Defense | Implementation | Detection Method |
|-------|---------|----------------|------------------|
| 1 | Input validation | Max length 1024 chars, reject repeated chars | Request validation filter |
| 2 | Regex timeout | TimeoutPattern wrapper with 100ms limit | TimeoutException log |
| 3 | Atomic groups | Rewrite (?\>...) patterns | Code review + linter |
| 4 | Rate limiting | Per-IP rate limit on content submission | API gateway metrics |
| 5 | Thread pool monitoring | Active thread count, blocking queue depth | HikariCP + JMX |
| 6 | CPU profiling | async-profiler for on-demand flame graphs | Scheduled flame graph capture |

## Related Tools and Libraries

| Tool | Purpose | Recommendation |
|------|---------|----------------|
| RE2/J | DFA-based regex engine (no ReDoS) | Consider for new services |
| regex-validate | ReDoS vulnerability scanner | Integrate in CI/CD |
| rxxr2 | Regex fuzzing tool | Use during regex development |
| safe-regex | Node.js ReDoS checker | For cross-platform teams |
| VulnRegexDetector | Pattern-based ReDoS detection | CI/CD integration |

## Investigation Case Study: Step-by-Step

### Step 1: Identify the Problem
The PagerDuty alert showed CPU > 95% across 500 nodes. The on-call engineer checked `top` and saw all CPUs at 99% utilization. Running `top -H -p <pid>` showed all threads in RUNNABLE state, indicating computation, not I/O wait.

### Step 2: Profile the CPU
The engineer ran async-profiler:
```bash
profiler.sh -d 60 -e cpu -f flame.html <pid>
```
The flame graph showed 85% of samples in `java.util.regex.Pattern` methods, specifically `GroupHead.match` and `Branch.match`.

### Step 3: Identify the Specific Pattern
Using JFR, the engineer identified the SQL ID of the running query. The thread stacks pointed to a specific content policy rule ID. By correlating the rule ID with the codebase, the team identified policy rule #1427.

### Step 4: Verify the Vulnerability
The team extracted the pattern and tested it locally with the attack payload. Timing confirmed: 30+ seconds for a 37-character input vs. < 1ms for normal inputs.

### Step 5: Mitigate
The team disabled the pattern via feature flag. CPU dropped from 99% to 30% within 2 minutes.

### Step 6: Fix and Prevent
The pattern was rewritten with atomic groups, input validation was added, and a regex timeout wrapper was implemented. All 2,147 existing patterns were audited for ReDoS vulnerabilities.

## Interactive Investigation Exercise

Using the provided source code and test inputs, you can reproduce the ReDoS attack:

1. Compile and run the vulnerable regex evaluation engine
2. Send the attack payload to the service
3. Observe CPU spike using your operating system's process monitor
4. Run async-profiler to generate a flame graph
5. Identify the hot methods in the java.util.regex package
6. Apply the fix (atomic groups + input validation + regex timeout)
7. Verify that the attack payload no longer causes high CPU

## Practice Scenarios

### Scenario A: Identify the Vulnerable Regex
You are given a set of 10 regex patterns. Three of them have catastrophic backtracking. Using timing tests and the ReDoSScanner tool, identify which patterns are vulnerable.

Test inputs to try:
- Pattern `(a|b)+$` against "aaaaaaaaaaaaaaaaaaaaaaaaaac"
- Pattern `(\w+\s*)+$` against "word1 word2 word3 word4 " + "x" × 30
- Pattern `(x+x+)+y` against "xxxxxxxxxxxxxxy"

### Scenario B: Fix Without Changing the Pattern
Management requires you to keep the existing regex pattern (no rewriting allowed). Implement defenses using input length validation and regex timeout only. Demonstrate that the same attack payload no longer causes high CPU.

### Scenario C: Build a ReDoS Scanner
Using the ReDoSScanner code from SOLUTION.md as a starting point, extend it to:
1. Accept a directory of regex pattern files
2. Test each pattern against 10 known ReDoS inputs
3. Report patterns that take > 100ms to evaluate
4. Suggest fixes (atomic groups, possessive quantifiers)

## Flame Graph Interpretation Guide

### Normal Flame Graph
```
____________________________________________
|  java.lang.Thread.run                     |
|    com.example.service.processRequest     |
|      com.example.service.validateInput    |
|        java.util.regex.Pattern.matcher    |  ← < 5% of samples
|          java.util.regex.Pattern$BmpChar  |
|____________________________________________|
```

### ReDoS Flame Graph
```
____________________________________________
|  java.lang.Thread.run                     |
|    java.util.regex.Pattern$GroupHead.match|  ← 35% of samples
|      java.util.regex.Pattern$Branch.match |  ← 28% of samples
|        java.util.regex.Pattern$Curly.match|  ← 10% of samples
|          java.util.regex.Pattern$Single   |  ← 5% of samples
|____________________________________________|
```

Key differences:
- Normal: flat, wide stack with low % in regex
- ReDoS: tall, narrow stack with 85%+ in regex
- Normal: quick traversal (microseconds)
- ReDoS: deep recursion (seconds)

## FAQ

### Q: What is catastrophic backtracking?
Catastrophic backtracking occurs when a regex pattern causes the NFA engine to explore an exponential number of paths before determining that a string does not match. This happens when patterns contain nested quantifiers (`(a+)+`) or overlapping alternation (`(a|aa|aaa)`). The backtracking algorithm tries every possible way to partition the input, leading to O(2^n) time complexity.

### Q: Can I use RE2/J instead of java.util.regex?
Yes, RE2/J is a DFA-based regex engine that guarantees linear-time matching and does not support backreferences or lookahead. This makes it immune to ReDoS. However, it does not support all Java regex features. Consider RE2/J for services where regex performance is critical and advanced features are not needed.

### Q: Do possessive quantifiers always prevent backtracking?
Possessive quantifiers (`*+`, `++`, `?+`) prevent the engine from giving up matched characters for backtracking. This is equivalent to wrapping the quantified group in an atomic group `(?>...)`. They prevent catastrophic backtracking when the vulnerable pattern is the quantified group itself.

### Q: What input length should I allow for regex evaluation?
For regex-heavy services, limit inputs to 256-1024 characters. The exact limit depends on your regex patterns. A 1024-character limit would have prevented the Cloudflare ReDoS incident (which used multi-kilobyte payloads) but would not have prevented this incident (37-character payload). Always combine length limits with regex timeout.

### Q: How do I set up regex timeout in Java?
Java's Pattern class does not support timeouts. Use a custom wrapper that runs the regex in a separate thread or schedules a watchdog to interrupt the current thread. See the TimeoutPattern class in SOLUTION.md for a complete implementation.

### Q: What's the most important defense against ReDoS?
Input length validation is the cheapest and most impactful defense. Even a simple limit of 1024 characters prevents most ReDoS payloads. Combined with a regex timeout of 50-100ms, this provides strong protection against both accidental and malicious ReDoS.

## Glossary

| Term | Definition |
|------|------------|
| ReDoS | Regular Expression Denial of Service — exploiting regex backtracking to cause CPU exhaustion |
| NFA | Nondeterministic Finite Automaton — regex engine that uses backtracking (Java, Perl, PCRE) |
| DFA | Deterministic Finite Automaton — regex engine that processes each character once (RE2, grep) |
| Backtracking | The process of trying alternative paths when a partial match fails |
| Catastrophic Backtracking | Exponential-time backtracking caused by nested quantifiers or overlapping alternation |
| Atomic Group | A group `(?>...)` that prevents backtracking into the group |
| Possessive Quantifier | A quantifier `*+`, `++`, `?+` that never gives up matched characters |
| Flame Graph | A visualization of CPU usage showing hot methods as stacked rectangles |
| async-profiler | A low-overhead sampling profiler for Java that generates flame graphs |
| Thread Pool Saturation | A condition where all threads in a pool are busy, causing new tasks to queue |

## Regex Performance Testing Checklist

Before deploying any new or modified regex pattern, verify:

1. Run against 1,000 valid inputs — all must complete in < 10ms
2. Run against 100 boundary inputs (max length, edge chars) — all < 50ms
3. Run against 10 ReDoS attack payloads from OWASP list — all < 100ms
4. Run with RegexValidator utility — no warnings
5. Code review: two engineers must approve the pattern
6. Documentation: OWASP reference and performance characteristics recorded

### Regex Pattern Review Template

```markdown
## Pattern Review
- Pattern: `^[\\w.-]+@[\\w.-]+\\.\\w{2,}$`
- Purpose: Email validation in user registration
- Vulnerability scan: ✅ No ReDoS detected
- Worst-case input: 254 chars (RFC 5321 max)
- Worst-case time: 3ms
- Reviewed by: @senior-engineer
- Date: 2024-06-15
```

## Command Reference Card

```bash
# Essential commands for ReDoS investigation

# async-profiler CPU profiling
profiler.sh -d 60 -e cpu -f /tmp/flame_cpu.html <pid>

# async-profiler wall-clock profiling
profiler.sh -d 60 -e wall -f /tmp/flame_wall.html <pid>

# Thread dump to check regex activity
jstack <pid> | grep -E "Pattern|Thread.State" | sort | uniq -c

# JFR recording
jcmd <pid> JFR.start name=diagnostic settings=profile duration=120s

# Live CPU monitoring per thread
top -H -p <pid>

# Check stack traces of hot threads
jcmd <pid> Thread.print | grep -A 15 "nid=0x"
```

```bash
# Essential commands for ReDoS investigation

# async-profiler CPU profiling
profiler.sh -d 60 -e cpu -f /tmp/flame_cpu.html <pid>

# async-profiler wall-clock profiling
profiler.sh -d 60 -e wall -f /tmp/flame_wall.html <pid>

# Thread dump to check regex activity
jstack <pid> | grep -E "Pattern|Thread.State" | sort | uniq -c

# JFR recording
jcmd <pid> JFR.start name=diagnostic settings=profile duration=120s

# Live CPU monitoring per thread
top -H -p <pid>

# Check stack traces of hot threads
jcmd <pid> Thread.print | grep -A 15 "nid=0x"
```

