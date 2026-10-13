# HTTP Clients (Java 11+) — Theoretical Foundation

## Core Concept

`java.net.http.HttpClient` (standard since 11) is the JDK's built-in HTTP/1.1
+ HTTP/2 client: immutable client (executor, proxy, auth, redirects,
timeouts configured once via builder), immutable `HttpRequest`s, and
pluggable `BodyHandler`s. One client instance serves the whole application
(it pools connections internally); requests are cheap value objects.

## Sync, Async, and Body Shapes

```java
HttpClient client = HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(5))
    .followRedirects(HttpClient.Redirect.NORMAL)
    .build();
HttpRequest req = HttpRequest.newBuilder(URI.create("https://example.com"))
    .timeout(Duration.ofSeconds(10))
    .GET().build();

// blocking
HttpResponse<String> r = client.send(req, HttpResponse.BodyHandlers.ofString());
// non-blocking
CompletableFuture<HttpResponse<String>> f =
    client.sendAsync(req, HttpResponse.BodyHandlers.ofString());
```

Two timeouts, two jobs: `connectTimeout` (TCP+TLS establishment, on the
client) vs per-request `timeout` (whole exchange). Body handlers
(`ofString`, `ofByteArray`, `ofFile`, `ofInputStream`, `discarding`)
decide where response bytes land — `ofString` on a gigabyte download is
the classic OOM, `ofFile`/`ofInputStream` the fix.

## HTTP/2 Behavior Worth Knowing

- Version is negotiated (ALPN over TLS; cleartext `h2c` needs explicit
  `.version(HTTP_2)` plus server support) — inspect
  `response.version()` rather than assuming.
- Multiplexing is per-client-connection: concurrent `sendAsync` calls share
  connections instead of opening one TCP stream each (the performance story
  vs `HttpURLConnection`).
- `HttpClient` is threadsafe and connection-pooling; creating one per
  request leaks pools and defeats multiplexing.

## Key Invariants

1. One shared `HttpClient`; many cheap requests.
2. Always set both timeouts (connect + request).
3. Match the body handler to the payload size.
4. `send` blocks the caller; `sendAsync` returns a `CompletableFuture`
   with identical completion semantics (status + body or exception).
5. Check `response.statusCode()` before parsing bodies — 4xx/5xx still
   complete normally.
