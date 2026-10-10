# Mental Models: ArrayList Deep Dive

## 1. Slots plus overflow
Think of `java.util.ArrayList` as numbered slots plus an overflow strategy: resizable array: Object[] elementData + size, contiguous storage.
Position first (growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf), then resolve the few items that share it.

## 2. Thresholds as tripwires
lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10 — each is a tripwire that converts a cheap shape into a
scalable one (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)). Below the wire, linear scan is fine; above it,
you pay for structure once and save on every later op.

## 3. Views as windows, not photos
`SubList view + fail-fast Itr/ListItr` is a window into the live store. Writing through the
window writes the room. Copy when you need a photo.

## 4. Nulls as contract, not accident
fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks. The rule exists so "absent" stays distinguishable from
"present" under the class's concurrency/ordering guarantees.

## 5. Growth cost as rent
set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it; two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact). You pay rent (copies/rotations) rarely and in bulk;
steady-state ops stay cheap. Presizing is paying a year up front.

## 6. The extra gear
MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves). That detail is what separates a passing interview answer
from one that matches `java.util.ArrayList`.
- Lab note (04-arraylist-deep/MENTAL_MODELS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/MENTAL_MODELS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/MENTAL_MODELS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/MENTAL_MODELS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
