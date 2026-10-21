# Lab 19: Server-Sent Events (SSE)

## Overview
Server-Sent Events enable real-time, unidirectional data streaming from server to client over HTTP. Learn SSE protocol, Spring WebFlux SSE, and reactive event streams.

## Topics Covered
- SSE protocol (EventSource)
- Spring MVC SSE with SseEmitter
- Reactive SSE with WebFlux
- Event stream formatting
- Connection management
- Reconnection and event ID tracking
- Backpressure handling

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- Basic HTTP knowledge

## Getting Started
`ash
mvn spring-boot:run
# SSE endpoint: http://localhost:8080/api/events/stream
`

## Key Dependencies
`xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\19-server-sent-events "THEORY.md") @"
# Theory: Server-Sent Events

## 1. SSE Protocol

SSE is defined by the W3C and uses standard HTTP with text/event-stream content type.

### Event Stream Format
`
event: message
id: 1
data: {"text": "Hello, world!"}
retry: 3000

event: error
data: An error occurred

`

### Key Headers
- Content-Type: text/event-stream
- Cache-Control: no-cache
- Connection: keep-alive

## 2. EventSource API

Browser-side JavaScript:
`javascript
const source = new EventSource('/api/events/stream');
source.onmessage = (event) => console.log(event.data);
source.addEventListener('custom', (event) => console.log(event.data));
`

## 3. Spring SSE Support

### SseEmitter (MVC)
- Thread-per-request model
- Manages connection lifecycle
- Sends events via SseEventBuilder

### Flux<ServerSentEvent> (WebFlux)
- Reactive non-blocking
- Backpressure-aware
- Built on Reactor

## 4. Connection Lifecycle

1. Client opens EventSource
2. Server sends event stream headers
3. Server pushes events as they occur
4. Client reconnects on connection loss
5. Server sends last-event-id for replay
