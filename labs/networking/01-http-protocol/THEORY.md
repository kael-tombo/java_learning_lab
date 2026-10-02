# HTTP Protocol - THEORY

## Overview

This document covers HTTP concepts with Java implementation examples.

## Content

Detailed content for HTTP Protocol networking lab.

## Topics Covered

- Core concepts and theory
- Java implementation patterns
- Best practices and common pitfalls
- Performance considerations
- Security aspects

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 9112: HTTP/1.1 (STD 99, Internet Standard) — 2022, obsoletes portions of RFC 7230 — https://www.rfc-editor.org/info/rfc9112/ — Takeaway tied to lab: model the message-syntax exercise on §2.1 (start-line + CRLF + headers + empty line + optional body) and §3 request-line; enforce mandatory Host header and 400 on missing/duplicate Host (§3.2).
- RFC 9112 §6 Message Body / Framing — 2022 — https://www.rfc-editor.org/info/rfc9112/ — Takeaway tied to lab: use Transfer-Encoding vs Content-Length precedence (§6.3) and the must-close-on-both rule in the Java socket framing exercise to explain request-smuggling pitfalls.
- Hypertext Transfer Protocol specifications index (httpwg.org) — living index (accessed Oct 2026) — https://httpwg.org/specs/ — Takeaway tied to lab: use as map from HTTP/1.1 (RFC 9112) to semantics/caching when extending the lab toward persistent connections and intermediaries.
- MDN HTTP resources and specifications — living reference (accessed Oct 2026) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Resources_and_specifications — Takeaway tied to lab: cross-check status-code/method semantics against RFC 9110/9112 while writing Java client/server assertions.
