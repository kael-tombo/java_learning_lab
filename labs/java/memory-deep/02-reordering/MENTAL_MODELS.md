# Mental Models: Reordering

## 1. The outbox tray (store buffer)

Each core has an outbox: sent mail (stores) sits in the tray until the
post room (coherent cache) collects it, while new incoming mail
(loads) is read immediately. Dekker is two offices each posting a
letter then instantly checking for the other's — both checks happen
while both letters are still in trays. The 1 ns drain is waiting for
the collection round before checking: same letters, ordered world.

## 2. The suggestion, not the schedule (source order)

Source order is a recipe's listed order ("chop, then boil"); the
kitchen (JIT, CPU, buffers) reorders steps that do not depend on each
other to keep burners busy. One cook never notices (dinner identical);
two cooks sharing one pantry notice constantly (ingredients moved).
Synchronization actions are the steps marked "do not rearrange across
this line" — everything else is the kitchen's business.

## 3. The starting pistol vs the photo finish

Free-running threads are marathoners starting whenever they arrive:
head-to-head moments are accidental. Barrier phasing is a group warm-up
that stretches the pack. The volatile-flag rendezvous is a starting
pistol for a ten-meter dash — both sprinters explode within
milliseconds by construction, so the photo (the racy window) catches
them together ~79% of the time. Rates measure the pistol, never the
runners' guilt (the verdict).

## 4. The one-hole fence (x86-TSO)

Picture a fence with four gates (LoadLoad, LoadStore, StoreStore,
StoreLoad): three locked, one open. Plain message-passing walks at a
locked gate (passes by luck of the fence, not by right). Dekker walks
at the open gate every round. "Strong hardware" means three locks, not
four — and the program that needs the fourth fails loudly.

## 5. Chains vs nets (release/acquire vs volatile)

Release/acquire ties two ropes (my release to your acquire, yours to
mine) — each rope holds its pair, but the middle still sags: the cross
observations slip through (61-90% anomalies). Full volatile strings a
net (StoreLoad fences both sides): nothing passes. Message-passing
needs one rope (snippet 4: 50000 intact); mutual observation needs the
net. Buying rope for a net's job is the characteristic misuse.

## 6. Three detectives (elimination)

Three suspects (compiler, CPU, buffers) for the missing order. The
drain interrogation changes only one's alibi (time in buffer) and the
crime stops — case closed against the buffer on x86, with the caveat
that on ARM the other two have records too (more pairs escape). Good
debugging, like good detective work, convicts by difference: change one
variable, watch the verdict, never trust the lineup (rates) alone.
