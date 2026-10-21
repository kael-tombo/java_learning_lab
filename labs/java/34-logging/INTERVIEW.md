# Interview Questions: Logging

## Company-Specific Focus

### Google
- SLF4J vs Log4j 2 vs java.util.logging — choosing a logging facade
- Log levels: TRACE, DEBUG, INFO, WARN, ERROR usage conventions
- Structured logging: JSON format for machine processing

### Microsoft
- Java logging vs .NET logging: log4j vs NLog/serilog
- Application Insights integration from Java
- Correlation IDs for distributed tracing in Azure

### Amazon
- Log aggregation in the cloud: sending logs to CloudWatch
- Async logging: preventing IO from blocking the application
- MDC (Mapped Diagnostic Context) for request-scoped context

### Meta
- Performance cost of logging at scale: string formatting and GC
- Log rotation: preventing disk full scenarios
- Avoid logging sensitive data: PII scrubbing

### Apple
- Unified logging on macOS
- Using System.Logger since Java 9
- Testing framework integration

### Oracle
- java.util.logging overview (JUL)
- The LogManager and configuration
- Integration: how JUL connects to SLF4J via jul-to-slf4j bridge
- System.Logger since Java 9

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (Logging patterns are applied to all production problems - no direct LC mappings) |
| 355 Design Twitter | Medium | Amazon, Google | Event log design pattern |

## Real Production Scenarios
- **Log4Shell (CVE-2021-44228)**: Log4j JNDI injection — a security disaster caused by a logging library
- **Amazon**: async appender losing logs during an outage — the buffer was too small
- **Netflix**: Logging in a critical path caused P99 latency increase due to string formatting

## Interview Patterns & Tips
- **Use SLF4J**: Parameterized logging {} avoids string creation if log level is disabled
- **Avoid string concat**: `log.debug("user " + id + " login")` — always creates strings. Use `log.debug("user {} login", id)`
- **Don't log sensitive data**: PII, passwords, tokens — use a filter if needed
- **Log context**: Add correlation ID to every log line for distributed debugging

## Deep Dive Questions
- **JVM**: How does the logging framework interact with the JVM when writing to disk?
- **Async logging**: How is the disruptor pattern used by log4j2 for high throughput?
- **Memory**: How does logging large strings affect GC?
- **Performance**: What is the cost of a single log.debug() call when disabled?
- **JUL vs Log4j vs SLF4J**: How do these frameworks interface with each other?