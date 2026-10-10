# Security: Bloom Filter

## False positives as bypass budget

p = 1% means 1% of absent-item checks take the "present" path. If that
path grants anything without exact confirmation (access, skip of
validation, cache-poison write), the FPR is an attacker success rate at
scale — 10k probes yield ~100 bypasses. Hits must confirm exactly; size p
from the cost of a wrongful hit, not from memory convenience.

## Filter-poisoning via saturation

An attacker able to insert (user-generated keys into a shared filter)
pushes load past design n → p → 1 → every query takes the expensive path
(CPU/disk/network amplification) or every gate opens. Mitigations: cap
inserts at design n with rebuild/rotation, authenticate insert paths,
monitor set-bit fraction (≈1/2 healthy) as a saturation alarm.

## Hash predictability

Non-keyed finalizers let attackers precompute colliding inputs that share
bit positions, inflating FPR for targeted keys (or forcing chosen false
positives). If inputs are adversarial, key the hash (secret seed, SipHash-
style) and treat the seed as sensitive — mismatched seeds across nodes
also break unions, so version seeds with the filter.

## Information leakage

Filter bits reveal set membership probabilistically to anyone holding the
filter (Safe-Browsing-style offline brute force: test candidate items
locally). Don't ship filters of sensitive sets (passwords, private IDs)
to untrusted clients — a filter is a lossy but queryable copy of the set.

## Deletion illusion

"Removed" items still query positive (bits shared) — revocation via
filter alone is broken. Pair with an exact revocation check or rotate to a
rebuilt filter excluding the item.
