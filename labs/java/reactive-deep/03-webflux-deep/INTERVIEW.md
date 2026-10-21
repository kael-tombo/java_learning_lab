# Interview Questions: WebFlux Deep Dive

## Company-Specific Focus

### Google
- WebFlux: reactive web framework from Spring
- @RestController: reactive controllers return Mono/Flux
- Spring WebFlux vs Spring MVC: non-blocking vs blocking

### Microsoft
- WebFlux vs .NET ASP.NET Core: both support reactive programming
- Functional endpoints: RouterFunctions for functional routing

### Amazon
- Non-blocking I/O: WebFlux handles more concurrent requests with fewer threads
- Netty: default embedded server for WebFlux
- Reactive MongoDB: reactive database access with WebFlux

### Meta
- WebClient: reactive HTTP client
- Server-Sent Events: returning Flux for SSE
- WebSocket: reactive WebSocket handler

### Apple
- Error handling: @ExceptionHandler in reactive controllers
- Validation: @Valid with reactive validation
- Security: Spring Security Reactive

### Oracle
- Spring WebFlux is part of the Spring Framework 5+
- Reactor Netty: underlying reactive networking layer
- Spring Data Reactive: reactive database support

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — WebFlux is a web framework) |

## Real Production Scenarios
- **Netflix**: WebFlux with Netty improved API gateway throughput by 200% over Spring MVC
- **LinkedIn**: WebFlux for real-time analytics dashboard with Server-Sent Events

## Interview Patterns & Tips
- **Reactive stack**: WebFlux works on the reactive stack with Netty
- **Non-blocking**: all operations are non-blocking and asynchronous
- **WebClient**: use WebClient instead of RestTemplate in reactive applications
- **Functional endpoints**: alternative to annotation-based controllers

## Deep Dive Questions
- **WebFlux vs MVC**: How does the reactive stack differ from the servlet stack?
- **Netty integration**: How does WebFlux work with Netty?
- **Request handling**: How does WebFlux process an HTTP request reactively?
- **Reactive security**: How does Spring Security integrate with WebFlux?
- **Reactive data**: How does reactive MongoDB/Redis work with WebFlux?