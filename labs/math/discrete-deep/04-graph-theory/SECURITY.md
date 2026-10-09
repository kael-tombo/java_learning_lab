# Security: Graph Theory in Practice

## Attack Graphs Are Reachability Problems

Model an infrastructure as a directed graph: nodes = assets/privileges (user shell, service account, admin on host B, domain controller), edges = "this foothold enables that privilege" (exploit, misconfiguration, credential reuse). Whether an attacker reaches the domain-admin node from an internet-facing node is exactly a BFS/DFS reachability query — O(V+E) for the traversal, but the security content is in the *edges*. Miss one edge (an implicit trust, a scheduled task) and the answer flips from "safe" to "compromised": graph completeness, not algorithm choice, is where attack graphs fail.

A cycle in an *authorization* graph (A grants B grants C grants A) is privilege amplification: revocation must break every path, not just one edge.

## Certificate Chains Must Be Path-Validated DAGs

TLS/X.509 chains are paths in a graph: leaf ← intermediate ← root, each arrow signed by the next. Two graph-theoretic rules keep this safe:

- **Cycle rejection**: a chain that loops back is invalid; implementations that don't detect cycles can be fed a self-signed loop (CVE-class bugs in older chain validators).
- **Path building only through trusted roots**: the accepted set is "paths terminating at a pinned root," so an attacker's node, however well-formed, is unreachable from the trust anchor.

Also relevant: name constraints and `basicConstraints` (CA:FALSE) prune edges before traversal — deny-by-default edge filtering.

## Cycles as Denial-of-Service (Algorithmic Complexity)

- **Cyclic or very deep structures in parsers**: recursive descent over a cyclic object graph → stack overflow (uncontrolled recursion depth from attacker-supplied edges). XML "billion laughs" is a *fan-out* explosion: entity expansion forms a DAG where each level multiplies size — 10 edges per node over 10 levels = 10¹⁰ output from 100 input nodes. Mitigation: hard caps on nodes/edges visited, iterative traversal with a budget, cycle detection on identity.
- **Graph-shaped query inputs**: a "friend-of-friend" API that BFSes to depth d on a dense graph returns O(branchingᵈ) nodes — bound depth *and* total visited count (e.g., 10,000-node budget) or an attacker turns a graph query into CPU/memory exhaustion.

## Routing and the BGP Graph

The internet's interdomain routing graph is managed by BGP: a mis-originated prefix (an AS claiming a route it doesn't own) is an *edge forgery* in the AS graph. Route hijacks work because the protocol historically authenticated neither the origin nor the path; RPKI (Resource Public Key Infrastructure) signs origin assertions so routers can filter edges claiming unauthorized origins. Graph-level defenses = validating edge provenance, not path-finding speed.

## Social Graphs and De-Anonymization

Anonymized data (purchases, follow edges) is a labeled graph; a few known edges (Alice ↔ Bob) let an attacker align the anonymized graph to identities by matching local structure — the Netflix/ AOL de-anonymization results are graph-matching attacks. Mitigations: add noise to edges (differential privacy on the adjacency relation), suppress high-degree nodes, or release only aggregated degrees rather than the edge set.

## Fraud and Money-Laundering as Cycle Detection

Layering in money laundering means creating paths that return funds to the origin with intermediate hops (mule accounts). AML systems run community detection and cycle searches over transaction graphs: a 4-hop cycle with near-equal inflow/outflow is suspicious. False positives explode as you raise the hop limit — with branching factor b, candidate paths grow b^h, so detectors cap h at 3–6 and pre-aggregate. The detection quality is a parameter choice driven by exactly the O(b^h) growth of path counting.

## Practical Hardening Checklist

- Cap graph input: max nodes, max edges, max depth (parse-time rejection, O(1) checks).
- Traverse iteratively with a visited set and a global budget counter.
- Reject cycles on inputs that must be trees/DAGs (builds, cert chains, recursive configs).
- Validate edge *provenance*, not just reachability, in any authorization or routing context.
