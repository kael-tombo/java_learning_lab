# Prevention: Avoiding ReDoS and High CPU Incidents

**Incident**: INC-2024-0610-REDOS
**Category**: Regular Expression Security / Performance
**Applies To**: All services using Java regex for input processing

## Prevention Strategies

### 1. Regex Pattern Review Standards

Every regex pattern added to the codebase must pass the following review:

| Check | Description | Action |
|-------|-------------|--------|
| Nested quantifiers | `(a+)+`, `(b*)*`, `(c+)+$` | Refactor to atomic group |
| Alternation with overlap | `(a\|aa\|aaa)` where branches overlap | Use possessive quantifier `++` |
| Lookaround nesting | `(?=.*(.)\1{2,})` with other groups | Test with ReDoS scanner |
| Long repetition | `.{8,40}` on long inputs | Limit input length |
| Capturing groups | Too many groups causing GC pressure | Use non-capturing `(?:...)` |

### 2. Regex Testing in CI/CD

Add automated ReDoS scanning to the CI/CD pipeline:

```yaml
# .github/workflows/redos-scan.yml
steps:
  - name: Scan regex patterns for ReDoS
    run: |
      java com.meta.moderation.ReDoSScanner \
        --scan-dir src/main/resources/regex-patterns/
      timeout: 30s
```

### 3. Input Validation Standards

| Rule | Value | Rationale |
|------|-------|-----------|
| Max input length | 1024 characters | Prevents large payloads from reaching regex engine |
| Max regex input | 256 characters | Even stricter for regex-heavy rules |
| Character limits | Block repeated chars > 10 consecutive | Common ReDoS pattern |
| Unicode normalization | NFC form | Prevents normalization ReDoS |
| Null bytes | Reject \0 | Prevents regex engine edge cases |

### 4. Java Regex Best Practices

#### Do: Use Possessive Quantifiers

```java
// Instead of: (a|aa|aaa|aaaa)+b
// Use:       (a|aa|aaa|aaaa)++b
// The ++ possessive quantifier prevents backtracking into the group
Pattern safePattern = Pattern.compile("(a|aa|aaa|aaaa)++b");
```

#### Do: Use Atomic Groups

```java
// Instead of: (a|b)+c
// Use:       (?>a|b)+c
// Atomic group (?>...) prevents all backtracking into the group
Pattern safePattern = Pattern.compile("(?>a|b)+c");
```

#### Do: Use Non-Capturing Groups

```java
// Instead of: (a|b|c)
// Use:       (?:a|b|c)
// Non-capturing groups reduce memory and GC pressure
Pattern efficientPattern = Pattern.compile("(?:a|b|c)+");
```

#### Do NOT: Nest Quantifiers

```java
// BAD — exponential backtracking:
Pattern bad = Pattern.compile("(a+)+b");

// GOOD — possessive quantifier:
Pattern good = Pattern.compile("(?:a+)++b");
// OR — use a simpler pattern:
Pattern good2 = Pattern.compile("a+b");
```

### 5. Regex Execution Timeout

Configure timeouts for ALL regex evaluations in production:

```java
// Application-wide regex timeout configuration
public class RegexConfig {
    // Standard timeout for most patterns
    public static final long DEFAULT_TIMEOUT_MS = 50L;

    // Strict timeout for patterns that process user input
    public static final long USER_INPUT_TIMEOUT_MS = 100L;

    // Generous timeout for complex but known-safe patterns
    public static final long COMPLEX_TIMEOUT_MS = 500L;

    // Configurable via feature flag
    public static long getTimeout(String patternId) {
        return FeatureFlag.get("regex_timeout_" + patternId, DEFAULT_TIMEOUT_MS);
    }
}
```

### 6. Monitoring: Regex Execution Time

Add regex execution time to application metrics:

```java
// Micrometer / Prometheus timer for regex evaluation
Timer regexTimer = Timer.builder("regex.evaluation.time")
    .description("Regex evaluation time in milliseconds")
    .tag("pattern_id", patternId)
    .register(meterRegistry);

Timer.Sample sample = Timer.start();
try {
    return pattern.matcher(input).matches();
} finally {
    sample.stop(regexTimer);
}
```

### 7. ReDoS Pattern Database

Maintain a database of known ReDoS-vulnerable patterns:

| Pattern | Risk Level | Input Trigger | Fix |
|---------|------------|---------------|-----|
| `(a\|aa\|aaa\|aaaa)+` | HIGH | "aaaa...aX" | Atomic group `(?>...)` |
| `(.\|..\|...)+` | HIGH | Repeated chars | Possessive `++` |
| `(a+)+b` | CRITICAL | "aaaa...X" | `(?:a+)++b` |
| `(\d+\| \d+)+$` | HIGH | Number string | Atomic group |
| `(.*,.*)+` | MEDIUM | CSV-like input | Simplify pattern |

### 8. Education and Training

| Topic | Audience | Frequency |
|-------|----------|-----------|
| Regex engine internals (NFA vs DFA) | All developers | Onboarding |
| Catastrophic backtracking workshop | All developers | Annually |
| ReDoS attack simulation | Security team | Quarterly |
| Atomic groups / possessive quantifiers | All developers | Onboarding |
| Regex performance profiling | Platform team | Annually |

### 9. Regex Linter Rules

Add automated linting to detect problematic regex patterns:

```java
// Checkstyle rule: flag patterns with nested quantifiers
// Pattern: (a+)+, (b*)*, (c+)*, etc.
public class NestedQuantifierCheck extends AbstractRegexCheck {
    private static final Pattern NESTED_QUANTIFIER =
        Pattern.compile("\\([^)]*[+*][^)]*\\)[+*]");

    @Override
    public void visitLiteralString(String literal) {
        if (NESTED_QUANTIFIER.matcher(literal).find()) {
            log(literal.getLineNo(), "Nested quantifier detected: " +
                "potential ReDoS vulnerability. Use atomic group (?>...)");
        }
    }
}
```

### 10. Incident Response Playbook for ReDoS

When a ReDoS attack is suspected:

1. **Detect**: CPU spike + threads in java.util.regex methods
2. **Confirm**: Run async-profiler flame graph
3. **Identify**: Extract the vulnerable pattern from thread stacks
4. **Mitigate**: Disable the pattern via feature flag
5. **Analyze**: Reproduce locally with the identified pattern and input
6. **Fix**: Rewrite with atomic groups / possessive quantifiers
7. **Deploy**: Deploy fix, re-enable pattern, verify CPU normal

### 11. Performance Testing Requirements

All regex patterns must pass performance tests:

```java
@Test
void regexShouldNotBacktrackCatastrophically() {
    String[] testInputs = {
        generateLongString('a', 10) + "X",
        generateLongString('a', 20) + "X",
        generateLongString('a', 30) + "X",
        generateLongString('a', 40) + "X",
    };

    for (String input : testInputs) {
        long start = System.nanoTime();
        pattern.matcher(input).matches();
        long duration = TimeUnit.NANOSECONDS.toMillis(
            System.nanoTime() - start);
        assertTrue(duration < 100,
            "Pattern took " + duration + "ms for input length " +
            input.length());
    }
}
```

### 11. Documentation Standards

All regex patterns must include documentation comments:
```java
// Pattern: accounts for OWASP email validation rules
// Vulnerability: verified against OWASP ReDoS list
// Performance: 100% of valid inputs complete in < 10ms
// Worst-case: Input of 100 chars completes in < 50ms
private static final Pattern EMAIL_PATTERN =
    Pattern.compile("^[\\w.-]+@[\\w.-]+\\.\\w{2,}$");
```

### 12. Performance Testing Requirements

All regex patterns must pass performance tests:
```java
@Test
void regexShouldNotBacktrackCatastrophically() {
    String[] inputs = {
        generateString('a', 10) + "X",
        generateString('a', 20) + "X",
        generateString('a', 30) + "X",
        generateString('a', 40) + "X",
    };
    for (String input : inputs) {
        long start = System.nanoTime();
        pattern.matcher(input).matches();
        long duration = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start);
        assertTrue(duration < 100,
            "Pattern took " + duration + "ms for input length " + input.length());
    }
}
```

### 13. Security Team Integration

Security team should:
- Regularly scan codebase for known ReDoS patterns
- Run regex fuzzing tools against policy rules
- Maintain a database of known ReDoS payloads
- Conduct penetration testing with ReDoS attack vectors
- Review all regex patterns before deployment to production

## References

- OWASP: "ReDoS Prevention Cheat Sheet" — (link removed)
- RexEgg: "Catastrophic Backtracking" — https://www.regular-expressions.info/catastrophic.html
- Stack Overflow: "Regex: Make possessive quantifier default" — RexEgg.com
- Java Documentation: "java.util.regex Pattern — Possessive Quantifiers" — Oracle
- SonarQube: "Regular expressions should not be vulnerable to ReDoS attacks" — RSPEC-5843
- GitHub Advisory: "ReDoS in Java patterns" — GitHub Security Lab
- Cloudflare: "How to Mitigate ReDoS Attacks" — Cloudflare Blog
- Google: "RE2: A DFA-based regex engine" — Google Open Source

