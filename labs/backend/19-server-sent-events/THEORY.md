# Theory: Server-Sent Events (SSE)

## What SSE Is

Server-Sent Events are a unidirectional, HTTP-based push channel: the client
opens a long-lived `GET` and the server streams `text/event-stream` responses.
Unlike WebSocket, the connection is plain HTTP, so it survives HTTP proxies,
works through standard server stacks, and gets automatic reconnection for free
via the browser's `EventSource` API. SSE carries only UTF-8 text (framed as
`data:` lines); binary must be base64-encoded.

## The Wire Format

Each event block is a group of `field: value` lines separated by a blank line:

```
id: 1042
event: order-update
retry: 3000
data: {"orderId":"A-17","status":"SHIPPED"}

```

- `data:` is the payload; multiple `data:` lines in one block join with `\n`.
- `id:` becomes `lastEventId`; on reconnect the browser sends it back as the
  `Last-Event-ID` header, letting the server resume where it left off.
- `event:` names the channel; the client adds a listener per name
  (`addEventListener("order-update")`), while nameless events fire `onmessage`.
- `retry:` overrides the reconnection delay in milliseconds.

## Reconnection Semantics

When the connection drops, the browser waits `retry` ms (default ~3 s) and
re-requests with `Last-Event-ID`. If the server replies 204, the browser stops
retrying — the standard way to tell clients "this stream is done." A 404 makes
the browser retry forever on some engines. Servers must be able to answer
"give me everything after id X," which implies either an in-memory ring
buffer or a durable event log behind the stream.

## Operational Realities

- **Proxy buffering**: nginx and many load balancers buffer upstream responses.
  Without `X-Accel-Buffering: no` (nginx) and gzip disabled for the stream,
  events arrive in multi-second batches and feel broken.
- **Connection limits**: HTTP/1.1 browsers cap ~6 connections per origin, and
  EventSource holds one. A dashboard with several tabs can starve normal
  fetches. HTTP/2 multiplexing removes the cap.
- **Heartbeats**: idle proxies kill silent connections after ~60 s. Servers send
  a comment heartbeat (`: ping\n\n`) every ~15–30 s; comments are ignored by
  EventSource but keep the TCP path alive.
- **Backpressure**: if a slow client doesn't drain its buffer, you either
  block (eating a thread per client), buffer unboundedly (OOM), or drop and
  resync. Reactive stacks (`Flux`) make the drop/resync choice explicit.

## When SSE vs WebSocket

Use SSE when data flows server→client and requests are occasional (dashboards,
notifications, agent-token streaming, progress bars). Use WebSocket for true
bidirectional traffic (chat, collaborative editing, game state). SSE's silent
killer is reconnection correctness: if the server cannot honor
`Last-Event-ID`, a user spanning a network blip sees duplicate or missing
events.

## Failure Modes in Production

- Client reconnect storms after a deploy: thousands of clients haven't yet
  received a `retry`, they reconnect in a synchronized wave; fix by sending
  jittered `retry` and honoring `Last-Event-ID` so resume is cheap.
- Sticky sessions missing: the reconnect lands on a different replica that has
  no session state; requires either shared event log (Redis Streams,
  Kafka) or sticky routing.
- Auth tokens expiring mid-stream: EventSource cannot set headers on its
  auto-reconnect, so token rotation requires `withCredentials` cookie auth or
  a manual reconnect wrapper.

## References

- WHATWG HTML Standard, "Server-sent events"
- Spring Framework `SseEmitter` / `WebFlux` SSE documentation
