# Network Security Deep - THEORY

## 1. Threat modelling is a design input, not a document

A threat model answers four questions, and skipping any one of them makes the artefact
decorative:

1. **What are we building?** — the data flow diagram, including trust boundaries.
2. **What can go wrong?** — threats per boundary, not a generic list.
3. **What are we doing about it?** — a control per threat, or an accepted risk.
4. **Did we do a good job?** — verification that the control works.

The fourth question is the one almost always skipped, and it is the one that determines
whether a control is real. A segmentation policy described in a design document is a
hypothesis; a probe that fails to traverse the network is evidence.

**Trust boundaries** are where the answer to "who are you?" changes. For a service
receiving requests from a gateway: the gateway→service boundary is one; service→database
another; and if a service calls a third-party API, that egress boundary is a third. Each
boundary needs a stated control, and boundaries nobody listed are boundaries nobody is
defending.

An **explicit out-of-scope list** is what makes a threat model honest. "Physical security
of the cloud provider's data centres is out of scope" is a useful sentence; it converts an
implicit assumption into a reviewable decision.

## 2. TLS 1.3: what actually happens

The handshake, in one flight each way:

```
  Client                                             Server
    │  ClientHello: key_share, supported_versions,        │
    │  supported_groups, signature_algorithms             │
    ├────────────────────────────────────────────────────▶│
    │                                        ServerHello:  │
    │  ◀───────────────────────────────��────────────────────┤  key_share
    │  { }  EncryptedExtensions: ALPN, SNI                │  (server picks)
    │  { }  Certificate: server chain                     │
    │  { }  CertificateVerify: signature over transcript  │
    │  { }  Finished: MAC over the whole transcript       │
    │                                                    │
    │  { }  client Finished                               │
    ├────────────────────────────────────────────────────▶│
    │                                        Application data can flow
```

Three properties that matter operationally:

- **The transcript MAC.** Every handshake message is covered by a running hash, so any
  message cannot be altered or removed without detection — including a downgrade attack.
- **Forward secrecy.** Session keys derive from an ephemeral key exchange (ECDHE), so
  decrypting traffic later does not reveal the past session even with the long-term key.
- **Fewer round trips.** TLS 1.3 removes the need for a separate session ticket round, and
  all handshake messages after ServerHello are encrypted, which is why an observer cannot
  even see the certificate.

**Session resumption** uses a PSK instead of a full handshake: one round trip instead of
two, and with QUIC, **0-RTT**. Resumption keys are bound to the session ticket, so
resumption is only as strong as the ticket's confidentiality — another reason ticket
lifetime is a security parameter and not a convenience setting.

## 3. Certificate lifecycle: where TLS deployments actually fail

The protocol is rarely the problem. The operational failures are:

| Failure | Cause | Prevention |
|---|---|---|
| Expiry outage | No monitoring, or monitoring alerts on the wrong threshold | Alert at 14 days for a 30-day cert; automate renewal |
| Wrong hostname | CN-only certificate, or a SAN missing one alias | SANs are mandatory; verify the exact dialed name |
| Wrong issuer in chain | Intermediate omitted from the served chain | Serve the full chain; test from a clean trust store |
| Untrusted client | Client cert not trusted because the CA was rotated | Trust bundle rotation with overlap |
| Key compromise | Key on disk, in an image, or in an env var | Ephemeral keys, never persisted |

**Rotation without an outage** requires overlap. The sequence is fixed:

1. Generate the new key and certificate.
2. Publish the new certificate in the trust bundle, **keeping the old one**.
3. Wait for peers to observe the new bundle.
4. Switch to signing with the new certificate.
5. Wait for the maximum lifetime of anything still using the old certificate.
6. Remove the old certificate.

Doing 4 before 2 causes failures; doing 6 before 5 causes failures. The wait in step 3 is
the one people skip, and it is the reason a "just rotated the cert" incident happens at
00:05.

**Ephemeral keys** are the strongest available practice for workload identity: a key
generated in memory at startup, never written to disk. Then a leaked key expires with the
pod, and a compromised process cannot be reused to impersonate a service next week.

## 4. Mutual TLS and the authorisation gap

mTLS answers one question: *is the peer who it claims to be?* It does not answer *may this
peer do this?* Those are separate decisions and conflating them is the standard error.

```
  PKIX validation        -> chain to a trusted root, validity, revocation
  Authorisation          -> is THIS identity permitted on THIS path?
```

A valid certificate for `reporting-svc` presented to the payments endpoint passes PKIX and
must still be rejected by an authorisation policy. In a mesh, this second check is a
service-level policy; the certificate alone is not authorisation.

**Identity must come from the certificate, not a header.** A header asserting
`X-Service-Identity: orders-svc` is trivially forged by any workload on the network. If a
system accepts a header-based identity, its entire mesh authorisation is bypassable, and
the bypass is invisible in the code that uses it.

## 5. Segmentation as a measurable quantity

The most useful reframing: **segmentation is a reduction in the number of reachable
service pairs.** Each policy removes edges from a graph, and the remaining edges are the
blast radius.

```
  Flat network with N services:        reachable pairs = N x (N - 1)
  Segmented (each reaches k others):   reachable pairs = N x k

  N = 400, k = 3:  159,600  ->  1,200 pairs    (99.2% reduction)
```

That number is the business case, and unlike "we improved security" it is checkable in a
review. It also exposes bad policies immediately: a policy set that leaves one service
reaching 200 others is a rounding error in aggregate and a catastrophic one for that
service.

Tiers help: app tier, data tier, control plane. The rule that generates the most value is
**the control plane is unreachable from the service estate.** A compromise that reaches the
certificate authority, the secret store, or the CI runners is qualitatively different from
one that reaches a neighbouring service, because from the control plane an attacker can
mint identity for everything.

## 6. Exception governance is the real work

A default-deny policy in a real organisation accumulates exceptions, and exceptions are
where the default quietly dies. Each one needs:

- a **ticket** (so it is visible in the normal workflow),
- a **named owner** (so there is someone to ask),
- a **compensating control** (the real reason it exists is a limitation elsewhere),
- a **justification** (so a reviewer can judge whether it still applies),
- an **expiry date**, enforced by the system.

The expiry is the part that must be automated. A control that depends on a reviewer
remembering to revisit it in nine months is a control that has already decayed, and
expiry enforcement in code is the only version that works at scale.

## 7. What a network control cannot see

This is the section that keeps network security from being over-trusted:

- **Inside an encrypted connection.** With TLS, the network layer sees a destination and
  a size. It cannot see whether the request was authorised, or what it did. This is why
  network controls are not a substitute for application authorisation.
- **Application logic.** SQL injection, IDOR, business-logic abuse, and privilege
  escalation within a permitted connection are invisible to an IDS. They are the majority
  of real breaches.
- **Compromised legitimate endpoints.** A stolen credential on an allowed path is
  indistinguishable from a legitimate call at the network layer.
- **Encrypted east-west traffic you cannot inspect.** Not necessarily a problem — but it
  means the compensating control is application-level authorisation plus workload
  identity, and that trade-off should be stated rather than assumed.

The honest position: network controls bound *where* an attacker can go; they say nothing
about *what* they may do once there. Both layers are required, and each covers the other's
blind spot.

## 8. Continuous verification

A control should be tested on a schedule, not at audit time:

- **Reachability probes** from a rotating service identity, attempting every known target.
  Success on an undeclared path means the policy does not match reality.
- **Policy diffing** against version control, alerting on *widening* specifically. A
  narrowing is safe; a widening is either an attacker or a well-meaning engineer.
- **Certificate monitoring** as an SLO with a target of zero expiry incidents.
- **Quarterly adversary simulation** with a realistic objective ("reach the production
  database"), because a connectivity check does not test escalation, credential reuse, or
  tooling.

The reporting discipline matters as much as the testing. A quarterly report that states
which controls are verified, which are assumed, and which are known not to be covered is
worth far more to a reviewer than a claim of complete coverage — because the second one is
either wrong or untested.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 8446 defines TLS 1.3, including the one-round-trip handshake, the transcript MAC
  that prevents downgrade, the key schedule, and PSK-based resumption.
  https://www.rfc-editor.org/info/rfc8446/
- NIST SP 800-207 defines the zero-trust tenets — never trust, always verify, assume
  breach — that the continuous-verification approach operationalises.
  https://csrc.nist.gov/pubs/sp/800/207/final
