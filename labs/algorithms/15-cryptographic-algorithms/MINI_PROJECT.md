# Mini Project: Hash Manifest Lite
> SHA-256 integrity checks for a folder, using only the platform provider.

## Background
- A manifest maps each file to its SHA-256 hex digest; verify recomputes and compares.
- Streaming keeps memory flat no matter the file size.
- This project covers integrity only - no secrecy, no signatures.
## Goal
Write manifest-create and manifest-verify for a directory tree.
Demonstrate tamper detection on a fixture with one flipped byte.
## Tasks
1. Walk a directory in sorted order and stream each file through SHA-256.
2. Write manifest lines as hex digest, byte size, relative path.
3. Verify by re-hashing and reporting OK, MODIFIED, MISSING, or EXTRA per file.
4. Build a tamper fixture (copy a clean tree, flip one byte) and show the report.
5. Time hashing of a 100 MB generated file and record MB/s.
6. Document the integrity-only guarantee and two things it does not provide.
## Acceptance criteria
- Clean tree verifies all-OK with exit code 0.
- Tamper fixture reports exactly one MODIFIED path.
- Deleted and added files report MISSING and EXTRA respectively.
- 100 MB file hashes without memory growth (streaming confirmed).
- README states the two non-guarantees explicitly.
## Pitfalls
- Reading whole files into memory instead of streaming.
- Comparing digests with early-exit equals in a security context.
- Hashing the manifest file itself and chasing a moving target.
- Assuming matching digests prove authorship (they prove integrity only).
## Stretch
- Tamper-timing table: detection latency vs file count.
- HMAC sketch (conceptual): which line changes if a key is introduced.
## Timebox
One evening session, roughly 2 hours with fixtures.
