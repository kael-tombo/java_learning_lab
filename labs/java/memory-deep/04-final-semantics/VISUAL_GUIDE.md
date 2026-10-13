# Visual Guide: Final Field Semantics

## The freeze chain (normal publication)

```
writer thread                        reader thread
------------                         -------------
w: this.a = v                        r1: h = shared
w: this.s = "n"+v                         |  (memory chain)
w: this.arr = {v, v+1}                    v
f: [constructor end: FREEZE]         r1 received
         |  hb
a: shared = new Holder(...) -------> h (non-null)
                                          |  (dereference chain)
                                          v
                                     r2: h.a, h.s, h.arr[i]
                                     ==> observes w (3000/3000)
```

## The escape (chain broken at link 2)

```
writer thread                        reader thread
------------                         -------------
a: published = this  ----EARLY-----> r1: p = published (non-null!)
   (no freeze yet)                        |
   ... 300 ms window ...                  v
                                     r2: p.x ==> 0 (default, LEGAL)
w: this.x = 42  (too late)
f: [constructor end: FREEZE]
```

The freeze postdates publication: nothing stands between `w` and the
early `r2`. Default 0 is a conforming observation.

## Transitivity (finals of finals)

```
Holder (freeze F_outer)
 +-- final int a            (store -> F_outer)
 +-- final String s         (store -> F_outer)
 +-- final int[] arr  -----> [v, v+1]  (element stores -> inner freeze
       (ref store -> F_outer)           -> F_outer -> publication)
```

Both freezes precede publication, so elements ride the composed chain.
Aliasing a caller-owned array cuts the inner link: element stores sit
outside construction and travel unprotected.

## Reference vs contents (the boundary)

```
final List<String> tags -----> List.of("a","b")   SAFE (immutable)
final List<String> tags -----> new ArrayList<>()  RACY contents
      ^                          ^
      | safe publication          | ordinary race rules
      (freeze)                    (needs own sync)
```

## String's two finals

```
String ---- final byte[] value ----> [p,a,y,l,o,a,d,...]  (transitive)
       ---- final byte coder  ---> 0 or 1
Racy handoff of the String reference still delivers both intact.
```
