# Why Build Your Own HashMap

Reading `HashMap.get` teaches the API; building a probing table teaches
the constraints. Every shortcut you consider — skipping the spread,
nulling on delete, ignoring tombstones in load math, copying slots on
resize — produces a table that passes small tests and fails at scale.
Each failure is one production outage you now recognize:

- Missing spread → systematic collisions on real-world hash distributions
  (`31*x`-style multipliers vary high bits most).
- Null-on-delete → phantom misses for keys beyond the hole — data loss
  that looks like data absence.
- Tombstone-blind load factor → a "half full" table probing like a full
  one — latency cliffs with no size change to explain them.
- Copy-instead-of-rehash → runs and garbage preserved across growth —
  paying O(n) for zero benefit.

The lab also draws the real boundary: chaining (HashMap) vs probing (your
table, IdentityHashMap, Python dict). Knowing both families — when cache
locality beats graceful degradation and vice versa — is what turns "I can
use a HashMap" into "I can choose a hash table".
## The five decisions as outage archetypes

Each skipped decision maps to a real incident class: missing spread →
latency cliffs on skewed keys (HashDoS-adjacent); null-on-delete → silent
data loss reading as absence; tombstone-blind load → "half full but slow"
mysteries; copy-resize → O(n) pauses buying nothing. Building the table
once converts all four from mysteries into checklist items — which is the
lab's real deliverable, more than the table itself. Keep the probe table
(2.5 / 6 / 50) taped to your monitor until the cap values become reflex.
