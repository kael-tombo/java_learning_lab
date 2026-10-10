# Why It Matters: ArrayList Deep Dive

## Everyday impact
- Nearly every request path touches `java.util.ArrayList` (caches, indexes, params, models).
  growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf is why those lookups stay flat as data grows.

## Cost impact
- two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact); set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it. One presize decision at startup can remove the only
  latency spikes the structure ever produces.

## Correctness impact
- lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10; fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks. Getting either wrong silently corrupts lookups —
  entries that exist but never match.

## Concurrency impact
- unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList. Choosing the wrong variant turns a fast map into a race log.

## Interview signal
- Stating growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf + lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10 + two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact) with the numbers (8/6/64,
  0.75/16, 1.5x/2x, RED=false/BLACK=true as applicable) separates recall
  from understanding. Extra credit: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_MATTERS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
