# Interview Questions: HTTP Clients

## Company-Specific Focus

### Google
- Java 11 HttpClient: modern replacement for HttpURLConnection
- HTTP/1.1 and HTTP/2: built-in HTTP/2 support
- WebSocket: built-in WebSocket client support

### Microsoft
- HttpClient vs .NET HttpClient: comparable design
- HTTP/2 multiplexing: performance benefits

### Amazon
- REST API consumption: HttpClient for calling REST services
- Connection pooling: keep-alive connections for efficiency
- Retry logic: implementing retry with circuit breaker pattern

### Meta
- Asynchronous: HttpClient.sendAsync() for non-blocking requests
- BodyHandlers: handling response bodies (String, InputStream, File)
- Timeouts: connect timeout, request timeout

### Apple
- HTTP/2: multiplexing over a single connection
- SSL/TLS: HTTPS with built-in TLS support
- Redirects: following HTTP redirects

### Oracle
- java.net.http.HttpClient (JDK 11+)
- HttpRequest: building HTTP requests
- HttpResponse: handling HTTP responses
- HTTP/2 and WebSocket support built-in

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — HTTP clients are networking APIs) |

## Real Production Scenarios
- **Netflix**: Java 11 HttpClient reduced connection overhead by 40% over HttpURLConnection
- **Uber**: HttpClient timeouts prevented cascading failures in microservice calls

## Interview Patterns & Tips
- **HttpClient is immutable**: one instance can be reused
- **send() vs sendAsync()**: blocking vs non-blocking
- **BodyHandlers**: ofString(), ofInputStream(), ofFile()
- **HTTP/2**: built-in, no additional dependencies

## Deep Dive Questions
- **HttpClient internals**: How does HttpClient manage connections?
- **HTTP/2**: How does HTTP/2 multiplexing work?
- **sendAsync**: How does HttpClient implement non-blocking requests?
- **BodyHandler**: How are response bodies handled?
- **Build pattern**: How does HttpRequest use the builder pattern?