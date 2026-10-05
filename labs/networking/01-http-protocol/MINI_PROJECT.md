# HTTP Protocol - MINI PROJECT

## Project: WireTalk — an HTTP/1.1 server and client you write by hand

No HTTP library. Raw `Socket` I/O, manual CRLF framing, status code handling, keep-alive,
and conditional requests. This is the lab that makes HTTP stop being magic.

### Architecture

```
  Client (WireTalkClient)                    Server (WireTalkServer)
  ─────────────────────                      ─────────────────────
  build request line + CRLF    ──socket──▶   read request line
  serialize headers (CRLF)     ──────────▶   read headers until blank line
  compute body framing         ──────────▶   parse Content-Length / chunked
  read status line                          route
  parse response headers                    serialize response
  honour Connection: close                  keep-alive loop
```

### Implementation

Request construction and correct framing rules:

```java
public final class HttpRequestWriter {
    /**
     * RFC 9112 framing: the message body is delimited by Content-Length, or by chunked
     * transfer coding. If BOTH are present, Transfer-Encoding wins - which is exactly the
     * ambiguity that request smuggling exploits.
     */
    public void write(OutputStream out, Request req) throws IOException {
        StringBuilder head = new StringBuilder();
        head.append(req.method()).append(' ').append(req.target()).append(" HTTP/1.1\r\n");
        // HTTP/1.1 requires Host. Multiple Host headers or a mismatch is a 400, not a shrug.
        head.append("Host: ").append(req.hostHeader()).append("\r\n");
        head.append("User-Agent: WireTalk/1.0\r\n");
        head.append("Connection: ").append(req.keepAlive() ? "keep-alive" : "close").append("\r\n");
        if (req.hasBody()) {
            head.append("Content-Type: ").append(req.contentType()).append("\r\n");
            head.append("Content-Length: ").append(req.body().length).append("\r\n");
        }
        if (req.ifNoneMatch() != null)
            head.append("If-None-Match: ").append(req.ifNoneMatch()).append("\r\n");   // conditional GET
        head.append("\r\n");                                    // blank line ENDS the header section

        out.write(head.toString().getBytes(US_ASCII));          // headers must be ASCII
        if (req.hasBody()) out.write(req.body());                // then the raw body
        out.flush();
    }
}
```

The server: read a line, read headers until blank, then frame the body:

```java
public final class HttpServer {
    void serve(Socket socket) throws IOException {
        var in = new BufferedInputStream(socket.getInputStream());
        var out = new BufferedOutputStream(socket.getOutputStream());
        boolean keepAlive = true;
        while (keepAlive) {                                    // keep-alive loop
            String requestLine = readLine(in);                 // read a CRLF-terminated line
            if (requestLine == null || requestLine.isEmpty()) break;   // client closed
            String[] parts = requestLine.split(" ");
            if (parts.length != 3 || !parts[2].equals("HTTP/1.1")) {
                respond(out, 400, "Bad Request", Map.of(), "malformed request line");
                break;
            }
            String method = parts[0], target = parts[1];

            // Read headers until the empty line. Header names are case-insensitive.
            Map<String, String> headers = readHeadersUntilBlankLine(in);
            if (!headers.containsKey("host")) {                // HTTP/1.1 mandates Host
                respond(out, 400, "Bad Request", Map.of(), "missing Host header");
                break;
            }

            byte[] body = frameBody(in, headers);              // Content-Length or chunked
            Response r = router.route(method, target, headers, body);
            boolean clientWantsClose = "close".equalsIgnoreCase(headers.getOrDefault("connection", ""));
            respond(out, r.status(), r.reason(), r.headers(), r.body());
            keepAlive = !clientWantsClose && r.keepAlive();
        }
        socket.close();
    }

    /** Chunked decoding: each chunk is a hex length line, then data, then CRLF. Terminated by 0. */
    private byte[] frameBody(InputStream in, Map<String, String> h) throws IOException {
        String te = h.get("transfer-encoding");
        if (te != null && te.toLowerCase().contains("chunked")) {
            ByteArrayOutputStream buf = new ByteArrayOutputStream();
            while (true) {
                int size = Integer.parseInt(readLine(in).trim().split(";")[0], 16);  // ignore extensions
                if (size == 0) { readLine(in); break; }
                buf.write(in.readNBytes(size));
                readLine(in);                                   // trailing CRLF after chunk data
            }
            return buf.toByteArray();
        }
        String cl = h.get("content-length");
        // No Transfer-Encoding and no Content-Length => body is empty for a request.
        return cl == null ? new byte[0] : in.readNBytes(Integer.parseInt(cl));
    }
}
```

Status code selection, which is a correctness decision rather than a cosmetic one:

```java
Response create(String body) {
    return new Response(201, "Created",
        Map.of("Location", "/widgets/" + id, "Content-Type", "application/json"), body);
    // 201 + Location tells the client the new resource's URI, enabling a GET-after-POST
    // without the client having to construct the URL itself.
}

Response notModified(String etag) {
    return new Response(304, "Not Modified", Map.of("ETag", etag), null);
    // 304 carries no body by definition; sending one is a protocol error and wastes bandwidth.
}

Response conflict(String currentState) {
    // 409 with the current state lets a client implement optimistic concurrency properly
    // instead of guessing whether its write "probably" succeeded.
    return new Response(409, "Conflict", Map.of("Content-Type", "application/problem+json"),
            problemJson("resource modified", currentState));
}
```

### Test It

```java
@Test void parsesAWellFormedRequest() throws Exception {
    var res = client.send(new Request("GET", "/widgets/7", Map.of(), null));
    assertThat(res.status()).isEqualTo(200);
    assertThat(res.headers()).containsEntry("content-type", "application/json");
}

@Test void rejectsMissingHostHeader() throws Exception {
    assertThat(rawRequest("GET /widgets/7 HTTP/1.1\r\n\r\n")).startsWith("HTTP/1.1 400");
}

@Test void keepAliveReusesTheConnection() throws Exception {
    client.connect();
    for (int i = 0; i < 5; i++) client.send(new Request("GET", "/widgets/" + i, Map.of(), null));
    assertThat(server.connectionsAccepted()).isEqualTo(1);   // one socket, five requests
}

@Test void decodesChunkedBodies() throws Exception {
    var res = client.sendRaw("POST /echo HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: chunked\r\n\r\n"
                           + "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n");
    assertThat(res.body()).isEqualTo("hello world");
}

@Test void conditionalGetReturns304() throws Exception {
    String etag = client.send(new Request("GET", "/widgets/1", Map.of(), null)).headers().get("etag");
    var second = client.send(new Request("GET", "/widgets/1", Map.of("If-None-Match", etag), null));
    assertThat(second.status()).isEqualTo(304);
    assertThat(second.body()).isEmpty();
}
```

### Deliverables

- [ ] `HttpRequestWriter` producing a spec-correct request line and header block
- [ ] `WireTalkServer` with keep-alive, header parsing, and `Host` enforcement
- [ ] Body framing for both `Content-Length` and chunked transfer coding
- [ ] A router with 200/201/304/400/404/405/409/500 responses and correct headers
- [ ] Conditional requests via `If-None-Match` and `If-Modified-Since`
- [ ] Tests: well-formed parse, missing Host, keep-alive reuse, chunked decode, 304
- [ ] A byte-level capture of one full exchange annotated in the README
- [ ] Hop-by-hop header table explaining why a proxy must strip each one
