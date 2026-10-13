# Real-World Project: File Integrity Manifest
> SHA-256 manifest creation and verification that detects any tampering - concepts, standard library only.

## Problem
A directory of reference files needs tamper evidence: any changed byte must be reported.
This project practices hash-based integrity without inventing any cryptography.
## Inputs
- Target directory tree (up to 1000 files) and a manifest path.
- Manifest format: one line per file with hex digest, byte size, and relative path.
- Tamper fixture: a copy of a clean tree with exactly one flipped byte in one file.
## Steps
1. Walk the tree in sorted order, streaming each file through SHA-256 from the platform provider.
2. Write the manifest with digest, size, and relative path per line.
3. Verify mode re-hashes every file and compares against the manifest entry.
4. Report OK, MISSING, MODIFIED, or EXTRA per file with a nonzero exit code on any mismatch.
5. Demonstrate detection on the tamper fixture and show the single MODIFIED line.
6. Document that this gives integrity only, not secrecy or authenticity.
## Acceptance criteria
- Clean tree verifies with all-OK and exit code 0.
- Tamper fixture reports exactly one MODIFIED file with the right path.
- Deleted file reports MISSING and added file reports EXTRA.
- 1000-file tree verifies in under 120 seconds on the lab machine.
- Manifest diff of two identical trees is byte-identical (sorted order is deterministic).
## Failure modes
- Unreadable files are reported as errors with paths, not silent skips.
- Symlinks are listed and skipped with a note instead of followed blindly.
- Manifest itself is excluded from the tree it describes to avoid self-reference.
## Extensions
- HMAC mode sketch (conceptual): what changes if a secret key authenticates the manifest.
- Watch mode that re-verifies on a timer and appends to a log.
## How to demo
- Show the tamper-fixture run with the single MODIFIED line highlighted.
- Explain in the README why hashing detects change but does not hide content.
