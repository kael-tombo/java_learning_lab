# File-Sync Integrity Checker on Merkle Proofs

Story. Two replicas of a 10k-file dataset must converge over a slow
link without re-sending everything. Block hashes roll up into a Merkle
root; differing subtrees pinpoint changed blocks, and inclusion proofs
of O(log n) hashes let either side verify a block against the root.

Tree build. Files chunked to 64 KB blocks, leaves SHA-256 hashed, pairs
up to the root with odd-leaf duplication documented. Root for the
fixture is published in the repo so any tampering with the fixture is
itself detectable.

Sync protocol. Exchange roots; on mismatch, descend to disagreeing
children and sync only those leaves. The counted win is bytes sent vs
full copy on scripted change sets (1 percent, 10 percent, 50 percent of
blocks touched).

Proof duties. prove(block) returns sibling hashes plus direction bits;
verify(block, proof, root) recomputes upward. Proofs checked against an
independent verifier on 5k random blocks; proof size must equal tree
depth exactly.

Transparency caller. Append-only audit log where each entry's inclusion
is provable against the published root; auditors sample 1k entries and
all verify. Second-preimage caution documented: domain-separated leaf
vs interior hashing.

Tamper drills. Flip one byte in a block (root changes, proof path
names the leaf), reorder two chunks (root changes), truncate the proof
(verify rejects), swap leaf/interior roles (domain tags reject).

Hand in. Tree, sync CLI, verifier, byte-saving table, tamper logs.
Scoring: proof exactness 12, sync savings counted 10, tamper handling 8.
## Sync ledger
- Root published per release.
- Change-set sizes: 1, 10, 50 percent.
- Bytes-saved table updated.
- Tamper drill monthly.
- Verifier version pinned.
