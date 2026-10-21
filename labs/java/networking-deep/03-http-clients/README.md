# HTTP Clients (Java 11+)

The JDK's built-in HTTP/1.1 + HTTP/2 client: one shared immutable
`HttpClient` (pooling + multiplexing inside), cheap `HttpRequest` values,
and body handlers matched to payload size.

## What this lab covers

- **One client, many requests**: builder configuration (executor, proxy,
  redirects) done once; requests as throwaway values
- **Two timeouts, two jobs**: connect timeout vs per-request timeout
- **Sync vs async**: blocking `send` vs `CompletableFuture` `sendAsync`
  (identical completion semantics)
- **Body handlers**: `ofString`/`ofByteArray` for small payloads,
  `ofFile`/`ofInputStream` for large ones; status codes before parsing

## Lab contents

THEORY.md builds the model (client → request → handler → version);
CODE_DEEP_DIVE.md walks sync/async calls; EXERCISES.md drills timeouts and
handlers; QUIZ.md and FLASHCARDS.md lock in the invariants (shared client,
both timeouts, handler sizing, status-first parsing).

## Prerequisites

Java 17+, HTTP fundamentals (methods, status codes, headers), lambda and
`CompletableFuture` basics.
