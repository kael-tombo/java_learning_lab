# Mental Models: Memory Barriers

## 1. The four-gate fence (taxonomy)

A barrier is a fence with one gate per pair: LoadLoad, LoadStore,
StoreStore, StoreLoad. Plain code runs an open field (all gates open).
Release locks the two departure gates *before* the flag (nothing
published leaves early). Acquire locks the two arrival gates *after*
the flag (nothing observed arrives early). SC additionally locks the
diagonal StoreLoad gate *after* each store — the only gate x86 charges
for, and the only one Dekker needs. Buy gates per shape, never the
whole fence by default.

## 2. The roach motel (movement)

Plain operations are guests, sync regions the motel: guests check in
from both sides and never check out. Arrivals from above drift past the
acquire line into the region (harmless: they only see more); departures
from below drift up into it (harmless: they publish no earlier than the
flag). What never happens: a guest leaving early — a successor
escaping above an acquire, or a predecessor sinking below a release.
Publication is safe because checking in only adds witnesses;
post-hoc observation is unordered because nobody was held at the door.

## 3. The toll ladder (pricing)

Three toll booths: plain (free passage, no receipt), release (stamped
ticket, ~1.3 ns — pairwise receipt), volatile store (full inspection,
~10 ns — system receipt). Reads use the express lane (~1.3 ns either
way on x86). The expense report writes itself: stamp tickets for
pipelines (50000 intact at ticket price), pay inspection for mutual
observation (Dekker zero), never pay inspection for a ticket's job
(~8x waste per store) or tickets for an inspection's job (61-90%
failures retained).

## 4. The accident (plain MP 0/2000)

A commuter jaywalks daily and arrives alive: the crossing (StoreStore
on TSO) happens to be safe at this hour, on this street. The 0/2000 is
the commute log; the verdict (`race`) is the city ordinance — the
street (ARM), the hour (JIT hoisting), or the traffic (load) changes,
and the log means nothing. Cross at the light (volatile/latch): same
arrival time today, legal arrival every day, everywhere.

## 5. Ropes vs nets (chains vs total order, reprised)

Two ropes (release/acquire pairs) hold two climbers pairwise; the
crevasse between (cross observations) stays open — 61-90% fall through
wearing rope-grade gear on a net-grade problem. The net (StoreLoad both
sides) or the helicopter (lock: no climb at all) closes the gap to
zero. Message-passing is a single rope traverse (one chain suffices);
Dekker is a crevasse crossing (only nets or helicopters apply). Gear
labels do not change the terrain.

## 6. The whisper network (opaque)

Opaque is office gossip: every rumor (value) eventually reaches
everyone, atomically (no half-sentences), in no particular order, with
no guarantee about which memo (data) travels with which announcement
(flag). Fine for "how busy is the kitchen" (counters, stats); ruinous
for "the kitchen is closed, stop serving" (publication, guards). Never
route decisions through gossip when the building has intercoms
(release), inspections (volatile), and locks.
