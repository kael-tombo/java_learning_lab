# Reflection: ArrayList Deep Dive

## What did you actually learn?
- Write the position rule from memory: growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf.
- Write the thresholds: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10. When do they *not* apply?

## Where did you get surprised?
- Growth (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)) vs your prior assumption — what changed?
- Null behavior (fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks) — did you predict it correctly before testing?

## Transfer check
- Given a new structure with the same shape (resizable array: Object[] elementData + size, contiguous storage), which invariant
  would you verify first, and how?
- Extra detail to retain: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).

## Calibration
- Rate 1-5: can you explain `add/get/set/remove/ensureCapacity/trimToSize` at the field level without notes?
- If below 4: redo EXERCISES.md #1 and #6, then re-take QUIZ.md.

## One-line synthesis
- `java.util.ArrayList`: position via growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf, scale via two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact), iterate via
  SubList view + fail-fast Itr/ListItr — everything else is commentary.
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFLECTION.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
