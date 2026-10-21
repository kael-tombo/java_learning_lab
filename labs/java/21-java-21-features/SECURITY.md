# Security Considerations for Java 21 Features

## Virtual Threads Security

### Thread Safety in Virtual Threads
Virtual threads share the same memory visibility guarantees as platform threads. The Java Memory Model applies equally. However, because virtual threads encourage writing synchronous code at scale, developers may inadvertently introduce shared mutable state:

```java
// UNSAFE: Shared mutable state in virtual threads
private int requestCounter = 0;

public void handleRequest() {
    requestCounter++;  // Race condition! Not atomic
}

// SAFE: Use atomic primitives or synchronization
private final AtomicInteger requestCounter = new AtomicInteger(0);

public void handleRequest() {
    requestCounter.incrementAndGet();  // Thread-safe
}
```

### Denial of Service via Virtual Thread Exhaustion
While virtual threads are lightweight, they still consume heap memory (~200 bytes each). An attacker who can trigger a large number of concurrent requests could exhaust heap memory:

```java
// Mitigation: Limit concurrent virtual threads with a semaphore
private final Semaphore concurrencyLimit = new Semaphore(10_000);

public void handleRequest() {
    if (!concurrencyLimit.tryAcquire(5, TimeUnit.SECONDS)) {
        throw new TooManyRequestsException();
    }
    try {
        // Process with virtual thread
    } finally {
        concurrencyLimit.release();
    }
}
```

### SecurityManager Interaction
Virtual threads inherit the security context of their parent. This is important when using `AccessController.doPrivileged` or `SecurityManager` (deprecated but still used in some environments).

## Pattern Matching Security

### Exhaustiveness and Auditing
Exhaustive pattern matching on sealed types provides compile-time guarantees that all cases are handled. This is a security feature: it prevents cases where a new subtype is added but the switch statement isn't updated, which could lead to unexpected behavior (e.g., returning sensitive data through a default case that should never be reached).

```java
// Audit requirement: All document types must be explicitly handled
sealed interface Document permits PublicDoc, ConfidentialDoc, SecretDoc {}

String process(Document doc) {
    return switch (doc) {
        case PublicDoc d -> d.content();  // Safe to return
        case ConfidentialDoc d -> d.redacted();  // Redact sensitive parts
        case SecretDoc d -> "ACCESS DENIED";  // Never expose
        // No default: compiler ensures all types are covered
    };
}
```

## String Templates Security

> **Status**: String Templates (JEP 430/459) were previewed in JDK 21/22 and withdrawn before JDK 23. They are not available in any shipping JDK today — the code below compiles on current JDKs, and the section keeps the security lessons the withdrawn preview was designed to teach.

### Injection Prevention (The Design Goal)
The withdrawn preview aimed to make interpolation safe-by-default. The lesson survives with standard APIs:

```java
// INSECURE: SQL injection via concatenation
String query = "SELECT * FROM users WHERE name = '" + userName + "'";

// SECURE: Parameterized statement keeps data out of the query structure
PreparedStatement ps = conn.prepareStatement(
    "SELECT * FROM users WHERE name = ?");
ps.setString(1, userName);
```

### Cross-Site Scripting (XSS) Prevention
```java
// Escape user-provided values before embedding them in HTML
static String escapeHtml(String raw) {
    return raw.replace("&", "&amp;").replace("<", "&lt;")
              .replace(">", "&gt;").replace("\"", "&quot;");
}

// Safe: The value is escaped, so a user cannot inject markup
String safeHtml = "<div>%s</div>".formatted(escapeHtml(userInput));
```

### Expression vs. Value Injection
The historical preview also carried a subtle rule worth remembering: if attackers can control the *embedded expressions* themselves, they can inject arbitrary code. User-supplied text must never be allowed to become template (or query) structure — only user *values* should flow into interpolation:

```java
// JavaScript-style danger (not compilable Java): user-chosen expressions
// injected into code text is exactly what template attacks exploit in
// languages that interpolate at runtime.

// SAFE in Java: user input is only ever a value passed to a parameter
String userName = getUserInput();
String result = "Hello %s".formatted(escapeHtml(userName));
```

The same distinction applies outside the (withdrawn) preview world: `String.formatted` evaluates only the arguments you hand it, and `PreparedStatement` binds only values — so a user can influence data, never structure.

## Structured Concurrency Security

### Task Isolation
Structured concurrency enforces task boundaries. If one subtask is compromised, it cannot affect others through shared scope-specific resources:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> untrusted = scope.fork(() -> untrustedService.call());
    Future<String> trusted = scope.fork(() -> trustedService.call());
    
    scope.join();
    scope.throwIfFailed();
    
    // Even if untrustedService throws, trustedService's result
    // is available (if it already completed)
    return trusted.resultNow();
}
```

### Resource Exhaustion Mitigation
Structured concurrency ensures that if a parent scope is cancelled, all child tasks are cancelled, preventing resource leaks that could be exploited for DoS attacks.

## General Security Best Practices

1. **Enable the Security Manager** (until removed) for sandboxing untrusted code in virtual threads
2. **Use ScopedValue not ThreadLocal** for authentication tokens and security contexts
3. **Validate interpolated values** before embedding them in SQL or markup
4. **Monitor virtual thread creation** for unusual spikes that could indicate an attack
5. **Audit pattern matching exhaustiveness** in security-critical code paths
