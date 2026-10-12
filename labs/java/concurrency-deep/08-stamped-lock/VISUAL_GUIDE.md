# StampedLock — Visual Guide

## The three modes at a glance

```
WRITE:        [W][version v]  exclusive; readers block, optimism returns 0
PESS. READ:   [R=n][version v]  n readers coexist; writer waits for n -> 0
OPTIMISTIC:   sample v ... copy fields ... validate(v still current?)
```

## Happy-path optimistic read (no writer)

```
Reader                      State word
  |  tryOptimisticRead() ---> [v7, no W]  returns v7
  |  cx = x, cy = y           (plain reads)
  |  validate(v7) ----------> [v7, no W]  MATCH -> use (cx, cy)
```

## Writer intervenes (validation fails)

```
Reader                      Writer                 State word
  |  sample v7                 |                      v7
  |  cx = x (old)              | writeLock, mutate    v7+W
  |  cy = y ...                | unlockWrite          v8
  |  validate(v7) --------> MISMATCH (v7 vs v8): discard, readLock, re-read
```

## Stamp 0 path (writer holding at sample time)

```
Reader                      State word
  |  tryOptimisticRead() ---> [W set]  returns 0
  |  copy (may be mid-write!) 
  |  validate(0) -----------> always FALSE -> fallback to readLock()
```

Never skip validation: the 0 path still copies garbage first.

## Upgrade outcomes

```
SOLE READER:   readLock --tryConvert--> [W]  success, no window
CONTENDED:     readLock --tryConvert--> 0     unlockRead + writeLock fallback
OPT + FREE:    optimistic --tryConvert--> [W] success
OPT + BUSY:    optimistic --tryConvert--> 0   take writeLock explicitly
```

## Reentrancy trap

```
Thread A: writeLock (held)
Thread A: writeLock again ---> enqueued behind itself ---> waits forever
(no owner field exists to notice both requests are from A)
```

Sanctioned shape: pass the stamp INTO callees; never re-acquire inside.

## Condition refusal

```
asReadLock().newCondition()  ---> UnsupportedOperationException
asWriteLock().newCondition() ---> UnsupportedOperationException
(no wait-sets anywhere in the design)
```

## Unlock pairing

```
readLock / writeLock / convert-success  --> exactly one unlock* each
unlockRead  unlockWrite  unlock(stamp-generic, slower)
NEVER double-unlock; NEVER skip; try/finally always.
```
